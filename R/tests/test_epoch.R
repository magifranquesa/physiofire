# Synthetic tests for R/epoch_lib.R (control selection, effect sizes, lead time, figure).
# Usage (from the repository root): Rscript R/tests/test_epoch.R

source("R/epoch_lib.R")
set.seed(1)
ok <- function(cond, msg) { if (!isTRUE(cond)) stop("FAILED: ", msg, call. = FALSE); cat("ok -", msg, "\n") }

# --- Control selection on a synthetic 0.05 deg grid ---------------------------------------------------------------
cfg <- list(region = list(lon_min = -8, lon_max = -6, lat_min = 41, lat_max = 43),
            grids = list(fine = list(resolution_deg = 0.05)))
tmpl <- grid_template(cfg, "fine")
ct <- cell_table(tmpl)
veg <- rep(2L, nrow(ct))                       # all shrubland ...
veg[ct$lon > -6.6] <- 1L                       # ... except an eastern band of woodland
unburned <- rep(1L, nrow(ct))
unburned[ct$lat > 42.55 & ct$lat < 42.65] <- 0L   # a band burned in a previous year
layers <- rast(tmpl, nlyrs = 5)
names(layers) <- c("land_fraction", "aridity_index", "elevation_m", "veg", "unburned")
values(layers) <- cbind(1, 0.5 + 0.1 * (ct$lat - 42), 600 + 100 * (ct$lon + 7), veg, unburned)
per <- st_sf(geometry = st_sfc(st_polygon(list(matrix(c(-7.1, 41.9, -6.9, 41.9, -6.9, 42.1, -7.1, 42.1, -7.1, 41.9),
                                                       ncol = 2, byrow = TRUE))), crs = 4326))
ccfg <- list(n_min = 3, n_max = 5, min_dist_km = 10, max_dist_km = 50, min_land_fraction = 0.5,
             max_aridity_abs_diff = 0.1, max_elevation_diff_m = 200)
s <- select_fire_cells(per, tmpl, layers, ccfg, burned_min = 0.5, veg_names = c("woodland", "shrubland"))
b <- s$cells[s$cells$group == "burned", ]
k <- s$cells[s$cells$group == "control", ]
ok(s$status == "ok", "status ok")
ok(nrow(b) == 16, sprintf("16 burned cells (0.2 x 0.2 deg perimeter on a 0.05 grid), got %d", nrow(b)))
ok(nrow(k) >= 3 && nrow(k) <= 5, sprintf("3-5 controls, got %d", nrow(k)))
ok(all(k$dist_cell_km >= 10) && all(k$dist_centre_km <= 50), "controls 10-50 km from the perimeter")
ok(all(k$veg == "shrubland"), "controls share the fire's dominant vegetation")
ok(!any(k$lat > 42.55 & k$lat < 42.65), "previously burned cells excluded")
ok(all(abs(k$elevation_m - s$ref["elevation_m"]) <= 200), "elevation within tolerance")
ok(all(abs(k$aridity_index - s$ref["aridity_index"]) <= 0.1), "aridity within tolerance")
ok(identical(group_stratum(c("heathland", "coniferous", "agricultural"),
                           list(woodland = "coniferous", shrubland = c("heathland", "sclerophyllous"))),
             c("shrubland", "woodland", "other")), "group to stratum")
ccfg2 <- ccfg; ccfg2$max_dist_km <- 11
s2 <- select_fire_cells(per, tmpl, layers, ccfg2, 0.5, c("woodland", "shrubland"))
ok(grepl("^insufficient_controls", s2$status) || nrow(s2$cells[s2$cells$group == "control", ]) >= 3,
   "too narrow ring: reported (no relaxation)")

# --- Effect sizes and lead time on synthetic anomalies ------------------------------------------------------------
# 12 fires; burned cells drift to -1.5 SD over the last 15 days for 'sif_apar', no signal for 'ndvi'
fires <- sprintf("f%02d", 1:12)
anom <- expand.grid(fire_id = fires, cell = 1:8, day_rel = -60:-1, variable = c("sif_apar", "ndvi"),
                    stringsAsFactors = FALSE)
anom$group <- ifelse(anom$cell <= 4, "burned", "control")
anom$cell_id <- paste(anom$fire_id, anom$cell)
anom$weight <- 1; anom$grid <- "base"; anom$series <- "loess_trail15"
fire_eff <- setNames(rnorm(12, 0, 0.2), fires)
sig <- with(anom, ifelse(variable == "sif_apar" & group == "burned", -1.5 * pmax(0, (day_rel + 15) / 15), 0))
anom$z <- sig + fire_eff[anom$fire_id] * (anom$group == "burned") + rnorm(nrow(anom), 0, 0.5)
fd <- fire_day_table(anom)
ok(nrow(fd) == 12 * 60 * 2, "one row per fire, day and variable")
eff <- effect_table(fd, B = 500)
lt <- lead_time(eff, list(sif_apar = -1, ndvi = -1), threshold = 0.5)
L <- lt$lead_days[lt$variable == "sif_apar"]
ok(L >= 5 && L <= 12, sprintf("sif_apar lead time between 5 and 12 days (signal reaches 0.5 SD at day -10), got %d", L))
ok(lt$lead_days[lt$variable == "ndvi"] == 0, "no lead time without signal")
ltb <- lead_time(eff, list(sif_apar = -1, ndvi = -1), 0.5, what = "burned")
ok(ltb$lead_days[ltb$variable == "sif_apar"] > 0, "burned-alone lead time detected")
fd$veg <- ifelse(fd$fire_id %in% fires[1:6], "shrubland", "woodland")
effs <- effect_table(fd, strata = "veg", B = 200)
ok(all(c("shrubland", "woodland") %in% effs$veg), "stratified effect table")
p <- plot_epoch(eff, "synthetic")
f <- tempfile(fileext = ".png")
ggsave(f, p, width = 160, height = 90, units = "mm", dpi = 150)
ok(file.exists(f) && file.size(f) > 0, "figure written")
cat("all R epoch tests passed\n")
