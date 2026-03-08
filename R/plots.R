
plot_density <- function(sample) {
  ggplot2::ggplot() +
    ggplot2::geom_density(
      ggplot2::aes(x = sample)
    )
}

plot_2d_density <- function(data, x, y) {
  ggplot2::ggplot() +
    ggplot2::geom_density2d_filled(
      data = data,
      ggplot2::aes(x = !!rlang::sym(x), y = !!rlang::sym(y))
    ) +
    ggplot2::xlim(c(0, 20)) +
    ggplot2::ylim(c(0, 20))
}
