# Supplementary Table S3: acceso a los datos

Borrador para el suplemento (12 de noviembre de 2026). Fuentes: `config/config.yaml`, `docs/data_sources.md` y los scripts de descarga (`src/physiofire/download/`).

- La tabla va en inglés, como en el artículo; las notas, en castellano.
- Los productos de Google Earth Engine (GEE) se leyeron con la API de Python (`earthengine-api`) a partir del asset ID, sin usar ninguna URL. Para ellos, el identificador exacto es el asset ID.

## Tabla

| Dataset | Version | Access | URL or GEE asset ID |
| --- | --- | --- | --- |
| TROPOSIF L2B solar-induced fluorescence (S5P-PAL) | Processor 01.00.01, Sentinel-5P Collection 03 | STAC catalogue, direct HTTPS download (no account) | STAC: https://data-portal.s5p-pal.com/api/s5p-l2, collection `L2B_SIF___`; product page: https://data-portal.s5p-pal.com/products/troposif.html |
| MODIS MCD15A3H fPAR (4-day, 500 m) | v061 | GEE | `MODIS/061/MCD15A3H` |
| MODIS MOD09GA surface reflectance (Terra, daily, 500 m) | v061 | GEE | `MODIS/061/MOD09GA` |
| MODIS MYD09GA surface reflectance (Aqua, daily, 500 m) | v061 | GEE | `MODIS/061/MYD09GA` |
| MODIS MCD43A4 NBAR (daily, 500 m) | v061 | GEE | `MODIS/061/MCD43A4` |
| MODIS MCD64A1 burned area (monthly, 500 m) | v061 | GEE | `MODIS/061/MCD64A1` |
| VIIRS VNP64A1 burned area (monthly, 500 m) | v002 | GEE | `NASA/VIIRS/002/VNP64A1` |
| ERA5-Land hourly (0.1°) | — | GEE | `ECMWF/ERA5_LAND/HOURLY` |
| ERA5-Land daily aggregates (0.1°) | — | GEE | `ECMWF/ERA5_LAND/DAILY_AGGR` |
| CEMS fire danger indices historical data (reference FWI, 0.25°) | System version 4.1, reanalysis | Copernicus EWDS API (`cdsapi`) | API: https://ewds.climate.copernicus.eu/api, dataset `cems-fire-historical-v1`; page: https://ewds.climate.copernicus.eu/datasets/cems-fire-historical-v1; DOI 10.24381/cds.0e89c522 |
| EFFIS burnt area perimeters | Database version of 7 Nov 2026, 03:46 UTC | Direct download | https://forest-fire.emergency.copernicus.eu/downloads/data.request.form/effis_layer.zip (layer `modis.ba.poly`) |
| NASA FIRMS VIIRS active fires, 375 m (S-NPP `SV-C2`, NOAA-20 `J1V-C2`, NOAA-21 `J2V-C2`) | Collection 2 | Archive download request (NASA Earthdata login) | https://firms.modaps.eosdis.nasa.gov/download/ |
| ESFire30 annual burned-area perimeters, Spain (Ochoa et al.) | Zenodo record of 26 May 2026 | Zenodo | https://zenodo.org/records/20257001 (DOI 10.5281/zenodo.20257001), file `ESFire30_1985_2025.zip` |
| FirEUrisk European fuel map (Aragoneses et al., 2023) | v2.0 | e-cienciaDatos (Dataverse API) | https://doi.org/10.21950/YABYCN; files via https://edatos.consorciomadrono.es/api/access/datafile/9603, `/9684`, `/9685` |
| CORINE Land Cover 2018 (100 m) | V20 | GEE | `COPERNICUS/CORINE/V20/100m/2018` (band `landcover`) |
| Global Aridity Index (Global-AI_ET0) | v3.1 | figshare | https://doi.org/10.6084/m9.figshare.7504448.v7, file `Global-AI_ET0__annual_v3_1.zip` (`ai_v31_yr.tif`) |
| CGIAR-CSI SRTM elevation (90 m) | v4.1 | GEE | `CGIAR/SRTM90_V4` |
| USDOS Large Scale International Boundaries, simplified | 2017 | GEE | `USDOS/LSIB_SIMPLE/2017` |
| Natural Earth Admin 0 – Countries, 1:10m (maps only) | 5.1.1 | Direct download | https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip |

## Notas

**ERA5-Land.** Todo se descargó desde GEE, no desde el CDS.
- **Horario:**
  - entradas del FWI a las 12 UTC (temperatura, punto de rocío, viento y precipitación de 24 h);
  - precipitación diaria del SPEI (`total_precipitation_hourly`, suma de las 24 horas);
  - viento medio de la ET₀.
- **Diario:**
  - radiación solar descendente (PAR = 0,48 × radiación);
  - temperaturas máxima y mínima, punto de rocío y radiación de la ET₀.

**FWI de CEMS.** El NetCDF descargado no lleva la versión en sus metadatos. La versión 4.1 es la que se pidió a la API (`system_version: 4_1`, `src/physiofire/download/cems_fwi.py`) y la que se sirvió.
- No quedó registrado si el EWDS devolvió el conjunto consolidado o el intermedio: se pide primero el consolidado.
- Solo se descargó agosto de 2025, para la comparación con el FWI propio.

**FirEUrisk.** Las tres URL de Dataverse corresponden al mapa (GeoTIFF), al manual de usuario y al readme. No está registrado qué número es cada fichero; en la tabla basta con el DOI. El MD5 del mapa está en `docs/data_sources.md`.

**Global-AI.** No se registró el enlace de descarga exacto de figshare.
- La versión 7 del registro corresponde a la v3.1 del índice: corrige el error de la ET₀ de la v3 (versión 5 del registro).

**ESFire30.** También se descargó `ESFire30_2001_2025.zip` (fechas corregidas con MODIS), pero no se usa.

**Uso limitado de algunos datasets:**
- **MCD43A4:** solo en el diagnóstico NBAR posterior (`docs/diagnostics/evi_nbar_fig3.md`). Si ese diagnóstico no entra en el suplemento, se quita de la tabla.
- **CORINE:** apoyo y contraste de la clase de brezal, no la clasificación principal.
- **Natural Earth:** solo en la cartografía de la Fig. 1, no en el análisis.

**Descargados pero fuera de los resultados (no van en la tabla):**
- fPAR de VIIRS VNP15A2H (`NASA/VIIRS/002/VNP15A2H`);
- focos activos de MODIS C6.1 (FIRMS `M-C61`);
- MCD12C1 como clasificación. Solo entra a través de la máscara `LC_MASK` del propio TROPOSIF.

**Fuentes que no se usaron:** CERES SYN1deg y GLEAM.
