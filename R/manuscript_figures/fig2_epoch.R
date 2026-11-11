# Figure 2: superposed-epoch composites of the 2025 case (double column).
# Inputs: data/processed/epoch/report2025_effects.csv (R/epoch_report_2025.R: burned - control difference and burned
# anomaly, 95% bootstrap interval by fire) and epoch_fire_days.csv (per fire and day: mean anomaly of the burned
# cells and of the controls). Rows: SIF/APAR without fPAR persistence, NDVI, EVI, FWI, AED; columns: all fires,
# shrubland, heathland (same groups as the report). Lines: difference (thick, shaded interval), burned cells (dashed)
# and controls (dotted, grey interval). Horizontal lines: 0 (thin, light grey, first layer, under bands and lines)
# and +-0.5 SD (dashed, lead-time threshold).
# DESCRIPTIVE CALCULATION FOR THE FIGURE: the control line is the mean over fires of the per-fire control anomaly in
# epoch_fire_days.csv, with the same fire-level bootstrap as the burned line (epoch_lib.R .boot_ci, same B, level and
# seed); it is not used by any criterion. The burned mean recomputed the same way is checked against the report.
# Days with fewer than MIN_FIRES fires with data are not drawn (the label gives the range of fires per day drawn).
# Usage (from the repository root): Rscript R/manuscript_figures/fig2_epoch.R

source("R/manuscript_figures/style.R")
source("R/epoch_lib.R")
ec <- cfg$epoch
thr <- as.numeric(ec$effect_threshold_sd)
MIN_FIRES <- 3L
CONTROL_COL <- "grey35"                                            # control line (dotted) and band: grey
vars <- c("sif_apar_nopersist", "ndvi", "evi", "fwi", "aed")
groups <- c(all = "All fires", shrubland = "Shrubland", heathland = "Heathland")
gfun <- list(all = function(x) rep(TRUE, nrow(x)), shrubland = function(x) x$clc_group == "shrubland",
             heathland = function(x) x$clc_group == "wet_heath")
e <- read_csv(file.path(root, "data/processed/epoch/report2025_effects.csv"), show_col_types = FALSE) |>
  filter(variable %in% vars, group %in% names(groups))
stopifnot(length(unique(e$series)) == 1, unique(e$series) == ec$main_series)

fd <- read_csv(file.path(root, "data/processed/epoch/epoch_fire_days.csv"), show_col_types = FALSE,
               col_types = cols(fire_id = col_character())) |>
  filter(series == ec$main_series, variable %in% vars)
set.seed(as.integer(cfg$random_seed))
B <- as.integer(ec$bootstrap_n); lev <- as.numeric(ec$ci_level)
ctl <- bind_rows(lapply(names(groups), function(g) fd[gfun[[g]](fd), ] |>
  group_by(variable, day_rel) |>
  summarise(mean_control = mean(control, na.rm = TRUE), mean_burned_chk = mean(burned, na.rm = TRUE),
            control_ci_lo = .boot_ci(control, B, lev)[1], control_ci_hi = .boot_ci(control, B, lev)[2],
            .groups = "drop") |> mutate(group = g)))
e <- e |> left_join(ctl, by = c("group", "variable", "day_rel")) |>
  mutate(var = factor(VAR_LAB[variable], levels = unname(VAR_LAB[vars])))
chk <- max(abs(e$mean_burned - e$mean_burned_chk), na.rm = TRUE)
message(sprintf("check: max |burned mean recomputed - report| = %.2e", chk))
stopifnot(chk < 1e-9)
e <- e |> mutate(across(c(mean_diff, ci_lo, ci_hi, mean_burned, mean_control, control_ci_lo, control_ci_hi),
                        ~ ifelse(n_fires >= MIN_FIRES, .x, NA_real_)))

nf <- e |> filter(n_fires >= MIN_FIRES) |> group_by(group, var) |>
  summarise(lo = min(n_fires), hi = max(n_fires), .groups = "drop") |>
  mutate(lab = ifelse(lo == hi, sprintf("n = %d fires", hi), sprintf("n = %d–%d fires", lo, hi)))
yl <- range(c(e$ci_lo, e$ci_hi, e$mean_burned, e$control_ci_lo, e$control_ci_hi, -thr, thr), na.rm = TRUE)
lt <- c(`Burned − control` = "solid", `Burned cells` = "22", `Controls` = "12")
lw <- c(`Burned − control` = 0.6, `Burned cells` = 0.35, `Controls` = 0.35)
long <- e |> select(group, var, day_rel, `Burned − control` = mean_diff, `Burned cells` = mean_burned,
                    Controls = mean_control) |>
  pivot_longer(-c(group, var, day_rel), names_to = "line", values_to = "y") |>
  mutate(line = factor(line, levels = names(lt)))

col_plot <- function(g) {
  d <- e |> filter(group == g)
  ggplot(d, aes(day_rel)) +
    geom_hline(yintercept = 0, colour = "grey80", linewidth = 0.3) +             # first layer: under bands and lines
    geom_hline(yintercept = c(-thr, thr), colour = "grey60", linewidth = 0.25, linetype = "longdash") +
    geom_ribbon(aes(ymin = control_ci_lo, ymax = control_ci_hi), fill = "grey60", alpha = 0.25, na.rm = TRUE) +
    geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi, fill = var), alpha = 0.3, na.rm = TRUE) +
    geom_line(data = long |> filter(group == g, line == "Controls"), aes(y = y, linetype = line, linewidth = line),
              colour = CONTROL_COL, na.rm = TRUE) +
    geom_line(data = long |> filter(group == g, line != "Controls"),
              aes(y = y, colour = var, linetype = line, linewidth = line), na.rm = TRUE) +
    geom_text(data = nf |> filter(group == g), aes(x = -59, y = yl[2], label = lab), inherit.aes = FALSE,
              hjust = 0, vjust = 1, size = (BASE_PT - 1) / .pt, family = FONT, colour = "grey30") +
    facet_grid(var ~ ., switch = "y") +
    scale_colour_manual(values = VAR_COL, guide = "none") + scale_fill_manual(values = VAR_COL, guide = "none") +
    scale_linetype_manual(values = lt, name = NULL) + scale_linewidth_manual(values = lw, name = NULL) +
    scale_x_continuous(limits = c(-60, -1), breaks = c(-60, -45, -30, -15, -1), expand = c(0.01, 0)) +
    scale_y_continuous(limits = yl) +
    labs(title = groups[[g]], x = "Days before ignition", y = NULL) + theme_ms() +
    theme(plot.title = element_text(size = BASE_PT + 1, hjust = 0.5, family = FONT),
          strip.placement = "outside", strip.text.y.left = element_text(angle = 90),
          legend.position = "top", legend.key.width = unit(7, "mm"), legend.key.height = unit(2.5, "mm"),
          legend.text = element_text(size = BASE_PT - 0.5, family = FONT))
}
ps <- lapply(names(groups), col_plot)
ps[[1]] <- ps[[1]] + labs(y = "Standardised anomaly (SD)")
ps[2:3] <- lapply(ps[2:3], function(p) p + theme(strip.text.y.left = element_blank(), strip.background.y = element_blank()))
# legend drawn as its own strip (line + band keys), above the panels
# difference and burned keys in black (drawn in the colour of each variable); controls in grey, as drawn
leg_items <- tibble(x = c(0, 1.25, 2.5), lab = names(lt), lty = unname(lt), lwd = unname(lw),
                    band = c("grey45", NA, "grey60"), col = c("black", "black", CONTROL_COL))
leg <- ggplot(leg_items) +
  geom_rect(data = leg_items |> filter(!is.na(band)), aes(xmin = x, xmax = x + 0.28, ymin = -0.35, ymax = 0.35,
                                                           fill = band), alpha = 0.35) +
  geom_segment(aes(x = x, xend = x + 0.28, y = 0, yend = 0, linetype = lty, linewidth = lwd, colour = col)) +
  geom_text(aes(x = x + 0.33, y = 0, label = lab), hjust = 0, size = (BASE_PT - 0.5) / .pt, family = FONT) +
  scale_fill_identity() + scale_linetype_identity() + scale_linewidth_identity() + scale_colour_identity() +
  coord_cartesian(xlim = c(-0.9, 4.4), ylim = c(-0.6, 0.6), expand = FALSE) + theme_void()
ps <- lapply(ps, function(p) p + theme(legend.position = "none"))
p <- wrap_plots(ps, nrow = 1) / leg + plot_layout(heights = c(1, 0.035)) +
  plot_annotation(tag_levels = list(c("(a)", "(b)", "(c)", "")))
save_fig(p, "fig2_epoch_2025", WIDTH_DOUBLE, 180)
