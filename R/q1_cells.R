# Cells of question 1 (docs/plan_q1_drought.md; config drought_q1.cells): 0.05 deg cells with >= 50 % land, dominant
# FirEUrisk class natural (closed/open forest, shrubland, heathland, grassland) and no burned area since 2013 by any
# source: MCD64A1 and VNP64A1 yearly burn history (2013-2025), EFFIS perimeters (2018-2025) and ESFire30 (Spain,
# 2013-2025). Static data only.
#
# Output: {drought_q1.out_dir}/drought_q1_cells.csv (iy, ix as in the Python grid; lon, lat; fuel_class, stratum;
#         aridity_index, aridity_class; lon01, lat01 = containing ERA5-Land 0.1 deg cell)
# Usage (from the repository root): Rscript R/q1_cells.R

source("R/config.R")
source("R/epoch_lib.R")
source("R/q1_lib.R")
suppressPackageStartupMessages(library(readr))
cfg <- load_config(); root <- find_repo_root()
q <- cfg$drought_q1; ec <- cfg$epoch
g <- q$cells$grid
tmpl <- grid_template(cfg, g)
gee_dir <- file.path(root, cfg$gee$out_dir)
y0 <- as.integer(q$cells$unburned_since)
y1 <- as.integer(substr(q$period[[2]], 1, 4))
nc <- function(path, var) rast(path, subds = var)

ct <- cell_table(tmpl)
land <- nc(file.path(gee_dir, sprintf("mask_peninsula_%s.nc", g)), "land_fraction")
ai <- nc(file.path(root, ec$static$aridity$out_dir, sprintf("aridity_gai_%s.nc", g)), "aridity_index")
vf <- vegetation_fractions(cfg, root, g, "fuel")
dom <- dominant_group(vf)
ct$land_fraction <- values(resample(land, tmpl, method = "near"))[, 1]
ct$aridity_index <- values(resample(ai, tmpl, method = "near"))[, 1]
ct$fuel_class <- names(vf)[values(resample(dom, tmpl, method = "near"))[, 1]]

# burned area since y0 by any source
burn_any <- function(prefix) {
  f <- list.files(gee_dir, pattern = sprintf("^%s_%s_[0-9]+_[0-9]+\\.nc$", prefix, g), full.names = TRUE)
  yy <- as.integer(regmatches(basename(f), regexec("_([0-9]{4})_([0-9]{4})\\.nc$", basename(f)))[[1]][2:3])
  if (yy[1] > y0 || yy[2] < y1) stop(sprintf("%s covers %d-%d, need %d-%d", prefix, yy[1], yy[2], y0, y1))
  r <- nc(f, "burned_fraction")
  max(r[[(y0:y1) - yy[1] + 1]], na.rm = TRUE) > 0
}
b_mcd <- burn_any("burn_history"); b_vnp <- burn_any("burn_history_vnp64a1")
eff <- st_read(list.files(file.path(root, cfg$effis$out_dir), "^effis_iberia_.*\\.gpkg$", full.names = TRUE),
               quiet = TRUE)
eff <- eff[eff$fire_year >= y0 & eff$fire_year <= y1, ]
b_eff <- rasterize(vect(st_transform(st_make_valid(eff), 4326)), tmpl, cover = TRUE, background = 0) > 0
esf_dir <- file.path(root, ec$esfire30$raw_dir)
esf <- lapply(y0:y1, function(y) {
  f <- file.path(esf_dir, gsub("\\{year\\}", y, ec$esfire30$annual))
  if (!file.exists(f)) { message("ESFire30 missing for ", y); return(NULL) }
  rasterize(vect(st_transform(st_make_valid(st_read(f, quiet = TRUE)), 4326)), tmpl, cover = TRUE, background = 0)
})
b_esf <- max(rast(Filter(Negate(is.null), esf))) > 0
burned <- c(resample(b_mcd, tmpl, method = "near"), resample(b_vnp, tmpl, method = "near"), b_eff, b_esf)
names(burned) <- c("mcd64a1", "vnp64a1", "effis", "esfire30")
bv <- as.data.frame(values(burned))
ct$burned_any <- rowSums(bv > 0, na.rm = TRUE) > 0

cells <- select_q1_cells(ct, q)
out_dir <- q1_path(root, q$out_dir)
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
write_csv(cells[, c("iy", "ix", "lon", "lat", "fuel_class", "stratum", "aridity_index", "aridity_class",
                    "lon01", "lat01", "land_fraction")], file.path(out_dir, "drought_q1_cells.csv"))
print(table(cells$fuel_class)); print(table(cells$stratum, cells$aridity_class, useNA = "ifany"))
cat("natural land cells:", sum(ct$land_fraction >= 0.5 & ct$fuel_class %in% unlist(q$cells$fuel_classes), na.rm = TRUE),
    " excluded as burned by source:", paste(names(bv), colSums(bv[ct$fuel_class %in% unlist(q$cells$fuel_classes) &
                                                                   !is.na(ct$land_fraction) & ct$land_fraction >= 0.5, ] > 0,
                                                                na.rm = TRUE), collapse = " "), "\n")
cat("selected:", nrow(cells), "cells;", nrow(unique(cells[, c("lon01", "lat01")])), "ERA5-Land cells\n")
