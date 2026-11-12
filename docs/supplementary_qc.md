# Supplementary Section S1. Data quality control

*Supplementary material of the manuscript, formatted for* Remote Sensing of Environment. *Last updated: 7 November 2026. Figures and tables referred to as `figures/qc/*` are in the project repository.*

This section documents the checks applied to the input data and the tests of the processing chain. None of them used time series at the locations of the selected fires: unless stated otherwise, they were run over the whole study area or at generic points chosen by a fixed rule (S1.9).

## S1.1. Scaling of the Google Earth Engine assets

The GEE assets of MODIS and VIIRS fPAR are distributed with different scaling (checked on the composite of 4–12 July 2025):

| Asset | `Fpar` type | Values | Fill | Treatment |
| --- | --- | --- | --- | --- |
| `MODIS/061/MCD15A3H` | integer | 0–100 | 249–255 | × 0.01; valid ≤ 100 |
| `NASA/VIIRS/002/VNP15A2H` | double | 0–1 (pre-scaled) | 2.49–2.55 | no factor; valid ≤ 1.0 |
| `NASA/VIIRS/002/VNP15A2H_RAW` | integer | 0–100 | 249–255 | as MODIS (not used) |

Applying the user-guide scale factor to the pre-scaled VIIRS asset gave a mean fPAR of 0.004 instead of 0.36–0.40. To catch this kind of error, every downloaded image is checked automatically: the median over valid cells must fall within a plausible range (fPAR 0.05–0.95; red 0.01–0.40; NIR 0.05–0.60; blue 0.005–0.30). This applies to MCD15A3H, VNP15A2H, MCD43A4, MOD09GA and MYD09GA.

The SCF_QC field occupies bits 5–7 of `FparLai_QC` in MCD15A3H but bits 0–2 in VNP15A2H (VNP15 User Guide v1.1, Table 4), and the cloud bits of `FparExtra_QC` also differ (Table S1.2). The fraction of retrievals of the main algorithm without saturation (93.0% VIIRS vs 93.6% MODIS) and of valid retrievals (97.3% vs 96.9%) over the study area in June–September 2025 confirmed that the masks are equivalent.

## S1.2. Cloud screening of fPAR

**Table S1.2.** Cloud flags of the fPAR products (MOD15 C6.1 User Guide, Table 5; VNP15 User Guide v1.1, Table 5).

| Flag | MCD15A3H | VNP15A2H | Filter |
| --- | --- | --- | --- |
| Cloud | `FparExtra_QC` bit 5 (internal mask) | bits 0–1 (confidence) | MODIS = 0; VIIRS ≤ 1 (probably clear kept) |
| Cloud shadow | bit 6 | bit 2 | = 0 |
| Cirrus | bit 4 | bit 3 | = 0 |
| MOD09 cloud state | `FparLai_QC` bits 3–4 | — | "significant clouds" and "mixed" removed |
| Aerosol | bit 3 (none/low vs average/high) | bits 4–5 (graded) | not applied; per-cell fraction stored |

**Effect in June–September 2025** (valid 500 m pixels removed by the `FparExtra_QC` filter):

| | MODIS | VIIRS |
| --- | --- | --- |
| All land | 8.6% | 13.5% |
| Woodland | 17% (25% in September) | 18.5% |
| Shrubland | 7.5% | 11.8% |
| Cropland | 6.5% | 11.2% |

- The MOD09 cloud state removed a further 2.2% of MODIS pixels (1.9% in woodland).
- Because each 0.05° cell aggregates many pixels, the fraction of cell-composites with data hardly changed (≥ 99.3%). The age of the last valid composite before a potential ignition day did not change either (MODIS: median 3 days, 90th percentile 5 days; VIIRS: 7 and 11 days), so the persistence limits (5 and 11 days) remain adequate.
- At generic woodland points, the `FparExtra_QC` filter reduced the composite-to-composite fPAR drops of MCD15A3H (Basque Country: SD of consecutive changes 0.16 → 0.11; minimum fPAR 0.30 → 0.54; changes > 0.1 from 15 to 9) but did not remove them. The MOD09 cloud state had almost no further effect (SD 0.110 → 0.109). The residual variability of MCD15A3H in woodland is therefore not explained by flagged clouds.
- **Aerosol flag.** Applying the MODIS aerosol bit would remove a further 16% of pixels (30% in woodland; 44% in woodland in August 2025), including many smoke-free summer days, because it lumps average and high aerosol. The VIIRS "high" class flagged 3.2% of pixels (7% in August 2025). The flag is stored as a smoke indicator (sensitivity analysis R8).

## S1.3. fPAR from MODIS and VIIRS, and the noise passed on to SIF/APAR

**Comparison of daily interpolated fPAR** (June–September 2025, 0.25°):
- whole study area: median per-cell bias of VIIRS relative to MODIS −0.010 (−2.4%), median correlation 0.67; SIF/APAR with VIIRS 4% higher (median);
- shrubland: differences of −2 to −5%; correlation of 15-day means of SIF/APAR 0.96–1.00;
- woodland (Basque Country, Girona): VIIRS fPAR 9–16% higher and SIF/APAR 10–14% lower, with the shape of the series preserved (r = 0.90–0.98).

**Noise** (median per cell over days with data from all sources):

| Vegetation (0.25°) | SD of daily Δ log fPAR, MODIS / VIIRS | Relative SD of Δ SIF/APAR, 7-day trailing mean, MODIS / VIIRS | Jumps > 10% (n), MODIS / VIIRS |
| --- | --- | --- | --- |
| Woodland | 0.036 / 0.008 | 0.080 / 0.072 | 14 / 13 |
| Shrubland | 0.022 / 0.009 | 0.088 / 0.087 | 18 / 18 |
| Savannas | 0.027 / 0.008 | 0.075 / 0.072 | 12 / 10 |
| All | 0.023 / 0.009 | 0.084 / 0.082 | 15 / 14 |

VIIRS injects 3–5 times less day-to-day noise into fPAR, partly because its 8-day compositing is itself a temporal average. In SIF/APAR the gain is modest (about 10% in woodland at 0.25°, < 3% at 0.05°), because SIF retrieval noise dominates. MCD15A3H was kept as the main source because of its 4-day compositing: with the cut-off rule, the latest usable composite is centred 2.5–5.5 days before ignition for MODIS and 4.5–11.5 days for VIIRS.

## S1.4. Daily surface reflectance (MOD09GA, MYD09GA)

**Negative reflectance.** The full-series download stopped on Terra, 29 March 2025, when the median blue reflectance (0.0049) fell below the plausible range. All three bands were abnormally low over the western half of the Peninsula, the only clear area that day:

| Day (Terra) | Red | NIR | Blue | Clear pixels with a negative band |
| --- | --- | --- | --- | --- |
| 28 March 2025 | 0.085 | 0.288 | 0.041 | 0.01% |
| **29 March 2025** | **0.037** | **0.183** | **0.006** | **25.7%** |
| 30 March 2025 | 0.096 | 0.310 | 0.046 | 0.0% |

This is the signature of atmospheric over-correction, which lowers all bands and inflates NDVI (≈ 0.68 instead of ≈ 0.54). Removing only the negative pixels was not enough: without them the day passed the median check (blue 0.0062) but remained biased. Two filters were therefore applied: (i) 500 m pixels with a negative reflectance in any band are discarded; (ii) a whole image is rejected if more than 10% of its screened pixels are negative, provided it has at least 10,000 screened pixels (about 2500 km²). Rejected images are logged and excluded; the download stops only after three consecutive rejections or more than five in a product-year, which would indicate a systematic (scaling) problem.

**Frequency over the record** (May 2018 – November 2026):

| | MOD09GA (Terra) | MYD09GA (Aqua) |
| --- | --- | --- |
| Images | 3097 | 3093 |
| 99th percentile of the negative-pixel fraction | 0.3% | 1.0% |
| Images > 10% | 3 | 2 |
| Images rejected | 1 (29 March 2025) | 0 |

The other images above 10% had less than 350 km² of clear area (winter). The next image with wide clear coverage, Aqua on 2 November 2026, had 4.1%. MOD09GA 2018–2024 was downloaded again with the same filters so that the whole record is processed identically: the filters changed 0.5–0.8% of 0.05° cells and removed 35–84 cell-days per year.

**Platform agreement and orbital drift.** Both platforms have drifted since their last inclination manoeuvres (Terra, February 2020; Aqua, December 2021). Terra's overpass moved earlier, to about 09:00 local time by late 2025 (nominal 10:30), and Aqua's later, to about 15:50 by August 2026 (nominal 13:30). In June–September 2025, NDVI from the two platforms agreed when both observed the same cell on the same day (median Aqua − Terra difference −0.001; interquartile range −0.011 to 0.009). Combining them gave a valid observation on 62% of cell-days (Terra 39%, Aqua 35%). **[TODO: Aqua − Terra difference by year over the full record (R15)]**

## S1.5. SIF

- **Quality filter.** The L2B product keeps retrievals with `qa_value` > 0.5. Because the penalties that build `qa_value` are multiples of 0.5, this also removes retrievals with a single penalty, mainly at viewing zenith angles > 60°.
- **Footprint gridding.** Pixel corners were checked to form simple (non self-intersecting) quadrilaterals before sub-point placement; no exception was found in June–September 2025.
- **Maps and series.** The chain was checked on June–September 2025 with maps of July–August means of each variable and of the fraction of days with valid SIF/APAR, and with time series at generic woodland and shrubland points (S1.9).

## S1.6. Tests of the epoch chain with synthetic data

Synthetic daily series (seasonal cycle plus Gaussian noise, January 2019 – September 2025, ignition on 10 August 2025) were processed with the same code as the real data (`tests/test_epoch.py`, `R/tests/test_epoch.R`).

- **No post-ignition leakage.** Replacing all values from the ignition date onwards with arbitrary values (a constant 10⁶, or random values with a different mean) left every anomaly of days −60 to −1 unchanged. Replacing all fPAR composites whose period ends on or after ignition with absurd values left the daily fPAR before ignition unchanged, with and without persistence.
- **Signal recovery.** With a linear decline of 3 SD over the 20 days before ignition injected into the burned cells of eight synthetic fires, the full chain (SIF/APAR from SIF, PAR and fPAR composites; anomalies; R statistics) recovered a SIF/APAR lead time of 9–12 days, and none for NDVI and EVI, which carried no signal.
- **Residual bias in cells without signal.** With 400 synthetic cells, the mean standardised anomaly of the last 7 days before ignition was −0.07 SD with the day-of-year median and −0.13 SD with LOESS, against 0.04 and −0.01 SD at the start of the window. Both are well below the 0.5 SD lead-time threshold, and they affect burned and control cells alike.
- **LOESS at the end of a truncated series.** In the epoch analysis each series ends at ignition, so the evaluated window lies at the end of the record. Two edge effects of the LOESS trend appeared:
  - *Seasonal leakage:* a local fit to the raw series absorbs part of the seasonal cycle near the series end, which biased control cells without signal by −0.3 to −0.4 noise SD. Fitting the trend to the deseasonalised series (one STL-like iteration) removed the bias.
  - *Absorption of the signal itself:* with the trend fitted on all pre-ignition data, a pre-fire decline pulls the end of the trend down, shifting the early window upwards (+0.16 to +0.45 SD on days −60 to −41 in three synthetic realisations) and damping the late signal. With the trend fitted only on data before day −60 and held constant afterwards, the early window stayed at −0.08 to −0.32 SD and the late signal matched the day-of-year median within 0.25 SD. The day-of-year median is the main definition; LOESS with this trend cut is a sensitivity analysis (R4).

## S1.7. Fire data

**FIRMS active fires** (archive request of 7 November 2026, one per country; S-NPP, NOAA-20, NOAA-21 and MODIS C6.1, January 2018 – November 2026):
- detections on islands removed with the peninsula mask;
- standard archive (to 31 July 2026): only `type` = 0 (presumed vegetation fire) kept;
- near-real-time part (no `type` flag): detections within 500 m (VIIRS) or 1000 m (MODIS) of a static-source detection (`type` = 2) of the 2018–2026 archive removed. This removed 15–16% of near-real-time detections, similar to the share of `type` = 2 in the archive (≈ 18%);
- VIIRS low-confidence and MODIS confidence < 30 removed;
- result: 425,154 detections. In northwestern Spain (lat > 41.5°, lon < −6°), daily VIIRS detections rose from about 40 on 7–8 August 2025 to more than 1100 from 10 August, with a maximum of 7244 on 17 August.

**EFFIS dates are not independent of FIRMS.** In 2025, the EFFIS start time matched the first VIIRS detection inside the perimeter within 10 minutes for 60% of perimeters with detections, and some start times are assigned in batches at round hours. Agreement between EFFIS and FIRMS was therefore not counted as independent confirmation, and the ignition rule takes the earliest date across sources instead (Section 2.3).

**Ignition rule.** For perimeters of 500 ha or more in 2025, the final ignition date was earlier than `FIREDATE` in 71 of 108 cases, by one or two days in 49 of them; the median difference from `FIREDATE` was 0 days for VIIRS, −1 day for MCD64A1 and 0 days for VNP64A1. Seven of the 108 perimeters carried the coherence flag (5 of the 25 perimeters ≥ 5000 ha), in all cases because of 1–11 VIIRS detections between 90 and 30 days before `FIREDATE`, against hundreds to thousands within the fire.

**ESFire30.** The Landsat perimeters of ESFire30 (Zenodo record 20257001, 1985–2025) cover Spain only: they overlap 33 of the 33 Spanish and 1 of the 20 Portuguese short-listed perimeters. In Portugal the unburned criterion of the controls therefore relies on EFFIS, MCD64A1 and VNP64A1.

## S1.8. Static fields

- **Aridity index.** Version 3 of the Global Aridity Index (figshare v5/v6) used air temperature in °C instead of K in the Stefan–Boltzmann term, which overestimated ET0 and gave too dry aridity values; version 3.1 (figshare v7, July 2025) corrects it and was used. The 30″ grid is aligned with the 0.05° grid, so each cell is the mean of 6 × 6 source pixels (sea pixels, coded 0, excluded). Values: 0.22 at Almería, 0.34 at Madrid, 1.87 at Santiago de Compostela; 5th–95th percentile over the study area 0.26–1.47. An earlier provisional index from ERA5-Land (P/|PET|, 1991–2020) correlated with it (r = 0.82) but was 39% lower (median ratio 1.63), consistent with the known overestimation of ERA5-Land potential evaporation; it is not used.
- **CORINE fractions.** CORINE 2018 was aggregated in GEE as the area mean of the class indicator of each group (in 16 tiles, because a single request exceeds the GEE reprojection limit). The group fractions sum to 1 within 0.001 in 99.9% of the 34,399 mapped 0.05° cells. CORINE was preferred over MCD12C1 (IGBP), which assigns almost no shrubland in the large 2025 fires and places Mediterranean shrubland and open woodland in its woody savanna, savanna and grassland classes.
- **FirEUrisk fuel fractions.** The 1 km fuel map (EPSG:3035, equal area) was aggregated by assigning 4 × 4 sub-points per pixel to the 0.05° cells; the type fractions sum to 1 in every cell with data (sea is coded as nonfuel type 7 and removed by the land mask). The 20 types listed in the Product User Manual are all present in the study area. Over the 24,687 land cells (≥ 50% land), the dominant classes are cropland (44.4%), shrubland (27.7%), closed forest (10.5%), grassland (8.3%), heathland and wet land (4.1%), nonfuel (3.5%) and open forest (1.6%). Agreement with the dominant CORINE group: 91% of heathland-and-wet-land cells are CORINE moors and heathland (322), so in Iberia this class is essentially Atlantic heathland, not wetland; closed forest cells are CORINE broadleaved (41%) or coniferous (39%) forest; 89% of cropland cells are CORINE agricultural areas. Open forest cells are CORINE broadleaved forest (42%) or agro-forestry (26%, dehesas and montados). FirEUrisk shrubland cells are spread over CORINE sclerophyllous vegetation (22%), agricultural areas (16%), coniferous (14%) and broadleaved (13%) forest and transitional woodland-shrub (12%); shrubland is also the main type with the largest validation errors in the product (commission 62%, omission 41%; Aragoneses et al., 2023).
- **Elevation.** Area-mean SRTM v4.1 (90 m). The 30 m SRTM exceeded the GEE user memory for this aggregation.

## S1.9. Generic points and control availability

**Generic points** for the chain checks were chosen by a fixed rule, deliberately not at fire locations: 0.25° cells with ≥ 95% land, unburned (MCD64A1, January–September 2025) in the cell and its eight neighbours, highest class purity (MCD12C1 woodland ≥ 60%, shrubland ≥ 50%), at least 2° apart, three per class.

**Control availability.** With the criteria of Section 2.9 (FirEUrisk fuel class, relative aridity tolerance ±15%), 37 of the 53 short-listed perimeters obtained at least three controls (all 53 have burned cells): 26 of 33 in the shrubland stratum (17 shrubland, 9 heathland), 2 of 5 in woodland (both closed forest, in Spain, with 4 and 1 burned cells), 4 of 8 in grassland and all 5 cropland fires. An earlier design (CORINE groups, absolute aridity tolerance ±0.1) gave 30 fires with controls and none in woodland; CORINE groups with the relative aridity tolerance give 35 (1 in woodland). Under that earlier design no single criterion explained the failures: relaxing one at a time increased the number of fires with controls to 36 (aridity ±0.2), 33 (elevation ±300 m), 37 (unburned since 2020 instead of 2017) and 38 (up to 5% burned in the cell instead of 0). The criteria were not relaxed. At 0.25°, only 8 perimeters have a cell at least 25% burned, and almost every 0.25° cell of northwestern Iberia contains burned area since 2017; the 0.25° grid is therefore a sensitivity analysis with its own control design (R5).

## S1.10. Fire Weather Index

**Inputs.** ERA5-Land hourly fields were taken from Google Earth Engine on the native 0.1° grid (cell centres at multiples of 0.1°; 7,814 land cells in the study region), without resampling. Values fetched at two cells and dates matched direct point queries exactly. The `_hourly` precipitation band of each image holds the amount of the hour ending at the image time (checked against the accumulated band on 5–6 March 2025), so the 24 h precipitation at noon is the sum of the images from 13:00 UTC of the previous day to 12:00 UTC. No land cell-day lacks an input.

**Implementation.** xclim 1.0.0 (`xclim.compute.fire.cffwis_indices`) was compared with the reference R implementation of the Canadian Forest Service (cffdrs 1.9.2, function `fwi`, batch mode with the same start-up codes and latitude adjustment) on 34 ERA5-Land cells (30 random land cells, seed 42, and 4 cells in the 2025 fire area) from 1 January to 31 August 2025 (8,262 cell-days), with identical noon inputs. For this check both implementations were started on 1 January 2025 with the standard start-up codes (FFMC 85, DMC 6, DC 15); this short run is used only for the implementation check, whereas the analysis uses the continuous run from 1 January 2017. The sample is rebuilt by `python -m physiofire.preprocess.fwi_cffdrs_sample` (identical to the original sample):

| Index | Max. absolute difference | 99th percentile |
| --- | --- | --- |
| DMC | 0.0002 | 0.00005 |
| DC | 0.0004 | 0.0002 |
| BUI | 0.0002 | 0.00005 |
| FFMC | 0.43 | 0.18 |
| ISI | 0.75 | 0.30 |
| FWI | 1.7 | 0.66 |

The FFMC difference has a single origin. xclim uses the coefficient 147.2 in the conversion between FFMC and fine fuel moisture content (Eqs. 1 and 10), as in the original equations (Van Wagner, 1987) and in the updated official source code (Wang et al., 2015, NOR-X-424), whereas cffdrs v1.9.2 computes it as 147.27723 (= 250 × 59.5/101; constant `FFMC_COEFFICIENT`, used in the FFMC and ISI functions). With the cffdrs coefficient set to 147.2 (same sample, 1 January–31 August 2025, 8,262 cell-days), the differences fall to storage precision:

| Index | Max. absolute difference | 99th percentile |
| --- | --- | --- |
| FFMC | 1.1 × 10⁻⁵ | 7.6 × 10⁻⁶ |
| ISI | 2.1 × 10⁻⁵ | 9.3 × 10⁻⁶ |
| FWI | 5.1 × 10⁻⁵ | 2.5 × 10⁻⁵ |

Command: `Rscript R/check_fwi_cffdrs.R data/interim/era5land_fwi/cffdrs_check_sample.csv 147.2`. xclim was used unmodified; the difference does not affect any decision of the 2025 case, because anomalies are standardised per cell. Script: `R/check_fwi_cffdrs.R`.

**Comparison with the CEMS fire danger reanalysis.** The FWI computed from ERA5-Land (0.1°, continuous from 1 January 2017) was compared with the operational CEMS reanalysis (`cems-fire-historical-v1`, version 4_1, consolidated, ERA5, 0.25°) for August 2025, after averaging the 0.1° cells within each 0.25° cell (cells with ≥ 50% land). The comparison covers all ERA5-Land land cells of the study region box, 35.25–44.25° N, 10.25° W–4.75° E: 1,283 cells of 0.25° (39,773 cell-days), of which about 210 lie outside the Iberian Peninsula (France 104, Algeria 87, Morocco 18, Andorra 1; nearest country of the cell centre). Script: `python -m physiofire.preprocess.fwi_cems_compare`.

| Index | r (pooled) | Bias (ERA5-Land − CEMS) | MAE | Median ERA5-Land / CEMS | r of the monthly mean (spatial) | Median temporal r per cell |
| --- | --- | --- | --- | --- | --- | --- |
| FWI | 0.986 | −1.6 | 2.4 | 38.5 / 39.8 | 0.986 | 0.991 |
| FFMC | 0.991 | −0.1 | 0.7 | 92.9 / 93.0 | 0.988 | 0.995 |
| DMC | 0.969 | +6.0 | 19.0 | 162 / 160 | 0.974 | 0.990 |
| DC | 0.996 | +0.8 | 15.3 | 761 / 759 | 0.996 | 1.000 |

The two products agree closely; ERA5-Land gives a slightly lower FWI (−4% in the median). With a start-up on 1 January 2025 instead of 2017, the DC was 29 units lower than CEMS in August 2025 (r = 0.978), so the long spin-up matters for the moisture codes. Within each 0.25° cell, the 0.1° cells differ by a median SD of 8 FWI units in August 2025 (regional SD 12), mostly through the moisture codes (DC: 67 against 134), whereas the same-day noon inputs vary little inside a 0.25° cell (temperature 0.4 °C, relative humidity 1%, wind 0.6 km h⁻¹). Part of the 0.1° variability therefore comes from the accumulated precipitation history, which ERA5-Land interpolates from ERA5 (Section 2.7).
