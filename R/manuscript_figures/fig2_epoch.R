# Figure 2: superposed-epoch composites of the 2025 case (double column).
# Input: data/processed/epoch/report2025_effects.csv (R/epoch_report_2025.R; median-by-DOY anomalies, backward
# 15-day mean, bootstrap by fire). Rows: SIF/APAR without fPAR persistence, NDVI, EVI, FWI, AED; columns: all fires,
# shrubland, heathland. Solid line and shading: burned - control difference and its 95% interval; thin dashed line:
# anomaly of the burned cells alone. Horizontal lines at 0 and +-0.5 SD (lead-time threshold).
# Usage (from the repository root): Rscript R/manuscript_figures/fig2_epoch.R

source("R/manuscript_figures/style.R")
thr <- 0.5
vars <- c("sif_apar_nopersist", "ndvi", "evi", "fwi", "aed")
groups <- c(all = "All fires", shrubland = "Shrubland", heathland = "Heathland")
e <- read_csv(file.path(root, "data/processed/epoch/report2025_effects.csv"), show_col_types = FALSE) |>
  filter(variable %in% vars, group %in% names(groups)) |>
  mutate(var = factor(VAR_LAB[variable], levels = unname(VAR_LAB[vars])))
stopifnot(length(unique(e$series)) == 1)
nf <- e |> group_by(group, var) |> summarise(lo = min(n_fires), hi = max(n_fires), .groups = "drop") |>
  mutate(lab = ifelse(lo == hi, sprintf("%d fires", hi), sprintf("%d–%d fires per day", lo, hi)))
yl <- range(c(e$ci_lo, e$ci_hi, e$mean_diff, e$mean_burned, -thr, thr), na.rm = TRUE)

col_plot <- function(g) {
  d <- e |> filter(group == g)
  ggplot(d, aes(day_rel)) +
    geom_hline(yintercept = 0, colour = "grey40", linewidth = 0.3) +
    geom_hline(yintercept = c(-thr, thr), colour = "grey55", linewidth = 0.25, linetype = "dotted") +
    geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi, fill = var), alpha = 0.25, na.rm = TRUE) +
    geom_line(aes(y = mean_burned, colour = var), linewidth = 0.3, linetype = "22", na.rm = TRUE) +
    geom_line(aes(y = mean_diff, colour = var), linewidth = 0.6, na.rm = TRUE) +
    geom_text(data = nf |> filter(group == g), aes(x = -59, y = yl[2], label = lab), inherit.aes = FALSE,
              hjust = 0, vjust = 1, size = (BASE_PT - 1) / .pt, family = FONT, colour = "grey30") +
    facet_grid(var ~ ., switch = "y") +
    scale_colour_manual(values = VAR_COL, guide = "none") + scale_fill_manual(values = VAR_COL, guide = "none") +
    scale_x_continuous(limits = c(-60, -1), breaks = c(-60, -45, -30, -15, -1), expand = c(0.01, 0)) +
    scale_y_continuous(limits = yl) +
    labs(title = groups[[g]], x = "Days before ignition", y = NULL) + theme_ms() +
    theme(plot.title = element_text(size = BASE_PT + 1, hjust = 0.5, family = FONT),
          strip.placement = "outside", strip.text.y.left = element_text(angle = 90))
}
ps <- lapply(names(groups), col_plot)
ps[2:3] <- lapply(ps[2:3], function(p) p + theme(strip.text.y.left = element_blank(), strip.background.y = element_blank()))
p <- wrap_plots(ps, nrow = 1) + tags_abc() &
  theme(plot.caption = element_text(size = BASE_PT - 1, hjust = 0, family = FONT))
p[[1]] <- p[[1]] + labs(y = "Standardised anomaly (SD)")
save_fig(p, "fig2_epoch_2025", WIDTH_DOUBLE, 170)
