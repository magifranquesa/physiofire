# Superposed-epoch statistics and figures (simplified 2025 analysis).
#
# Input:  standardised anomalies from physiofire.epoch (long table: fire_id, grid, cell_id, group, weight, variable,
#         series, day_rel, z) and the cell table from R/epoch_cells.R (for the fire's vegetation group) and the
#         fires table (for the country).
# Main result: per day (-60 .. -1), the mean across fires of the burned - control difference (SD units), its
#         fire-level bootstrap CI and the paired effect size dz; the burned-cell anomaly alone; lead times (earliest
#         day from which the effect stays >= epoch.effect_threshold_sd in the expected sign with a CI excluding 0).
#         All results also stratified by vegetation stratum (epoch.strata: woodland, shrubland, grassland, other,
#         from the fire's dominant CORINE group) and by country. Main series: epoch.main_series (median by day of
#         year); the LOESS series is a sensitivity run.
# Output: {out_dir}/epoch_effects_*.csv, epoch_lead_times.csv, figures/epoch/epoch_*.png
#
# Usage (from the repository root):
#   Rscript R/epoch_analysis.R <anomalies.csv> [cells.csv] [fires.csv] [out_dir] [fig_dir]

source("R/config.R")
source("R/epoch_lib.R")
suppressPackageStartupMessages(library(readr))
cfg <- load_config()
root <- find_repo_root()
ec <- cfg$epoch
args <- commandArgs(trailingOnly = TRUE)
if (!length(args)) stop("usage: Rscript R/epoch_analysis.R <anomalies.csv> [cells.csv] [fires.csv] [out_dir] [fig_dir]")
out_dir <- if (length(args) >= 4) args[4] else file.path(root, ec$out_dir)
fig_dir <- if (length(args) >= 5) args[5] else file.path(cfg$paths$figures, "epoch")   # cfg$paths already absolute
cells_csv <- if (length(args) >= 2) args[2] else file.path(out_dir, "epoch_cells.csv")
fires_csv <- if (length(args) >= 3) args[3] else file.path(root, ec$selected_fires)
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(fig_dir, showWarnings = FALSE, recursive = TRUE)

anom <- read_csv(args[1], col_types = cols(fire_id = col_character(), cell_id = col_character(),
                                           .default = col_guess()), progress = FALSE)
fire_veg <- read_csv(cells_csv, col_types = cols(fire_id = col_character(), .default = col_guess()),
                     progress = FALSE) |> distinct(fire_id, grid, veg = stratum, clc_group = fire_veg)
country <- read_csv(fires_csv, col_types = cols(fire_id = col_character(), .default = col_guess()),
                    progress = FALSE) |> distinct(fire_id, country)

fd <- fire_day_table(anom) |> left_join(fire_veg, by = c("fire_id", "grid")) |> left_join(country, by = "fire_id")
write_csv(fd, file.path(out_dir, "epoch_fire_days.csv"))
B <- as.integer(ec$bootstrap_n); lev <- as.numeric(ec$ci_level); seed <- as.integer(cfg$random_seed)
thr <- as.numeric(ec$effect_threshold_sd); sgn <- ec$expected_sign

strata_sets <- list(all = character(), vegetation = "veg", country = "country")
leads <- list()
for (nm in names(strata_sets)) {
  s <- strata_sets[[nm]]
  eff <- effect_table(fd, strata = s, B = B, level = lev, seed = seed)
  write_csv(eff, file.path(out_dir, sprintf("epoch_effects_%s.csv", nm)))
  for (what in c("diff", "burned")) {
    leads[[length(leads) + 1]] <- lead_time(eff, sgn, thr, strata = s, what = what) |> mutate(strata = nm)
  }
  for (g in unique(eff$grid)) {
    e <- eff[eff$grid == g, ]
    if (!length(s)) {
      p <- plot_epoch(e, sprintf("All fires, %s grid", g), thr)
      ggsave(file.path(fig_dir, sprintf("epoch_all_%s.png", g)), p, width = 180, height = 100, units = "mm", dpi = 200)
    } else {
      for (lv in unique(na.omit(e[[s]]))) {
        p <- plot_epoch(e[!is.na(e[[s]]) & e[[s]] == lv, ], sprintf("%s = %s, %s grid", nm, lv, g), thr)
        ggsave(file.path(fig_dir, sprintf("epoch_%s_%s_%s.png", nm, gsub("[^A-Za-z0-9]", "", lv), g)), p,
               width = 180, height = 100, units = "mm", dpi = 200)
      }
    }
  }
}
lt <- bind_rows(leads)
write_csv(lt, file.path(out_dir, "epoch_lead_times.csv"))
print(as.data.frame(lt |> filter(strata == "all")))
message("wrote ", out_dir, " and ", fig_dir)
