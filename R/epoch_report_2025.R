# Report of the 2025 case (superposed epoch, main series): figures for the main variables, lead times with a
# fire-level bootstrap interval, the burned - control comparison of FWI against SIF/APAR, and the evaluation of the
# decision criterion as written in CLAUDE.md / methods 2.10. Reads the outputs of R/epoch_analysis.R; it changes
# no analysis parameter.
#
# Lead time (point estimate): rule of methods 2.10 (lead_time(): mean difference >= threshold SD in the expected
# sign with a CI excluding 0 on every day up to day -1). Bootstrap interval: fires resampled with replacement
# (B = epoch.bootstrap_n, seed = random_seed); in each replicate the lead time is the earliest day from which the
# replicate's mean difference stays >= threshold in the expected sign up to day -1 (no CI condition inside the
# replicate); 2.5-97.5 percentiles and the fraction of replicates with a lead time > 0.
#
# Usage (from the repository root): Rscript R/epoch_report_2025.R

source("R/config.R")
source("R/epoch_lib.R")
suppressPackageStartupMessages({ library(readr); library(tidyr) })
cfg <- load_config(); root <- find_repo_root(); ec <- cfg$epoch
out_dir <- file.path(root, ec$out_dir)
fig_dir <- file.path(cfg$paths$figures, "epoch")
B <- as.integer(ec$bootstrap_n); lev <- as.numeric(ec$ci_level); seed <- as.integer(cfg$random_seed)
thr <- as.numeric(ec$effect_threshold_sd); sgn <- ec$expected_sign
main <- ec$main_series
vars <- c("sif_apar_nopersist", "sif_apar", "ndvi", "evi", "fwi", "aed")
lab <- c(sif_apar_nopersist = "SIF/APAR (no fPAR persistence)", sif_apar = "SIF/APAR (5-day persistence)",
         ndvi = "NDVI (Terra + Aqua)", evi = "EVI (Terra + Aqua)", fwi = "FWI (ERA5-Land)",
         aed = "AED (ET0, ERA5-Land)")

fd <- read_csv(file.path(out_dir, "epoch_fire_days.csv"), show_col_types = FALSE,
               col_types = cols(fire_id = col_character())) |>
  filter(series == main, variable %in% vars) |>
  mutate(fuel = clc_group)

lead_boot <- function(d, s, threshold, B, seed) {
  # d: fire x day table (fire_id, day_rel, diff) for one variable
  w <- d |> select(fire_id, day_rel, diff) |> pivot_wider(names_from = day_rel, values_from = diff)
  m <- as.matrix(w[, as.character(sort(as.integer(names(w)[-1])))])
  days <- sort(as.integer(colnames(m)))
  set.seed(seed)
  lead_of <- function(mu) {
    met <- !is.na(mu) & s * mu >= threshold
    if (!met[length(met)]) return(0L)
    k <- max(which(!met), 0L)
    as.integer(-days[k + 1])
  }
  boots <- replicate(B, lead_of(colMeans(m[sample.int(nrow(m), replace = TRUE), , drop = FALSE], na.rm = TRUE)))
  c(boot_lo = unname(quantile(boots, 0.025)), boot_hi = unname(quantile(boots, 0.975)),
    p_lead_gt0 = mean(boots > 0), lead_mean_rule = lead_of(colMeans(m, na.rm = TRUE)))
}

groups <- list(all = function(x) TRUE, shrubland = function(x) x$fuel == "shrubland",
               heathland = function(x) x$fuel == "wet_heath")
eff_all <- list(); leads <- list()
for (gname in names(groups)) {
  sub <- fd[groups[[gname]](fd), ]
  eff <- effect_table(sub, strata = character(), B = B, level = lev, seed = seed) |> mutate(group = gname)
  eff_all[[gname]] <- eff
  for (v in vars) {
    s <- variable_sign(v, sgn)
    for (what in c("diff", "burned")) {
      pt <- lead_time(eff[eff$variable == v, ], sgn, thr, what = what)$lead_days
      dd <- sub[sub$variable == v, ] |> mutate(diff = if (what == "diff") diff else burned)
      bt <- lead_boot(dd, s, thr, B, seed)
      leads[[length(leads) + 1]] <- data.frame(group = gname, variable = v, measure = what,
                                               n_fires = n_distinct(dd$fire_id), lead_days = pt, t(bt))
    }
  }
}
eff_all <- bind_rows(eff_all)
leads <- bind_rows(leads)
write_csv(eff_all, file.path(out_dir, "report2025_effects.csv"))
write_csv(leads, file.path(out_dir, "report2025_lead_times.csv"))

# --- Figures: burned - control and burned alone, main variables, by group --------------------------------------
fig_vars <- c("sif_apar_nopersist", "ndvi", "evi", "fwi", "aed")
for (gname in names(groups)) {
  e <- eff_all |> filter(group == gname, variable %in% fig_vars) |>
    mutate(variable = factor(lab[variable], levels = lab[fig_vars]))
  nf <- n_distinct(fd$fire_id[groups[[gname]](fd)])
  long <- bind_rows(
    e |> transmute(variable, day_rel, est = mean_diff, lo = ci_lo, hi = ci_hi, panel = "Burned − control"),
    e |> transmute(variable, day_rel, est = mean_burned, lo = burned_ci_lo, hi = burned_ci_hi, panel = "Burned cells"))
  p <- ggplot(long, aes(day_rel, est)) +
    geom_hline(yintercept = 0, colour = "grey40", linewidth = 0.3) +
    geom_hline(yintercept = c(-thr, thr), colour = "grey70", linetype = "dashed", linewidth = 0.3) +
    geom_ribbon(aes(ymin = lo, ymax = hi), fill = "steelblue", alpha = 0.25) +
    geom_line(colour = "steelblue4", linewidth = 0.6) +
    facet_grid(panel ~ variable, labeller = label_wrap_gen(18)) +
    labs(x = "Days relative to ignition", y = "Standardised anomaly (SD)",
         title = sprintf("2025 case, %s (%d fires); median-DOY anomalies, 15-day trailing mean; 95%% bootstrap CI",
                         gname, nf)) +
    theme_bw(base_size = 9) + theme(panel.grid.minor = element_blank())
  ggsave(file.path(fig_dir, sprintf("report2025_epoch_%s.png", gname)), p, width = 220, height = 110, units = "mm",
         dpi = 200)
}

# --- FWI vs SIF/APAR: burned - control on the same axes ---------------------------------------------------------
cmp <- eff_all |> filter(variable %in% c("fwi", "sif_apar_nopersist")) |>
  mutate(variable = lab[variable], group = factor(group, levels = names(groups)))
p <- ggplot(cmp, aes(day_rel, mean_diff, colour = variable, fill = variable)) +
  geom_hline(yintercept = 0, colour = "grey40", linewidth = 0.3) +
  geom_hline(yintercept = c(-thr, thr), colour = "grey70", linetype = "dashed", linewidth = 0.3) +
  geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi), alpha = 0.15, colour = NA) +
  geom_line(linewidth = 0.7) +
  facet_wrap(~group, nrow = 1) +
  scale_colour_manual(values = c("#b2182b", "#2166ac"), aesthetics = c("colour", "fill")) +
  labs(x = "Days relative to ignition", y = "Burned − control (SD)", colour = NULL, fill = NULL,
       title = "Burned − control difference: FWI vs SIF/APAR (expected sign: FWI +, SIF/APAR −)") +
  theme_bw(base_size = 9) + theme(legend.position = "bottom", panel.grid.minor = element_blank())
ggsave(file.path(fig_dir, "report2025_fwi_vs_sifapar.png"), p, width = 220, height = 90, units = "mm", dpi = 200)

options(width = 200)
print(leads |> mutate(across(where(is.numeric), ~ round(.x, 3))), row.names = FALSE)
win <- eff_all |> filter(variable %in% c("fwi", "sif_apar_nopersist"), day_rel >= -15) |>
  group_by(group, variable) |>
  summarise(mean_diff_last15 = round(mean(mean_diff, na.rm = TRUE), 2),
            days_ci_excl0 = sum(ci_lo > 0 | ci_hi < 0, na.rm = TRUE), .groups = "drop")
print(as.data.frame(win))
message("wrote report2025_* in ", out_dir, " and ", fig_dir)
