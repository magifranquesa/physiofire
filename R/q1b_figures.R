# Figures of Q1b (docs/plan_q1b.md; results in docs/results_q1b.md). Reads the outputs of
# `python -m physiofire.drought_q1b` and `python -m physiofire.drought_q1b_report`; it changes nothing in the
# analysis. Figures marked "post hoc" show diagnostics declared after seeing the result.
#
# Output ({drought_q1b.fig_dir}):
#   q1b_h3b.png               H3b by stratum against NDVI and EVI (mean paired score, CI) and season (descriptive)
#   q1b_time_to_response.png  cumulative share responded by day, shrubland, by season (censoring at +90)
#   q1b_analysis1.png         H1 (PAR-corrected, robust to noise, sensitivities) and H2b by stratum
#   q1b_lag_spei090.png       lag at SPEI-90 with lags -15..+60 (backward mean): masses at the boundaries
#   q1b_posthoc_left_censored.png  post hoc: H3b without pairs "responding" at the window start, by season
# Usage (from the repository root): Rscript R/q1b_figures.R

source("R/config.R")
suppressPackageStartupMessages({ library(readr); library(dplyr); library(tidyr); library(ggplot2); library(patchwork) })
cfg <- load_config(); root <- find_repo_root(); qb <- cfg$drought_q1b; q <- cfg$drought_q1
od <- file.path(root, qb$out_dir); fig_dir <- file.path(root, qb$fig_dir)
dir.create(fig_dir, showWarnings = FALSE, recursive = TRUE)
alpha <- as.numeric(q$analysis1$alpha)
th <- theme_bw(base_size = 9) + theme(panel.grid.minor = element_blank(), legend.position = "bottom")
save <- function(p, f, w = 180, h = 110) ggsave(file.path(fig_dir, f), p, width = w, height = h, units = "mm", dpi = 300)
st_lab <- c(shrubland = "Shrubland\n(decides)", forest = "Forest", grassland = "Grassland\n(reference)",
            wet_heath_only = "Heathland only\n(descriptive)")
var_lab <- c(sif_apar = "SIF/APAR", ndvi = "NDVI", evi = "EVI")
var_col <- c(`SIF/APAR` = "#d95f02", NDVI = "#1b7837", EVI = "#762a83")
ag_col <- c(NDVI = "#1b7837", EVI = "#762a83")
pd <- position_dodge(width = 0.6)

h <- read_csv(file.path(od, "hypotheses_q1b.csv"), show_col_types = FALSE) |>
  mutate(against = toupper(against), stratum = factor(st_lab[stratum], levels = rev(st_lab)))

# 1. H3b -------------------------------------------------------------------------------------------------------
lab_test <- c(H3b = "All events (criterion)", H3b_season_spring_descriptive = "Spring onsets (descriptive)",
              H3b_season_summer_descriptive = "Summer onsets (descriptive)",
              H3b_backward_par_corrected_sens = "Backward, PAR-corr. (sens.)")
h3 <- h |> filter(test %in% names(lab_test)) |>
  mutate(test = factor(lab_test[test], levels = lab_test), met = ifelse(met, "met", "not met"))
p <- ggplot(h3, aes(mean_score, stratum, colour = against, shape = met)) +
  geom_vline(xintercept = 0, colour = "grey50") +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.2, orientation = "y", position = pd, na.rm = TRUE) +
  geom_point(size = 2, position = pd, na.rm = TRUE) +
  geom_text(aes(label = sprintf("%d ev., d=%+.0f", n_events, median_d)), size = 2, position = pd, vjust = -0.9,
            na.rm = TRUE, show.legend = FALSE) +
  facet_wrap(~test, nrow = 1) + scale_colour_manual(values = ag_col, name = "Against") +
  scale_shape_manual(values = c(met = 16, `not met` = 1), name = NULL, drop = FALSE) +
  scale_x_continuous(expand = expansion(mult = 0.15)) +
  labs(x = "Mean paired score over events (< 0: SIF/APAR responds first)", y = NULL,
       caption = "d: median over events of the median paired difference in response day (days); criterion: CI < 0 and d <= -5") + th
save(p, "q1b_h3b.png", w = 220, h = 95)

# 2. time to response --------------------------------------------------------------------------------------------
km <- read_csv(file.path(od, "summary_time_to_response.csv"), show_col_types = FALSE) |>
  filter(stratum == "shrubland") |>
  mutate(variable = factor(var_lab[variable], levels = var_lab),
         season = factor(season, levels = c("all", "spring", "summer"),
                         labels = c("All events", "Spring onsets", "Summer onsets")))
nlab <- km |> group_by(season, variable) |> summarise(n = first(n), .groups = "drop") |>
  group_by(season) |> summarise(lab = paste(sprintf("%s n=%d", variable, n), collapse = "\n"), .groups = "drop")
p <- ggplot(km, aes(day, cum_share_responded, colour = variable)) + geom_vline(xintercept = 0, colour = "grey60") +
  geom_step() + facet_wrap(~season) + scale_colour_manual(values = var_col, name = NULL) +
  geom_text(data = nlab, aes(x = 90, y = 0.02, label = lab), inherit.aes = FALSE, hjust = 1, vjust = 0, size = 2.2) +
  labs(x = "Day relative to drought onset (SPEI-90, definition B)", y = "Cumulative share responded",
       title = "Time to response, shrubland cell-episodes in events (observed variables)",
       caption = "Censored at +90 days (no response in the window). Responses at -30: already <= -0.5 SD at the window start") + th
save(p, "q1b_time_to_response.png", h = 85)

# 3. analysis 1 ---------------------------------------------------------------------------------------------------
lab1 <- c(H1_par_corrected = "H1 PAR-corrected", H1_robust_noise = "H1 robust to noise",
          H1_centred_sens = "H1 centred (sens.)", H1_partial_sens = "H1 partial r (sens.)")
h1 <- h |> filter(test %in% names(lab1)) |> mutate(test = factor(lab1[test], levels = lab1),
                                                   met = ifelse(met, "met", "not met"))
p1 <- ggplot(h1, aes(fraction, stratum, colour = against, shape = met)) +
  geom_vline(xintercept = 0.5, colour = "grey50") +
  geom_vline(xintercept = as.numeric(q$analysis1$h1_min_fraction), colour = "firebrick", linetype = 2) +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.2, orientation = "y", position = pd, na.rm = TRUE) +
  geom_point(size = 2, position = pd, na.rm = TRUE) + facet_wrap(~test, nrow = 1) +
  scale_colour_manual(values = ag_col, name = "Against") +
  scale_shape_manual(values = c(met = 16, `not met` = 1), name = NULL, drop = FALSE) +
  labs(x = "Fraction of cells with a shorter SIF/APAR scale", y = NULL, title = "H1") + th
lab2 <- c(H2b = "H2b backward mean", H2b_centred_sens = "H2b centred (sens.)")
h2 <- h |> filter(test %in% names(lab2)) |> mutate(test = factor(lab2[test], levels = lab2),
                                                   met = ifelse(met, "met", "not met"))
p2 <- ggplot(h2, aes(median_diff, stratum, colour = against, shape = met)) +
  geom_vline(xintercept = 0, colour = "grey50") +
  geom_vline(xintercept = as.numeric(q$analysis1$h2_max_median_lag_diff_days), colour = "firebrick", linetype = 2) +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.2, orientation = "y", position = pd, na.rm = TRUE) +
  geom_point(size = 2, position = pd, na.rm = TRUE) +
  geom_text(aes(label = sprintf("n=%d (-%d edge)", n_cells, n_boundary_excluded)), size = 2, position = pd,
            vjust = -0.9, na.rm = TRUE, show.legend = FALSE) +
  facet_wrap(~test, nrow = 1) + scale_colour_manual(values = ag_col, name = "Against") +
  scale_shape_manual(values = c(met = 16, `not met` = 1), name = NULL, drop = FALSE) +
  scale_x_continuous(expand = expansion(mult = 0.2)) +
  labs(x = "Median lag difference at SPEI-90 (days)", y = NULL, title = "H2b") + th
save((p1 / p2) + plot_layout(guides = "collect", heights = c(1, 1)) & theme(legend.position = "bottom"),
     "q1b_analysis1.png", w = 220, h = 150)

# 4. lag at SPEI-90 ------------------------------------------------------------------------------------------------
c1 <- read_csv(file.path(od, sprintf("analysis1b_cells_%s.csv", qb$analysis1$smoothing)), show_col_types = FALSE)
lg <- c1 |> filter(explanatory == "spei", variable %in% names(var_lab), p_h2 < alpha, stratum %in% names(st_lab)) |>
  mutate(variable = factor(var_lab[variable], levels = var_lab), stratum = factor(st_lab[stratum], levels = st_lab))
p <- ggplot(lg, aes(lag_h2)) + geom_histogram(binwidth = 2, boundary = 0, fill = "grey40") +
  geom_vline(xintercept = 0, colour = "firebrick", linetype = 2) +
  facet_grid(stratum ~ variable, scales = "free_y") +
  labs(x = "Lag of maximum correlation with SPEI-90 (days), backward 15-day mean", y = "Cells",
       caption = "Lags allowed -15..+60; the backward mean delays every variable by about 7 days") + th
save(p, "q1b_lag_spei090.png", h = 110)

# 5. post hoc: left-censored pairs ---------------------------------------------------------------------------------
lc <- read_csv(file.path(od, "summary_posthoc_h3b_left_censored.csv"), show_col_types = FALSE) |>
  mutate(against = toupper(against), stratum = factor(st_lab[stratum], levels = rev(st_lab)),
         pairs = factor(pairs, levels = c("all_pairs", "without_left_censored"),
                        labels = c("All pairs", "Without pairs responding at day -30")),
         season = factor(season, levels = c("all", "spring", "summer"),
                         labels = c("All events", "Spring onsets", "Summer onsets")))
p <- ggplot(lc, aes(mean_score, stratum, colour = against)) + geom_vline(xintercept = 0, colour = "grey50") +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.2, orientation = "y", position = pd, na.rm = TRUE) +
  geom_point(size = 2, position = pd, na.rm = TRUE) + facet_grid(pairs ~ season) +
  scale_colour_manual(values = ag_col, name = "Against") +
  labs(x = "Mean paired score over events (< 0: SIF/APAR responds first)", y = NULL,
       title = "Post hoc: H3b without left-censored pairs, by season of onset") + th
save(p, "q1b_posthoc_left_censored.png", h = 110)
message("wrote figures in ", fig_dir)
