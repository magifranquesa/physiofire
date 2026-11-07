# Functions for the simplified superposed-epoch analysis (2025 case).
#   - burned cells and matched control cells per fire (select_fire_cells)
#   - per-fire daily burned - control differences, effect sizes with fire-level bootstrap, lead times, figures
# Used by R/epoch_cells.R and R/epoch_analysis.R; tested with synthetic data in R/tests/test_epoch.R.

suppressPackageStartupMessages({
  library(dplyr)
  library(sf)
  library(terra)
  library(ggplot2)
})

# --- Grid ---------------------------------------------------------------------------------------------------------

grid_template <- function(cfg, gname) {
  r <- cfg$region
  rast(xmin = r$lon_min, xmax = r$lon_max, ymin = r$lat_min, ymax = r$lat_max,
       resolution = as.numeric(cfg$grids[[gname]]$resolution_deg), crs = "EPSG:4326")
}

# All cells with centre coordinates and Python-grid indices (iy south to north, ix west to east, 0-based)
cell_table <- function(tmpl) {
  n <- ncell(tmpl)
  xy <- xyFromCell(tmpl, seq_len(n))
  rc <- rowColFromCell(tmpl, seq_len(n))
  data.frame(cell = seq_len(n), lon = xy[, 1], lat = xy[, 2], ix = rc[, 2] - 1L, iy = nrow(tmpl) - rc[, 1])
}

cell_polygons <- function(ct, res) {
  h <- res / 2
  st_sfc(lapply(seq_len(nrow(ct)), function(i) {
    x <- ct$lon[i]; y <- ct$lat[i]
    st_polygon(list(matrix(c(x - h, y - h, x + h, y - h, x + h, y + h, x - h, y + h, x - h, y - h),
                           ncol = 2, byrow = TRUE)))
  }), crs = 4326)
}

# Vegetation class fractions on grid g for a source (epoch.controls.vegetation):
#   "fuel":   FirEUrisk fuel-type fractions (python -m physiofire.preprocess.fuel) summed into epoch.fuel.classes
#   "corine": CORINE 2018 group fractions (epoch.corine.groups, GEE)
# Returns a SpatRaster with one layer per class, named as in the config.
vegetation_fractions <- function(cfg, root, g, source = cfg$epoch$controls$vegetation) {
  ec <- cfg$epoch
  if (source == "fuel") {
    f <- file.path(root, ec$fuel$out_dir, sprintf("fuel_fireurisk_%s.nc", g))
    tf <- rast(f, subds = "type_fraction")
    types <- as.integer(unlist(ec$fuel$types))
    stopifnot(nlyr(tf) == length(types))
    cls <- ec$fuel$classes
    out <- rast(lapply(names(cls), function(k) sum(tf[[match(as.integer(unlist(cls[[k]])), types)]])))
    names(out) <- names(cls)
  } else if (source == "corine") {
    out <- rast(file.path(root, cfg$gee$out_dir, sprintf("corine_%d_%s.nc", as.integer(ec$corine$year), g)),
                subds = "fraction")
    stopifnot(nlyr(out) == length(ec$corine$groups))
    names(out) <- names(ec$corine$groups)
  } else stop("unknown vegetation source: ", source)
  out
}

# Dominant vegetation class per cell: index (1-based, order of the layers) of the class with the largest fraction.
# frac: SpatRaster with one layer per class (vegetation_fractions).
dominant_group <- function(frac) {
  d <- which.max(frac)
  names(d) <- "veg"
  d
}

# Analysis stratum (woodland, shrubland, grassland, other) of a vegetation class (epoch.strata[[source]])
group_stratum <- function(group, strata) {
  out <- rep("other", length(group))
  for (s in names(strata)) out[group %in% unlist(strata[[s]])] <- s
  out
}

# --- Burned and control cells for one fire ------------------------------------------------------------------------
# perimeter: sf (one or more polygons of the fire), any CRS.
# layers: SpatRaster aligned with tmpl, with land_fraction, aridity_index, elevation_m, veg (group index) and
#         unburned (1 = no burn since ccfg$unburned_since up to the fire year, by EFFIS, MCD64A1, VNP64A1, ESFire30).
# Returns list(cells = data.frame or NULL, status, fire_veg).
select_fire_cells <- function(perimeter, tmpl, layers, ccfg, burned_min, veg_names) {
  res <- res(tmpl)[1]
  per <- st_union(st_make_valid(st_transform(perimeter, 4326)))
  cover <- rasterize(vect(st_sf(geometry = per)), tmpl, cover = TRUE, background = 0)
  ct <- cbind(cell_table(tmpl), as.data.frame(values(layers)), burned_fraction = values(cover)[, 1])
  ct$burned_fraction[is.na(ct$burned_fraction)] <- 0
  min_land <- as.numeric(ccfg$min_land_fraction)
  burned <- ct[ct$burned_fraction >= burned_min & !is.na(ct$land_fraction) & ct$land_fraction >= min_land, ]
  if (!nrow(burned)) return(list(cells = NULL, status = "no_burned_cells", fire_veg = NA_character_))

  w <- burned$burned_fraction
  veg_w <- tapply(w, burned$veg, sum)
  fire_veg <- as.integer(names(veg_w)[which.max(veg_w)])
  ref_ai <- weighted.mean(burned$aridity_index, w, na.rm = TRUE)
  ref_el <- weighted.mean(burned$elevation_m, w, na.rm = TRUE)

  # candidates: centre within max_dist of the perimeter (pre-filter on a box), whole cell >= min_dist away
  max_km <- as.numeric(ccfg$max_dist_km); min_km <- as.numeric(ccfg$min_dist_km)
  bb <- st_bbox(per)
  pad <- (max_km + 5) / 80   # degrees, generous at Iberian latitudes
  cand <- ct[ct$lon >= bb$xmin - pad & ct$lon <= bb$xmax + pad & ct$lat >= bb$ymin - pad & ct$lat <= bb$ymax + pad, ]
  per_m <- st_transform(per, 3035)
  pts <- st_transform(st_as_sf(cand, coords = c("lon", "lat"), crs = 4326, remove = FALSE), 3035)
  cand$dist_centre_km <- as.numeric(st_distance(pts, per_m)[, 1]) / 1000
  cand <- cand[cand$dist_centre_km <= max_km, ]
  cand$dist_cell_km <- as.numeric(st_distance(st_transform(cell_polygons(cand, res), 3035), per_m)[, 1]) / 1000
  # aridity tolerance relative to the burned cells' index: |AI_c - AI_b| / AI_b <= max_aridity_rel_diff
  max_ai <- as.numeric(ccfg$max_aridity_rel_diff) * ref_ai; max_el <- as.numeric(ccfg$max_elevation_diff_m)
  ok <- cand$dist_cell_km >= min_km & cand$burned_fraction == 0 &
    !is.na(cand$land_fraction) & cand$land_fraction >= min_land &
    !is.na(cand$unburned) & cand$unburned == 1 &
    !is.na(cand$veg) & cand$veg == fire_veg &
    !is.na(cand$aridity_index) & abs(cand$aridity_index - ref_ai) <= max_ai &
    !is.na(cand$elevation_m) & abs(cand$elevation_m - ref_el) <= max_el
  cand <- cand[ok, ]
  # ranking among valid candidates: closest in elevation and aridity (each relative to its tolerance), then distance
  cand$score <- abs(cand$elevation_m - ref_el) / max_el + abs(cand$aridity_index - ref_ai) / max_ai
  cand <- head(cand[order(cand$score, cand$dist_centre_km), ], as.integer(ccfg$n_max))

  burned$group <- "burned"; burned$dist_centre_km <- 0; burned$dist_cell_km <- 0; burned$score <- NA_real_
  cand$group <- rep("control", nrow(cand))
  status <- "ok"
  if (nrow(cand) < as.integer(ccfg$n_min)) {
    status <- sprintf("insufficient_controls (%d)", nrow(cand))
    cand <- cand[0, ]
  }
  cols <- c("group", "cell", "iy", "ix", "lon", "lat", "burned_fraction", "veg", "aridity_index", "elevation_m",
            "land_fraction", "dist_centre_km", "dist_cell_km", "score")
  out <- rbind(burned[, cols], cand[, cols])
  out$veg <- veg_names[out$veg]
  list(cells = out, status = status, fire_veg = veg_names[fire_veg],
       ref = c(aridity_index = ref_ai, elevation_m = ref_el))
}

# --- Statistics ---------------------------------------------------------------------------------------------------
# anom: long table from physiofire.epoch (fire_id, grid, cell_id, group, weight, variable, series, day_rel, z)

fire_day_table <- function(anom) {
  anom |>
    group_by(fire_id, grid, variable, series, day_rel) |>
    summarise(burned = {
                b <- group == "burned" & is.finite(z)
                if (any(b)) weighted.mean(z[b], weight[b]) else NA_real_
              },
              control = { k <- group == "control" & is.finite(z); if (any(k)) mean(z[k]) else NA_real_ },
              n_burned = sum(group == "burned" & is.finite(z)),
              n_control = sum(group == "control" & is.finite(z)), .groups = "drop") |>
    mutate(diff = burned - control)
}

.boot_ci <- function(x, B, level) {
  x <- x[is.finite(x)]
  if (length(x) < 2) return(c(NA_real_, NA_real_))
  m <- colMeans(matrix(sample(x, length(x) * B, replace = TRUE), nrow = length(x)))
  unname(quantile(m, c((1 - level) / 2, 1 - (1 - level) / 2)))
}

# Across fires, per day: mean difference (SD units), paired effect size dz = mean / sd, bootstrap CI over fires;
# and the same for the burned-cell anomaly alone. strata: extra grouping columns present in fd (e.g. veg, country).
effect_table <- function(fd, strata = character(), B = 2000, level = 0.95, seed = 42) {
  set.seed(seed)
  fd |>
    group_by(across(all_of(c(strata, "grid", "variable", "series", "day_rel")))) |>
    summarise(n_fires = sum(is.finite(diff)),
              mean_diff = mean(diff, na.rm = TRUE),
              sd_diff = sd(diff, na.rm = TRUE),
              ci_lo = .boot_ci(diff, B, level)[1], ci_hi = .boot_ci(diff, B, level)[2],
              mean_burned = mean(burned, na.rm = TRUE),
              burned_ci_lo = .boot_ci(burned, B, level)[1], burned_ci_hi = .boot_ci(burned, B, level)[2],
              .groups = "drop") |>
    mutate(dz = mean_diff / sd_diff)
}

# Lead time: earliest day d such that, on every day from d to -1, the effect is at least `threshold` SD in the
# expected direction and its CI excludes zero. Returned as days before ignition (0 = never, i.e. not on day -1).
lead_time <- function(eff, expected_sign, threshold, strata = character(), what = c("diff", "burned")) {
  what <- match.arg(what)
  est <- if (what == "diff") "mean_diff" else "mean_burned"
  lo <- if (what == "diff") "ci_lo" else "burned_ci_lo"
  hi <- if (what == "diff") "ci_hi" else "burned_ci_hi"
  eff |>
    group_by(across(all_of(c(strata, "grid", "variable", "series")))) |>
    arrange(day_rel, .by_group = TRUE) |>
    summarise(lead_days = {
                s <- unname(expected_sign[[first(variable)]])
                if (is.null(s)) s <- NA_real_
                met <- !is.na(s) & s * .data[[est]] >= threshold &
                  ((s < 0 & .data[[hi]] < 0) | (s > 0 & .data[[lo]] > 0))
                met[is.na(met)] <- FALSE
                # run of TRUE ending on the last day (-1)
                r <- rev(cumprod(rev(met)))
                as.integer(sum(r))
              },
              n_fires = max(n_fires), .groups = "drop") |>
    mutate(measure = what)
}

# --- Figures ------------------------------------------------------------------------------------------------------

plot_epoch <- function(eff, title = NULL, threshold = 0.5) {
  long <- bind_rows(
    eff |> transmute(variable, series, day_rel, est = mean_diff, lo = ci_lo, hi = ci_hi,
                     panel = "Burned − control"),
    eff |> transmute(variable, series, day_rel, est = mean_burned, lo = burned_ci_lo, hi = burned_ci_hi,
                     panel = "Burned cells"))
  ggplot(long, aes(day_rel, est, colour = series, fill = series)) +
    geom_hline(yintercept = 0, colour = "grey40", linewidth = 0.3) +
    geom_hline(yintercept = c(-threshold, threshold), colour = "grey70", linetype = "dashed", linewidth = 0.3) +
    geom_ribbon(aes(ymin = lo, ymax = hi), alpha = 0.2, colour = NA) +
    geom_line(linewidth = 0.6) +
    facet_grid(panel ~ variable) +
    labs(x = "Days relative to ignition", y = "Standardised anomaly (SD)", colour = NULL, fill = NULL,
         title = title) +
    theme_bw(base_size = 9) +
    theme(legend.position = "bottom", panel.grid.minor = element_blank())
}
