# Fire sample of the 2025 case by rule (decided 2026-11-07), replacing the manual selection:
# all short-listed perimeters (EFFIS > shortlist.min_area_ha) of the selection stratum (epoch.selection.strata)
# with a valid ignition date (earliest-date rule, R/fire_candidates.R), no coherence flag and >= n_min controls.
# Exclusions are recorded in the columns `exclude` (TRUE/FALSE) and `exclude_reason`: by the general rule
# epoch.selection.max_days_before_effis (ignition too early relative to EFFIS) or by hand; if the output file
# already exists, those two columns are kept for the fires already listed.
#
# Input:  data/interim/fires/fire_shortlist_{year}.csv (R/fire_shortlist.R, after R/epoch_cells.R on the short list)
# Output: epoch.selected_fires (data/fires/selected_fires.csv)
#
# Usage (from the repository root): Rscript R/select_fires.R [year]

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
})
source("R/config.R")
cfg <- load_config()
root <- find_repo_root()
args <- commandArgs(trailingOnly = TRUE)
year <- if (length(args)) as.integer(args[1]) else as.integer(cfg$fires$first_case_year)
sel <- cfg$epoch$selection
out <- file.path(root, cfg$epoch$selected_fires)

tab <- read_csv(file.path(root, cfg$effis$out_dir, sprintf("fire_shortlist_%d.csv", year)),
                show_col_types = FALSE, col_types = cols(effis_id = col_character()))
if (any(is.na(tab$cells_status))) stop("short list without burned/control cells: run R/epoch_cells.R first")
n_min <- as.integer(cfg$epoch$controls$n_min)
s <- tab |>
  filter(stratum %in% unlist(sel$strata), !is.na(ignition_date), !coherence_flag,
         cells_status == "ok", n_controls >= n_min) |>
  arrange(desc(burned_ha)) |>
  transmute(fire_id = effis_id, country, name, burned_ha = round(burned_ha), ignition_date, ignition_source,
            effis_firedate = as.Date(effis_firedate), ignition_minus_effis_days, review_early,
            fuel_class = fire_veg, stratum, n_burned_cells, n_controls,
            selection_rule = sel$rule, selection_date = format(Sys.Date()),
            exclude = FALSE, exclude_reason = NA_character_)
# general rule: ignition too early relative to EFFIS without independent confirmation -> excluded
early <- !is.na(s$ignition_minus_effis_days) & s$ignition_minus_effis_days < -as.numeric(sel$max_days_before_effis)
if (file.exists(out)) {
  old <- read_csv(out, show_col_types = FALSE, col_types = cols(fire_id = col_character(), .default = col_guess()))
  i <- match(s$fire_id, old$fire_id)
  s$exclude[!is.na(i)] <- as.logical(old$exclude[i[!is.na(i)]])
  s$exclude_reason[!is.na(i)] <- as.character(old$exclude_reason[i[!is.na(i)]])
  s$selection_date[!is.na(i)] <- as.character(old$selection_date[i[!is.na(i)]])
  gone <- setdiff(old$fire_id, s$fire_id)
  if (length(gone)) warning("fires in the existing file no longer meet the rule: ", paste(gone, collapse = ", "))
}
s$exclude[early] <- TRUE
s$exclude_reason[early] <- sel$early_ignition_reason
dir.create(dirname(out), showWarnings = FALSE, recursive = TRUE)
write_csv(s, out, na = "")
message(sprintf("%d fires (%d excluded) -> %s", nrow(s), sum(s$exclude), out))
