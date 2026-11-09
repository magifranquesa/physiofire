# EXPLORATORY time-series figures (config explore_timeseries): descriptive only, no statistics, part of no
# criterion. Reads {out_dir}/explore_cells.csv and explore_series.csv (python -m physiofire.explore_timeseries).
#
# One figure per August 2025 fire (burned cell + 2 controls) and one for the summer 2022 drought (4 shrubland cells):
# rows SIF/APAR, NDVI, EVI (standardised anomaly: daily in light grey, backward 15-day mean in colour) and SPEI-90;
# April-October of the case year; vertical line at the ignition (fires) or drought onset (SPEI-90, definition B).
# Output: {fig_dir}/explore_fire_<country>_<fire_id>.png, explore_drought_2022.png
# Usage (from the repository root): Rscript R/explore_timeseries_figures.R

source("R/config.R")
suppressPackageStartupMessages({ library(readr); library(dplyr); library(ggplot2); library(scales) })
cfg <- load_config(); root <- find_repo_root(); et <- cfg$explore_timeseries
od <- file.path(root, et$out_dir); fig_dir <- file.path(root, et$fig_dir)
dir.create(fig_dir, showWarnings = FALSE, recursive = TRUE)
cells <- read_csv(file.path(od, "explore_cells.csv"), show_col_types = FALSE)
s <- read_csv(file.path(od, "explore_series.csv"), show_col_types = FALSE) |> mutate(date = as.Date(date))
var_lab <- c(sif_apar = "SIF/APAR", ndvi = "NDVI", evi = "EVI", spei_090 = "SPEI-90")
var_col <- c(`SIF/APAR` = "#d95f02", NDVI = "#1b7837", EVI = "#762a83", `SPEI-90` = "#2166ac")
ylim <- c(-4, 4)
invisible(Sys.setlocale("LC_TIME", "C"))                       # English month names
wrap <- function(x) paste(strwrap(x, width = 170), collapse = "\n")
th <- theme_bw(base_size = 8) + theme(panel.grid.minor = element_blank(), legend.position = "none",
                                      strip.text.y = element_text(face = "bold"),
                                      plot.title = element_text(face = "bold", colour = "firebrick"))

col_label <- function(r) {
  if (r$case_type == "fire") {
    what <- if (r$role == "burned") sprintf("BURNED (%.0f %% burned)", 100 * r$burned_fraction) else
      sub("control_", "Control ", r$role)
    sprintf("%s\n%s, %s (%.3f, %.3f)", what, r$cell_id, r$fuel_class, r$lon, r$lat)
  } else {
    sprintf("Event %s (%d cells), onset %s\n%s, %s (%.3f, %.3f)", sub("event_", "", r$role), r$event_cells,
            format(as.Date(r$marker_date), "%d %b"), r$cell_id, r$fuel_class, r$lon, r$lat)
  }
}

plot_case <- function(cs) {
  cc <- cells |> filter(case == cs)
  cc$col <- vapply(seq_len(nrow(cc)), function(i) col_label(cc[i, ]), "")
  d <- s |> filter(case == cs) |> left_join(cc |> select(role, col), by = "role") |>
    mutate(var = factor(var_lab[variable], levels = var_lab), col = factor(col, levels = cc$col))
  out <- d |> filter(variable != "spei_090") |>
    summarise(n = sum(!is.na(daily_z)), o = sum(abs(daily_z) > ylim[2], na.rm = TRUE))
  mk <- cc |> transmute(col = factor(col, levels = cc$col), date = as.Date(marker_date))
  yr <- as.integer(substr(cc$marker_date[1], 1, 4))
  xl <- as.Date(sprintf("%d-%02d-01", yr, as.integer(et$months[[1]]))) +
    c(0, as.numeric(as.Date(sprintf("%d-%02d-01", yr, as.integer(et$months[[2]]) + 1)) -
                    as.Date(sprintf("%d-%02d-01", yr, as.integer(et$months[[1]]))) - 1))
  p <- ggplot(d, aes(date)) + geom_hline(yintercept = 0, colour = "grey60", linewidth = 0.3)
  if (cc$case_type[1] == "fire") {
    bm <- mk |> filter(grepl("^BURNED", col))
    p <- p + geom_rect(data = bm, aes(xmin = date, xmax = xl[2], ymin = -Inf, ymax = Inf), inherit.aes = FALSE,
                       fill = "grey85", alpha = 0.6) +
      geom_text(data = bm, aes(x = date, y = ylim[1] + 0.3, label = " masked from ignition"), inherit.aes = FALSE,
                hjust = 0, size = 1.9, colour = "grey40")
  }
  p <- p + geom_vline(data = mk, aes(xintercept = date), colour = "firebrick", linetype = 2, linewidth = 0.4) +
    geom_point(aes(y = squish(daily_z, ylim)), colour = "grey75", size = 0.35, na.rm = TRUE) +
    geom_line(aes(y = smooth_z, colour = var), linewidth = 0.55, na.rm = TRUE) +
    facet_grid(var ~ col) + scale_colour_manual(values = var_col) +
    scale_x_date(limits = xl, date_breaks = "1 month", date_labels = "%b", expand = c(0, 0)) +
    scale_y_continuous(limits = ylim, oob = squish) + th
  if (cc$case_type[1] == "fire") {
    r <- cc[1, ]
    ttl <- sprintf("EXPLORATORY (descriptive only)\n%s, %s: %s ha, ignition %s", r$name, r$country,
                   format(r$burned_ha, big.mark = " "), r$marker_date)
    lab_v <- "ignition (dashed; also on the controls)"
  } else {
    ttl <- "EXPLORATORY (descriptive only) - summer 2022 drought, shrubland cells without fire (question 1 cells)"
    lab_v <- "drought onset of the cell (SPEI-90, definition B, dashed)"
  }
  p + labs(x = NULL, y = "Standardised anomaly (SD of the smoothed anomaly)   |   SPEI-90", title = ttl,
           caption = wrap(sprintf(paste0("Colour: backward 15-day mean of the median-by-DOY anomaly (2018-2025). Grey: ",
                                    "daily anomaly in the same units (%.1f %% of daily values beyond +-4, drawn at the ",
                                    "edge). Vertical line: %s. Not part of any criterion; cells chosen by a fixed rule ",
                                    "(config explore_timeseries)."), 100 * out$o / out$n, lab_v)))
}

for (cs in unique(cells$case)) {
  w <- if (startsWith(cs, "fire")) 190 else 240
  f <- file.path(fig_dir, sprintf("explore_%s.png", cs))
  ggsave(f, plot_case(cs), width = w, height = 150, units = "mm", dpi = 300)
  message("wrote ", f)
}
