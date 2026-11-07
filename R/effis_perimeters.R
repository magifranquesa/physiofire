# EFFIS burnt-area perimeters for mainland Spain and Portugal (FIREDATE year within effis.years).
#
# Input:  EFFIS database (config: effis.raw_dir / effis.layer).
# Output: data/interim/fires/effis_iberia_{y0}_{y1}.gpkg, with start_utc / final_utc / lastupd_utc (parsed EFFIS
#         dates), burned_ha and fire_year added to the original fields.
#
# Usage (from the repository root): Rscript R/effis_perimeters.R

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(sf)
  library(terra)
})
source("R/config.R")
cfg <- load_config()
root <- find_repo_root()
ec <- cfg$effis
y0 <- as.integer(ec$years[[1]]); y1 <- as.integer(ec$years[[2]])
out_dir <- file.path(root, ec$out_dir)
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

# --- EFFIS perimeters ----------------------------------------------------------------------------------------
eff <- st_read(file.path(root, ec$raw_dir, ec$layer), quiet = TRUE) |>
  filter(COUNTRY %in% unlist(ec$countries)) |>
  mutate(start_utc = as.POSIXct(FIREDATE, tz = "UTC", format = "%Y-%m-%d %H:%M:%S"),
         final_utc = as.POSIXct(FINALDATE, tz = "UTC", format = "%Y-%m-%d %H:%M:%S"),
         lastupd_utc = as.POSIXct(substr(LASTUPDATE, 1, 19), tz = "UTC", format = "%Y-%m-%d %H:%M:%S"),
         burned_ha = as.numeric(AREA_HA),
         fire_year = as.integer(format(start_utc, "%Y"))) |>
  filter(fire_year >= y0, fire_year <= y1)
eff <- st_make_valid(eff)

# mainland only: centroid in a peninsula-mask cell with land_fraction > 0
mask <- rast(file.path(root, cfg$firms$peninsula_mask), subds = "land_fraction")
cen <- st_coordinates(st_transform(st_point_on_surface(st_transform(st_geometry(eff), 3035)), 4326))
lf <- terra::extract(mask, cen)[, 1]
eff <- eff[!is.na(lf) & lf > 0, ]
st_write(eff, file.path(out_dir, sprintf("effis_iberia_%d_%d.gpkg", y0, y1)), delete_dsn = TRUE, quiet = TRUE)
message(sprintf("EFFIS mainland ES/PT %d-%d: %d perimeters", y0, y1, nrow(eff)))
print(as.data.frame(st_drop_geometry(eff) |> count(fire_year, COUNTRY) |>
                      tidyr::pivot_wider(names_from = COUNTRY, values_from = n)))
message("CLASS values: ", paste(names(table(eff$CLASS)), table(eff$CLASS), sep = "=", collapse = ", "))

