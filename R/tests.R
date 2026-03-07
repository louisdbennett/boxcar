ks <- function(x, cdf, ...) {
  n <- length(x)
  
  x <- sort(x)
  
  Fx <- cdf(x, ...)
  
  i <- seq_len(n)
  D <- max(max(i / n - Fx), max(Fx - (i - 1) / n))
  
  statistic <- (sqrt(n) + 0.12 + 0.11 / sqrt(n)) * D

  if(statistic >= 1.358) {
    return('reject')
  } else {
    return('accept')
  }
}
