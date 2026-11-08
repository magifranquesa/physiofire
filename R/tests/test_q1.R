# Synthetic tests of the question-1 helpers (R/q1_lib.R). Usage: Rscript R/tests/test_q1.R
source("R/q1_lib.R")
ok <- function(cond, msg) { if (!isTRUE(cond)) stop("FAIL: ", msg); cat("ok -", msg, "\n") }

classes <- list(semiarid = c(0, 0.5), dry_subhumid = c(0.5, 0.65), humid = c(0.65, 100))
ok(identical(aridity_class(c(0.3, 0.5, 0.64, 0.65, 2, NA), classes),
             c("semiarid", "dry_subhumid", "dry_subhumid", "humid", "humid", NA)), "aridity classes [lower, upper)")
# 0.05 deg cell centres x.025 / x.075 fall in the 0.1 deg cell centred at the nearest multiple of 0.1
ok(isTRUE(all.equal(containing_centre(c(-9.975, -9.925, 0.025, 0.075, 4.475)), c(-10.0, -9.9, 0.0, 0.1, 4.5))),
   "containing ERA5-Land cell centre")
strata <- list(shrubland = c("shrubland", "wet_heath"), forest = c("closed_forest", "open_forest"),
               grassland = "grassland")
ok(identical(class_stratum(c("wet_heath", "open_forest", "cropland"), strata), c("shrubland", "forest", NA)),
   "class to stratum")
qcfg <- list(cells = list(min_land_fraction = 0.5, fuel_classes = c("closed_forest", "open_forest", "shrubland",
                                                                     "wet_heath", "grassland")),
             strata = strata, aridity_classes = classes)
ct <- data.frame(lon = c(-5.025, -5.075, -5.125, -5.175, -5.225), lat = 40.025,
                 land_fraction = c(1, 0.4, 1, 1, 1),
                 fuel_class = c("shrubland", "shrubland", "cropland", "closed_forest", "grassland"),
                 burned_any = c(FALSE, FALSE, FALSE, TRUE, FALSE), aridity_index = c(0.3, 0.3, 0.3, 0.7, 0.6))
s <- select_q1_cells(ct, qcfg)
ok(nrow(s) == 2 && all(s$fuel_class == c("shrubland", "grassland")), "selection: land, natural class, unburned")
ok(identical(s$stratum, c("shrubland", "grassland")) && identical(s$aridity_class, c("semiarid", "dry_subhumid")),
   "selected cells carry stratum and aridity class")
ok(isTRUE(all.equal(clamp_spei(c(-Inf, -1, Inf, NA), 3.09), c(-3.09, -1, 3.09, NA))), "clamp of infinite SPEI")
ok(identical(clamp_spei(c(-Inf, 1), NULL), c(-Inf, 1)), "no clamp when limit is NULL")
dates <- seq(as.Date("2020-02-27"), as.Date("2020-03-02"), by = "day")
nl <- dates[format(dates, "%m-%d") != "02-29"]
ok(identical(restore_feb29(c(1, 2, 3, 4), nl, dates), c(1, 2, NA, 3, 4)), "29 February restored as NA")
cat("all question-1 helper tests passed\n")
