# physiofire: derived datasets

Derived datasets supporting the study *Drought sensitivity versus anticipation: satellite chlorophyll fluorescence and fire-prone conditions in the Iberian Peninsula* (Franquesa et al., in preparation). The analysis code, configuration and the small result tables are in the companion code record (GitHub `magifranquesa/physiofire`, archived on Zenodo); this record holds the larger intermediate products that the code reads, so that the analyses can be re-run without downloading the original satellite and reanalysis data.

Version 1.0.0, 12 November 2026. This record: https://doi.org/10.5281/zenodo.24179626 (concept DOI; v1.0.0 is https://doi.org/10.5281/zenodo.24179627). Code record: https://doi.org/10.5281/zenodo.24179252 (concept DOI; v1.0.0 is https://doi.org/10.5281/zenodo.24179253).

## How to use

Unpack the archive in the root of the code repository, keeping the paths below (`data/processed/...`, `data/interim/...`). The pipeline steps that read them are listed in the repository `README.md` ("Reproducing the analyses"). All files are plain CSV (UTF-8, comma-separated, header row) or NetCDF-4 (CF conventions), readable with any standard tool (pandas, xarray, R `readr`, `ncdf4`, `terra`).

## Study region and grids

- Region: mainland Spain and Portugal, bounding box 10.0° W–4.5° E, 35.5–44.5° N (EPSG:4326). Balearic and Canary Islands excluded.
- `fine` grid: 0.05° (180 rows × 290 columns), the main analysis grid. `base` grid: 0.25° (36 × 58), sensitivity only. Both grids are aligned with the region bounds (cell edges at multiples of the resolution). Cell indices `iy`, `ix` are zero-based row and column; `lon`, `lat` are cell centres.
- ERA5-Land variables (FWI, ET₀, SPEI) are on the native 0.1° grid; `lon01`, `lat01` give the centre of the 0.1° cell containing a 0.05° cell.
- Daily series run from 1 May 2018 (start of the TROPOSIF record) to 31 December 2025 (2,802 days) unless stated otherwise; dates are UTC days.

## Contents

Sizes are approximate. Columns and variables follow the names used in the code and the article.

### `data/processed/epoch/` — 2025 fire analysis (Section 2.6 of the article)

| File | Size | Content |
| --- | --- | --- |
| `epoch_series_fine.csv` | 30 MB | Standardised anomalies (`z`) of SIF/APAR, NDVI, EVI, FWI and AED for every burned and control cell of the 22 fires, days −60 to −1 relative to ignition (`day_rel`), 15-day backward means (`series = median_doy_trail15`); `group` = burned/control, `weight` = burned fraction |
| `epoch_fire_days.csv` | 3.5 MB | Fire-level means of burned cells and controls and their difference (`diff`) per variable and day |
| `spei3_fires_2025_daily.csv` | 2 MB | Daily SPEI-3 (90-day scale) of 2025 for the 140 ERA5-Land cells containing the burned and control cells (post hoc, descriptive) |
| `spei3_fires_2025_spring.csv` | < 1 MB | Per fire: April–May 2025 summary of SPEI-3 for burned cells (`B`) and controls (`C`) and the value on the ignition date |

The small tables of this analysis (`epoch_cells.csv`, `epoch_effects_*.csv`, `epoch_lead_times.csv`, `report2025_*.csv`) and the fire table `data/fires/selected_fires.csv` are in the code record.

### `data/processed/drought_q1/` — time-scale analysis (Section 2.7)

| File | Size | Content |
| --- | --- | --- |
| `drought_q1_series.nc` | 607 MB | Daily series of the 6,771 selected cells (`time` × `cell`): `sif_apar`, `sif`, `sif_par`, `fpar`, `ndvi`, `evi`, `aed` (ET₀, mm day⁻¹) and the daily SPEI at 15, 30, 60, 90, 180 and 365 days (`spei_015` … `spei_365`). Screened and spike-filtered as described in the article; raw values, not anomalies |
| `drought_q1_cells.csv` | 0.6 MB | The 6,771 cells: grid indices, coordinates, FirEUrisk fuel class, stratum, aridity index and class, containing ERA5-Land cell, land fraction |
| `analysis1_cells.csv` | 10 MB | Per cell and variable: maximum signed correlation with the SPEI (`r`), permutation p-value (`p`), optimal accumulation scale (`scale_days`) and lag (`lag_days`); the same at the fixed 90-day scale (`r_h2`, `p_h2`, `lag_h2`) |
| `posthoc_par_cells.csv` | 2 MB | Per cell: correlations of SIF/APAR, NDVI and PAR with AED and SPEI-30, and partial correlations controlling for PAR (PAR diagnostic) |

Summary tables (`hypotheses.csv`, `summary_*.csv`, `posthoc_par_diagnostic.csv`, `analysis2_episodes.csv`, `decision.json`) are in the code record.

### `data/processed/drought_q1b/` — onset analysis (Section 2.8)

| File | Size | Content |
| --- | --- | --- |
| `episodes_A.csv`, `episodes_B.csv`, `episodes_C.csv` | 1.8, 1.6, 0.2 MB | Drought onsets per cell under the three candidate definitions (B is the one used), with the event grouping (`event`) |
| `analysis2b_episodes.csv` | 2.7 MB | Per cell and onset (definition B): response day of SIF/APAR, NDVI and EVI (`resp_*`, right-censored at +90), observability flags (`obs_*`) and the backward-mean / PAR-corrected sensitivity (`bw*` columns) |
| `analysis1b_cells_backward.csv`, `analysis1b_cells_centred.csv` | 5.8, 2.8 MB | Scale and lag analysis repeated with backward means and with PAR-corrected SIF/APAR (sensitivity H1/H2b) |
| `noise_cells.csv`, `noise_fraction.csv` | 5.8, 1.5 MB | Noise-matching sensitivity: per-cell results for the five replicate seeds and the noise fraction added to NDVI and EVI |
| `par_fit.csv`, `par_series.nc` | 0.6, 50 MB | PAR correction of SIF/APAR: fitted slope per cell (`b_par`, `n_fit_days`) and the daily PAR series of the 6,771 cells |

Summary tables (`hypotheses_q1b.csv`, `summary_*.csv`, `decision_q1b.*`, `definition.json`, `event_count.csv`, `noise_h1_replicates.csv`) are in the code record.

### `data/processed/` — gridded SIF/APAR of summer 2025

| File | Size | Content |
| --- | --- | --- |
| `sif_apar_fine_20250601_20250907.nc` | 169 MB | Daily 0.05° grids, 1 June–7 September 2025: `sif` (TROPOSIF daily mean, footprint-weighted), `sif_sem`, `sif_weight` (equivalent full soundings), `par`, `fpar`, `apar`, `sif_apar`, `sif_par`, `ndvi`, `evi` and NIRv-based variants. Produced to test the processing chain before the analyses; not used to select fires or cells |
| `sif_apar_base_20250601_20250907.nc` | 8 MB | The same on the 0.25° grid |

### `data/interim/spei/` — climatic water balance and SPEI (Section 2.3)

| File | Size | Content |
| --- | --- | --- |
| `water_balance_1991.nc` … `water_balance_2025.nc` | 35 files, 25 MB each (≈ 890 MB) | Daily precipitation (`pr`), FAO-56 reference evapotranspiration (`et0`) and their difference (`d`), mm day⁻¹, on the 0.1° ERA5-Land grid of the region, one file per year. Inputs of the daily SPEI |
| `spei_q1.nc` | 201 MB | Daily SPEI at 15–365 days (`spei_015` … `spei_365`) for the 3,137 ERA5-Land cells containing the time-scale analysis cells, 2018–2025; `lon01`, `lat01` |
| `spei_q1_clamped.csv` | 0.7 MB | Count of values clipped to ±3.09 per cell and scale |

### `data/interim/explore/` — exploratory series (Fig. 3, Figs. S1–S6)

| File | Size | Content |
| --- | --- | --- |
| `explore_cells.csv` | < 1 MB | The 21 cells shown (one burned cell and two controls of six fires; four drought-event cells of 2022) |
| `explore_series.csv` | 1.4 MB | Daily (`daily_z`) and 15-day backward-mean (`smooth_z`) standardised anomalies of SIF/APAR, NDVI and EVI, and daily SPEI-3, April–October of the case year |
| `spei_q1.nc` | 0.3 MB | Daily SPEI-3 of the 21 ERA5-Land cells of those cells |

### `data/interim/static/` — static layers on both grids

| File | Size | Content |
| --- | --- | --- |
| `fuel_fireurisk_fine.nc`, `fuel_fireurisk_base.nc` | 4.4, 0.2 MB | Area fraction of each of the 20 FirEUrisk first-level fuel types per cell (`type_fraction`) and pixel count |
| `aridity_gai_fine.nc`, `aridity_gai_base.nc` | 0.3, < 0.1 MB | Mean Global Aridity Index v3.1 per cell and number of 30″ pixels |

Total: about 2.0 GB.

Not included (regenerable from the files above or from the original providers): the regional TROPOSIF L2B subsets (≈ 3,100 daily files), the Google Earth Engine extractions (MODIS fPAR and reflectance, ERA5-Land, burned area), the ERA5-Land FWI and ET₀ hourly inputs, `spei_q1_params.rds` (fitted log-logistic parameters, R-specific) and the sensitivity run with 5-day fPAR persistence.

## Provenance and attribution

All variables derive from the public datasets listed in Supplementary Table S3 of the article: TROPOSIF L2B (S5P-PAL, processor 01.00.01, collection 03; contains modified Copernicus Sentinel data 2018–2025), MODIS MCD15A3H, MOD09GA, MYD09GA, MCD43A4 and MCD64A1 v061 and VIIRS VNP64A1 v002 (NASA LP DAAC, via Google Earth Engine), ERA5-Land (Copernicus Climate Change Service; generated using Copernicus Climate Change Service information 2026), EFFIS burnt area perimeters (Copernicus Emergency Management Service), NASA FIRMS VIIRS active fires, ESFire30 (Ochoa et al., 2026, CC BY 4.0), the FirEUrisk European fuel map v2.0 (Aragoneses et al., 2023), CORINE Land Cover 2018, the Global Aridity Index v3.1 (Zomer et al., 2022, CC BY 4.0), CGIAR-CSI SRTM v4.1 and USDOS LSIB 2017. Neither the European Commission, ECMWF nor the other providers are responsible for any use of this derived data.

## Licence

These derived datasets are released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0). Please cite the article and this record, and acknowledge the original data providers listed above.

## File list (for upload)

```
data/processed/epoch/epoch_series_fine.csv
data/processed/epoch/epoch_fire_days.csv
data/processed/epoch/spei3_fires_2025_daily.csv
data/processed/epoch/spei3_fires_2025_spring.csv
data/processed/drought_q1/drought_q1_series.nc
data/processed/drought_q1/drought_q1_cells.csv
data/processed/drought_q1/analysis1_cells.csv
data/processed/drought_q1/posthoc_par_cells.csv
data/processed/drought_q1b/episodes_A.csv
data/processed/drought_q1b/episodes_B.csv
data/processed/drought_q1b/episodes_C.csv
data/processed/drought_q1b/analysis2b_episodes.csv
data/processed/drought_q1b/analysis1b_cells_backward.csv
data/processed/drought_q1b/analysis1b_cells_centred.csv
data/processed/drought_q1b/noise_cells.csv
data/processed/drought_q1b/noise_fraction.csv
data/processed/drought_q1b/par_fit.csv
data/processed/drought_q1b/par_series.nc
data/processed/sif_apar_fine_20250601_20250907.nc
data/processed/sif_apar_base_20250601_20250907.nc
data/interim/spei/water_balance_1991.nc ... data/interim/spei/water_balance_2025.nc
data/interim/spei/spei_q1.nc
data/interim/spei/spei_q1_clamped.csv
data/interim/explore/explore_cells.csv
data/interim/explore/explore_series.csv
data/interim/explore/spei_q1.nc
data/interim/static/fuel_fireurisk_fine.nc
data/interim/static/fuel_fireurisk_base.nc
data/interim/static/aridity_gai_fine.nc
data/interim/static/aridity_gai_base.nc
```

Zenodo accepts up to 50 GB per record; a single `.zip` (or one per top-level folder) keeping these relative paths is the simplest upload.
