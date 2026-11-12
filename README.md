# physiofire

Code, configuration and derived results of the study **"Drought sensitivity versus anticipation: satellite chlorophyll fluorescence and fire-prone conditions in the Iberian Peninsula"** (Franquesa, Otón, Chuvieco, Torres-Vázquez and Vicente-Serrano; manuscript in preparation, 2026).

The study asks whether satellite solar-induced chlorophyll fluorescence normalised by absorbed PAR (SIF/APAR, from TROPOMI) detects fire-prone conditions earlier than greenness indices (MODIS NDVI and EVI) and weather-based danger ratings (Fire Weather Index) in mainland Spain and Portugal, 2018–2025, at 0.05°. Three analyses, each with its plan and decision criterion fixed before execution:

1. **2025 fire analysis**: superposed-epoch comparison of burned cells and matched unburned controls during the 60 days before 22 large shrubland and heathland fires of 2025.
2. **Time-scale analysis**: optimal SPEI accumulation scale and lag of SIF/APAR, NDVI and EVI across 6,751 cells of natural vegetation.
3. **Onset analysis**: response timing of each indicator at 228 drought onsets defined from a daily SPEI-3.

Main result: SIF/APAR tracks drought at shorter accumulation scales than greenness, but it does not respond earlier at drought onset and did not separate burned from unburned vegetation before the 2025 fires.

- Article: *in preparation* (reference and DOI will be added here).
- Code archive: Zenodo, concept DOI [10.5281/zenodo.24179252](https://doi.org/10.5281/zenodo.24179252) (always the latest version; v1.0.0 = [10.5281/zenodo.24179253](https://doi.org/10.5281/zenodo.24179253)).
- Derived datasets (~2 GB): Zenodo data record, concept DOI [10.5281/zenodo.24179626](https://doi.org/10.5281/zenodo.24179626) (v1.0.0 = [10.5281/zenodo.24179627](https://doi.org/10.5281/zenodo.24179627)), described in [`docs/zenodo/README_data.md`](docs/zenodo/README_data.md).

## Pre-registration

The plan and decision criterion of each analysis were committed before any vegetation series was extracted or any result computed. Annotated git tags mark those commits (`git show <tag>`):

| Tag | Commit (date) | Content |
| --- | --- | --- |
| `prereg-fire2025` | `a7f894f` (2026-11-08) | 2025 fire analysis: controls, thresholds, anomalies, masking and decision criterion. Fire sample fixed by rule earlier in `47e6488` (2026-11-07; `data/fires/selected_fires.csv`) |
| `prereg-timescale` | `76ae9af` (2026-11-08) | Time-scale analysis: plan and criterion in `c84924c` (`docs/plan_q1_drought.md`, config `drought_q1`); final configuration (SPEI clipping, implementation details) in `76ae9af` |
| `prereg-onset` | `d093008` (2026-11-08) | Onset analysis (post hoc follow-up of the time-scale analysis): plan `docs/plan_q1b.md` and config `drought_q1b` |

Later corrections to the code are documented in `docs/closeout_checks.md`; additional analyses are labelled exploratory or post hoc there and in the article.

## Repository layout

| Path | Content |
| --- | --- |
| `config/config.yaml` | Every parameter: region, grids, periods, product versions, screening thresholds, anomaly method, fire selection and control matching rules, analysis plans. Read by both Python and R |
| `src/physiofire/` | Python package: downloads (`download/`), gridding and preprocessing (`preprocess/`), SIF/APAR and vegetation indices (`indices.py`), anomalies and spike filter (`anomalies.py`), 2025 fire analysis (`epoch.py`), time-scale analysis (`drought_q1*.py`), onset analysis (`drought_q1b*.py`), exploratory series, reports |
| `R/` | Fire sample (EFFIS perimeters, FIRMS, ignition dates, selection, control cells), epoch statistics and lead times, daily SPEI (`spei_lib.R`, `q1_spei.R`), FWI check against cffdrs, figures (`R/manuscript_figures/`) |
| `tests/` | pytest unit tests of the Python modules |
| `notebooks/` | Quality-control scripts of the SIF/APAR chain (plain Python, numbered) |
| `data/` | Not versioned except the fire table (`data/fires/selected_fires.csv`) and the small result tables of each analysis (`data/processed/epoch/`, `drought_q1/`, `drought_q1b/`, `screening/`) |
| `figures/manuscript/`, `figures/supplement/` | Article and supplement figures as produced by `R/manuscript_figures/` |
| `docs/` | Project documents (see below) |

### Documents

Most project documents are the working log of the study and are written in Spanish; the ones used directly in the article are in English.

| File | Content |
| --- | --- |
| `docs/plan_q1_drought.md`, `docs/plan_q1b.md` | Pre-registered plans of the time-scale and onset analyses (Spanish) |
| `docs/results_case2025.md`, `docs/results_q1_drought.md`, `docs/results_q1b.md` | Results of the three analyses as computed, with the commands used (Spanish) |
| `docs/closeout_checks.md` | Verification notes, corrections and post hoc checks made during the write-up (Spanish) |
| `docs/methods_equations.md` | Methods as implemented, with equations and the values of every parameter (Spanish) |
| `docs/supplementary_qc.md` | Quality control of the data chain: FWI validation, MODIS screening, fPAR, screening thresholds (English) |
| `docs/data_sources.md` | Data sources: access, versions, checks and known issues (Spanish) |
| `docs/supplementary_table_S3.md` | Dataset versions and access links (Supplementary Table S3) |
| `docs/fire_shortlist_2025.md` | The 53 candidate perimeters of 2025 and the selection outcome (Spanish) |
| `docs/diagnostics/` | NBAR check of the June 2025 EVI anomaly (Supplementary Text S2) |
| `docs/zenodo/README_data.md` | Description of the derived-data record |
| `CLAUDE.md` | Project brief for the AI coding assistant used during development: objectives, rules of the epoch analysis, decisions and their dates (Spanish) |

## Setup

Windows was the development platform; the code has no Windows-specific dependencies.

**Python** (conda, conda-forge; exact versions in `environment.lock.yml`):

```
conda env create -f environment.yml
conda run -n physiofire pip install -e . --no-deps
conda run -n physiofire pytest
```

**R** (4.6, CRAN; not managed by conda because `r-terra` is unmaintained on conda-forge for Windows). Package versions are pinned with renv:

```r
install.packages("renv")
renv::restore()
```

## Reproducing the analyses

All commands run from the repository root, with the `physiofire` conda environment (Python) and the renv library (R). Parameters are read from `config/config.yaml`; every module documents its command line in its docstring or header (`python -m <module> --help`). The command sequences actually used for each result are in `docs/results_case2025.md`, `docs/results_q1_drought.md` and `docs/results_q1b.md`.

1. **Downloads** (accounts: see "Credentials"): `python -m physiofire.download.troposif --start 2018-05-01 --end 2025-12-31` (TROPOSIF L2B, regional subset, resumable); `python -m physiofire.download.gee <product> --start ... --end ...` for `fpar`, `shortwave`, `mod09ga`, `myd09ga`, `nbar`, `mask`, `burn_history` (full list in the module docstring); `python -m physiofire.download.era5land_fwi`, `era5land_aed`, `era5land_precip`; `python -m physiofire.download.cems_fwi --year 2025 --months 8` (reference FWI). EFFIS perimeters, FIRMS archives, ESFire30, FirEUrisk and Global-AI are manual downloads (`docs/data_sources.md`, `docs/supplementary_table_S3.md`).
2. **Gridded inputs**: `python -m physiofire.preprocess.troposif_grid`, `preprocess.fwi`, `preprocess.aed`, `preprocess.water_balance --years 1991 2025`, `preprocess.fuel`, `preprocess.aridity`; `python -m physiofire.indices` (SIF/APAR, NDVI and EVI grids of summer 2025).
3. **Fire sample**: `Rscript R/effis_perimeters.R`, `R/firms_clean.R`, `R/fire_candidates.R`, `R/fire_shortlist.R`, `R/select_fires.R` (writes `data/fires/selected_fires.csv`), then `Rscript R/epoch_cells.R` (burned and control cells).
4. **SIF/APAR validity thresholds**: `python -m physiofire.screening_thresholds --classes shrubland wet_heath --tag shrubland --noise-factor 2` (`data/processed/screening/README.md`).
5. **2025 fire analysis**: `python -m physiofire.epoch --grid fine`, `Rscript R/epoch_analysis.R <epoch series CSV>`, `Rscript R/epoch_report_2025.R`.
6. **Time-scale analysis**: `Rscript R/q1_cells.R`, `Rscript R/q1_spei.R`, `python -m physiofire.drought_q1 series`, `python -m physiofire.drought_q1 analysis`, `python -m physiofire.drought_q1_report`, `Rscript R/q1_figures.R`.
7. **Onset analysis**: `python -m physiofire.drought_q1b count|par|analysis1|analysis2|noise|decide`, `python -m physiofire.drought_q1b_report`, `python -m physiofire.drought_q1b_posthoc_both`, `Rscript R/q1b_figures.R`.
8. **Exploratory series (Fig. 3, S1–S6)**: `python -m physiofire.explore_timeseries cells`, `Rscript R/explore_spei.R`, `python -m physiofire.explore_timeseries series`.
9. **Figures**: `Rscript R/manuscript_figures/all_figures.R` (Figs. 1–5 and S1–S7, `figures/manuscript/`), `Rscript R/manuscript_figures/export_supplement.R` (300-ppi PNG, `figures/supplement/`).
10. **Checks**: `Rscript R/check_fwi_cffdrs.R`, `python -m physiofire.preprocess.fwi_cems_compare`, `python -m physiofire.report_valid_days`, `Rscript R/fires_spei3_spring.R`; results in `docs/closeout_checks.md` and `docs/supplementary_qc.md`.

Steps 1–2 take days of downloads. The Zenodo data record contains the outputs of steps 2 and 5–8 (about 2 GB), so steps 4–10 can be re-run without the raw data.

## Data

- **Original datasets**: obtained from their providers; versions and access links in `docs/supplementary_table_S3.md`. The repository stores none of them.
- **Derived datasets** (daily series of the analysis cells, SPEI inputs, gridded SIF/APAR of summer 2025): Zenodo data record https://doi.org/10.5281/zenodo.24179626 (CC BY 4.0), see `docs/zenodo/README_data.md`.
- **Result tables** small enough to version are in `data/processed/` (see `.gitignore` for the list).

## Credentials

Not stored in the repository: NASA Earthdata (`~/_netrc` on Windows or `earthaccess.login()`), Copernicus CDS/EWDS (`~/.cdsapirc`).

Google Earth Engine (project in `config.yaml`): the default `earthengine authenticate` client is blocked by Google, so use gcloud application-default credentials with your own OAuth desktop client (Google Cloud console > Google Auth Platform > Clients; add yourself as test user):

```
gcloud.cmd auth application-default login --client-id-file=<client_secret.json> --scopes=https://www.googleapis.com/auth/earthengine,https://www.googleapis.com/auth/cloud-platform
```

`physiofire.download.gee.initialize()` passes these credentials to `ee.Initialize` explicitly.

## Licence and citation

Code: MIT licence (`LICENSE`). Derived datasets: CC BY 4.0. Citation metadata in `CITATION.cff` (GitHub "Cite this repository"); the article reference will be added there when published.

The code was written with the help of an AI coding assistant (Claude Code); every analysis decision, parameter and result was reviewed by the authors, and the pre-registered plans, closeout checks and result documents record that process.

## Acknowledgement of data providers

TROPOSIF (ESA S5P-PAL; contains modified Copernicus Sentinel data), MODIS and VIIRS products (NASA LP DAAC, via Google Earth Engine), ERA5-Land (Copernicus Climate Change Service), EFFIS and CEMS fire danger indices (Copernicus Emergency Management Service), NASA FIRMS, ESFire30 (Ochoa et al., 2026), the FirEUrisk European fuel map (Aragoneses et al., 2023), CORINE Land Cover, the Global Aridity Index (Zomer et al., 2022), CGIAR-CSI SRTM and USDOS LSIB.
