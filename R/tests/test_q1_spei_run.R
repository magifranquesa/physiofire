# End-to-end test of R/q1_spei.R on synthetic yearly water-balance files (1991-2025, 3 x 3 cells at 0.1 deg) and a
# temporary configuration: output dimensions, days, 29 February, and equality with spei_daily() on the same series.
# Usage: Rscript R/tests/test_q1_spei_run.R
source("R/config.R"); source("R/spei_lib.R"); source("R/q1_lib.R")
suppressPackageStartupMessages({ library(ncdf4); library(yaml) })
ok <- function(cond, msg) { if (!isTRUE(cond)) stop("FAIL: ", msg); cat("ok -", msg, "\n") }
tmp <- normalizePath(file.path(tempdir(), "q1_spei_test"), winslash = "/", mustWork = FALSE)
dir.create(file.path(tmp, "spei"), recursive = TRUE, showWarnings = FALSE)
set.seed(7)
lon <- c(-5.1, -5.0, -4.9); lat <- c(40.0, 40.1, 40.2)
series <- list()
for (y in 1991:2025) {
  days <- seq(as.Date(sprintf("%d-01-01", y)), as.Date(sprintf("%d-12-31", y)), by = "day")
  doy <- as.integer(format(days, "%j"))
  arr <- array(NA_real_, c(3, 3, length(days)))                    # lon, lat, time
  for (i in 1:3) for (j in 1:3) arr[i, j, ] <- 2 * sin(2 * pi * doy / 365) + (i - j) + rnorm(length(days), 0, 3)
  series[[as.character(y)]] <- arr
  dx <- ncdim_def("lon", "degrees_east", lon); dy <- ncdim_def("lat", "degrees_north", lat)
  dt <- ncdim_def("time", "days since 1970-01-01", as.numeric(days))
  v <- ncvar_def("d", "mm day-1", list(dx, dy, dt), NA)
  f <- nc_create(file.path(tmp, "spei", sprintf("water_balance_%d.nc", y)), v)
  ncvar_put(f, v, arr); nc_close(f)
}
cells <- data.frame(iy = 1:2, ix = 1:2, lon = c(-5.075, -4.925), lat = c(40.025, 40.175), fuel_class = "shrubland",
                    stratum = "shrubland", aridity_index = 0.4, aridity_class = "semiarid",
                    lon01 = c(-5.1, -4.9), lat01 = c(40.0, 40.2), land_fraction = 1)
write.csv(cells, file.path(tmp, "drought_q1_cells.csv"), row.names = FALSE)
cfg <- read_yaml("config/config.yaml")
cfg$drought_q1$out_dir <- tmp
cfg$drought_q1$spei$out_dir <- file.path(tmp, "spei")
cfg$drought_q1$spei$scales_days <- c(30L, 90L)
cfg$drought_q1$spei$clip <- 3.09
cfg_file <- file.path(tmp, "config_test.yaml")
write_yaml(cfg, cfg_file)
rc <- system2(file.path(R.home("bin"), "Rscript"), c("R/q1_spei.R", "2", cfg_file), stdout = TRUE, stderr = TRUE)
cat(tail(rc, 3), sep = "\n")
out <- file.path(tmp, "spei", "spei_q1.nc")
ok(file.exists(out), "q1_spei.R wrote the NetCDF")
nc <- nc_open(out)
tt <- as.Date(ncvar_get(nc, "time"), origin = "1970-01-01")
s90 <- ncvar_get(nc, "spei_090"); lon01 <- ncvar_get(nc, "lon01"); lat01 <- ncvar_get(nc, "lat01")
nc_close(nc)
ok(min(tt) == as.Date("2018-01-01") && max(tt) == as.Date("2025-12-31"), "output days from the first period year")
ok(all(dim(s90) == c(length(tt), 2)), "output (time, cell)")
ok(all(is.na(s90[format(tt, "%m-%d") == "02-29", ])), "29 February is NA")
# equality with spei_daily on the same cell series (cell 2 = lon -4.9, lat 40.2 -> array index [3, 3])
dall <- unlist(lapply(series, function(a) a[3, 3, ]))
dates <- seq(as.Date("1991-01-01"), as.Date("2025-12-31"), by = "day")
nl <- drop_feb29(dall, dates)
ref <- spei_daily(nl$x, 1991, 90)
want <- restore_feb29(clamp_spei(ref$spei, 3.09), nl$dates, dates)[dates >= as.Date("2018-01-01")]
ok(isTRUE(all.equal(as.numeric(s90[, 2]), want, tolerance = 1e-6)), "SPEI equals spei_daily on the same series")
ok(lon01[2] == -4.9 && lat01[2] == 40.2, "cell coordinates stored")
cat("q1_spei.R end-to-end test passed\n")
