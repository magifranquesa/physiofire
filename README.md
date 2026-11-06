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

## Credentials

Not stored in the repository: NASA Earthdata (`~/_netrc` on Windows or `earthaccess.login()`), Copernicus CDS (`~/.cdsapirc`).

Google Earth Engine (project in `config.yaml`): the default `earthengine authenticate` client is blocked by Google, so use gcloud application-default credentials with your own OAuth desktop client (Google Cloud console > Google Auth Platform > Clients; add yourself as test user):

```
gcloud.cmd auth application-default login --client-id-file=<client_secret.json> --scopes=https://www.googleapis.com/auth/earthengine,https://www.googleapis.com/auth/cloud-platform
```

`physiofire.download.gee.initialize()` passes these credentials to `ee.Initialize` explicitly.
