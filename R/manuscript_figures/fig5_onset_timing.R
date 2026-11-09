# Figure 5: response timing at drought onsets in shrubland (Q1b, double column).
# Inputs: data/processed/drought_q1b/hypotheses_q1b.csv (H3b sign scores with bootstrap CI by event; season split,
# exploratory) and analysis2b_episodes.csv (response day per cell-episode and variable).
# (a) mean sign score of SIF/APAR vs NDVI and vs EVI with its 95% interval: all events (criterion), spring and summer
#     onsets (exploratory). (b) distribution of the paired differences in response day d = T(SIF/APAR) - T(reference).
# DESCRIPTIVE CALCULATION FOR THE FIGURE (panel b): d per cell-episode in events with both variables observed, as in
# drought_q1b.pair_scores: d = Ta - Tb if both respond; Ta - 90 or 90 - Tb (bound) if one is censored at +90; doubly
# censored pairs left out (not informative). No new parameters or statistics; the counts and the median over events of
# the event median d are checked against hypotheses_q1b.csv.
# Usage (from the repository root): Rscript R/manuscript_figures/fig5_onset_timing.R

source("R/manuscript_figures/style.R")
hb <- cfg$drought_q1b$h3b
censor <- as.integer(hb$censor_day)
od <- file.path(root, cfg$drought_q1b$out_dir)
refs <- c(ndvi = "NDVI", evi = "EVI")
season_lab <- c(all = "All events", spring = "Spring onsets\n(exploratory)", summer = "Summer onsets\n(exploratory)")

# --- (b) paired differences ----------------------------------------------------------------------------------------
ep <- read_csv(file.path(od, "analysis2b_episodes.csv"), show_col_types = FALSE) |>
  filter(stratum == "shrubland", event >= 0)
pairs <- bind_rows(lapply(names(refs), function(b) {
  ta <- ep$resp_sif_apar; tb <- ep[[paste0("resp_", b)]]
  ok <- ep$obs_sif_apar & ep[[paste0("obs_", b)]]
  fa <- is.finite(ta); fb <- is.finite(tb)
  d <- ifelse(fa & fb, ta - tb, ifelse(fa, ta - censor, ifelse(fb, censor - tb, NA_real_)))
  type <- ifelse(fa & fb, "Both responded", ifelse(fa | fb, "One censored at +90 (bound)", NA))
  tibble(event = ep$event, season = ep$event_season, against = refs[[b]], d = d, type = type)[ok & (fa | fb), ]
}))

# check against the stored H3b results
hq <- read_csv(file.path(od, "hypotheses_q1b.csv"), show_col_types = FALSE) |> filter(stratum == "shrubland")
chk <- pairs |> group_by(against) |>
  summarise(n_pairs = n(), n_events = n_distinct(event),
            median_d = median(tapply(d, event, median)), .groups = "drop") |>
  left_join(hq |> filter(test == "H3b") |> transmute(against = toupper(against), n_pairs_ref = n_pairs_informative,
                                                     n_events_ref = n_events, median_d_ref = median_d), by = "against")
print(as.data.frame(chk))
stopifnot(all(chk$n_pairs == chk$n_pairs_ref), all(chk$n_events == chk$n_events_ref),
          all(abs(chk$median_d - chk$median_d_ref) < 1e-9))

pb_data <- bind_rows(pairs |> mutate(season = "all"), pairs |> filter(season %in% c("spring", "summer"))) |>
  mutate(season = factor(season_lab[season], levels = season_lab), against = factor(against, levels = refs),
         type = factor(type, levels = c("Both responded", "One censored at +90 (bound)")))
med <- pb_data |> group_by(season, against) |>
  summarise(md = median(tapply(d, event, median)), n = n(), .groups = "drop")
pb <- ggplot(pb_data, aes(d, fill = against, alpha = type)) +
  geom_histogram(binwidth = 5, boundary = 0, colour = NA, position = "stack") +
  geom_vline(xintercept = 0, colour = "grey30", linewidth = 0.3) +
  geom_vline(data = med, aes(xintercept = md), linetype = "22", linewidth = 0.4, colour = "grey10") +
  geom_text(data = med, aes(x = -118, y = Inf, label = sprintf("%d pairs\nmedian d = %+.0f", n, md)),
            inherit.aes = FALSE, hjust = 0, vjust = 1.2, size = (BASE_PT - 1) / .pt, family = FONT,
            lineheight = 0.9, colour = "grey25") +
  facet_grid(against ~ season, scales = "free_y") +
  scale_fill_manual(values = VAR_COL, guide = "none") +
  scale_alpha_manual(values = c(`Both responded` = 0.9, `One censored at +90 (bound)` = 0.4), name = NULL) +
  scale_x_continuous(limits = c(-120, 120), breaks = seq(-100, 100, 50)) +
  labs(x = "d = response day of SIF/APAR − reference (days; < 0: SIF/APAR first)", y = "Cell-episodes") +
  theme_ms() + theme(legend.position = "bottom", legend.margin = margin(0, 0, 0, 0),
                     panel.spacing.x = unit(3, "mm"))

# --- (a) sign scores -------------------------------------------------------------------------------------------------
tests <- c(H3b = "all", H3b_season_spring_descriptive = "spring", H3b_season_summer_descriptive = "summer")
pa_data <- hq |> filter(test %in% names(tests)) |>
  mutate(season = factor(season_lab[tests[test]], levels = rev(season_lab)),
         against = factor(toupper(against), levels = refs))
pd <- position_dodge(width = 0.55)
pa <- ggplot(pa_data, aes(mean_score, season, colour = against)) +
  geom_vline(xintercept = 0, colour = "grey30", linewidth = 0.3) +
  geom_errorbar(aes(xmin = ci_lo, xmax = ci_hi), width = 0.25, orientation = "y", position = pd, linewidth = 0.4) +
  geom_point(size = 1.4, position = pd) +
  geom_text(aes(x = ci_hi, label = sprintf("  %d ev.", n_events)), position = pd, hjust = 0,
            size = (BASE_PT - 1.5) / .pt, family = FONT, show.legend = FALSE) +
  scale_colour_manual(values = VAR_COL, name = "SIF/APAR vs") +
  scale_x_continuous(limits = c(-0.6, 0.95), breaks = seq(-0.5, 0.75, 0.25)) +
  labs(x = "Mean sign score (< 0: SIF/APAR first)", y = NULL) + theme_ms() +
  theme(legend.position = "bottom", legend.margin = margin(0, 0, 0, 0))

p <- (pa | pb) + plot_layout(widths = c(1, 2.3)) + tags_abc()
save_fig(p, "fig5_onset_timing", WIDTH_DOUBLE, 100)
