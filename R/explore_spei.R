# SPEI-90 for the ERA5-Land cells of the exploratory time-series figures (config explore_timeseries;
# python -m physiofire.explore_timeseries cells). Same method, reference period and clipping as question 1
# (R/q1_spei.R, R/spei_lib.R): needed because the burned cells of 2025 are outside the question 1 cells.
#
# Output: {explore_timeseries.out_dir}/spei_q1.nc (spei_090(time, cell), lon01, lat01; same layout as R/q1_spei.R,
#         read by drought_q1.build_series)
# Usage (from the repository root): Rscript R/explore_spei.R

source("R/config.R")
source("R/spei_lib.R")
source("R/q1_lib.R")
suppressPackageStartupMessages({ library(readr); library(terra); library(ncdf4) })
cfg <- load_config(); root <- find_repo_root()
q <- cfg$drought_q1; sp <- q$spei; et <- cfg$explore_timeseries
scale <- 90L; ref <- as.integer(unlist(sp$reference)); limit <- as.numeric(sp$clip)
od <- q1_path(root, et$out_dir)
cells <- read_csv(file.path(od, "explore_cells.csv"), show_col_types = FALSE)
e5 <- unique(cells[, c("lon01", "lat01")]); xy <- as.matrix(e5)
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
out_start <- as.Date(sprintf("%s-01-01", substr(q$period[[1]], 1, 4))); out_days <- dates[dates >= out_start]
S <- sapply(seq_len(ncol(Dn)), function(j) {
  r <- spei_daily(Dn[, j], y_first, scale, ref)
  restore_feb29(clamp_spei(r$spei, limit), nl$dates, dates)[dates >= out_start]
})
tdim <- ncdim_def("time", "days since 1970-01-01", as.numeric(out_days))
cdim <- ncdim_def("cell", "", seq_len(nrow(e5)), create_dimvar = FALSE)
vars <- list(ncvar_def("spei_090", "1", list(tdim, cdim), NA, prec = "float", longname = "daily SPEI, 90-day scale"),
             ncvar_def("lon01", "degrees_east", cdim, NA, prec = "double"),
             ncvar_def("lat01", "degrees_north", cdim, NA, prec = "double"))
f <- file.path(od, "spei_q1.nc")
nco <- nc_create(f, vars)
ncvar_put(nco, "spei_090", S); ncvar_put(nco, "lon01", e5$lon01); ncvar_put(nco, "lat01", e5$lat01)
ncatt_put(nco, 0, "method", sprintf("as R/q1_spei.R: log-logistic, ub-pwm, reference %d-%d, clipped to +-%s",
                                    ref[1], ref[2], limit))
nc_close(nco)
message("wrote ", f, " (", ncol(S), " ERA5-Land cells)")
