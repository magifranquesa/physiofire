# Figure 3 and Supplementary Figure S3: exploratory daily series (double column).
# Input: data/interim/explore/explore_{cells,series}.csv (python -m physiofire.explore_timeseries; descriptive only,
# cells chosen by a fixed rule before inspection). Main text: A Rua (fire 278475); Supplement S3: the other five
# fires and the summer 2022 drought. The exploratory status is stated in the caption, not in the figure.
# Columns: burned cell and two controls (fires) or one cell per drought event; rows SIF/APAR, NDVI, EVI (grey points:
# daily standardised anomaly; line: backward 15-day mean) and SPEI-90. Dashed line: ignition / drought onset.
# Usage (from the repository root): Rscript R/manuscript_figures/fig3_explore.R

source("R/manuscript_figures/style.R")
suppressPackageStartupMessages(library(scales))
et <- cfg$explore_timeseries
od <- file.path(root, et$out_dir)
cells <- read_csv(file.path(od, "explore_cells.csv"), show_col_types = FALSE)
s <- read_csv(file.path(od, "explore_series.csv"), show_col_types = FALSE) |> mutate(date = as.Date(date))
vars <- c("sif_apar", "ndvi", "evi", "spei_090")
ylim <- c(-4, 4)
MAIN_CASE <- "fire_ES_278475"                                       # A Rua

col_title <- function(r) {
  if (r$case_type == "fire") {
    head <- if (r$role == "burned") sprintf("Burned cell (%.0f%% burned)", 100 * r$burned_fraction) else
      sub("control_", "Control ", r$role)
  } else head <- sprintf("Event %s (%d cells)", sub("event_", "", r$role), r$event_cells)
  sprintf("%s\n%s, %s", head, sub("wet_heath", "heathland", r$fuel_class), fmt_coord(r$lon, r$lat))
}
fmt_coord <- function(lon, lat) sprintf("%.3f° %s, %.3f° %s", abs(lat), ifelse(lat >= 0, "N", "S"),
                                        abs(lon), ifelse(lon >= 0, "E", "W"))

col_plot <- function(r, first, month_step = 1) {
  d <- s |> filter(case == r$case, role == r$role, variable %in% vars) |>
    mutate(var = factor(VAR_LAB[variable], levels = unname(VAR_LAB[vars])))
  yr <- as.integer(substr(r$marker_date, 1, 4))
  xl <- as.Date(c(sprintf("%d-04-01", yr), sprintf("%d-10-31", yr)))
  mk <- as.Date(r$marker_date)
  p <- ggplot(d, aes(date)) + geom_hline(yintercept = 0, colour = "grey50", linewidth = 0.25)
  if (r$role == "burned")
    p <- p + annotate("rect", xmin = mk, xmax = xl[2], ymin = -Inf, ymax = Inf, fill = "grey88")
  mk_lab <- data.frame(var = factor(VAR_LAB[vars[1]], levels = unname(VAR_LAB[vars])), x = mk, y = ylim[2] - 0.2,
                       label = if (r$case_type == "fire") "Ignition" else "Drought onset")
  p <- p + geom_vline(xintercept = mk, colour = "grey15", linetype = "22", linewidth = 0.35) +
    geom_text(data = mk_lab, aes(x = x, y = y, label = label), inherit.aes = FALSE, hjust = 1.08, vjust = 1,
              size = (BASE_PT - 1) / .pt, family = FONT, colour = "grey15") +
    geom_point(aes(y = squish(daily_z, ylim)), colour = "grey65", size = 0.45, stroke = 0, na.rm = TRUE) +
    geom_line(aes(y = smooth_z, colour = var), linewidth = 0.5, na.rm = TRUE) +
    facet_grid(var ~ ., switch = "y") + scale_colour_manual(values = VAR_COL, guide = "none") +
    scale_x_date(limits = xl, date_breaks = sprintf("%d month", month_step), date_labels = "%b", expand = c(0, 0)) +
    scale_y_continuous(limits = ylim, oob = squish, breaks = c(-4, -2, 0, 2, 4)) +
    labs(title = col_title(r), x = NULL, y = if (first) "Standardised anomaly (SD) | SPEI" else NULL) + theme_ms() +
    theme(plot.title = element_text(size = BASE_PT, hjust = 0.5, family = FONT, lineheight = 0.95),
          strip.placement = "outside", strip.text.y.left = element_text(angle = 90))
  if (!first) p <- p + theme(strip.text.y.left = element_blank(), strip.background.y = element_blank())
  p
}

case_fig <- function(cs, name) {
  cc <- cells |> filter(case == cs)
  step <- if (nrow(cc) > 3) 2 else 1                                  # 4 columns (drought): every two months
  ps <- lapply(seq_len(nrow(cc)), function(i) col_plot(cc[i, ], i == 1, step))
  w <- WIDTH_DOUBLE
  save_fig(wrap_plots(ps, nrow = 1) + tags_abc(), name, w, if (nrow(cc) > 3) 120 else 130)
}

case_fig(MAIN_CASE, "fig3_explore_A_Rua")
others <- setdiff(unique(cells$case), MAIN_CASE)
for (i in seq_along(others)) case_fig(others[i], sprintf("figS3_%d_explore_%s", i, sub("^fire_", "", others[i])))
