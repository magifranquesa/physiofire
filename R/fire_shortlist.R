# Short list of large fires of one year for manual selection (docs/fire_shortlist_{year}.md).
#
# From the candidate table (R/fire_candidates.R): perimeters above shortlist.min_area_ha, with the date of each
# source, the final ignition date and its source, the coherence and review flags, the dominant vegetation (CORINE
# 2018 group fractions on the 0.05 deg grid, area-weighted over the cells overlapping the perimeter) and, if
# R/epoch_cells.R has been run on the short list, the number of burned cells and of valid control cells.
# Static data only: no vegetation or meteorological time series are extracted.
#
# Usage (from the repository root): Rscript R/fire_shortlist.R [year]   (default: fires$first_case_year)

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(sf)
  library(terra)
})
source("R/config.R")
source("R/epoch_lib.R")
cfg <- load_config()
root <- find_repo_root()
sc <- cfg$shortlist
args <- commandArgs(trailingOnly = TRUE)
year <- if (length(args)) as.integer(args[1]) else as.integer(cfg$fires$first_case_year)
out_dir <- file.path(root, cfg$effis$out_dir)

cand <- read_csv(file.path(out_dir, sprintf("fire_candidates_%d.csv", year)), show_col_types = FALSE,
                 col_types = cols(effis_id = col_character())) |>
  filter(burned_ha >= as.numeric(sc$min_area_ha))
gpkg <- list.files(out_dir, pattern = "^effis_iberia_[0-9]+_[0-9]+\\.gpkg$", full.names = TRUE)
per <- st_read(gpkg, quiet = TRUE) |> mutate(id = as.character(id)) |> filter(id %in% cand$effis_id)
per <- per[match(cand$effis_id, per$id), ]

# CORINE 2018 group fractions on the 0.05 deg grid, area-weighted over the cells overlapping the perimeter
ec <- cfg$epoch
groups <- names(ec$corine$groups)
clc <- rast(file.path(root, cfg$gee$out_dir, sprintf("corine_%d_fine.nc", as.integer(ec$corine$year))),
            subds = "fraction")
names(clc) <- groups
x <- terra::extract(clc, vect(st_transform(per, 4326)), exact = TRUE)
veg <- x |> group_by(ID) |>
  summarise(across(all_of(groups), ~ 100 * sum(.x * fraction, na.rm = TRUE) / sum(fraction)), .groups = "drop")
veg$dominant <- groups[apply(as.matrix(veg[, groups]), 1, which.max)]
nat <- c("broadleaved", "coniferous", "mixed_forest", "natural_grassland", "heathland", "sclerophyllous",
         "transitional", "agricultural", "agri_natural_mosaic", "agroforestry")
veg$other <- 100 - rowSums(veg[, nat])

# Burned cells and valid controls per fire (R/epoch_cells.R run on all short-listed perimeters; static data only)
cs_file <- file.path(out_dir, sprintf("shortlist_cells_%d", year), "epoch_cells_status.csv")
cs <- if (file.exists(cs_file)) read_csv(cs_file, show_col_types = FALSE, col_types = cols(fire_id = col_character()))
if (is.null(cs)) message("no ", cs_file, ": burned-cell and control columns left empty")

tab <- cand |> bind_cols(veg[match(seq_len(nrow(cand)), veg$ID), -1]) |>
  mutate(name = ifelse(is.na(commune), province, paste0(commune, " (", province, ")")),
         stratum = group_stratum(dominant, ec$strata))
if (!is.null(cs)) {
  tab <- tab |> left_join(cs |> transmute(effis_id = fire_id, n_burned_cells = n_burned,
                                          n_controls = suppressWarnings(ifelse(grepl("^insufficient", status),
                                                              as.integer(sub(".*\\(([0-9]+)\\).*", "\\1", status)),
                                                              n_control)),
                                          cells_status = status), by = "effis_id")
} else {
  tab$n_burned_cells <- NA_integer_; tab$n_controls <- NA_integer_; tab$cells_status <- NA_character_
}
write_csv(tab, file.path(out_dir, sprintf("fire_shortlist_%d.csv", year)))

veg_es <- c(broadleaved = "frondosas", coniferous = "coníferas", mixed_forest = "bosque mixto",
            natural_grassland = "pastizal natural", heathland = "landas y brezales",
            sclerophyllous = "matorral esclerófilo", transitional = "transición bosque-matorral",
            sparse_vegetation = "vegetación escasa", burnt_areas = "zonas quemadas", agricultural = "agrícola",
            agri_natural_mosaic = "mosaico agrícola-natural", agroforestry = "agroforestal",
            artificial = "artificial", water_wetland = "agua y humedales")
str_es <- c(woodland = "arbolado", shrubland = "matorral", grassland = "pasto", other = "otro")

# --- Markdown -----------------------------------------------------------------------------------------------------
fmt_d <- function(d) ifelse(is.na(d), "—", format(as.Date(d), "%d/%m"))
fmt_p <- function(p) ifelse(is.na(p), "—", sprintf("%.0f", p))
flag <- function(f) ifelse(f, "**sí**", "no")
fmt_n <- function(n) ifelse(is.na(n), "—", as.character(n))
rows <- sprintf("| %d | %s | %s | %s | %s | %s | %s | %s | %s | **%s** (%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s |",
                seq_len(nrow(tab)), tab$effis_id, tab$name, tab$country,
                formatC(round(tab$burned_ha), format = "d", big.mark = ".", decimal.mark = ","),
                fmt_d(tab$effis_first), fmt_d(tab$viirs_first), fmt_d(tab$mcd64a1_first), fmt_d(tab$vnp64a1_first),
                fmt_d(tab$ignition_date), gsub("\\+", ", ", tab$ignition_source),
                fmt_p(tab$broadleaved), fmt_p(tab$coniferous), fmt_p(tab$mixed_forest), fmt_p(tab$natural_grassland),
                fmt_p(tab$heathland), fmt_p(tab$sclerophyllous), fmt_p(tab$transitional), fmt_p(tab$agricultural),
                fmt_p(tab$agri_natural_mosaic), fmt_p(tab$agroforestry),
                fmt_p(tab$other), veg_es[tab$dominant], str_es[tab$stratum],
                fmt_n(tab$n_burned_cells), fmt_n(tab$n_controls),
                ifelse(tab$coherence_flag, sprintf("**sí** (%d VIIRS, %s %%)", tab$viirs_n_prior,
                                                   sub(".", ",", sprintf("%.1f", 100 * tab$viirs_prior_frac),
                                                       fixed = TRUE)), "no"),
                flag(tab$review_early))
md <- c(
  sprintf("# Lista corta de grandes incendios de %d (perímetros de EFFIS > %s ha)", year,
          formatC(as.numeric(sc$min_area_ha), format = "d", big.mark = ".", decimal.mark = ",")),
  "",
  sprintf("Generada el %s con `Rscript R/fire_shortlist.R` a partir de `data/interim/fires/fire_candidates_%d.csv`. Solo información estática: no se ha extraído ninguna serie de vegetación ni de meteorología.", format(Sys.Date(), "%d/%m/%Y"), year),
  "",
  "**Columnas**",
  "",
  "- **Fechas** (día/mes, UTC): primera fecha de cada fuente dentro del perímetro, entre FIREDATE − 30 días y FINALDATE + 1 día. VIIRS: detecciones `type = 0` sin confianza baja.",
  "- **Ignición**: la más temprana de las cuatro fuentes; entre paréntesis, la fuente o fuentes que la fijan.",
  "- **Vegetación (CORINE Land Cover 2018, 100 m, agregado a 0,05°)**: porcentaje de cada grupo, medio ponderado por la superficie del perímetro en cada celda de 0,05°. Frond. = frondosas (311), Conif. = coníferas (312), Mixto = bosque mixto (313), Pastizal = pastizal natural (321), Landas = landas y brezales (322), Escler. = matorral esclerófilo (323), Trans. = transición bosque-matorral (324), Agríc. = cultivos y prados (211–242), Mosaico = mosaico agrícola con vegetación natural (243), Agrofor. = sistemas agroforestales, dehesas y montados (244); Otro = vegetación escasa, zonas quemadas (334, sobre todo de 2017), artificial y agua. \"Dominante\" es el grupo con más superficie, el que se usa para emparejar los controles. Estrato: arbolado = 311–313, matorral = 322–324, pasto = 321.",
  "- **Celdas / Controles**: celdas de 0,05° con al menos un 25 % dentro del perímetro, y celdas de control válidas (se usan como máximo 5; hacen falta 3) con los criterios de `config.yaml` (`epoch.controls`): sin quemar desde 2017 (EFFIS, MCD64A1, VNP64A1 y ESFire30), mismo grupo dominante de CORINE, aridez ±0,1, altitud ±200 m y a 10–50 km del perímetro. Solo información estática.",
  "- **Coherencia**: actividad VIIRS o MCD64A1/VNP64A1 dentro del perímetro entre 90 y 30 días antes de FIREDATE; entre paréntesis, detecciones previas y su fracción del total.",
  "- **Revisar**: ignición más de 3 días antes de FIREDATE sin marca de coherencia (posible fusión de perímetros).",
  "",
  "| # | ID EFFIS | Municipio (provincia) | País | ha | EFFIS | VIIRS | MCD64A1 | VNP64A1 | Ignición (fuente) | Frond. % | Conif. % | Mixto % | Pastizal % | Landas % | Escler. % | Trans. % | Agríc. % | Mosaico % | Agrofor. % | Otro % | Dominante (estrato) | Celdas | Controles | Coherencia | Revisar |",
  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
  rows,
  "",
  "## Selección",
  "",
  "Marcar aquí los 10–15 incendios elegidos (ID EFFIS), con la fecha de ignición contrastada y la fecha de la selección, antes de analizar nada.",
  ""
)
writeLines(md, file.path(root, "docs", sprintf("fire_shortlist_%d.md", year)), useBytes = TRUE)
message(sprintf("%d perimeters > %s ha -> docs/fire_shortlist_%d.md", nrow(tab), sc$min_area_ha, year))
