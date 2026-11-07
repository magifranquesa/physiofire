# Candidate fire table for one year: EFFIS perimeters with an ignition date and a coherence flag.
#
# Rule (config.yaml, section ignition). With alignment on ignition and masking from that day, the dangerous error
# is a LATE date (post-ignition data would enter the pre-fire window), so:
#   ignition date = earliest of EFFIS FIREDATE, first VIIRS detection (type 0, confidence not low), first MCD64A1
#   and first VNP64A1 burn date, each inside the perimeter and within
#   [FIREDATE - ignition_window_before_days, FINALDATE + ignition_window_after_days];
#   coherence flag = any VIIRS detection or burn date inside the perimeter in
#   [FIREDATE - prior_lookback_days, FIREDATE - ignition_window_before_days) (possible merged perimeters or an
#   earlier fire); flagged perimeters are excluded in principle.
# Dates are UTC calendar days (burned-area products have daily resolution).
#
# This is NOT the selection: no vegetation or meteorological series are extracted, and the selection criteria
# (area, vegetation, overlap...) are applied later to this table.
#
# Input:  data/interim/fires/effis_iberia_*.gpkg (R/effis_perimeters.R), data/interim/firms/firms_iberia_clean.csv
#         (R/firms_clean.R), {mcd64a1,vnp64a1}_burndate_*.nc (python -m physiofire.download.gee burn_dates).
# Output: data/interim/fires/fire_candidates_{year}.csv and a summary.
#
# Usage (from the repository root): Rscript R/fire_candidates.R [year]   (default: fires$first_case_year)

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(sf)
  library(terra)
})
source("R/config.R")
cfg <- load_config()
root <- find_repo_root()
ic <- cfg$ignition
args <- commandArgs(trailingOnly = TRUE)
year <- if (length(args)) as.integer(args[1]) else as.integer(cfg$fires$first_case_year)
out_dir <- file.path(root, cfg$effis$out_dir)
w_before <- as.integer(ic$ignition_window_before_days)
w_after <- as.integer(ic$ignition_window_after_days)
lookback <- as.integer(ic$prior_lookback_days)

# --- Perimeters of the year --------------------------------------------------------------------------------------
gpkg <- list.files(out_dir, pattern = "^effis_iberia_[0-9]+_[0-9]+\\.gpkg$", full.names = TRUE)
stopifnot(length(gpkg) == 1)
e <- st_read(gpkg, quiet = TRUE) |> filter(fire_year == year)
e$effis_date <- as.Date(e$start_utc, tz = "UTC")
e$final_date <- as.Date(ifelse(is.na(e$final_utc), e$start_utc, e$final_utc) |> as.POSIXct(tz = "UTC"), tz = "UTC")
e$win_start <- e$effis_date - w_before
e$win_end <- e$final_date + w_after
e$prior_start <- e$effis_date - lookback
message(sprintf("%d perimeters in %d", nrow(e), year))

# Earliest date in the ignition window and count of dates in the prior window, per perimeter, from a list of
# date vectors (one element per perimeter)
summarise_dates <- function(dl, prefix) {
  out <- lapply(seq_along(dl), function(i) {
    d <- dl[[i]]
    d <- d[!is.na(d)]
    inw <- d[d >= e$win_start[i] & d <= e$win_end[i]]
    prior <- d[d >= e$prior_start[i] & d < e$win_start[i]]
    data.frame(first = if (length(inw)) min(inw) else as.Date(NA), n = length(inw), n_prior = length(prior),
               first_prior = if (length(prior)) min(prior) else as.Date(NA))
  })
  out <- bind_rows(out)
  names(out) <- paste0(prefix, "_", names(out))
  out
}

# --- VIIRS active fires --------------------------------------------------------------------------------------------
firms <- read_csv(file.path(root, cfg$firms$out_dir, "firms_iberia_clean.csv"),
                  col_types = cols(acq_time = col_character(), .default = col_guess()), progress = FALSE) |>
  filter(source %in% unlist(cfg$firms$viirs_sources),
         acq_date >= as.Date(sprintf("%d-01-01", year)) - lookback,
         acq_date <= as.Date(sprintf("%d-12-31", year)) + w_after + 60)
f_sf <- st_as_sf(firms, coords = c("longitude", "latitude"), crs = 4326)
hits <- st_intersects(st_transform(e, 3035), st_transform(f_sf, 3035))
viirs <- summarise_dates(lapply(hits, function(idx) firms$acq_date[idx]), "viirs")

# --- Burned-area burn dates (pixel centres inside the perimeter) ---------------------------------------------------
burn_dates <- function(product) {
  files <- list.files(file.path(root, ic$burn_date_dir), pattern = sprintf("^%s_burndate_.*\\.nc$", product),
                      full.names = TRUE)
  if (!length(files)) stop("no burn-date files for ", product, " in ", ic$burn_date_dir)
  v <- vect(st_transform(e, 4326))
  per_file <- lapply(files, function(f) {
    r <- rast(f, subds = "burn_date")
    x <- terra::extract(r, v, ID = TRUE)
    vals <- as.matrix(x[, -1, drop = FALSE])
    split(as.vector(vals), rep(x$ID, times = ncol(vals)))
  })
  lapply(seq_len(nrow(e)), function(i) {
    d <- unlist(lapply(per_file, function(p) p[[as.character(i)]]))
    as.Date(d[!is.na(d)], origin = "1970-01-01")
  })
}
mcd <- summarise_dates(burn_dates("mcd64a1"), "mcd64a1")
vnp <- summarise_dates(burn_dates("vnp64a1"), "vnp64a1")

# --- Candidate table ----------------------------------------------------------------------------------------------
tab <- st_drop_geometry(e) |>
  transmute(effis_id = id, country = COUNTRY, province = PROVINCE, commune = COMMUNE, burned_ha,
            effis_firedate = start_utc, effis_finaldate = final_utc, effis_class = CLASS,
            effis_first = effis_date) |>
  bind_cols(viirs, mcd, vnp)
srcs <- unlist(ic$sources)
first_mat <- sapply(srcs, function(s) as.numeric(tab[[paste0(s, "_first")]]))
if (is.null(dim(first_mat))) first_mat <- matrix(first_mat, nrow = 1, dimnames = list(NULL, srcs))
tab$ignition_date <- as.Date(apply(first_mat, 1, function(r) if (all(is.na(r))) NA else min(r, na.rm = TRUE)),
                             origin = "1970-01-01")
tab$ignition_source <- apply(first_mat, 1, function(r) {
  if (all(is.na(r))) return(NA_character_)
  paste(srcs[!is.na(r) & r == min(r, na.rm = TRUE)], collapse = "+")
})
tab$ignition_minus_effis_days <- as.integer(tab$ignition_date - tab$effis_first)
tab$n_prior_activity <- tab$viirs_n_prior + tab$mcd64a1_n_prior + tab$vnp64a1_n_prior
tab$coherence_flag <- tab$n_prior_activity > 0
# relative weight of the prior activity (for deciding whether a flag is material), and a review marker for
# ignitions much earlier than EFFIS that are not flagged (possible merged perimeters within the window)
tab$viirs_prior_frac <- with(tab, viirs_n_prior / pmax(viirs_n + viirs_n_prior, 1))
tab$burn_prior_frac <- with(tab, (mcd64a1_n_prior + vnp64a1_n_prior) /
                              pmax(mcd64a1_n + vnp64a1_n + mcd64a1_n_prior + vnp64a1_n_prior, 1))
tab$review_early <- !is.na(tab$ignition_minus_effis_days) &
  tab$ignition_minus_effis_days < -as.integer(ic$review_early_days)
tab$prior_sources <- apply(tab[, c("viirs_n_prior", "mcd64a1_n_prior", "vnp64a1_n_prior")], 1,
                           function(r) paste(c("viirs", "mcd64a1", "vnp64a1")[r > 0], collapse = "+"))
tab <- tab |> arrange(desc(burned_ha))
write_csv(tab, file.path(out_dir, sprintf("fire_candidates_%d.csv", year)))

# --- Summary ------------------------------------------------------------------------------------------------------
tab$size <- cut(tab$burned_ha, c(-Inf, 100, 500, 1000, 5000, Inf),
                labels = c("<100", "100-500", "500-1000", "1000-5000", ">=5000"), right = FALSE)
sm <- tab |> group_by(size) |>
  summarise(n = n(), with_viirs = sum(viirs_n > 0), with_mcd64a1 = sum(mcd64a1_n > 0),
            with_vnp64a1 = sum(vnp64a1_n > 0),
            ign_by_effis = sum(grepl("effis", ignition_source)),
            ign_by_viirs = sum(grepl("viirs", ignition_source)),
            ign_by_mcd64a1 = sum(grepl("mcd64a1", ignition_source)),
            ign_by_vnp64a1 = sum(grepl("vnp64a1", ignition_source)),
            earlier_than_effis = sum(ignition_minus_effis_days < 0, na.rm = TRUE),
            earlier_gt1d = sum(ignition_minus_effis_days < -1, na.rm = TRUE),
            flagged = sum(coherence_flag), review_early = sum(review_early), .groups = "drop")
print(as.data.frame(sm))
write_csv(sm, file.path(out_dir, sprintf("fire_candidates_%d_summary.csv", year)))
message("largest perimeters:")
print(as.data.frame(head(tab |> select(effis_id, country, commune, burned_ha, effis_first, viirs_first, mcd64a1_first,
                                       vnp64a1_first, ignition_date, ignition_source, coherence_flag,
                                       prior_sources), 30)))
