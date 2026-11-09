# Common data and panel builder for Figure 4 and Supplementary Figure S4 (optimal SPEI scale, question 1).
# Input: data/processed/drought_q1/analysis1_cells.csv. Nothing is recomputed: shares of cells by optimal scale.
# Main variables (SIF/APAR, NDVI, EVI): cells with significant r* (permutation test). Secondary variables (SIF,
# SIF/PAR, fPAR): no permutation test, all cells (descriptive, as in docs/results_q1_drought.md).

source("R/manuscript_figures/style.R")
q <- cfg$drought_q1
alpha <- as.numeric(q$analysis1$alpha); h1_min <- as.numeric(q$analysis1$h1_min_fraction)
scales_d <- as.integer(unlist(q$spei$scales_days))
MAIN_V <- c("sif_apar", "ndvi", "evi"); SEC_V <- c("sif", "sif_par", "fpar")
# fuel classes of the figure: closed and open forest merged as "Forest" (as the forest stratum in panel c)
FUEL_FIG <- c(closed_forest = "Forest", open_forest = "Forest", shrubland = "Shrubland", wet_heath = "Heathland",
              grassland = "Grassland")
ARID_LAB <- c(semiarid = "Semi-arid", dry_subhumid = "Dry sub-humid", humid = "Humid")

scale_cells <- read_csv(file.path(root, "data/processed/drought_q1/analysis1_cells.csv"), show_col_types = FALSE) |>
  filter(explanatory == "spei", !is.na(scale_days), (variable %in% MAIN_V & p < alpha) | variable %in% SEC_V) |>
  mutate(var = factor(VAR_LAB[variable], levels = unname(VAR_LAB[c(MAIN_V, SEC_V)])),
         scale = factor(scale_days, levels = scales_d))

# Share of cells by scale per facet; the facet label carries the counts (in the order of the variables)
share_panel <- function(d, facet_col, facet_levels, title = NULL, y_lab) {
  d <- d |> mutate(facet = factor(.data[[facet_col]], levels = facet_levels), var = droplevels(var))
  sh <- d |> count(facet, var, scale, .drop = FALSE) |> group_by(facet, var) |>
    mutate(n_cells = sum(n), share = ifelse(n_cells > 0, n / n_cells, NA_real_)) |> ungroup()
  lab <- sh |> distinct(facet, var, n_cells) |> group_by(facet) |>
    summarise(lab = sprintf("%s\nn = %s", first(facet), paste(n_cells, collapse = " / ")), .groups = "drop")
  sh <- sh |> left_join(lab, by = "facet") |> mutate(lab = factor(lab, levels = lab[order(facet)] |> unique()))
  ggplot(sh, aes(scale, share, fill = var)) +
    geom_col(position = position_dodge(width = 0.85), width = 0.8, colour = "grey30", linewidth = 0.1,
             na.rm = TRUE) +
    facet_wrap(~lab, nrow = 1) +
    scale_fill_manual(values = VAR_COL, name = NULL) +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1), expand = expansion(mult = c(0, 0.05))) +
    labs(x = "Optimal SPEI scale (days)", y = y_lab, title = title) + theme_ms() +
    theme(legend.position = "bottom", legend.margin = margin(0, 0, 0, 0),
          strip.text = element_text(size = BASE_PT - 0.5, lineheight = 0.95),
          plot.title = element_text(size = BASE_PT + 0.5, family = FONT))
}
