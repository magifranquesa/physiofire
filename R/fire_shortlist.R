# Short list of large fires of one year for manual selection (docs/fire_shortlist_{year}.md).
#
# From the candidate table (R/fire_candidates.R): perimeters above shortlist.min_area_ha, with the date of each
# source, the final ignition date and its source, the coherence and review flags, the vegetation (FirEUrisk fuel
# classes, main, and CORINE 2018 groups, support; fractions on the 0.05 deg grid, area-weighted over the cells
# overlapping the perimeter) and, if
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

# Vegetation fractions on the 0.05 deg grid, area-weighted over the cells overlapping the perimeter:
# FirEUrisk fuel classes (main: dominant class, stratum, control matching) and CORINE 2018 groups (support)
ec <- cfg$epoch
pv <- vect(st_transform(per, 4326))
perim_mean <- function(fr) {
  x <- terra::extract(fr, pv, exact = TRUE)
  x |> group_by(ID) |>
    summarise(across(all_of(names(fr)), ~ 100 * sum(.x * fraction, na.rm = TRUE) / sum(fraction)), .groups = "drop")
}
fuel_cls <- names(ec$fuel$classes)
fv <- perim_mean(vegetation_fractions(cfg, root, "fine", "fuel"))
fv$dominant <- fuel_cls[apply(as.matrix(fv[, fuel_cls]), 1, which.max)]
groups <- names(ec$corine$groups)
cv <- perim_mean(vegetation_fractions(cfg, root, "fine", "corine"))
names(cv)[-1] <- paste0("clc_", groups)
cv$clc_dominant <- groups[apply(as.matrix(cv[, paste0("clc_", groups)]), 1, which.max)]
veg <- fv |> left_join(cv, by = "ID")

# Burned cells and valid controls per fire (R/epoch_cells.R run on all short-listed perimeters; static data only)
cs_file <- file.path(out_dir, sprintf("shortlist_cells_%d", year), "epoch_cells_status.csv")
cs <- if (file.exists(cs_file)) read_csv(cs_file, show_col_types = FALSE, col_types = cols(fire_id = col_character()))
if (is.null(cs)) message("no ", cs_file, ": burned-cell and control columns left empty")

tab <- cand |> bind_cols(veg[match(seq_len(nrow(cand)), veg$ID), -1]) |>
  mutate(name = ifelse(is.na(commune), province, paste0(commune, " (", province, ")")),
         dominant_perimeter = dominant)
if (!is.null(cs)) {
  tab <- tab |> left_join(cs |> transmute(effis_id = fire_id, n_burned_cells = n_burned,
                                          n_controls = suppressWarnings(ifelse(grepl("^insufficient", status),
                                                              as.integer(sub(".*\\(([0-9]+)\\).*", "\\1", status)),
                                                              n_control)),
                                          cells_status = status, fire_veg), by = "effis_id")
  # the class used for matching and strata is the dominant class of the burned cells (R/epoch_cells.R);
  # the perimeter-weighted dominant is used only when the fire has no burned cells
  tab$dominant <- ifelse(is.na(tab$fire_veg), tab$dominant_perimeter, tab$fire_veg)
} else {
  tab$n_burned_cells <- NA_integer_; tab$n_controls <- NA_integer_; tab$cells_status <- NA_character_
  tab$fire_veg <- NA_character_
}
tab$stratum <- group_stratum(tab$dominant, ec$strata$fuel)
write_csv(tab, file.path(out_dir, sprintf("fire_shortlist_%d.csv", year)))

fuel_es <- c(closed_forest = "bosque cerrado", open_forest = "bosque abierto", shrubland = "matorral",
             wet_heath = "brezal y zonas húmedas", grassland = "pastizal", cropland = "cultivos",
             nonfuel = "sin combustible")
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
rows <- sprintf("| %d | %s | %s | %s | %s | %s | %s | %s | %s | **%s** (%s) | %s | %s | %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s |",
                seq_len(nrow(tab)), tab$effis_id, tab$name, tab$country,
                formatC(round(tab$burned_ha), format = "d", big.mark = ".", decimal.mark = ","),
                fmt_d(tab$effis_first), fmt_d(tab$viirs_first), fmt_d(tab$mcd64a1_first), fmt_d(tab$vnp64a1_first),
                fmt_d(tab$ignition_date), gsub("\\+", ", ", tab$ignition_source),
                fmt_p(tab$closed_forest), fmt_p(tab$open_forest), fmt_p(tab$shrubland), fmt_p(tab$wet_heath),
                fmt_p(tab$grassland), fmt_p(tab$cropland), fmt_p(tab$nonfuel),
                paste0(fuel_es[tab$dominant], ifelse(tab$dominant != tab$dominant_perimeter, "†", "")),
                str_es[tab$stratum], veg_es[tab$clc_dominant],
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
  "- **Vegetación (mapa de combustibles de FirEUrisk, 1 km, hacia 2019; agregado a 0,05°)**: porcentaje de cada clase, medio ponderado por la superficie del perímetro en cada celda de 0,05°. B. cerr. = bosque cerrado (cubierta de copas ≥ 70 %; tipos 1122, 1212, 1302), B. ab. = bosque abierto (15–70 %; 1121, 1211, 1301), Mator. = matorral (21–23), Brezal = brezal y zonas húmedas (51–53), Pastiz. = pastizal (31–33), Cult. = cultivos herbáceos y leñosos (41, 42), Sin comb. = urbano, agua, suelo desnudo y vegetación escasa (61, 62, 7). \"Dominante\" es la clase con más superficie en las celdas quemadas (≥ 25 % dentro del perímetro, ponderadas por su fracción quemada), la que se usa para emparejar los controles y estratificar; † = distinta de la dominante en todo el perímetro (la de los porcentajes). Estrato: arbolado = bosque cerrado o abierto, matorral = matorral o brezal, pasto = pastizal. **CORINE**: grupo dominante de CORINE 2018 (apoyo; porcentajes de todos los grupos en el CSV).",
  "- **Celdas / Controles**: celdas de 0,05° con al menos un 25 % dentro del perímetro, y celdas de control válidas (se usan como máximo 5; hacen falta 3) con los criterios de `config.yaml` (`epoch.controls`): sin quemar desde 2017 (EFFIS, MCD64A1, VNP64A1 y ESFire30), misma clase dominante de FirEUrisk que las celdas quemadas, aridez ±15 % (relativa), altitud ±200 m y a 10–50 km del perímetro. Solo información estática.",
  "- **Coherencia**: actividad VIIRS o MCD64A1/VNP64A1 dentro del perímetro entre 90 y 30 días antes de FIREDATE; entre paréntesis, detecciones previas y su fracción del total.",
  "- **Revisar**: ignición más de 3 días antes de FIREDATE sin marca de coherencia (posible fusión de perímetros).",
  "",
  "| # | ID EFFIS | Municipio (provincia) | País | ha | EFFIS | VIIRS | MCD64A1 | VNP64A1 | Ignición (fuente) | B. cerr. % | B. ab. % | Mator. % | Brezal % | Pastiz. % | Cult. % | Sin comb. % | Dominante (estrato) | CORINE | Celdas | Controles | Coherencia | Revisar |",
  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
  rows,
  "",
  "## Selección",
  "",
  "Marcar aquí los 10–15 incendios elegidos (ID EFFIS), con la fecha de ignición contrastada y la fecha de la selección, antes de analizar nada.",
  ""
)
writeLines(md, file.path(root, "docs", sprintf("fire_shortlist_%d.md", year)), useBytes = TRUE)
message(sprintf("%d perimeters > %s ha -> docs/fire_shortlist_%d.md", nrow(tab), sc$min_area_ha, year))
