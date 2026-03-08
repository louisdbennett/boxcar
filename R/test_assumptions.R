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

plots$plot_density(driver_interarrivals)
plots$plot_density(rider_interarrivals)

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

plots$plot_2d_density(drivers, 'initial_location_x', 'initial_location_y')
plots$plot_2d_density(riders, 'pickup_location_x', 'pickup_location_y')
plots$plot_2d_density(riders, 'dropoff_location_x', 'dropoff_location_y')

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

plots$plot_2d_density(
  data.frame(
    dropoff_location_x = runif(10000, 0, 20),
    dropoff_location_y = runif(10000, 0, 20)
  ),
  'dropoff_location_x',
  'dropoff_location_y'
)

taxi_mle <- posteriors$mle_mvn(
  as.matrix(drivers[, c('initial_location_x', 'initial_location_y')]),
  ndrivers
)
