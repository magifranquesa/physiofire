# SPEI-3 (90-day scale) of the ERA5-Land cells containing the burned and control cells of the 22 fires of 2025, to
# support the descriptive statement of the Discussion on the wet spring of 2025. POST HOC and DESCRIPTIVE: it is not
# part of any pre-registered criterion and changes no result. Same method, reference period (1991-2020) and clipping
# as question 1 (R/q1_spei.R, R/spei_lib.R), as in R/explore_spei.R; needed because the burned cells of 2025 are
# outside the question 1 cells.
#
# Outputs (in {epoch.out_dir}):
#   spei3_fires_2025_daily.csv   daily SPEI-90 of 2025 per ERA5-Land cell (lon01, lat01)
#   spei3_fires_2025_spring.csv  per fire: burned-fraction-weighted mean over burned cells (B) and equal-weight mean
#                                over controls (C) of daily SPEI-90, summarised over April-May 2025 (min, median,
#                                max, share of days > 0) and on the ignition date
# Usage (from the repository root): Rscript R/fires_spei3_spring.R

source("R/config.R")
source("R/spei_lib.R")
source("R/q1_lib.R")
suppressPackageStartupMessages({ library(readr); library(dplyr); library(terra) })
cfg <- load_config(); root <- find_repo_root()
q <- cfg$drought_q1; sp <- q$spei
scale <- 90L; ref <- as.integer(unlist(sp$reference)); limit <- as.numeric(sp$clip)
od <- q1_path(root, cfg$epoch$out_dir)

fires <- read_csv(file.path(root, "data/fires/selected_fires.csv"), show_col_types = FALSE) |>
  filter(!exclude) |> select(fire_id, country, name, ignition_date)
cells <- read_csv(file.path(od, "epoch_cells.csv"), show_col_types = FALSE) |>
  filter(grid == "fine", fire_id %in% fires$fire_id) |>
  mutate(lon01 = containing_centre(lon), lat01 = containing_centre(lat))
stopifnot(nrow(cells) == 241, n_distinct(cells$fire_id) == 22)

e5 <- distinct(cells, lon01, lat01); xy <- as.matrix(e5)
y_first <- ref[1]; y_last <- as.integer(substr(q$period[[2]], 1, 4))
wb_dir <- q1_path(root, sp$out_dir)
D <- do.call(rbind, lapply(y_first:y_last, function(y) {
  r <- rast(file.path(wb_dir, sprintf("water_balance_%d.nc", y)), subds = "d")
  t(as.matrix(terra::extract(r, xy, method = "simple")))
}))
dates <- seq(as.Date(sprintf("%d-01-01", y_first)), as.Date(sprintf("%d-12-31", y_last)), by = "day")
stopifnot(nrow(D) == length(dates))
if (anyNA(D)) message("missing D values: ", sum(is.na(D)))
nl <- drop_feb29(seq_along(dates), dates); Dn <- D[nl$x, , drop = FALSE]
S <- sapply(seq_len(ncol(Dn)), function(j) {
  r <- spei_daily(Dn[, j], y_first, scale, ref)
  restore_feb29(clamp_spei(r$spei, limit), nl$dates, dates)
})
keep <- format(dates, "%Y") == "2025"
daily <- bind_rows(lapply(seq_len(nrow(e5)), function(j)
  tibble(lon01 = e5$lon01[j], lat01 = e5$lat01[j], date = dates[keep], spei_090 = S[keep, j])))
write_csv(daily, file.path(od, "spei3_fires_2025_daily.csv"))

# per fire and day: B = burned-fraction-weighted mean over burned cells, C = mean over controls (Eq. 3 weights)
fd <- cells |> select(fire_id, group, burned_fraction, lon01, lat01) |>
  inner_join(daily, by = c("lon01", "lat01"), relationship = "many-to-many") |>
  mutate(w = if_else(group == "burned", burned_fraction, 1)) |>
  group_by(fire_id, group, date) |>
  summarise(spei = weighted.mean(spei_090, w, na.rm = TRUE), .groups = "drop")
spring <- fd |> filter(format(date, "%m") %in% c("04", "05")) |>
  group_by(fire_id, group) |>
  summarise(min = min(spei), median = median(spei), max = max(spei), share_positive = mean(spei > 0),
            .groups = "drop")
at_ign <- fd |> inner_join(fires |> select(fire_id, ignition_date), by = "fire_id") |>
  filter(date == ignition_date) |> select(fire_id, group, at_ignition = spei)
out <- spring |> left_join(at_ign, by = c("fire_id", "group")) |>
  inner_join(fires, by = "fire_id") |>
  mutate(group = recode(group, burned = "B", control = "C")) |>
  select(fire_id, country, name, ignition_date, group, min, median, max, share_positive, at_ignition) |>
  arrange(country, fire_id, group)
write_csv(out, file.path(od, "spei3_fires_2025_spring.csv"))

cat("SPEI-3 (90-day) in April-May 2025, per fire (B = burned cells, C = controls):\n")
print(as.data.frame(out |> mutate(name = substr(name, 1, 28),
                                  across(c(min, median, max, share_positive, at_ignition), ~ round(.x, 2)))),
      row.names = FALSE)
cat("\nBurned-cell values over April-May, by country (ranges over fires):\n")
print(as.data.frame(out |> filter(group == "B") |> group_by(country) |>
                      summarise(n = n(), min_of_min = round(min(min), 2), median_lo = round(min(median), 2),
                                median_hi = round(max(median), 2), max_of_max = round(max(max), 2),
                                fires_median_positive = sum(median > 0), fires_all_days_positive = sum(min > 0),
                                at_ignition_lo = round(min(at_ignition), 2), at_ignition_hi = round(max(at_ignition), 2),
                                .groups = "drop")), row.names = FALSE)
message("wrote ", file.path(od, "spei3_fires_2025_spring.csv"), " (", nrow(e5), " ERA5-Land cells)")
