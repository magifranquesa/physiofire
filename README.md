# PHYSIOFIRE – proof of concept

Does the satellite SIF/APAR anomaly depart from normal before wildfires, earlier than NDVI/EVI, and carry information not already in the FWI? Iberian Peninsula, 2018 onwards. See `CLAUDE.md` for scope, methods and decisions.

## Languages

- **Python** (`src/physiofire/`): data download, gridding, QC, indices and anomalies (gridded data).
- **R** (`R/`): fire table, superposed epoch analysis, statistics and publication figures.
- Exchange formats: NetCDF (CF) for grids, CSV for tables.

## Setup (Windows)

```powershell
C:\ProgramData\miniconda3\Scripts\conda.exe env create -f environment.yml
C:\ProgramData\miniconda3\Scripts\conda.exe run -n physiofire pip install -e . --no-deps
C:\ProgramData\miniconda3\Scripts\conda.exe run -n physiofire pytest
```

Exact Python package versions: `environment.lock.yml`.

R is not managed by conda (r-terra is unmaintained on conda-forge for Windows). Use a current CRAN R install; package versions are pinned with renv:

```r
install.packages("renv")
renv::restore()
```

## Layout

- `config/config.yaml`: region, period, grids, method parameters, fire selection criteria (read by both Python and R).
- `data/`: not versioned (except `data/fires/selected_fires.csv`).
- `docs/`: project documents, data source notes, selection criteria.
- `notebooks/`, `figures/`, `tests/`.

## Pre-registration tags

Annotated git tags on the commits that fixed each analysis before any vegetation series was extracted (`git show <tag>`):

| Tag | Commit (date) | Content |
| --- | --- | --- |
| `prereg-fire2025` | `a7f894f` (2026-11-08) | 2025 fire case: controls, thresholds, anomalies, masking and decision criterion. Fire sample fixed by rule earlier in `47e6488` (2026-11-07; `data/fires/selected_fires.csv`) |
| `prereg-timescale` | `76ae9af` (2026-11-08) | Question 1 (drought time scale): plan and criterion in `c84924c` (`docs/plan_q1_drought.md`, config `drought_q1`); final configuration (SPEI clipping, implementation details) in `76ae9af` |
| `prereg-onset` | `d093008` (2026-11-08) | Q1b (drought onset, post hoc follow-up of question 1): plan `docs/plan_q1b.md` and config `drought_q1b` |

## Reproducing the analyses

All commands run from the repository root, with the `physiofire` conda environment (Python) and the renv library (R). Parameters are read from `config/config.yaml`; every module documents its command line in its docstring or header (`python -m <module> --help`). The exact command sequences used for each result are in `docs/results_case2025.md`, `docs/results_q1_drought.md` and `docs/results_q1b.md`.

1. **Downloads** (accounts: see "Credentials"): `python -m physiofire.download.troposif --start 2018-05-01 --end 2025-12-31` (TROPOSIF L2B, regional subset, resumable); `python -m physiofire.download.gee <product> --start ... --end ...` for `fpar`, `shortwave`, `mod09ga`, `myd09ga`, `nbar`, `mask`, `burn_history` (full list in the module docstring); `python -m physiofire.download.era5land_fwi`, `era5land_aed`, `era5land_precip`; `python -m physiofire.download.cems_fwi --year 2025 --months 8` (reference FWI). EFFIS perimeters, FIRMS archives, ESFire30, FirEUrisk and Global-AI are manual downloads (`docs/data_sources.md`, `docs/supplementary_table_S3.md`).
2. **Gridded inputs**: `python -m physiofire.preprocess.troposif_grid`, `preprocess.fwi`, `preprocess.aed`, `preprocess.water_balance --years 1991 2025`, `preprocess.fuel`, `preprocess.aridity`; `python -m physiofire.indices` (SIF/APAR, NDVI and EVI grids of summer 2025).
3. **Fire sample**: `Rscript R/effis_perimeters.R`, `R/firms_clean.R`, `R/fire_candidates.R`, `R/fire_shortlist.R`, `R/select_fires.R` (writes `data/fires/selected_fires.csv`), then `Rscript R/epoch_cells.R` (burned and control cells).
4. **SIF/APAR validity thresholds**: `python -m physiofire.screening_thresholds --classes shrubland wet_heath --tag shrubland --noise-factor 2` (`data/processed/screening/README.md`).
5. **2025 fire analysis**: `python -m physiofire.epoch --grid fine`, `Rscript R/epoch_analysis.R <epoch series CSV>`, `Rscript R/epoch_report_2025.R`.
6. **Time-scale analysis (question 1)**: `Rscript R/q1_cells.R`, `Rscript R/q1_spei.R`, `python -m physiofire.drought_q1 series`, `python -m physiofire.drought_q1 analysis`, `python -m physiofire.drought_q1_report`, `Rscript R/q1_figures.R`.
7. **Onset analysis (Q1b)**: `python -m physiofire.drought_q1b count|par|analysis1|analysis2|noise|decide`, `python -m physiofire.drought_q1b_report`, `python -m physiofire.drought_q1b_posthoc_both`, `Rscript R/q1b_figures.R`.
8. **Exploratory series (Fig. 3, S1-S6)**: `python -m physiofire.explore_timeseries cells`, `Rscript R/explore_spei.R`, `python -m physiofire.explore_timeseries series`.
9. **Figures**: `Rscript R/manuscript_figures/all_figures.R` (Figs. 1-5 and S1-S7, `figures/manuscript/`), `Rscript R/manuscript_figures/export_supplement.R` (300-ppi PNG, `figures/supplement/`).
10. **Checks**: `Rscript R/check_fwi_cffdrs.R`, `python -m physiofire.preprocess.fwi_cems_compare`, `python -m physiofire.report_valid_days`, `Rscript R/fires_spei3_spring.R`; results in `docs/closeout_checks.md` and `docs/supplementary_qc.md`.

Steps 1-2 take days of downloads. The Zenodo data record (`docs/zenodo/README_data.md`) contains the outputs of steps 2 and 5-8 (about 2 GB), so steps 4-10 can be re-run without the raw data.

## Data availability, licence and citation

- Code, configuration and the small result tables: this repository (MIT licence, `LICENSE`); archived on Zenodo at each release.
- Derived datasets (daily series, SPEI inputs, gridded SIF/APAR; about 2 GB): Zenodo data record, CC BY 4.0, described in `docs/zenodo/README_data.md`.
- Original datasets: from their providers, listed with versions and access links in `docs/supplementary_table_S3.md`.
- Citation: `CITATION.cff` (GitHub "Cite this repository"); the journal article will be added there when published.

## Credentials

Not stored in the repository: NASA Earthdata (`~/_netrc` on Windows or `earthaccess.login()`), Copernicus CDS (`~/.cdsapirc`).

Google Earth Engine (project in `config.yaml`): the default `earthengine authenticate` client is blocked by Google, so use gcloud application-default credentials with your own OAuth desktop client (Google Cloud console > Google Auth Platform > Clients; add yourself as test user):

```
gcloud.cmd auth application-default login --client-id-file=<client_secret.json> --scopes=https://www.googleapis.com/auth/earthengine,https://www.googleapis.com/auth/cloud-platform
```

`physiofire.download.gee.initialize()` passes these credentials to `ee.Initialize` explicitly.
