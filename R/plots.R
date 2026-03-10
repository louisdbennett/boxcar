
plot_density <- function(sample, x_lab = NULL, x_lim = c(NA_real_, NA_real_)) {
  ggplot2::ggplot() +
    ggplot2::geom_density(
      ggplot2::aes(x = sample)
    ) +
    ggplot2::ylab(NULL) +
    ggplot2::xlab(x_lab) +
    ggplot2::xlim(x_lim) +
    ggplot2::theme_minimal()
}

plot_2d_density <- function(data, x, y, title) {
  ggplot2::ggplot() +
    ggplot2::geom_density2d_filled(
      data = data,
      ggplot2::aes(x = !!rlang::sym(x), y = !!rlang::sym(y))
    ) +
    ggplot2::xlim(c(0, 20)) +
    ggplot2::ylim(c(0, 20)) +
    ggplot2::labs(title = title) +
    ggplot2::theme_void() +
    ggplot2::theme(
      legend.position = 'none',
      plot.title = ggplot2::element_text(hjust = 0.5)
    )
}
