ks <- function(x, cdf, ...) {
  n <- length(x)
  
  x <- sort(x)
  
  Fx <- cdf(x, ...)
  
  i <- seq_len(n)
  D <- max(max(i / n - Fx), max(Fx - (i - 1) / n))
  
  statistic <- (sqrt(n) + 0.12 + 0.11 / sqrt(n)) * D

  if(statistic >= 1.358) {
    return(list(statistic = statistic, result = 'reject'))
  } else {
    return(list(statistic = statistic, result = 'accept'))
  }
}

predictive_dist <- function(N = 1000, rep = 1000, shape, rate) {
  purrr::map(1:N, \(i) {
    samp_rate <- stats::rgamma(1, shape = shape, rate = rate)

    samp <- stats::rexp(rep, samp_rate)

    data.frame(
      mean = mean(samp),
      sd = stats::sd(samp),
      skewness = sum((samp - mean(samp))^3) / length(samp) / (stats::sd(samp)^3)
    )
  }) |> 
    purrr::list_rbind()
}

predictive_ints <- function(summ) {
  mean <- stats::quantile(
    summ$mean,
    probs = c(0.025, 0.0975),
    USE.NAMES = FALSE
  )

  sd <- stats::quantile(
    summ$sd,
    probs = c(0.025, 0.0975),
    USE.NAMES = FALSE
  )

  skewness <- stats::quantile(
    summ$skewness,
    probs = c(0.025, 0.0975),
    USE.NAMES = FALSE
  )

  list(mean = mean, sd = sd, skewness = skewness)
}
