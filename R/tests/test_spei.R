# Synthetic checks of the daily SPEI (concretion 5 of docs/plan_q1_drought.md): the SPEI package (1.8.1) fits one
# distribution per day of year with frequency-365 series, uses only the reference period for the fit, our
# cumulative-sum accumulation equals the package's own, and the result is standard normal where it should be.
# Usage: Rscript R/tests/test_spei.R
source("R/spei_lib.R")
suppressPackageStartupMessages(library(lmom))
ok <- function(cond, msg) { if (!isTRUE(cond)) stop("FAIL: ", msg); cat("ok -", msg, "\n") }
set.seed(42)

# --- 29 February and rolling sums ---------------------------------------------------------------------------------
dates <- seq(as.Date("1991-01-01"), as.Date("2025-12-31"), by = "day")
z <- drop_feb29(seq_along(dates), dates)
ok(length(z$x) == 35 * 365, "29 February removed: 365 days per year")
ok(!any(format(z$dates, "%m-%d") == "02-29"), "no 29 February left")
x <- rnorm(200)
ok(isTRUE(all.equal(roll_sum(x, 7)[7:200], zoo::rollapply(x, 7, sum, align = "right"))), "roll_sum equals rollapply")
ok(all(is.na(roll_sum(x, 7)[1:6])), "roll_sum NA for incomplete windows")
x2 <- x; x2[50] <- NA
ok(all(is.na(roll_sum(x2, 7)[50:56])) && !is.na(roll_sum(x2, 7)[57]), "roll_sum NA where the window has a gap")

# --- Synthetic daily water balance: seasonal mean, 35 years --------------------------------------------------------
ny <- 35; year0 <- 1991
doy <- rep(1:365, ny)
d <- 2 * sin(2 * pi * doy / 365) + rnorm(365 * ny, 0, 3)

# (a) package accumulation (scale = k, rectangular kernel) == our cumsum accumulation passed with scale = 1
k <- 30
r_pkg <- SPEI::spei(ts(d, start = c(year0, 1), frequency = 365), scale = k, na.rm = TRUE,
                    ref.start = c(1991, 1), ref.end = c(2020, 365), verbose = FALSE)
r_our <- spei_daily(d, year0, k)
ok(isTRUE(all.equal(as.numeric(r_pkg$fitted), r_our$spei)), "SPEI with our accumulation equals the package (k = 30)")

# (b) one fit per day of year: 365 parameter sets, all different
ok(all(dim(r_our$coef) == c(3, 365)), "365 log-logistic parameter sets (one per day of year)")
ok(length(unique(round(r_our$coef[1, ], 6))) > 300, "parameters differ between days of year")

# (c) within the reference period, each day of year is ~standard normal
s <- matrix(r_our$spei, nrow = 365)            # day of year x year
ref_cols <- (1991:2020) - year0 + 1
m <- rowMeans(s[, ref_cols], na.rm = TRUE); sd_ <- apply(s[, ref_cols], 1, sd, na.rm = TRUE)
ok(abs(mean(m[31:365])) < 0.05 && abs(mean(sd_[31:365]) - 1) < 0.1,
   sprintf("reference period ~N(0,1) by day of year (mean %.3f, SD %.3f)", mean(m[31:365]), mean(sd_[31:365])))

# (d) only the reference period is used for the fit: changing 2021-2025 does not change the parameters,
#     and a shift after 2020 appears as a shift of the SPEI
d2 <- d; post <- (2021 - year0) * 365 + 1; d2[post:length(d2)] <- d2[post:length(d2)] - 3
r2 <- spei_daily(d2, year0, k)
ok(isTRUE(all.equal(r2$coef, r_our$coef)), "parameters depend only on the reference period")
a2 <- r2$spei[(post + k):length(d2)]; a1 <- r_our$spei[(post + k):length(d)]
ok(median(a2, na.rm = TRUE) < median(a1, na.rm = TRUE) - 1, "a drier period after 2020 gives a lower SPEI")
cat(sprintf("  non-finite SPEI after a shift of -3/day (outside the reference support): %d of %d
",
            sum(is.infinite(a2)), length(a2)))

# (e) the transformation is qnorm(cdfglo(acc, params of that day)): check day 200 of 2023
acc <- roll_sum(d, k)
i <- (2023 - year0) * 365 + 200
ok(isTRUE(all.equal(r_our$spei[i], qnorm(lmom::cdfglo(acc[i], r_our$coef[, 200])))),
   "SPEI = qnorm(log-logistic CDF with the day-of-year parameters)")

# (f) the daily method reproduces the package's standard monthly SPEI when applied to monthly data
mon <- tapply(d, rep(1:(12 * ny), each = 1, length.out = 365 * ny)[seq_along(d)], sum)   # pseudo-months
mon <- as.numeric(mon[1:(12 * ny)])
r_m_pkg <- SPEI::spei(ts(mon, start = c(year0, 1), frequency = 12), scale = 3, na.rm = TRUE,
                      ref.start = c(1991, 1), ref.end = c(2020, 12), verbose = FALSE)
acc3 <- roll_sum(mon, 3)
r_m_our <- SPEI::spei(ts(acc3, start = c(year0, 1), frequency = 12), scale = 1, na.rm = TRUE,
                      ref.start = c(1991, 1), ref.end = c(2020, 12), verbose = FALSE)
ok(isTRUE(all.equal(as.numeric(r_m_pkg$fitted), as.numeric(r_m_our$fitted))),
   "monthly: cumsum accumulation + scale 1 equals the package with scale 3")

# (g) timing on one cell and six scales (to estimate the full run)
t0 <- Sys.time()
for (sc in c(15, 30, 60, 90, 180, 365)) invisible(spei_daily(d, year0, sc))
cat(sprintf("time for one cell, six scales: %.1f s\n", as.numeric(difftime(Sys.time(), t0, units = "secs"))))
cat("all SPEI tests passed\n")
