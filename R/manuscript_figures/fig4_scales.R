# Figure 4: drought response scales (question 1, double column).
# Inputs: data/processed/drought_q1/analysis1_cells.csv (optimal SPEI scale per cell and variable, permutation p) and
# hypotheses.csv (H1 with 1-degree block bootstrap). Nothing is recomputed: shares of significant cells by scale.
# (a) optimal SPEI scale of SIF/APAR, NDVI, EVI (and SIF, SIF/PAR, fPAR in lighter tones) by fuel type;
# (b) the same for the shrubland stratum by aridity class (main variables); (c) H1 by stratum with the 0.60 line.
# Usage (from the repository root): Rscript R/manuscript_figures/fig4_scales.R

source("R/manuscript_figures/style.R")
q <- cfg$drought_q1
alpha <- as.numeric(q$analysis1$alpha); h1_min <- as.numeric(q$analysis1$h1_min_fraction)
scales <- as.integer(unlist(q$spei$scales_days))
main <- c("sif_apar", "ndvi", "evi"); sec <- c("sif", "sif_par", "fpar")
var_levels <- unname(VAR_LAB[c(main, sec)])
fuel_lab <- c(closed_forest = "Closed forest", open_forest = "Open forest", shrubland = "Shrubland",
              wet_heath = "Heathland", grassland = "Grassland")
arid_lab <- c(semiarid = "Semi-arid", dry_subhumid = "Dry sub-humid", humid = "Humid")

a <- read_csv(file.path(root, "data/processed/drought_q1/analysis1_cells.csv"), show_col_types = FALSE) |>
  # main variables: cells with significant r*; secondary (no permutation test): all cells, descriptive as in Q1
  filter(explanatory == "spei", !is.na(scale_days),
         (variable %in% main & p < alpha) | variable %in% sec) |>
  mutate(var = factor(VAR_LAB[variable], levels = var_levels), scale = factor(scale_days, levels = scales))

share <- function(d, ...) d |> count(..., var, scale, .drop = FALSE) |> group_by(..., var) |>
  mutate(n_sig = sum(n), share = ifelse(n_sig > 0, n / n_sig, NA_real_)) |> ungroup()

# checks against the manuscript text (section 3.2)
shr <- a |> filter(stratum == "shrubland")
msg <- shr |> group_by(variable) |> summarise(n_sig = n(), median_scale = median(scale_days),
                                              mode_scale = as.integer(names(which.max(table(scale_days)))))
print(as.data.frame(msg))
print(as.data.frame(shr |> filter(variable %in% main) |> group_by(aridity_class, variable) |>
                      summarise(median_scale = median(scale_days), n = n(), .groups = "drop")))

bars <- function(d) {
  ggplot(d, aes(scale, share, fill = var)) +
    geom_col(position = position_dodge(width = 0.85), width = 0.8, colour = "grey30", linewidth = 0.1) +
    scale_fill_manual(values = VAR_COL, name = NULL, drop = TRUE) +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1), expand = expansion(mult = c(0, 0.05))) +
    labs(x = "Optimal SPEI scale (days)", y = "Share of significant cells") + theme_ms()
}
nlab <- function(d) d |> distinct(across(-c(scale, n, share)), n_sig) |>
  group_by(across(-c(var, n_sig))) |>
  summarise(lab = paste(sprintf("%s %d", var, n_sig), collapse = "\n"), .groups = "drop")

# (a) by fuel type, six variables
da <- share(a |> filter(fuel_class %in% names(fuel_lab)), fuel_class) |>
  mutate(fuel = factor(fuel_lab[fuel_class], levels = fuel_lab))
pa <- bars(da) + facet_wrap(~fuel, nrow = 1) +
  geom_text(data = nlab(da |> select(fuel, var, scale, n, share, n_sig)), aes(x = 0.6, y = Inf, label = lab),
            inherit.aes = FALSE, hjust = 0, vjust = 1.1, size = (BASE_PT - 1.5) / .pt, family = FONT,
            lineheight = 0.9, colour = "grey30") +
  labs(y = "Share of cells") +
  theme(legend.position = "top", legend.margin = margin(0, 0, 0, 0)) +
  guides(fill = guide_legend(nrow = 1))

# (b) shrubland stratum by aridity class, main variables
db <- share(shr |> filter(variable %in% main) |> mutate(var = droplevels(var)), aridity_class) |>
  mutate(arid = factor(arid_lab[aridity_class], levels = arid_lab))
pb <- bars(db) + facet_wrap(~arid, nrow = 1) +
  geom_text(data = nlab(db |> select(arid, var, scale, n, share, n_sig)), aes(x = 0.6, y = Inf, label = lab),
            inherit.aes = FALSE, hjust = 0, vjust = 1.1, size = (BASE_PT - 1.5) / .pt, family = FONT,
            lineheight = 0.9, colour = "grey30") +
  theme(legend.position = "none")

# (c) H1 by stratum
st_lab <- c(shrubland = "Shrubland\n(decides)", forest = "Forest", grassland = "Grassland\n(reference)",
            wet_heath_only = "Heathland\n(descriptive)")
h <- read_csv(file.path(root, "data/processed/drought_q1/hypotheses.csv"), show_col_types = FALSE) |>
  filter(hypothesis == "H1", stratum %in% names(st_lab)) |>
  mutate(stratum = factor(st_lab[stratum], levels = rev(st_lab)), against = factor(toupper(against), c("NDVI", "EVI")))
pd <- position_dodge(width = 0.5)
pc <- ggplot(h, aes(fraction, stratum, colour = against)) +
  geom_vline(xintercept = 0.5, colour = "grey60", linewidth = 0.25) +
  geom_vline(xintercept = h1_min, colour = "grey15", linetype = "22", linewidth = 0.35) +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.25, orientation = "y", position = pd, linewidth = 0.4) +
  geom_point(size = 1.4, position = pd) +
  scale_colour_manual(values = VAR_COL, name = "SIF/APAR vs") +
  scale_x_continuous(limits = c(0.25, 1), breaks = seq(0.3, 1, 0.1)) +
  labs(x = "Fraction of cells with a shorter SIF/APAR scale (H1)", y = NULL) + theme_ms() +
  theme(legend.position = "top", legend.margin = margin(0, 0, 0, 0))

p <- pa / (pb + pc + plot_layout(widths = c(1.6, 1))) + plot_layout(heights = c(1, 1)) + tags_abc()
save_fig(p, "fig4_scales", WIDTH_DOUBLE, 140)
