# Daily SPEI for question 1 (docs/plan_q1_drought.md): log-logistic distribution fitted by unbiased probability-
# weighted moments, one fit per day of year (29 February removed), reference period 1991-2020, with the R package
# SPEI (1.8.1). The n-day accumulation of the daily water balance D = P - ET0 is computed here with cumulative sums
# and passed to SPEI::spei() with scale = 1: identical to the package's own rectangular-kernel accumulation
# (checked in R/tests/test_spei.R) and much faster for daily series.
suppressPackageStartupMessages(library(SPEI))

# Remove 29 February: returns list(x, dates) with 365 days per year
drop_feb29 <- function(x, dates) {
  keep <- !(format(dates, "%m-%d") == "02-29")
  list(x = x[keep], dates = dates[keep])
}

# Right-aligned n-day sums (NA for the first n-1 days or if any day in the window is NA)
roll_sum <- function(x, n) {
  if (n == 1) return(x)
  ok <- !is.na(x)
  cs <- cumsum(ifelse(ok, x, 0)); cn <- cumsum(ok)
  out <- rep(NA_real_, length(x))
  i <- n:length(x)
  out[i] <- cs[i] - c(0, cs)[i - n + 1]
  nv <- cn[i] - c(0, cn)[i - n + 1]
  out[i][nv < n] <- NA
  out
}

# Daily SPEI of one series of D (one value per day, 29 February already removed, starting on 1 January of year0).
# Returns list(spei = numeric vector, coef = 3 x 365 matrix of log-logistic parameters).
spei_daily <- function(d, year0, scale_days, ref = c(1991, 2020)) {
  acc <- roll_sum(d, scale_days)
  x <- ts(acc, start = c(year0, 1), frequency = 365)
  r <- SPEI::spei(x, scale = 1, distribution = "log-Logistic", fit = "ub-pwm", na.rm = TRUE,
                  ref.start = c(ref[1], 1), ref.end = c(ref[2], 365), verbose = FALSE)
  list(spei = as.numeric(r$fitted), coef = r$coefficients[, 1, ])
}
