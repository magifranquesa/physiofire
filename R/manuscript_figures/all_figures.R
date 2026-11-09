# All manuscript and supplementary figures in one vector PDF for the co-authors:
# figures/manuscript/all_figures.pdf (A4 portrait, one figure per page at its final size, with a heading).
# Runs every figure script with save_fig() in collect mode (style.R), so the pages are the same plots as the
# individual files; it does not write the individual files.
# Usage (from the repository root): Rscript R/manuscript_figures/all_figures.R

collected <- new.env()
options(ms.collect = collected)
scripts <- c("fig1_study_area.R", "fig2_epoch.R", "fig3_explore.R", "fig4_scales.R", "fig5_onset_timing.R",
             "figS4_secondary_scales.R")
for (s in scripts) source(file.path("R/manuscript_figures", s), local = new.env())
options(ms.collect = NULL)
source("R/manuscript_figures/style.R")
suppressPackageStartupMessages(library(grid))

pages <- c(fig1_study_area = "Figure 1", fig2_epoch_2025 = "Figure 2", fig3_explore_A_Rua = "Figure 3",
           fig4_scales = "Figure 4", fig5_onset_timing = "Figure 5")
s3 <- sort(grep("^figS3_", ls(collected), value = TRUE))
pages <- c(pages, setNames(sprintf("Figure S3.%d", seq_along(s3)), s3), figS4_secondary_scales = "Figure S4")
stopifnot(all(names(pages) %in% ls(collected)), all(ls(collected) %in% names(pages)))

f <- file.path(fig_dir, "all_figures.pdf")
cairo_pdf(f, width = 210 / 25.4, height = 297 / 25.4, family = FONT, onefile = TRUE)
for (nm in names(pages)) {
  x <- get(nm, envir = collected)
  grid.newpage()
  grid.text(sprintf("%s  (%s, %d × %d mm)", pages[[nm]], nm, x$width, x$height),
            x = unit(10, "mm"), y = unit(1, "npc") - unit(12, "mm"), just = c("left", "top"),
            gp = gpar(fontfamily = FONT, fontsize = 9, fontface = "bold"))
  pushViewport(viewport(x = unit(0.5, "npc"), y = unit(1, "npc") - unit(20, "mm"), just = c("centre", "top"),
                        width = unit(x$width, "mm"), height = unit(x$height, "mm")))
  grid.draw(patchwork::patchworkGrob(x$plot))
  popViewport()
}
invisible(dev.off())
message("wrote ", f, " (", length(pages), " pages)")
