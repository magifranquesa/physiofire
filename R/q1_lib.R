# Functions of question 1 (docs/plan_q1_drought.md; config drought_q1): cell selection and daily SPEI per cell.
# Tested with synthetic data in R/tests/test_q1.R.

# Aridity class from the Global-AI index (classes: named list of [lower, upper) bounds)
aridity_class <- function(ai, classes) {
  out <- rep(NA_character_, length(ai))
  for (k in names(classes)) {
    b <- as.numeric(unlist(classes[[k]]))
    out[!is.na(ai) & ai >= b[1] & ai < b[2]] <- k
  }
  out
}

# Centre of the coarse cell (centres at multiples of res, e.g. ERA5-Land 0.1 deg) that contains each point
containing_centre <- function(x, res = 0.1) round(round(x / res) * res, 6)

# Stratum of a fuel class (strata: named list of class vectors); NA if none
class_stratum <- function(cls, strata) {
  out <- rep(NA_character_, length(cls))
  for (s in names(strata)) out[cls %in% unlist(strata[[s]])] <- s
  out
}

# Cell selection from a cell table with columns land_fraction, fuel_class, burned_any (TRUE if any burned area since
# drought_q1.cells.unburned_since by any source), aridity_index. Returns the selected rows with stratum, aridity
# class and the containing ERA5-Land cell.
select_q1_cells <- function(ct, qcfg) {
  cc <- qcfg$cells
  keep <- !is.na(ct$land_fraction) & ct$land_fraction >= as.numeric(cc$min_land_fraction) &
    ct$fuel_class %in% unlist(cc$fuel_classes) & !is.na(ct$burned_any) & !ct$burned_any
  out <- ct[keep, ]
  out$stratum <- class_stratum(out$fuel_class, qcfg$strata)
  out$aridity_class <- aridity_class(out$aridity_index, qcfg$aridity_classes)
  out$lon01 <- containing_centre(out$lon); out$lat01 <- containing_centre(out$lat)
  out
}

# SPEI handling of values outside the support of the fitted distribution (+-Inf): clamp to +-limit (NULL = keep)
clamp_spei <- function(x, limit) {
  if (is.null(limit)) return(x)
  x[is.infinite(x) & x < 0] <- -limit
  x[is.infinite(x) & x > 0] <- limit
  x
}

# Put 29 February back as NA: x has 365 values per year for dates_noleap; returns values on dates_all
restore_feb29 <- function(x, dates_noleap, dates_all) {
  out <- rep(NA_real_, length(dates_all))
  out[match(dates_noleap, dates_all)] <- x
  out
}

# Path from the configuration: absolute paths are kept, relative ones are taken from the repository root
q1_path <- function(root, p) if (grepl("^([A-Za-z]:)?[/\\]", p)) p else file.path(root, p)
