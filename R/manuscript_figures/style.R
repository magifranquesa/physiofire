# Common style of the manuscript figures (R/manuscript_figures/fig*.R): sizes, font, colours, theme and saving.
# Sourced by every figure script; changes nothing in the analysis.

source("R/config.R")
suppressPackageStartupMessages({ library(readr); library(dplyr); library(tidyr); library(ggplot2); library(patchwork) })
invisible(Sys.setlocale("LC_TIME", "C"))                        # English month names

cfg <- load_config(); root <- find_repo_root()
fig_dir <- file.path(root, "figures", "manuscript")
dir.create(fig_dir, showWarnings = FALSE, recursive = TRUE)

WIDTH_DOUBLE <- 190; WIDTH_SINGLE <- 90                          # mm
FONT <- "Arial"; BASE_PT <- 7

# One colour per variable in every figure (same hues as figures/explore/).
VAR_COL <- c(`SIF/APAR` = "#d95f02", NDVI = "#1b7837", EVI = "#762a83", FWI = "#b2182b", AED = "#8c510a",
             `SPEI-90` = "#2166ac", SPEI = "#2166ac",
             SIF = "#f4a261", `SIF/PAR` = "#fdd0a2", fPAR = "#bdbdbd")   # secondary: lighter tones
VAR_LAB <- c(sif_apar = "SIF/APAR", sif_apar_nopersist = "SIF/APAR", ndvi = "NDVI", evi = "EVI", fwi = "FWI",
             aed = "AED", spei_090 = "SPEI-90", sif = "SIF", sif_par = "SIF/PAR", fpar = "fPAR")

theme_ms <- function() {
  theme_bw(base_size = BASE_PT, base_family = FONT) +
    theme(panel.grid.minor = element_blank(), panel.grid.major = element_line(linewidth = 0.2, colour = "grey90"),
          panel.border = element_rect(linewidth = 0.3), axis.ticks = element_line(linewidth = 0.3),
          strip.background = element_rect(fill = "grey95", linewidth = 0.3),
          strip.text = element_text(size = BASE_PT, margin = margin(2, 2, 2, 2)),
          axis.text = element_text(size = BASE_PT - 0.5, colour = "grey20"),
          axis.title = element_text(size = BASE_PT + 0.5), legend.text = element_text(size = BASE_PT),
          legend.title = element_text(size = BASE_PT), legend.key.size = unit(3, "mm"),
          plot.tag = element_text(size = BASE_PT + 2, face = "bold", family = FONT),
          plot.margin = margin(2, 3, 2, 2))
}

tags_abc <- function() plot_annotation(tag_levels = "a", tag_prefix = "(", tag_suffix = ")")

# Vector PDF (cairo, fonts embedded) and 600 ppi PNG. With options(ms.collect = <environment>) the figure is stored
# in that environment instead (used by all_figures.R to build one PDF with every figure).
save_fig <- function(p, name, width, height) {
  env <- getOption("ms.collect")
  if (is.environment(env)) {
    assign(name, list(plot = p, width = width, height = height), envir = env)
    return(invisible(NULL))
  }
  ggsave(file.path(fig_dir, paste0(name, ".pdf")), p, width = width, height = height, units = "mm",
         device = cairo_pdf, family = FONT)
  ggsave(file.path(fig_dir, paste0(name, ".png")), p, width = width, height = height, units = "mm", dpi = 600,
         type = "cairo")
  message(sprintf("wrote %s.{pdf,png} (%d x %d mm)", file.path(fig_dir, name), width, height))
}
