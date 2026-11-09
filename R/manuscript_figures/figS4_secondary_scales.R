# Supplementary Figure S4: optimal SPEI scale of SIF, SIF/PAR and fPAR (question 1, double column), same format as
# Figure 4 (a) and (b). These variables have no permutation test: all cells, descriptive. Counts in the panel
# headers, in the order SIF / SIF/PAR / fPAR.
# Usage (from the repository root): Rscript R/manuscript_figures/figS4_secondary_scales.R

source("R/manuscript_figures/scales_common.R")
YLAB <- "Share of cells (all cells)"
sec_cells <- scale_cells |> filter(variable %in% SEC_V)
pa <- share_panel(sec_cells |> filter(fuel_class %in% names(FUEL_FIG)) |> mutate(fuel = FUEL_FIG[fuel_class]),
                  "fuel", unique(FUEL_FIG), y_lab = YLAB) + guides(fill = guide_legend(nrow = 1))
pb <- share_panel(sec_cells |> filter(stratum == "shrubland") |> mutate(arid = ARID_LAB[aridity_class]), "arid",
                  ARID_LAB, title = "Shrubland and heathland, by aridity class", y_lab = YLAB) +
  theme(legend.position = "none")
p <- pa / (pb + plot_spacer() + plot_layout(widths = c(1.6, 1))) + plot_layout(heights = c(1, 1)) + tags_abc()
save_fig(p, "figS4_secondary_scales", WIDTH_DOUBLE, 140)
