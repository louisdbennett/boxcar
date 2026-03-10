box::use(R/plots)
box::use(R/posteriors)
box::use(R/tests)

drivers <- readxl::read_excel('data-raw/drivers.xlsx')
riders <- readxl::read_excel('data-raw/riders.xlsx')

f <- \(loc) stringr::str_split(gsub('\\(|\\)', '', loc), ', ')

drivers$initial_location_x <- as.numeric(purrr::map_chr(f(drivers$initial_location), 1))
drivers$initial_location_y <- as.numeric(purrr::map_chr(f(drivers$initial_location), 2))

riders$pickup_location_x <- as.numeric(purrr::map_chr(f(riders$pickup_location), 1))
riders$pickup_location_y <- as.numeric(purrr::map_chr(f(riders$pickup_location), 2))

riders$dropoff_location_x <- as.numeric(purrr::map_chr(f(riders$dropoff_location), 1))
riders$dropoff_location_y <- as.numeric(purrr::map_chr(f(riders$dropoff_location), 2))

ndrivers <- nrow(drivers)
nriders <- nrow(riders)

driver_interarrivals <- drivers$arrival_time[-1] - drivers$arrival_time[-ndrivers]
rider_interarrivals <- riders$request_time[-1] - riders$request_time[-nriders]

plots$plot_density(driver_interarrivals, 'Driver Interarrivals')
plots$plot_density(rider_interarrivals, 'Rider Interarrivals')

p1 <- plots$plot_density(
  rgamma(10000, shape = 3, rate = 1),
  x_lab =  "Gamma(\u03B1 = 3, \u03B2 = 1)",
  x_lim = c(0, 15)
)

p2 <- plots$plot_density(
  rgamma(10000, shape = 300, rate = 100),
  x_lab = "Gamma(\u03B1 = 300, \u03B2 = 100)",
  x_lim = c(0, 15)
)

ggplot2::ggsave(
  "outputs/stats/gamma_dist.png",
  cowplot::plot_grid(p1, p2),
  width = 10,
  height = 4,
  units = 'in'
)

# perform Kolmogorov-Smirnov tests against recommendations
tests$ks(
  driver_interarrivals,
  pexp,
  rate = 3
)

tests$ks(
  rider_interarrivals,
  pexp,
  rate = 30
)

trust <- 1000
driver_params <- posteriors$gamma(trust * 3, trust, driver_interarrivals)
rider_params <- posteriors$gamma(trust * 30, trust, rider_interarrivals)

# perform prior and posterior predictive checks
driver_prior_predictive <- tests$predictive_dist(
  shape = trust * 3,
  rate = trust
)

driver_posterior_predictive <- tests$predictive_dist(
  shape = driver_params$alpha,
  rate = driver_params$beta
)

tests$predictive_ints(driver_prior_predictive)
tests$predictive_ints(driver_posterior_predictive)

mean(driver_interarrivals)
sd(driver_interarrivals)
sum((driver_interarrivals - mean(driver_interarrivals))^3) / length(driver_interarrivals) / (sd(driver_interarrivals)^3)

rider_prior_predictive <- tests$predictive_dist(
  shape = trust * 30,
  rate = trust
)

rider_posterior_predictive <- tests$predictive_dist(
  shape = rider_params$alpha,
  rate = rider_params$beta
)

tests$predictive_ints(rider_prior_predictive)
tests$predictive_ints(rider_posterior_predictive)

mean(rider_interarrivals)
sd(rider_interarrivals)
sum((rider_interarrivals - mean(rider_interarrivals))^3) / length(rider_interarrivals) / (sd(rider_interarrivals)^3)

## locations ----

plots$plot_2d_density(
  drivers,
  'initial_location_x',
  'initial_location_y',
  'Driver Online Locations'
)

p1 <- plots$plot_2d_density(
  riders, 
  'pickup_location_x', 
  'pickup_location_y',
  'Rider Online Locations'
)

p2 <- plots$plot_2d_density(
  riders,
  'dropoff_location_x',
  'dropoff_location_y',
  'Rider Destination Locations'
)

p3 <- plots$plot_2d_density(
  data.frame(
    dropoff_location_x = runif(10000, 0, 20),
    dropoff_location_y = runif(10000, 0, 20)
  ),
  'dropoff_location_x',
  'dropoff_location_y',
  'Uniform(0, 20) Locations'
)

ggplot2::ggsave(
  "outputs/stats/rider_locations.png",
  cowplot::plot_grid(p1, p2, p3, nrow = 1),
  width = 12,
  height = 4,
  units = 'in'
)

tests$ks(
  riders$pickup_location_x,
  punif,
  min = 0,
  max = 20
)

tests$ks(
  riders$pickup_location_y,
  punif,
  min = 0,
  max = 20
)

tests$ks(
  riders$dropoff_location_x,
  punif,
  min = 0,
  max = 20
)

tests$ks(
  riders$dropoff_location_y,
  punif,
  min = 0,
  max = 20
)

Z <- as.matrix(riders[, c(
  "pickup_location_x",
  "pickup_location_y",
  "dropoff_location_x",
  "dropoff_location_y"
)])

rider_mle <- posteriors$mle_mvn(Z, nriders)

plots$plot_2d_density(
  as.data.frame(mnormt::rmnorm(
    10000,
    mean = rider_mle$mu[1:2],
    rider_mle$Sigma[1:2, 1:2]
  )),
  'pickup_location_x',
  'pickup_location_y'
)

plots$plot_2d_density(
  as.data.frame(
    mnormt::rmnorm(
      10000, 
      mean = rider_mle$mu[3:4], 
      rider_mle$Sigma[3:4, 3:4]
    )
  ),
  'dropoff_location_x',
  'dropoff_location_y'
)

tests$ks(
  drivers$initial_location_x,
  punif,
  min = 0,
  max = 20
)

tests$ks(
  drivers$initial_location_y,
  punif,
  min = 0,
  max = 20
)

taxi_mle <- posteriors$mle_mvn(
  as.matrix(drivers[, c('initial_location_x', 'initial_location_y')]),
  ndrivers
)

## taxi offline times
tests$ks(
  drivers$offline_time - drivers$arrival_time,
  punif,
  min = 6,
  max = 8
)


## rider cancellation times
pickup_mle <- 1 / mean(time_to_pickup[riders$pickup_time != -1])

props <- sapply(1:10000, \(i) {
  pickup_times <- rexp(10000, pickup_mle)
  cancel_times <- rexp(10000, 5)
  mean(pickup_times > cancel_times)
})

quantile(props, p = c(0.025, 0.0975))

mean(riders$pickup_time == -1)

time_to_pickup <- riders$pickup_time - riders$request_time
n_cancels <- sum(riders$pickup_time == -1)
n_pickups <- sum(riders$pickup_time != -1)

n_cancels / (n_pickups + n_cancels) * pickup_mle

## journey length
dist <- sqrt((riders$pickup_location_x - riders$dropoff_location_x) ^ 2 + (riders$pickup_location_y - riders$dropoff_location_y) ^ 2)
times <- riders$dropoff_time - riders$pickup_time

dist <- dist[!riders$dropoff_time == -1]
times <- times[!riders$dropoff_time == -1]

trip_time <- dist / 20

z <- times / trip_time

tests$ks(
  z,
  punif,
  min = 0.8,
  max = 1.2
)

tests$ks(
  z,
  punif,
  min = min(z),
  max = max(z)
)

p <- plots$plot_density(z, x_lim = c(0.5, 1.5), x_lab = 'Normalised journey times')

ggplot2::ggsave('outputs/stats/unif.png', p, width = 8, height = 4, units = 'in')


a_hat <- min(z)
b_hat <- max(z)

ks_obs <- ks.test(z, "punif", a_hat, b_hat)$statistic

B <- 10000
ks_sim <- numeric(B)

for(i in 1:B){
  x_sim <- runif(length(z), a_hat, b_hat)
  a_s <- min(x_sim)
  b_s <- max(x_sim)
  ks_sim[i] <- ks.test(x_sim, "punif", a_s, b_s)$statistic
}

p_value <- mean(ks_sim >= ks_obs)
