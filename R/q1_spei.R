# Daily SPEI of question 1 (docs/plan_q1_drought.md; config drought_q1.spei) for the ERA5-Land 0.1 deg cells that
# contain the selected 0.05 deg cells (R/q1_cells.R). Reads the yearly water balance D = P - ET0
# (python -m physiofire.preprocess.water_balance, 1991-2025), removes 29 February, accumulates D over each scale with
# cumulative sums and fits one log-logistic per day of year on 1991-2020 with the SPEI package (R/spei_lib.R).
#
# Output: {drought_q1.spei.out_dir}/spei_q1.nc (spei_<scale>(time, cell), lon01, lat01; days of
#         drought_q1.period[1] year .. period[2], 29 February = NA) and spei_q1_params.rds (fitted parameters)
# Usage (from the repository root): Rscript R/q1_spei.R [n_cores] [config.yaml]

source("R/config.R")
source("R/spei_lib.R")
source("R/q1_lib.R")
suppressPackageStartupMessages({ library(readr); library(terra); library(parallel); library(ncdf4) })
cfg <- load_config(if (length(commandArgs(trailingOnly = TRUE)) >= 2) commandArgs(trailingOnly = TRUE)[2] else NULL)
root <- find_repo_root()
q <- cfg$drought_q1; sp <- q$spei
args <- commandArgs(trailingOnly = TRUE)
n_cores <- if (length(args) >= 1) as.integer(args[1]) else max(1L, detectCores() - 2L)
scales <- as.integer(unlist(sp$scales_days)); ref <- as.integer(unlist(sp$reference))
limit <- if (is.null(sp$inf_clamp)) stop("drought_q1.spei.inf_clamp must be set (decision pending)") else
  if (identical(sp$inf_clamp, "none")) NULL else as.numeric(sp$inf_clamp)

cells <- read_csv(file.path(q1_path(root, q$out_dir), "drought_q1_cells.csv"), show_col_types = FALSE)
e5 <- unique(cells[, c("lon01", "lat01")])
xy <- as.matrix(e5[, c("lon01", "lat01")])
y_first <- ref[1]; y_last <- as.integer(substr(q$period[[2]], 1, 4))
wb_dir <- q1_path(root, sp$out_dir)
d_list <- lapply(y_first:y_last, function(y) {
  r <- rast(file.path(wb_dir, sprintf("water_balance_%d.nc", y)), subds = "d")
  v <- t(as.matrix(terra::extract(r, xy, method = "simple")))
  if (nrow(v) != length(seq(as.Date(sprintf("%d-01-01", y)), as.Date(sprintf("%d-12-31", y)), by = "day")))
    stop("unexpected number of days in ", y)
  v
})
D <- do.call(rbind, d_list)                       # days x cells
dates <- seq(as.Date(sprintf("%d-01-01", y_first)), as.Date(sprintf("%d-12-31", y_last)), by = "day")
stopifnot(nrow(D) == length(dates))
if (anyNA(D)) message("missing D values: ", sum(is.na(D)), " (cells with any: ", sum(colSums(is.na(D)) > 0), ")")
nl <- drop_feb29(seq_along(dates), dates)
Dn <- D[nl$x, , drop = FALSE]

out_start <- as.Date(sprintf("%s-01-01", substr(q$period[[1]], 1, 4)))
out_days <- dates[dates >= out_start]
one_cell <- function(j) {
  res <- lapply(scales, function(s) {
    r <- spei_daily(Dn[, j], y_first, s, ref)
    v <- clamp_spei(r$spei, limit)
    list(spei = restore_feb29(v, nl$dates, dates)[dates >= out_start], coef = r$coef,
         n_inf = sum(is.infinite(r$spei)))
  })
  names(res) <- paste0("spei_", sprintf("%03d", scales))
  res
}
t0 <- Sys.time()
cl <- makeCluster(n_cores)
clusterExport(cl, c("Dn", "nl", "dates", "out_start", "scales", "ref", "limit", "y_first", "spei_daily", "roll_sum",
                    "clamp_spei", "restore_feb29"))
clusterEvalQ(cl, suppressPackageStartupMessages(library(SPEI)))
res <- parLapply(cl, seq_len(ncol(Dn)), one_cell)
stopCluster(cl)
message(sprintf("SPEI for %d cells x %d scales in %.1f min", ncol(Dn), length(scales),
                as.numeric(difftime(Sys.time(), t0, units = "mins"))))

# NetCDF (time, cell)
tdim <- ncdim_def("time", "days since 1970-01-01", as.numeric(out_days))
cdim <- ncdim_def("cell", "", seq_len(nrow(e5)), create_dimvar = FALSE)
vars <- c(lapply(names(res[[1]]), function(v) ncvar_def(v, "1", list(tdim, cdim), NA, prec = "float",
                                                         longname = sprintf("daily SPEI, %s-day scale", sub("spei_0*", "", v)),
                                                         compression = 4)),
          list(ncvar_def("lon01", "degrees_east", cdim, NA, prec = "double"),
               ncvar_def("lat01", "degrees_north", cdim, NA, prec = "double")))
f <- file.path(wb_dir, "spei_q1.nc")
nco <- nc_create(f, vars)
for (v in names(res[[1]])) ncvar_put(nco, v, sapply(res, function(r) r[[v]]$spei))
ncvar_put(nco, "lon01", e5$lon01); ncvar_put(nco, "lat01", e5$lat01)
ncatt_put(nco, 0, "method", sprintf("log-logistic, ub-pwm, one fit per day of year (29 Feb removed), reference %d-%d, SPEI %s; +-Inf clamped to %s",
                                    ref[1], ref[2], as.character(packageVersion("SPEI")),
                                    if (is.null(limit)) "none" else limit))
nc_close(nco)
saveRDS(list(cells = e5, scales = scales, coef = lapply(res, function(r) lapply(r, `[[`, "coef"))),
        file.path(wb_dir, "spei_q1_params.rds"))
ninf <- sapply(names(res[[1]]), function(v) sum(sapply(res, function(r) r[[v]]$n_inf)))
print(ninf)
message("wrote ", f)
