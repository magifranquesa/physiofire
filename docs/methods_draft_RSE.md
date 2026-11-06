# Satellite chlorophyll fluorescence as an early indicator of wildfire danger in the Iberian Peninsula: methods (draft)

*Working draft of the Materials and Methods section, formatted for* Remote Sensing of Environment. *Last updated: 6 November 2026.*

> **Draft status (remove before submission).**
> - **[Implemented]** steps run end to end for the sample period (1 June – 7 September 2025).
> - **[Planned]** steps are designed but not yet run.
> - **[PROVISIONAL]** items will be replaced (PAR source, percentile thresholds).
> - **[TODO]** marks decisions still pending with co-authors; **[ref]** marks references still to be added.
> - Fire selection criteria will be fixed and versioned *before* any vegetation time series is examined at fire locations.

---

## 2. Materials and methods

### 2.1. Rationale and overview

Operational fire danger indices such as the Canadian Fire Weather Index (FWI; Van Wagner, 1987) are driven only by meteorology and do not observe the physiological state of live vegetation. Optical vegetation indices (NDVI, EVI) and live fuel moisture products respond to water stress mainly through changes in canopy structure and pigments, which lag the onset of stress by one to two weeks (Tang et al., 2026).

Sun-induced chlorophyll fluorescence (SIF) observed from space can be decomposed as
$$\mathrm{SIF} = \mathrm{PAR}\times f_\mathrm{PAR}\times \Phi_F, \tag{1}$$
where PAR is incoming photosynthetically active radiation, $f_\mathrm{PAR}$ the fraction of PAR absorbed by the canopy, and $\Phi_F$ the apparent fluorescence yield (including the escape probability). The ratio
$$\mathrm{SIF/APAR} = \frac{\mathrm{SIF}}{\mathrm{PAR}\times f_\mathrm{PAR}} \tag{2}$$
therefore isolates a physiological signal from radiation and canopy structure. Globally, this ratio responds to drought within about 3 days, against about 8 days for EVI and 12–13 days for LAI (Tang et al., 2026).

We test whether anomalies of SIF/APAR depart from normal conditions before wildfires, earlier than NDVI and EVI, and whether they carry information not contained in the FWI or in the atmospheric evaporative demand (AED). We use a superposed epoch design with matched non-fire controls.

The processing chain (Fig. 1 **[TODO: workflow figure]**) has five stages:
1. Retrieval-level SIF gridded with footprint weighting.
2. Ancillary fPAR, PAR and reflectance on the same grids.
3. SIF/APAR, SIF/PAR and optical indices.
4. Daily anomalies.
5. Epoch composites around selected fires and matched controls.

Unless stated otherwise, method parameters follow Tang et al. (2026), whose code and data are openly available (https://doi.org/10.5281/zenodo.18327559).

### 2.2. Study area and period

- **Area:** mainland Spain and Portugal, within 10°W–4.5°E and 35.5°N–44.5°N. The Balearic, Canary, Azores and Madeira archipelagos are excluded.
- **Land mask:** the fraction of each grid cell inside the mainland polygons of Spain and Portugal, computed from the US Department of State Large Scale International Boundaries (LSIB, 2017). Cells with a land fraction ≥ 0.5 are analysed.
- **Climate and vegetation:** the region spans a strong gradient, from humid Atlantic and Cantabrian forests in the north and northwest to semi-arid Mediterranean shrublands and croplands in the southeast **[TODO: aridity classes from Global-AI_PET_v3]**.
- **Analysis period:** from May 2018, the start of the TROPOMI SIF record, onwards.
- **Main case study:** the summer of 2025, which combined a prolonged heatwave with large wildfires in northwestern Spain and in Portugal in August. Fires from 2018 (when the 60-day pre-fire window is covered by data), 2022 and 2024 are added for the full test.
- **Sample period:** the processing chain was first run and checked for 1 June – 7 September 2025, which covers the 60-day window preceding mid-August ignitions plus margins for temporal smoothing and interpolation.

### 2.3. Data

The datasets used are listed in Table 1.

**Table 1.** Datasets. Dates refer to the record available at the time of writing.

| Variable | Product | Native resolution | Access | Reference |
| --- | --- | --- | --- | --- |
| SIF (743–758 nm, day-length corrected) | TROPOSIF L2B v01.00.01 (Sentinel-5P TROPOMI) | ~3.5 × 5.5 km (7 km along-track before Aug 2019), daily | S5P-PAL STAC | Guanter et al. (2021) |
| fPAR | MODIS MCD15A3H v061 | 500 m, 4-day | Google Earth Engine (GEE) | Myneni et al. (2002) |
| Red, NIR, blue NBAR | MODIS MCD43A4 v061 | 500 m, daily | GEE | Schaaf et al. (2002) |
| PAR **[PROVISIONAL]** | ERA5-Land downward shortwave × 0.48 | 0.1°, daily | GEE | Muñoz-Sabater et al. (2021) |
| PAR (candidate) | CERES SYN1deg-Day Ed4B | 1°, daily | NASA ASDC | **[ref]** |
| Meteorology, AED **[Planned]** | ERA5-Land | 0.1°, hourly/daily | GEE | Muñoz-Sabater et al. (2021) |
| FWI (operational reference) **[Planned]** | CEMS fire danger indices, historical (v4.1 **[TODO: confirm]**) | 0.25°, daily | Copernicus EWDS | Vitolo et al. (2020) |
| Land cover | MODIS MCD12C1 v061, IGBP scheme | 0.05°, yearly | GEE | Friedl and Sulla-Menashe **[ref]** |
| Burned area (control screening only) | MODIS MCD64A1 v061 | 500 m, monthly | GEE | Giglio et al. (2018) |
| Fire perimeters and dates **[Planned]** | National fire maps (Ochoa et al. **[ref]**), EFFIS perimeters, NASA FIRMS VIIRS active fires | vector / 375 m | — | **[ref]** |

### 2.4. SIF processing **[Implemented]**

**Source product.** We used the TROPOSIF L2B product (Guanter et al., 2021). It contains, for each day, all TROPOMI retrievals with quality value `qa_value` > 0.5 from all orbits; `qa_value` is a score built from penalties for viewing and solar zenith angles, radiance level, fit quality and SIF range. Each global daily file was:
1. downloaded from the S5P-PAL STAC catalogue;
2. subset to pixels whose centre lies within the study region plus a 0.1° buffer;
3. discarded, keeping only the subset.

The subset retains all variables along the pixel dimension. We used the day-length corrected SIF retrieved in the 743–758 nm window (`SIF_Corr_743`), as in Tang et al. (2026), together with its 1σ retrieval error (`SIF_ERROR_743`).

**Screening.** Following Tang et al. (2026), we removed:
- retrievals with an effective cloud fraction (`cloud_fraction_L2`) > 0.5;
- snow/ice and barren pixels, using the product's land cover mask (MCD12C1 2018 classes 15 and 16).

The L2B product applies the quality filter as `qa_value` > 0.5, whereas Tang et al. (2026) excluded values < 0.5. Because penalties are multiples of 0.5, the L2B screening additionally removes retrievals carrying a single penalty, mainly at viewing zenith angles > 60°. A snow mask from ERA5-Land snow cover will be applied to the full series **[TODO: ERA5-Land vs GlobSnow]**; it is irrelevant for the summer sample.

**Footprint-weighted gridding.** At 0.05° the grid cell (about 4.3 × 5.6 km at 40°N) is similar in size to a TROPOMI pixel, so assigning each retrieval to the cell containing its centre would bias the spatial distribution and leave gaps. Each pixel $i$ was therefore divided into $k\times k$ sub-points ($k=4$), placed by bilinear interpolation between its four corners. Each sub-point carries a weight $1/k^2$ to the cell in which it falls, which approximates the fraction $w_{ij}$ of pixel $i$ overlapping cell $j$. Pixel corners were checked to form simple (non self-intersecting) quadrilaterals; no exception was found in the sample period.

For each cell and day,
$$\overline{\mathrm{SIF}}_j=\frac{\sum_i w_{ij}\,\mathrm{SIF}_i}{\sum_i w_{ij}},\qquad
\sigma_{\overline{\mathrm{SIF}},j}=\frac{\sqrt{\sum_i w_{ij}^2\,\sigma_i^2}}{\sum_i w_{ij}}, \tag{3}$$
where $\sigma_i$ is the retrieval error. We also stored the equivalent number of full pixels ($\sum_i w_{ij}$) and the number of distinct pixels touching the cell.

Grids at 0.25° (as in Tang et al., 2026) and 0.05° were produced independently. Both are aligned with the region bounds, so 0.25° cells contain exactly 5 × 5 cells of 0.05°.

### 2.5. fPAR and surface reflectance **[Implemented]**

MODIS products were aggregated in Google Earth Engine (Gorelick et al., 2017) to the 0.05° grid. In each cell we took the area-weighted mean of valid 500 m pixels and their count (reprojection from the sinusoidal grid with `reduceResolution`). The 0.25° grid was then built locally as the count-weighted mean of the 5 × 5 contained 0.05° cells, which guarantees consistency between scales.

**fPAR.** fPAR from MCD15A3H (Myneni et al., 2002) was retained only for retrievals of the main (radiative transfer) algorithm (SCF_QC, bits 5–7 of `FparLai_QC`, ≤ 1) and valid range (≤ 100 before scaling). Each 4-day composite was assigned to its central time (start + 1.5 days). Daily values were obtained by linear interpolation between composite centres, bridging gaps of up to 12 days, as in Tang et al. (2026).

**[Planned] Burn-date cut-off for fPAR (epoch analysis).** For the epoch analysis, the fPAR series of each burned cell is cut at the cell's burn date $d_c$ (Section 2.11) *before* interpolation. Any composite whose compositing period ends on or after $d_c$ (start + 3 days ≥ $d_c$) is removed, so that no post-fire composite enters the daily values of the pre-fire window. Between the last pre-fire composite centre and $d_c$, values are left missing **[TODO: or carried forward from the last composite for at most 4 days]**. The uncut series is kept only for descriptive maps.

**Optical indices.** MCD43C4, used by Tang et al. (2026), is not available in GEE. We therefore aggregated its 500 m counterpart, MCD43A4 nadir BRDF-adjusted reflectance (NBAR; Schaaf et al., 2002), to 0.05°. MCD43C4 is itself derived from this aggregation. We kept reflectances with mandatory quality ≤ 1 (full or magnitude BRDF inversion). NDVI and EVI (Huete et al., 2002) were computed at 0.05° from cell-mean red ($R$), near-infrared (NIR) and blue ($B$) reflectances, using the EVI formulation of Tang et al. (2026):
$$\mathrm{NDVI}=\frac{\mathrm{NIR}-R}{\mathrm{NIR}+R},\qquad
\mathrm{EVI}=2.5\,\frac{\mathrm{NIR}-R}{\mathrm{NIR}+6R-7.5B+1}. \tag{4}$$
EVI values outside [0, 1] were discarded. 0.25° indices were obtained as count-weighted means of the 0.05° indices, mirroring the resampling of indices from 0.05° to 0.25° in Tang et al. (2026).

**[Planned] Temporal footprint of NBAR and a daily optical competitor.** MCD43A4 NBAR for a nominal date is retrieved from a 16-day window of multi-angular observations around that date **[TODO: verify window placement in the MCD43 C6.1 user guide; nominal date expected to be the 9th day, i.e. observations from $t-8$ to $t+7$]**. This has two consequences for the epoch analysis:
- NBAR dates within about 8 days before a burn date contain post-fire observations; in the epoch analysis they are masked ($t \ge d_c - 8$).
- The window delays and smooths the optical response, which would artificially favour SIF/APAR in a lead-time comparison.

We therefore add a daily, non-BRDF-adjusted NDVI/EVI from MODIS surface reflectance (MOD09GA, Terra, and MYD09GA, Aqua; collection 6.1, in GEE). It is screened with the `state_1km` flags (cloud, cloud shadow, cirrus, adjacency) and limited to sensor zenith angles ≤ 40° **[TODO: thresholds]**, and it is aggregated to the same grids. It is used as the main optical competitor in the lead-time analysis, with MCD43A4 as a secondary reference.

**[Planned] Effective temporal window of each product.** The temporal support of each input (Table 2) is reported, because it bounds the lead time that each variable can show.

**Table 2.** Effective temporal window of each input (**[TODO: verify entries marked *]**).

| Variable | Product | Temporal support of one daily value |
| --- | --- | --- |
| SIF | TROPOSIF L2B | single overpass (~13:30 local solar time), day-length corrected |
| fPAR | MCD15A3H | 4-day composite* (best retrieval within the period), linearly interpolated between composite centres |
| NBAR NDVI/EVI | MCD43A4 | 16-day multi-angular retrieval window* |
| Daily NDVI/EVI | MOD09GA/MYD09GA | single overpass (Terra ~10:30, Aqua ~13:30, both drifting at end of mission) |
| PAR, AED | ERA5-Land | daily aggregate (00–24 UTC) |
| FWI | CEMS (ERA5) | daily at 12:00 local time; the DMC and DC subindices carry multi-week memory of *past* weather by design |
| Smoothing | all | trailing window of $w$ days (Section 2.8), i.e. a lag of about $(w-1)/2$ days applied equally to all variables |

### 2.6. Photosynthetically active radiation **[PROVISIONAL]**

**Reference choice and its problem.** Tang et al. (2026) used all-sky direct plus diffuse surface PAR from CERES SYN1deg Ed4.1. That edition is no longer distributed; the current release, SYN1deg Ed4B (published May 2025), runs to 31 August 2026. From April 2022 onwards, Ed4B uses NOAA-20 only (no Terra/Aqua) and the MERRA-2 reanalysis for cloud retrievals and flux computations. The product's data quality summary warns that input changes may introduce spurious discontinuities, and this one falls within our main analysis period.

**Discontinuity test [Planned].** We will test for a discontinuity in April 2022 by comparing, for each 1° cell of the region, monthly CERES SYN1deg Ed4B surface PAR with monthly ERA5-Land surface downward shortwave radiation aggregated to the CERES grid. The test looks for a step in the CERES/ERA5-Land ratio between May 2018 – March 2022 and April 2022 – August 2026 **[TODO: test statistic, e.g. difference in monthly-anomaly ratio with block bootstrap]**. Using shortwave rather than PAR from the reference is sufficient for this purpose, because the PAR/shortwave ratio varies little in time, so a step in CERES PAR would appear as a step in the ratio.

**Provisional source.** Until the test is completed, PAR is estimated as
$$\mathrm{PAR}=f\times\mathrm{SW}_\downarrow, \tag{5}$$
where $\mathrm{SW}_\downarrow$ is the ERA5-Land daily mean surface downward shortwave radiation (W m⁻², from `surface_solar_radiation_downwards_sum`/86 400). It is bilinearly resampled from 0.1° to 0.05° and averaged to 0.25°; $f=0.48$ is a typical PAR/shortwave energy ratio (values of 0.45–0.50 are common **[ref]**).

A constant $f$ rescales SIF/APAR uniformly and does not alter the timing or relative magnitude of its anomalies. However, absolute SIF/APAR values are not comparable with those of Tang et al. (2026). If a discontinuity is found in CERES, ERA5-Land will be adopted as the definitive PAR source, because it provides a homogeneous record and low latency, which also suits a future near-operational test.

### 2.7. Fluorescence ratios **[Implemented]**

**Daily ratios.** SIF/APAR (Eq. 2) and SIF/PAR were computed daily for each cell, with SIF from Eq. (3), PAR from Eq. (5) and daily fPAR (Section 2.5). Following Tang et al. (2026), values below the 1st or above the 99th percentile were discarded. The percentiles are computed over all land cells and days. For the sample period they were computed on the sample itself **[PROVISIONAL: to be recomputed on the full record]**.

**[Planned] Outlier screening without removing extreme stress.** A filter at the 1st and 99th percentiles computed over all cells and days can preferentially remove the extreme low values of a record-breaking season such as 2025, which is precisely the signal of interest. The pooled filter is therefore replaced by a two-step screening:
1. **Input validity:** SIF/APAR is not computed where the denominator is unreliable: $f_\mathrm{PAR} < f_\mathrm{min}$, PAR $< \mathrm{PAR}_\mathrm{min}$, or fewer than $n_\mathrm{min}$ equivalent TROPOMI pixels **[TODO: thresholds]**.
2. **Per-cell robust filter:** only isolated spikes are removed, using values further than $k$ median absolute deviations from the cell's median for the same season **[TODO: $k$, e.g. 6; season definition]**. Post-burn data are excluded when computing these statistics.

Ratio values are not clipped at a lower percentile, because negative SIF retrievals are unbiased noise and clipping them only on one side would bias the mean. The pooled 1–99 filter of Tang et al. (2026) is kept as a sensitivity test.

As a diagnostic, we will report the fraction of data in the pre-fire windows of fire cells, and in matched control windows, that the pooled filter would have removed, as a function of day relative to $d_c$. A concentration of removals in the days before burning in fire cells, but not in controls, would indicate that the pooled filter biases the comparison.

**[Planned] Sensitivity to the structural normalisation.** MCD15A3H fPAR is the fraction absorbed by the whole canopy, not by chlorophyll. In Mediterranean summers part of a decrease in SIF/APAR can therefore reflect pigment loss rather than a change in fluorescence yield. As a sensitivity test, we also compute SIF/(PAR × NIRv) and SIF/NIRv, with NIRv = NDVI × NIR as in Tang et al. (2026), Eq. 2.

**[Planned] Sensitivity to PAR timing.** The day-length corrected SIF is compared with daily mean PAR. As a sensitivity test, PAR is also taken at the TROPOMI overpass (~13:30 local solar time) from ERA5-Land hourly shortwave **[TODO: matching of the instantaneous SIF_743 vs SIF_Corr_743]**.

**[TODO] Inverse-variance weighting.** Weighting retrievals in Eq. (3) by $w_{ij}/\sigma_i^2$ instead of $w_{ij}$ will be evaluated.

**Expected role of SIF/PAR.** SIF/PAR retains $f_\mathrm{PAR}$ (Eq. 1) and is expected to behave like EVI. It is therefore carried as an intermediate reference between the physiological (SIF/APAR) and structural (EVI) signals.

### 2.8. Anomalies **[Planned]**

Daily anomalies of SIF/APAR, SIF/PAR, NDVI, EVI, AED and FWI will be computed following Tang et al. (2026), in three steps:
1. Remove a long-term trend estimated with LOESS, with a span of 40% of the record.
2. Subtract the mean daily seasonal cycle of the detrended series.
3. Apply a 15-day × 3 × 3-cell moving mean.

**Short climatology.** The TROPOMI record only starts in May 2018, so the climatology is short (about eight seasons). We will therefore also compute anomalies relative to the day-of-year median of the full period, and report the sensitivity of the results to this choice.

**Smoothing window.** The 15-day smoothing limits the attainable lead time. We will repeat the analysis with shorter windows (7 days) at 0.25°, where single-day retrieval errors are smaller (Section 3 **[TODO]**).

**[Planned] Rules that prevent post-fire leakage (epoch analysis).** Centred temporal smoothing and 3 × 3 spatial smoothing would bring post-burn data into the pre-fire window and could create an artificial lead time. For the epoch analysis:
1. **Masking before any statistic.** In every burned cell, all data from its burn date $d_c$ onwards are masked *before* computing trends, seasonal cycles, filters or any smoothing (Section 2.11). This also keeps the post-fire recovery years of a cell out of its climatology.
2. **Trailing windows only.** Temporal smoothing uses trailing windows that end on the evaluated day, $\bar{x}(t) = \mathrm{mean}\{x(t-w+1),\dots,x(t)\}$, with a minimum number of valid days **[TODO]**.
3. **Spatial smoothing.** No spatial smoothing is applied at 0.25° (3 × 3 cells span about 75 km). At 0.05° a 3 × 3 window may be used as a sensitivity test, always after masking each cell from its own burn date.
4. **Descriptive use only for centred smoothing.** The centred 15-day × 3 × 3 smoothing of Tang et al. (2026) is used only for descriptive maps.

**[Planned] Two anomaly definitions, equal weight.** Anomalies relative to LOESS trend plus mean seasonal cycle, and anomalies relative to the day-of-year median, are carried through the whole analysis and reported with equal weight. Neither is designated as the main definition.

### 2.9. Atmospheric evaporative demand and fire weather **[Planned]**

**AED.** We use AED rather than vapour pressure deficit (VPD), the variable of Tang et al. (2026), as the atmospheric reference, because it integrates temperature, humidity, wind and radiation. AED will be computed as FAO-56 Penman–Monteith reference evapotranspiration (Allen et al., 1998) from ERA5-Land daily inputs:
- 2 m maximum and minimum temperature;
- 2 m dew point;
- 10 m wind;
- net shortwave and longwave radiation;
- surface pressure.

**[TODO: use AED already computed by the IPE group if available; its method takes precedence.]** Because Tang et al. (2026) used VPD, comparisons with their response times are not direct, and this will be discussed.

**FWI.** The operational reference is the CEMS historical fire danger reanalysis (Vitolo et al., 2020), computed from ERA5 with inputs at 12:00 local time, at 0.25°. An FWI computed from ERA5-Land hourly data at local noon will be used for consistency checks at 0.05° **[TODO: FWI implementation]**.

**[Planned]** FWI is expressed as local percentiles (relative to the cell's own distribution of the season) and as EFFIS danger classes, rather than as anomalies **[TODO: EFFIS class thresholds]**.

### 2.10. Fire sample **[Planned; criteria to be fixed before analysis]**

**Sources.** Fire perimeters will be taken from:
- national fire maps for Spain (Ochoa et al. **[ref]**);
- EFFIS perimeters for Spain and Portugal, which use a homogeneous method and are also used to cross-check perimeters and dates;
- **[TODO: Portuguese fire map source]**.

**Ignition dates.** The ignition date of each fire will be confirmed by at least two sources: map date, earliest VIIRS active-fire detection within the perimeter (NASA FIRMS, S-NPP and NOAA-20), and national ignition records (EGIF, ICNF) where accessible. EFFIS dates may refer to detection, and nearby perimeters may be merged; both cases will be checked against FIRMS.

**Selection.** Fires will be selected manually but according to written criteria, fixed and versioned before any vegetation time series is examined at fire locations:
- a minimum area **[TODO]**, prioritising large fires given the 0.25° scale; the fraction of the 0.25° and 0.05° cells burned will be recorded;
- a confirmed ignition date;
- a clear dominant vegetation type;
- no overlap with other fires within the 60-day pre-fire window.

The sample will be balanced across vegetation types (shrubland, woodland, and grassland as a negative control, since cured grasses are dead fuel), countries, regions and years. The selected fires and the criteria each meets will be provided as supplementary material.

### 2.11. Superposed epoch analysis **[Planned]**

**Day 0 per cell.** The epoch is defined per grid cell, not per fire. Day 0 of a cell, $d_c$, is its burn date:
- the earliest VIIRS 375 m active-fire detection (S-NPP and NOAA-20, nominal and high confidence **[TODO: confidence rule]**) falling inside both the cell and the fire perimeter;
- if no such detection exists, the earliest MCD64A1 burn date in the cell.

A cell is attributed to a fire if the burned fraction of the cell (from the perimeter) is at least $f_\mathrm{min}$ **[TODO: threshold at 0.25° and 0.05°]**. A large fire therefore contributes several cells with different day 0 values.

**[TODO] Days between ignition and $d_c$.** For cells that burn several days after the fire's ignition, the days between the two dates are pre-burn for the cell, but the fire is already active nearby (smoke, heat). These days are flagged and excluded in the main analysis **[TODO: confirm]**. An analysis aligned on the fire's ignition date is reported as a complement.

**Epoch series.** For each fire cell, the anomaly series of each variable will be extracted for the 60 days preceding $d_c$ (days $-60$ to $-1$), after applying the masking and trailing-window rules of Section 2.8.

**[Planned] Smoke.** Days with high aerosol loading are flagged in fire and control cells alike, using the TROPOMI UV aerosol index or MODIS AOD, and excluded in a sensitivity test **[TODO: product (e.g. S5P L3 AER_AI or MCD19A2 in GEE) and threshold]**.

**Controls.** Each fire will be compared with non-fire controls matched by vegetation type, region and calendar date. Controls are unburned cells (MCD64A1 and fire maps) outside a buffer around any fire in the window **[TODO: number of controls, buffer, region definition]**.

**Lead time.** For each variable, the lead time is defined as the earliest day before ignition from which the fire composite departs significantly from the control distribution **[TODO: test, e.g. block-bootstrap confidence intervals of the fire–control difference, with correction for multiple days]**.

**[Planned] Noise-robust lead time.** Because the first significant day depends on sample size and noise, we also report, for each day before $d_c$, the standardised effect size of the fire–control difference (difference of means divided by the pooled control standard deviation). The lead time is then the first day on which the effect size exceeds a common threshold (e.g. 0.5 standard deviations) and stays above it until day $-1$ **[TODO: persistence rule]**, with its uncertainty from the bootstrap described below. The same threshold is used for all variables.

**[Planned] Information beyond the FWI: conditional logistic regression.** Fire cells and their matched controls form matched case–control sets. The added value of SIF/APAR is tested with conditional logistic regression (R, `survival::clogit`):
- base model: FWI + AED + NDVI (daily optical index);
- full model: base model + SIF/APAR.

Each predictor is taken at a common lead (e.g. the trailing mean over days $-7$ to $-1$) **[TODO: leads to test]**. Models are compared with a likelihood-ratio test and the change in AUC (ΔAUC). The AUC of SIF/APAR within FWI danger classes is kept as a complementary analysis.

**[Planned] Dependence between fires.** Fires that burn during the same weather episode or in the same region are not independent. All bootstrap uncertainties are therefore obtained by resampling groups (fire episodes, or region × week blocks) rather than individual fires or cells **[TODO: group definition]**.

**Stratification.** All results will be stratified by vegetation type and by country, and repeated at 0.25° and 0.05°.

**Ignition bias.** Because fire occurrence also reflects human ignition patterns, results are interpreted as conditional on ignition, and this limitation will be discussed.

**Decision criterion.** The proof of concept will be considered positive if SIF/APAR departs from controls earlier than NDVI/EVI and discriminates within FWI classes, at least in shrubland and woodland.

### 2.12. Vegetation classification **[Implemented, provisional]**

**MCD12C1.** Vegetation types are currently derived from MCD12C1 IGBP class percentages (2024) on the 0.05° grid, averaged to 0.25°. Classes are grouped as:
- woodland: classes 1–5, evergreen/deciduous needleleaf and broadleaf, and mixed forests;
- shrubland: classes 6–7, closed and open shrublands;
- grassland: class 10.

Woody savannas (class 8) are left out of these groups, because IGBP classes can confuse Mediterranean shrubland, open woodland and *dehesa*. **[TODO: contrast MCD12C1 with CORINE Land Cover or ESA WorldCover before using it for stratification and control matching.]**

**[Planned] Land cover year.** For stratification and control matching, the land cover of the year before each fire is used. Alternatively, a fixed map from before the study period (2017) is used, so that fire-induced changes do not enter the classification. The 2024 map used for the quality-control points of the sample period is not used in the epoch analysis.

### 2.13. Quality control of the processing chain **[Implemented]**

**Maps.** The chain was checked on the sample period with maps of July–August means of each variable and of the fraction of days with valid SIF/APAR at both scales.

**Series at generic points.** Time series were examined at generic woodland and shrubland points chosen by a fixed rule, deliberately not at fire locations:
- 0.25° cells with ≥ 95% land;
- unburned (MCD64A1, January–September 2025) in the cell and its eight neighbours;
- highest class purity (woodland ≥ 60%, shrubland ≥ 50%);
- at least 2° apart, three per class.

### 2.14. Preregistration **[TODO]**

The fire selection criteria, the epoch rules (Sections 2.8 and 2.11), the lead-time definitions and the decision criterion will be preregistered (OSF or Zenodo) before the epoch series of the selected fires are examined.

### 2.15. Software and reproducibility

**Software.** Gridded processing was implemented in Python 3.11 (xarray, NumPy, netCDF4, earthengine-api, earthaccess); statistical analysis and figures are implemented in R 4.6 (sf, terra, ggplot2). All parameters are stored in a single configuration file. Package versions are locked (conda and renv), and product versions and processing identifiers are recorded in the output metadata. **[TODO: code and data availability statement, Zenodo DOI.]**

---

## References

- Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998. Crop evapotranspiration: guidelines for computing crop water requirements. FAO Irrigation and Drainage Paper 56. FAO, Rome.
- Giglio, L., Boschetti, L., Roy, D.P., Humber, M.L., Justice, C.O., 2018. The Collection 6 MODIS burned area mapping algorithm and product. Remote Sens. Environ. 217, 72–85.
- Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., Moore, R., 2017. Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sens. Environ. 202, 18–27.
- Guanter, L., Bacour, C., Schneider, A., Aben, I., van Kempen, T.A., Maignan, F., Retscher, C., Köhler, P., Frankenberg, C., Joiner, J., Zhang, Y., 2021. The TROPOSIF global sun-induced fluorescence dataset from the Sentinel-5P TROPOMI mission. Earth Syst. Sci. Data 13, 5423–5440. https://doi.org/10.5194/essd-13-5423-2021
- Huete, A., Didan, K., Miura, T., Rodriguez, E.P., Gao, X., Ferreira, L.G., 2002. Overview of the radiometric and biophysical performance of the MODIS vegetation indices. Remote Sens. Environ. 83, 195–213.
- Muñoz-Sabater, J., et al., 2021. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth Syst. Sci. Data 13, 4349–4383.
- Myneni, R.B., et al., 2002. Global products of vegetation leaf area and fraction absorbed PAR from year one of MODIS data. Remote Sens. Environ. 83, 214–231.
- Schaaf, C.B., et al., 2002. First operational BRDF, albedo nadir reflectance products from MODIS. Remote Sens. Environ. 83, 135–148.
- Tang, Z., Miralles, D.G., Guo, Z., Maes, W.H., 2026. Fast response of satellite fluorescence-derived plant physiology to drought stress. Nat. Commun. 17, 2886. https://doi.org/10.1038/s41467-026-70076-0
- Van Wagner, C.E., 1987. Development and structure of the Canadian Forest Fire Weather Index System. Forestry Technical Report 35. Canadian Forestry Service, Ottawa.
- Vitolo, C., Di Giuseppe, F., Barnard, C., et al., 2020. ERA5-based global meteorological wildfire danger maps. Sci. Data 7, 216. https://doi.org/10.1038/s41597-020-0554-z
- **[ref]** CERES SYN1deg Ed4B; MCD12C1 (Friedl and Sulla-Menashe); Ochoa et al. fire maps; EFFIS; FIRMS; LSIB; PAR/shortwave ratio.

**Data DOIs** (to be included in the data availability statement):
- TROPOSIF: via S5P-PAL **[TODO: DOI]**.
- MODIS v061: MCD15A3H, MCD43A4, MCD12C1 and MCD64A1, DOIs of the form 10.5067/MODIS/<product>.061.
- CEMS fire danger: 10.24381/cds.0e89c522.
