
gamma <- function(alpha0, beta0, sample) {
  alpha <- alpha0 + length(sample)
  beta <- beta0 + sum(sample)

  list(alpha = alpha, beta = beta)
}

mle_mvn <- function(Z, n) {
  mu <- colMeans(Z)
  Sigma <- t(Z - mu) %*% (Z - mu) / n
  return(list(mu = mu, Sigma = Sigma))
}