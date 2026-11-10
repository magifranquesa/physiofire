# Figure 4: drought response scales (question 1, double column).
# Inputs: analysis1_cells.csv (via scales_common.R) and data/processed/drought_q1/hypotheses.csv (H1, 1-degree block
# bootstrap). (a) optimal SPEI scale of SIF/APAR, NDVI and EVI in significant cells by fuel type (closed and open
# forest merged); (b) the same in the shrubland stratum (shrubland and heathland) by aridity class; (c) H1 by stratum
# with the 0.60 criterion. Counts in the panel headers, in the order SIF/APAR / NDVI / EVI. SIF, SIF/PAR and fPAR:
# Supplementary Figure S4 (figS4_secondary_scales.R).
# Usage (from the repository root): Rscript R/manuscript_figures/fig4_scales.R

source("R/manuscript_figures/scales_common.R")
YLAB <- "Share of significant cells"
main_cells <- scale_cells |> filter(variable %in% MAIN_V)

# checks against the manuscript text (section 3.2)
shr <- main_cells |> filter(stratum == "shrubland")
print(as.data.frame(shr |> group_by(variable) |> summarise(n = n(), median = median(scale_days))))
print(as.data.frame(shr |> filter(variable == "sif_apar") |> group_by(aridity_class) |>
                      summarise(n = n(), median = median(scale_days),
                                mode = as.integer(names(which.max(table(scale_days)))))))

pa <- share_panel(main_cells |> filter(fuel_class %in% names(FUEL_FIG)) |> mutate(fuel = FUEL_FIG[fuel_class]),
                  "fuel", unique(FUEL_FIG), y_lab = YLAB) + guides(fill = guide_legend(nrow = 1))
pb <- share_panel(shr |> mutate(arid = ARID_LAB[aridity_class]), "arid", ARID_LAB,
                  title = "Shrubland and heathland, by aridity class", y_lab = YLAB) +
  theme(legend.position = "none")

st_lab <- c(shrubland = "Shrubland\nstratum", forest = "Forest", grassland = "Grassland\n(reference)",
            wet_heath_only = "Heathland only\n(descriptive)")
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
  theme(legend.position = "bottom", legend.margin = margin(0, 0, 0, 0))

p <- pa / (pb + pc + plot_layout(widths = c(1.6, 1))) + plot_layout(heights = c(1, 1)) + tags_abc()
save_fig(p, "fig4_scales", WIDTH_DOUBLE, 140)
