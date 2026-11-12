# Supplementary figures as PNG at 300 ppi in figures/supplement/, numbered in the order of the supplement:
#   figS1-figS5 = exploratory series of the other five fires (figS3_1 ... figS3_5), figS6 = summer 2022 drought
#   (figS3_6), figS7 = optimal SPEI scale of SIF, SIF/PAR and fPAR (figS4_secondary_scales).
# Same plots as the individual files (save_fig() in collect mode, as all_figures.R); same size, only the resolution
# changes. Nothing is recomputed.
# Usage (from the repository root): Rscript R/manuscript_figures/export_supplement.R

collected <- new.env()
options(ms.collect = collected)
for (s in c("fig3_explore.R", "figS4_secondary_scales.R"))
  source(file.path("R/manuscript_figures", s), local = new.env())
options(ms.collect = NULL)
source("R/manuscript_figures/style.R")

order <- c(figS1 = "figS3_1_explore_ES_277940", figS2 = "figS3_2_explore_ES_277944",
           figS3 = "figS3_3_explore_PT_278492", figS4 = "figS3_4_explore_PT_278497",
           figS5 = "figS3_5_explore_PT_278493", figS6 = "figS3_6_explore_drought_2022",
           figS7 = "figS4_secondary_scales")
out_dir <- file.path(root, "figures/supplement")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
for (k in names(order)) {
  f <- get(order[[k]], envir = collected)
  ggsave(file.path(out_dir, paste0(k, ".png")), f$plot, width = f$width, height = f$height, units = "mm",
         dpi = 300, type = "cairo")
  message(sprintf("%s.png <- %s (%d x %d mm, 300 ppi)", k, order[[k]], f$width, f$height))
}
