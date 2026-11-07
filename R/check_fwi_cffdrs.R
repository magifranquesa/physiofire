# Cross-check of the gridded FWI System (xclim, python -m physiofire.preprocess.fwi) against the reference R
# implementation of the Canadian Forest Service (package cffdrs), on a sample of ERA5-Land cells.
# Same noon inputs, same start (first day of the sample), standard start-up codes, latitude day-length adjustment.
#
# Input:  data/interim/era5land_fwi/cffdrs_check_sample.csv (columns time, lat, lon, id, tas, hurs, sfcWind, pr and
#         the xclim outputs FFMC, DMC, DC, ISI, BUI, FWI)
# Output: printed summary of the differences (max absolute and relative), per index
#
# Usage (from the repository root): Rscript R/check_fwi_cffdrs.R [sample.csv]

suppressPackageStartupMessages({
  library(cffdrs)
  library(dplyr)
  library(readr)
})
args <- commandArgs(trailingOnly = TRUE)
f <- if (length(args)) args[1] else "data/interim/era5land_fwi/cffdrs_check_sample.csv"
x <- read_csv(f, show_col_types = FALSE) |> arrange(id, time)
idx <- c("FFMC", "DMC", "DC", "ISI", "BUI", "FWI")
res <- bind_rows(lapply(split(x, x$id), function(d) {
  inp <- data.frame(id = d$id, lat = d$lat, long = d$lon, yr = as.integer(format(d$time, "%Y")),
                    mon = as.integer(format(d$time, "%m")), day = as.integer(format(d$time, "%d")),
                    temp = d$tas, rh = d$hurs, ws = d$sfcWind, prec = d$pr)
  r <- fwi(inp, init = data.frame(ffmc = 85, dmc = 6, dc = 15, lat = d$lat[1]), batch = TRUE, out = "fwi",
           lat.adjust = TRUE, uppercase = TRUE)
  out <- data.frame(id = d$id, time = d$time)
  for (v in idx) { out[[paste0(v, "_xclim")]] <- d[[v]]; out[[paste0(v, "_cffdrs")]] <- r[[v]] }
  out
}))
summ <- bind_rows(lapply(idx, function(v) {
  a <- res[[paste0(v, "_xclim")]]; b <- res[[paste0(v, "_cffdrs")]]
  data.frame(index = v, n = sum(is.finite(a) & is.finite(b)), max_abs_diff = max(abs(a - b), na.rm = TRUE),
             p99_abs_diff = unname(quantile(abs(a - b), 0.99, na.rm = TRUE)),
             max_rel_diff_pct = 100 * max(abs(a - b) / pmax(abs(b), 1), na.rm = TRUE),
             r = cor(a, b, use = "complete.obs"))
}))
print(summ, digits = 4)
aug <- res[format(res$time, "%m") == "08", ]
cat(sprintf("August only: FWI max |diff| = %.4f over %d cell-days\n",
            max(abs(aug$FWI_xclim - aug$FWI_cffdrs)), nrow(aug)))
