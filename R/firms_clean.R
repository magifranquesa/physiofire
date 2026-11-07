# Clean FIRMS active-fire detections for the Iberian Peninsula.
#
# Input: FIRMS archive downloads, one folder per country and source (data/raw/firms/{spain,portugal}/DL_FIRE_*),
# each with a standard-processing part (fire_archive_*.csv) and a near-real-time part (fire_nrt_*.csv).
# Rules (config.yaml, section firms):
#   - mainland only: detections in cells of the peninsula mask with land_fraction > 0 (islands out);
#   - standard archive: keep type == 0 (presumed vegetation fire);
#   - NRT part (no 'type' column): drop detections within a buffer of any archive type-2 (static land source)
#     detection of 2018-2026;
#   - confidence: VIIRS drop class 'l'; MODIS drop < modis_min_confidence.
# Output: data/interim/firms/firms_iberia_clean.csv (one row per detection; UTC date and time) and
#         data/interim/firms/static_sources.gpkg (type-2 points, for reference).
#
# Usage (from the repository root): Rscript R/firms_clean.R

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(sf)
  library(terra)
})
source("R/config.R")
cfg <- load_config()
root <- find_repo_root()
fc <- cfg$firms

read_part <- function(path) {
  parts <- strsplit(normalizePath(path, winslash = "/"), "/")[[1]]
  n <- length(parts)
  d <- read_csv(path, col_types = cols(.default = col_character()), progress = FALSE)
  if (!"type" %in% names(d)) d$type <- NA_character_
  d |>
    transmute(latitude = as.numeric(latitude), longitude = as.numeric(longitude),
              acq_date = as.Date(acq_date), acq_time = sprintf("%04d", as.integer(acq_time)),
              satellite, instrument, confidence, version, frp = as.numeric(frp), daynight,
              type = as.integer(type),
              country_file = parts[n - 2],
              source = sub("^DL_FIRE_(.*)_[0-9]+$", "\\1", parts[n - 1]),
              part = ifelse(grepl("^fire_nrt_", parts[n]), "nrt", "archive"))
}

files <- list.files(file.path(root, fc$raw_dir), pattern = "^fire_(archive|nrt)_.*\\.csv$",
                    recursive = TRUE, full.names = TRUE)
det <- bind_rows(lapply(files, read_part))
message(sprintf("read %d files, %d detections", length(files), nrow(det)))

# Mainland mask (islands out)
mask <- rast(file.path(root, fc$peninsula_mask), subds = "land_fraction")
lf <- terra::extract(mask, as.matrix(det[, c("longitude", "latitude")]))[, 1]
det <- det[!is.na(lf) & lf > 0, ]
message(sprintf("mainland: %d detections", nrow(det)))

# Static-source mask from archive type-2 detections (buffered, projected to ETRS89-LAEA)
is_viirs <- det$source %in% unlist(fc$viirs_sources)
static_pts <- det |> filter(part == "archive", type == as.integer(fc$static_type)) |>
  st_as_sf(coords = c("longitude", "latitude"), crs = 4326) |> st_transform(3035)
static_v <- st_union(st_buffer(static_pts, as.numeric(fc$static_buffer_m_viirs)))
static_m <- st_union(st_buffer(static_pts, as.numeric(fc$static_buffer_m_modis)))
st_write(static_pts, file.path(root, fc$out_dir, "static_sources.gpkg"), delete_dsn = TRUE, quiet = TRUE)

nrt <- which(det$part == "nrt")
nrt_pts <- st_transform(st_as_sf(det[nrt, ], coords = c("longitude", "latitude"), crs = 4326), 3035)
in_static <- logical(nrow(det))
in_static[nrt] <- ifelse(is_viirs[nrt],
                         lengths(st_intersects(nrt_pts, static_v)) > 0,
                         lengths(st_intersects(nrt_pts, static_m)) > 0)

conf_ok <- ifelse(is_viirs, !(det$confidence %in% unlist(fc$viirs_drop_confidence)),
                  suppressWarnings(as.numeric(det$confidence)) >= as.numeric(fc$modis_min_confidence))
keep_type <- ifelse(det$part == "archive", det$type == as.integer(fc$keep_type), !in_static)

summary_tbl <- det |>
  mutate(type_ok = keep_type, conf_ok = conf_ok) |>
  group_by(source, part) |>
  summarise(n = n(), dropped_type_or_static = sum(!type_ok), dropped_low_conf = sum(type_ok & !conf_ok),
            kept = sum(type_ok & conf_ok), .groups = "drop")
print(as.data.frame(summary_tbl))

clean <- det[keep_type & conf_ok, ] |> arrange(acq_date, acq_time)
dir.create(file.path(root, fc$out_dir), showWarnings = FALSE, recursive = TRUE)
write_csv(clean, file.path(root, fc$out_dir, "firms_iberia_clean.csv"))
write_csv(summary_tbl, file.path(root, fc$out_dir, "firms_iberia_clean_summary.csv"))
message(sprintf("wrote %d detections to %s", nrow(clean), file.path(fc$out_dir, "firms_iberia_clean.csv")))
