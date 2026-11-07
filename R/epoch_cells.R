# Burned and control cells of each selected fire (simplified 2025 analysis, 0.05 deg grid).
#
# Burned cells: fraction of the cell inside the EFFIS perimeter >= epoch.burned_min_fraction[grid].
# Controls (epoch.controls): 3-5 cells per fire, unburned since `unburned_since` up to the fire year (EFFIS
# perimeters, MCD64A1 and VNP64A1 yearly burn history, ESFire30 perimeters in Spain), same dominant vegetation class
# as the burned cells (epoch.controls.vegetation: FirEUrisk fuel classes, or CORINE 2018 groups), aridity index
# (Global-AI v3.1, relative tolerance) and elevation within tolerance, and between min_dist_km (whole cell) and
# max_dist_km (centre) from the perimeter.
# Static inputs only: no vegetation or meteorological series are read.
#
# Input:  fires table (default epoch.selected_fires; columns fire_id = EFFIS id, ignition_date, ...),
#         data/interim/fires/effis_iberia_*.gpkg, ESFire30 shapefiles, data/interim/gee/{static, mask_peninsula,
#         corine_2018, burn_history, burn_history_vnp64a1}_*.nc, data/interim/static/{aridity_gai,
#         fuel_fireurisk}_*.nc
# Output: {out_dir}/epoch_cells.csv and epoch_cells_status.csv
#
# Usage (from the repository root): Rscript R/epoch_cells.R [fires.csv] [out_dir] [config.yaml]

source("R/config.R")
source("R/epoch_lib.R")
suppressPackageStartupMessages(library(readr))
args <- commandArgs(trailingOnly = TRUE)
cfg <- load_config(if (length(args) >= 3) args[3] else NULL)   # 3rd argument: alternative config (diagnostics)
root <- find_repo_root()
ec <- cfg$epoch
cc <- ec$controls
fires_csv <- if (length(args) >= 1) args[1] else file.path(root, ec$selected_fires)
out_dir <- if (length(args) >= 2) args[2] else file.path(root, ec$out_dir)
if (!file.exists(fires_csv)) stop("fires table not found: ", fires_csv, " (manual selection pending)")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
gee_dir <- file.path(root, cfg$gee$out_dir)

fires <- read_csv(fires_csv, col_types = cols(fire_id = col_character(), .default = col_guess()))
fires$ignition_date <- as.Date(fires$ignition_date)
fires$year <- as.integer(format(fires$ignition_date, "%Y"))
gpkg <- list.files(file.path(root, cfg$effis$out_dir), pattern = "^effis_iberia_[0-9]+_[0-9]+\\.gpkg$",
                   full.names = TRUE)
eff <- st_read(gpkg, quiet = TRUE) |> mutate(id = as.character(id))
veg_src <- cc$vegetation
strata <- ec$strata[[veg_src]]
since <- as.integer(cc$unburned_since)

nc <- function(path, var) rast(path, subds = var)
# yearly burn-history stack (layers by index: terra does not read the 'year' coordinate)
burn_hist <- function(prefix, g) {
  f <- list.files(gee_dir, pattern = sprintf("^%s_%s_[0-9]+_[0-9]+\\.nc$", prefix, g), full.names = TRUE)
  if (length(f) != 1) stop(sprintf("expected one %s file for grid %s, found %d", prefix, g, length(f)))
  yy <- as.integer(regmatches(basename(f), regexec("_([0-9]{4})_([0-9]{4})\\.nc$", basename(f)))[[1]][2:3])
  r <- nc(f, "burned_fraction")
  stopifnot(nlyr(r) == yy[2] - yy[1] + 1)
  list(r = r, y0 = yy[1], y1 = yy[2])
}
# ESFire30 annual perimeters (Spain), one sf per year
esf_dir <- file.path(root, ec$esfire30$raw_dir)
esfire <- function(y) {
  f <- file.path(esf_dir, gsub("\\{year\\}", y, ec$esfire30$annual))
  if (!file.exists(f)) stop("ESFire30 file not found: ", f)
  st_transform(st_make_valid(st_read(f, quiet = TRUE)), 4326)
}

all_cells <- list(); status <- list()
for (g in unlist(ec$grids)) {
  tmpl <- grid_template(cfg, g)
  static <- c(nc(file.path(gee_dir, sprintf("mask_peninsula_%s.nc", g)), "land_fraction"),
              nc(file.path(root, ec$static$aridity$out_dir, sprintf("aridity_gai_%s.nc", g)), "aridity_index"),
              nc(file.path(gee_dir, sprintf("static_%s.nc", g)), "elevation_m"))
  names(static) <- c("land_fraction", "aridity_index", "elevation_m")
  vf <- vegetation_fractions(cfg, root, g, veg_src)
  groups <- names(vf)
  veg <- dominant_group(vf)
  thr <- as.numeric(cc$max_burned_fraction[[g]])
  hist <- list(mcd64a1 = burn_hist("burn_history", g), vnp64a1 = burn_hist("burn_history_vnp64a1", g))
  for (y in sort(unique(fires$year))) {
    yrs <- seq(since, y)
    ok_y <- lapply(names(hist), function(h) {
      b <- hist[[h]]
      if (y > b$y1) stop(sprintf("%s burn history ends in %d; fire year %d needs it", h, b$y1, y))
      max(b$r[[yrs - b$y0 + 1]], na.rm = TRUE) <= thr
    })
    e_y <- eff[eff$fire_year >= since & eff$fire_year <= y, ]
    e_cov <- rasterize(vect(st_transform(e_y, 4326)), tmpl, cover = TRUE, background = 0)
    esf_files <- file.path(esf_dir, vapply(yrs, function(yy) gsub("\\{year\\}", yy, ec$esfire30$annual), ""))
    esf_yrs <- yrs[file.exists(esf_files)]
    if (length(esf_yrs) < length(yrs)) message("ESFire30 missing for: ", paste(setdiff(yrs, esf_yrs), collapse = ", "))
    s_cov <- max(rast(lapply(esf_yrs, function(yy) rasterize(vect(esfire(yy)), tmpl, cover = TRUE, background = 0))))
    unburned <- ok_y[[1]] & ok_y[[2]] & (e_cov <= thr) & (s_cov <= thr)
    names(unburned) <- "unburned"
    layers <- c(resample(static, tmpl, method = "near"), resample(veg, tmpl, method = "near"),
                resample(unburned, tmpl, method = "near"))
    for (i in which(fires$year == y)) {
      f <- fires[i, ]
      per <- eff[eff$id == f$fire_id, ]
      if (!nrow(per)) { status[[length(status) + 1]] <- data.frame(fire_id = f$fire_id, grid = g,
                                                                    status = "perimeter_not_found"); next }
      s <- select_fire_cells(per, tmpl, layers, cc, as.numeric(ec$burned_min_fraction[[g]]), groups)
      status[[length(status) + 1]] <- data.frame(
        fire_id = f$fire_id, grid = g, status = s$status, fire_veg = s$fire_veg,
        stratum = group_stratum(s$fire_veg, strata),
        n_burned = if (is.null(s$cells)) 0L else sum(s$cells$group == "burned"),
        n_control = if (is.null(s$cells)) 0L else sum(s$cells$group == "control"))
      if (!is.null(s$cells)) {
        all_cells[[length(all_cells) + 1]] <- data.frame(fire_id = f$fire_id, grid = g, fire_veg = s$fire_veg,
                                                         stratum = group_stratum(s$fire_veg, strata), s$cells) |>
          mutate(cell_id = sprintf("%s_%d_%d", g, iy, ix))
      }
    }
  }
}
cells <- bind_rows(all_cells)
st <- bind_rows(status)
write_csv(cells, file.path(out_dir, "epoch_cells.csv"))
write_csv(st, file.path(out_dir, "epoch_cells_status.csv"))
print(as.data.frame(st |> count(grid, status)))
message(sprintf("wrote %s", file.path(out_dir, "epoch_cells.csv")))
