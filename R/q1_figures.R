# Figures of question 1 (docs/plan_q1_drought.md; results in docs/results_q1_drought.md). Reads the outputs of
# `python -m physiofire.drought_q1 analysis` and `python -m physiofire.drought_q1_report`; it changes nothing in
# the analysis. Figures marked "post hoc" show diagnostics declared after seeing the result.
#
# Output ({drought_q1.fig_dir}):
#   q1_hypotheses.png       H1, H2, H3 by stratum against NDVI and EVI, with the pre-registered thresholds
#   q1_scale_share.png      share of cells by optimal SPEI scale, by variable and stratum
#   q1_scale_maps.png       optimal SPEI scale of SIF/APAR, NDVI and EVI (cells with significant r*)
#   q1_lag_spei090.png      lag at SPEI-90 (cells significant at that scale): mass at 0 (censoring)
#   q1_posthoc_events.png   post hoc: responding cells per drought event (August events)
#   q1_posthoc_par.png      post hoc: lag-0 correlations with AED and SPEI-30, raw and given PAR
# Usage (from the repository root): Rscript R/q1_figures.R

source("R/config.R")
suppressPackageStartupMessages({ library(readr); library(dplyr); library(tidyr); library(ggplot2); library(patchwork) })
cfg <- load_config(); root <- find_repo_root(); q <- cfg$drought_q1
od <- file.path(root, q$out_dir); fig_dir <- file.path(root, q$fig_dir)
dir.create(fig_dir, showWarnings = FALSE, recursive = TRUE)
alpha <- as.numeric(q$analysis1$alpha)
a1 <- q$analysis1; a2 <- q$analysis2
th <- theme_bw(base_size = 9) + theme(panel.grid.minor = element_blank(), legend.position = "bottom")
save <- function(p, f, w = 180, h = 110) ggsave(file.path(fig_dir, f), p, width = w, height = h, units = "mm", dpi = 300)

st_lab <- c(shrubland = "Shrubland\n(decides)", forest = "Forest", grassland = "Grassland\n(reference)",
            wet_heath_only = "Heathland only\n(descriptive)")
var_lab <- c(sif_apar = "SIF/APAR", ndvi = "NDVI", evi = "EVI", sif = "SIF", sif_par = "SIF/PAR", fpar = "fPAR")
ag_col <- c(ndvi = "#1b7837", evi = "#762a83")

# 1. hypotheses -------------------------------------------------------------------------------------------------
h <- read_csv(file.path(od, "hypotheses.csv"), show_col_types = FALSE) |>
  mutate(stratum = factor(st_lab[stratum], levels = rev(st_lab)), against = toupper(against),
         est = ifelse(hypothesis == "H1", fraction, median_diff),
         lab = ifelse(hypothesis == "H3", sprintf("%s ev.", n_events), sprintf("n=%d", n_cells)),
         met = ifelse(met, "met", "not met"))
pd <- position_dodge(width = 0.6)
panel <- function(hh, title, xlab, ref, thr) {
  ggplot(hh, aes(est, stratum, colour = against, shape = met)) +
    geom_vline(xintercept = ref, colour = "grey50") +
    geom_vline(xintercept = thr, colour = "firebrick", linetype = 2) +
    geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.2, orientation = "y", position = pd, na.rm = TRUE) +
    geom_point(size = 2, position = pd, na.rm = TRUE) +
    geom_text(aes(label = lab), size = 2.2, position = position_dodge(width = 0.6), vjust = -0.9, na.rm = TRUE,
              show.legend = FALSE) +
    scale_colour_manual(values = setNames(ag_col, toupper(names(ag_col))), name = "Against") +
    scale_shape_manual(values = c(met = 16, `not met` = 1), name = NULL, drop = FALSE) +
    scale_x_continuous(expand = expansion(mult = 0.15)) +
    labs(title = title, x = xlab, y = NULL) + th
}
p1 <- panel(filter(h, hypothesis == "H1"), "H1: optimal scale shorter", "Fraction of cells (SIF/APAR shorter)",
            0.5, as.numeric(a1$h1_min_fraction))
p2 <- panel(filter(h, hypothesis == "H2"), "H2: lag at SPEI-90", "Median lag difference (days)", 0,
            as.numeric(a1$h2_max_median_lag_diff_days))
p3 <- panel(filter(h, hypothesis == "H3"), "H3: response day", "Median over events (days)", 0,
            as.numeric(a2$h3_max_median_diff_days))
save((p1 | p2 | p3) + plot_layout(guides = "collect") & theme(legend.position = "bottom"), "q1_hypotheses.png",
     h = 95)

# 2. share of optimal scale ---------------------------------------------------------------------------------------
sh <- read_csv(file.path(od, "summary_scale_share.csv"), show_col_types = FALSE) |>
  filter(stratum != "wet_heath_only") |>
  mutate(stratum = factor(st_lab[stratum], levels = st_lab), variable = factor(var_lab[variable], levels = var_lab),
         scale_days = factor(scale_days))
p <- ggplot(sh, aes(variable, share, fill = scale_days)) + geom_col(width = 0.75) +
  facet_wrap(~stratum) + scale_fill_viridis_d(option = "C", direction = -1, name = "Optimal SPEI scale (days)") +
  labs(x = NULL, y = "Share of cells",
       caption = "SIF/APAR, NDVI, EVI: cells with significant r*; SIF, SIF/PAR, fPAR: all cells (descriptive)") +
  th + theme(axis.text.x = element_text(angle = 45, hjust = 1))
save(p, "q1_scale_share.png", h = 90)

# 3. maps of optimal scale ----------------------------------------------------------------------------------------
c1 <- read_csv(file.path(od, "analysis1_cells.csv"), show_col_types = FALSE) |> filter(explanatory == "spei")
m <- c1 |> filter(variable %in% c("sif_apar", "ndvi", "evi"), p < alpha) |>
  mutate(variable = factor(var_lab[variable], levels = var_lab[c("sif_apar", "ndvi", "evi")]),
         scale_days = factor(scale_days))
p <- ggplot(m, aes(lon, lat, fill = scale_days)) + geom_tile(width = 0.05, height = 0.05) +
  facet_wrap(~variable) + coord_quickmap() +
  scale_fill_viridis_d(option = "C", direction = -1, name = "Optimal SPEI scale (days)") +
  labs(x = NULL, y = NULL, caption = "Cells with significant r* (year permutation, p < 0.05), all strata") + th
save(p, "q1_scale_maps.png", h = 80)

# 4. lag at SPEI-90 ----------------------------------------------------------------------------------------------
lg <- c1 |> filter(variable %in% c("sif_apar", "ndvi", "evi"), p_h2 < alpha, stratum != "wet_heath_only") |>
  mutate(variable = factor(var_lab[variable], levels = var_lab[c("sif_apar", "ndvi", "evi")]),
         stratum = factor(st_lab[stratum], levels = st_lab))
p <- ggplot(lg, aes(lag_h2)) + geom_histogram(binwidth = 2, boundary = 0, fill = "grey40") +
  facet_grid(stratum ~ variable, scales = "free_y") +
  labs(x = "Lag of maximum correlation with SPEI-90 (days)", y = "Cells",
       caption = paste("Lags allowed 0-60 days on a centred 15-day mean: the masses at 0 and 60 are censored",
                       "(true lag may be < 0 or > 60)")) + th
save(p, "q1_lag_spei090.png", h = 110)

# 5. post hoc: events ---------------------------------------------------------------------------------------------
ev <- read_csv(file.path(od, "posthoc_events.csv"), show_col_types = FALSE) |>
  filter(stratum == "shrubland") |>
  arrange(onset_first, event) |>
  mutate(event_lab = sprintf("Event %d\n%s %s, %d cells", event, month.abb[as.integer(format(onset_first, "%m"))],
                             format(onset_first, "%Y"), n_cells),
         event_lab = factor(event_lab, levels = unique(event_lab))) |>
  select(event_lab, n_cells, n_resp_sif_apar, n_resp_ndvi, n_resp_evi) |>
  pivot_longer(starts_with("n_resp_"), names_to = "variable", values_to = "n") |>
  mutate(variable = factor(var_lab[sub("n_resp_", "", variable)], levels = var_lab[c("sif_apar", "ndvi", "evi")]))
p <- ggplot(ev, aes(variable, n / n_cells, fill = variable)) + geom_col(width = 0.7) +
  geom_text(aes(label = sprintf("%d/%d", n, n_cells)), vjust = -0.3, size = 2.4) +
  facet_wrap(~event_lab, nrow = 1) + scale_y_continuous(limits = c(0, 1.1), breaks = seq(0, 1, 0.25)) +
  scale_fill_manual(values = c(`SIF/APAR` = "#d95f02", NDVI = "#1b7837", EVI = "#762a83"), guide = "none") +
  labs(x = NULL, y = "Share of shrubland cells with a response",
       title = "Post hoc: responses per drought event (shrubland stratum)",
       caption = "Response: anomaly <= -0.5 SD for >= 15 days within -30..+90 days of the SPEI-90 onset") + th
save(p, "q1_posthoc_events.png", h = 75)

# 6. post hoc: PAR -----------------------------------------------------------------------------------------------
pc <- read_csv(file.path(od, "posthoc_par_diagnostic.csv"), show_col_types = FALSE) |>
  filter(stratum != "wet_heath_only") |>
  select(stratum, ends_with("_median")) |>
  pivot_longer(-stratum, names_to = "k", values_to = "r") |>
  mutate(k = sub("_median$", "", k), given_par = grepl("_given_par$", k), k = sub("_given_par$", "", k)) |>
  filter(k %in% c("r_sifapar_aed", "r_sifapar_spei030", "r_ndvi_aed", "r_ndvi_spei030")) |>
  mutate(var = ifelse(grepl("sifapar", k), "SIF/APAR", "NDVI"), expl = ifelse(grepl("aed", k), "AED", "SPEI-30"),
         given_par = ifelse(given_par, "partial, given PAR", "raw"),
         stratum = factor(st_lab[stratum], levels = st_lab))
p <- ggplot(pc, aes(stratum, r, fill = given_par)) + geom_col(position = position_dodge(0.75), width = 0.7) +
  geom_hline(yintercept = 0) + facet_grid(expl ~ var) +
  scale_fill_manual(values = c(raw = "grey65", `partial, given PAR` = "#d95f02"), name = NULL) +
  labs(x = NULL, y = "Median r over cells (lag 0, April-October)",
       title = "Post hoc: is the SIF/APAR link carried by radiation (PAR)?") + th
save(p, "q1_posthoc_par.png", h = 100)
message("wrote figures in ", fig_dir)
