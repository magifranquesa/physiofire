# Satellite chlorophyll fluorescence as an early indicator of wildfire danger in the Iberian Peninsula: methods (draft)

*Working draft of the Materials and Methods section, formatted for* Remote Sensing of Environment. *Last updated: 7 November 2026.*

> **Draft status (remove before submission).**
> - Sections 2.1–2.10 describe the analysis that produces the results of the proof of concept (2025 case, 0.05° grid). Section 2.11 lists the sensitivity and robustness analyses (results in the Supplementary Material). Data quality control is documented separately in `docs/supplementary_qc.md` (Supplementary Section S1).
> - **[TODO]** marks decisions or steps still pending; **[ref]** marks references still to be added.
> - All thresholds of the fire sample, the control cells and the lead-time definition were fixed on 7 November 2026, before any vegetation or meteorological time series was extracted at fire locations.

---

## 2. Materials and methods

### 2.1. Rationale and overview

Operational fire danger indices such as the Canadian Fire Weather Index (FWI; Van Wagner, 1987) are driven only by meteorology and do not observe the physiological state of live vegetation. Optical vegetation indices (NDVI, EVI) and live fuel moisture products respond to water stress mainly through changes in canopy structure and pigments, which lag the onset of stress.

Sun-induced chlorophyll fluorescence (SIF) observed from space can be decomposed as
$$\mathrm{SIF} = \mathrm{PAR}\times f_\mathrm{PAR}\times \Phi_F, \tag{1}$$
where PAR is incoming photosynthetically active radiation, $f_\mathrm{PAR}$ the fraction of PAR absorbed by the canopy, and $\Phi_F$ the apparent fluorescence yield (including the escape probability). The ratio
$$\mathrm{SIF/APAR} = \frac{\mathrm{SIF}}{\mathrm{PAR}\times f_\mathrm{PAR}} \tag{2}$$
therefore isolates a physiological signal from radiation and canopy structure. At the global scale, this ratio responds to drought within a few days, earlier than EVI and LAI (Tang et al., 2026).

We test whether anomalies of SIF/APAR depart from normal conditions before large wildfires, earlier than NDVI and EVI, and whether they carry information not contained in the FWI or in the atmospheric evaporative demand (AED). The design is a superposed epoch analysis of manually selected large fires of 2025, each compared with nearby unburned control cells of the same vegetation type, on a 0.05° grid.

### 2.2. Study area and period

The study area is mainland Spain and Portugal (10°W–4.5°E, 35.5°N–44.5°N; Balearic, Canary, Azores and Madeira archipelagos excluded). Grid cells with at least half of their area inside the mainland polygons of the two countries (LSIB, 2017 **[ref]**) are analysed. The region spans a strong aridity gradient, from humid Atlantic forests and heathlands in the northwest (aridity index > 1.5; Zomer et al., 2022) to semi-arid Mediterranean shrublands and croplands in the southeast (< 0.3).

The analysis uses data from May 2018, the start of the TROPOMI SIF record, onwards. The case study is the summer of 2025, when a prolonged heatwave in August coincided with very large wildfires in northwestern Spain and in central and northern Portugal.

All data are on a regular 0.05° latitude–longitude grid (about 4.3 × 5.6 km at 40°N) aligned with the region bounds.

### 2.3. Fire sample

**Perimeters.** Burned-area perimeters were taken from the European Forest Fire Information System (EFFIS; San-Miguel-Ayanz et al., 2012 **[ref]**), which maps fires of about 30 ha or more from MODIS 250 m imagery with a common method for both countries. Perimeters were downloaded on 7 November 2026.

**Ignition date.** Because each epoch is aligned on ignition and all cells of a fire are masked from that date onwards (Section 2.8), a late ignition date is the dangerous error: burning, smoke and early fire damage would then enter the "pre-fire" window as an apparent precursor signal. An early date only removes a few genuine pre-fire days. The ignition date was therefore taken as the **earliest** of four estimates, each restricted to the perimeter and to the window [$\mathrm{FIREDATE} - 30$ d, $\mathrm{FINALDATE} + 1$ d]:
- the EFFIS start date (`FIREDATE`);
- the first VIIRS 375 m active-fire detection (NASA FIRMS archive, S-NPP, NOAA-20 and NOAA-21; presumed vegetation fires, low-confidence detections removed);
- the first MCD64A1 burn date (Collection 6.1, 500 m; Giglio et al., 2018);
- the first VNP64A1 burn date (VIIRS burned area, Collection 2, 500 m) **[ref]**.

Perimeters with VIIRS detections or burn dates inside them between 90 and 30 days before `FIREDATE` were flagged as possible merged perimeters or earlier fires (coherence flag). The 90-day lookback covers the 30-day dating window plus the 60-day epoch window.

**Selection.** A short list was built with all 2025 EFFIS perimeters larger than 2000 ha in the study area (53 perimeters; Table S1). Large fires were preferred because each covers several 0.05° cells. For each perimeter the short list gives the date of each source, the final ignition date, the coherence flag, the fuel-type and CORINE vegetation composition (Section 2.9), and the number of burned cells and of valid control cells. Instead of a manual choice, the sample was defined by a rule fixed before any time series was examined at fire locations: all short-listed fires of the shrubland stratum (Section 2.9) with a valid ignition date, without the coherence flag and with at least three valid control cells (24 fires). Fires whose ignition date was more than 7 days earlier than the EFFIS start date were excluded, because the satellite dates are searched inside the same EFFIS perimeter and cannot rule out a merged perimeter or an earlier fire inside it; without an independent record (e.g. the Spanish or Portuguese fire statistics) the pre-fire window may be misaligned. This rule removed two fires, leaving 22 (15 in Spain and 7 in Portugal; 15 shrubland and 7 heathland; Table S1). No other fire was excluded. The sample, with the exclusions and their reasons, was recorded with its date in the project repository (`data/fires/selected_fires.csv`) before any time series was examined at fire locations. The configuration of the main analysis (fire sample, cells, thresholds and parameters) was fixed before extracting any fire series: commit `a7f894f` (8 November 2026) of the project repository. Woodland fires were not included in the 2025 case, because only two of the five woodland fires had enough controls; woodland is left for the full analysis with more years.

### 2.4. Data

The datasets used are listed in Table 1.

**Table 1.** Datasets used in the main analysis.

| Variable | Product | Native resolution | Access | Reference |
| --- | --- | --- | --- | --- |
| SIF (743–758 nm, day-length corrected) | TROPOSIF L2B v01.00.01 (Sentinel-5P TROPOMI) | ~3.5 × 5.5 km, daily | S5P-PAL | Guanter et al. (2021) |
| fPAR | MODIS MCD15A3H v061 | 500 m, 4-day | Google Earth Engine (GEE) | Myneni et al. (2002) |
| Surface reflectance (red, NIR, blue) | MODIS MOD09GA and MYD09GA v061 | 500 m, daily | GEE | Vermote **[ref]** |
| PAR | ERA5-Land surface downward shortwave radiation | 0.1°, daily | GEE | Muñoz-Sabater et al. (2021) |
| AED (FAO-56 ET0) | ERA5-Land daily aggregates (temperature, dew point, solar radiation, pressure) and hourly wind | 0.1°, daily | GEE | Allen et al. (1998) |
| Fire weather (FWI system) | Computed from ERA5-Land hourly (2 m temperature and dew point, 10 m wind at 12:00 UTC; 24 h precipitation), xclim 1.0.0 | 0.1°, daily | GEE | Van Wagner (1987) |
| FWI (operational reference) | CEMS fire danger indices, historical reanalysis **[TODO: version]** | 0.25°, daily | Copernicus EWDS | Vitolo et al. (2020) |
| Fire perimeters | EFFIS burnt areas | vector (MODIS 250 m) | EFFIS | **[ref]** |
| Active fires | NASA FIRMS VIIRS 375 m (S-NPP, NOAA-20, NOAA-21) | point | FIRMS | Schroeder et al. (2014) **[ref]** |
| Burned area | MODIS MCD64A1 v061; VIIRS VNP64A1 v002 | 500 m, monthly | GEE | Giglio et al. (2018); **[ref]** |
| Burned area (Spain) | ESFire30, Landsat 30 m annual perimeters, 1985–2025 | vector (30 m) | Zenodo, 10.5281/zenodo.20257001 | Ochoa et al. **[ref]** |
| Fuel types | FirEUrisk European fuel map v2.0, first-level types (circa 2019) | 1 km | e-cienciaDatos, 10.21950/YABYCN | Aragoneses et al. (2023) |
| Land cover (support) | CORINE Land Cover 2018 v20 | 100 m | GEE | EEA **[ref]** |
| Aridity index | Global Aridity Index v3.1 (P/ET0, 1970–2000) | 30″ | figshare, 10.6084/m9.figshare.7504448.v7 | Zomer et al. (2022) |
| Elevation | SRTM v4.1 (CGIAR-CSI) | 90 m | GEE | Jarvis et al. (2008) **[ref]** |

### 2.5. SIF/APAR

**SIF.** We used the day-length corrected SIF retrieved in the 743–758 nm window (`SIF_Corr_743`) of the TROPOSIF L2B product (Guanter et al., 2021), which contains all retrievals with quality value > 0.5. Retrievals with an effective cloud fraction > 0.5, and pixels flagged as snow/ice or barren in the product's land cover mask, were removed. Each retrieval was assigned to the 0.05° cells it overlaps, with weights proportional to the overlapping area, approximated by dividing the pixel into 4 × 4 sub-points placed by bilinear interpolation between its corners. For each cell and day,
$$\overline{\mathrm{SIF}}_j=\frac{\sum_i w_{ij}\,\mathrm{SIF}_i}{\sum_i w_{ij}}, \tag{3}$$
where $w_{ij}$ is the fraction of pixel $i$ overlapping cell $j$.

**fPAR.** MCD15A3H fPAR (Myneni et al., 2002) was aggregated in GEE (Gorelick et al., 2017) to the 0.05° grid as the area-weighted mean of valid 500 m pixels. Only retrievals of the main radiative-transfer algorithm were kept (SCF_QC ≤ 1), and pixels flagged as cloudy, cloud shadow or cirrus (`FparExtra_QC`), or with a MOD09 cloud state of "significant clouds" or "mixed" (`FparLai_QC`), were removed. fPAR was never smoothed in time, because a smoothed fPAR reacts late to structural loss and biases SIF/APAR low. Each 4-day composite was assigned to its central date and daily values were obtained by linear interpolation between composite centres, bridging gaps of up to 12 days.

**PAR.** Daily PAR was computed as
$$\mathrm{PAR}=f\times\mathrm{SW}_\downarrow, \tag{4}$$
where $\mathrm{SW}_\downarrow$ is the ERA5-Land daily mean surface downward shortwave radiation, bilinearly resampled to 0.05°, and $f = 0.48$ is a typical PAR/shortwave energy ratio **[ref]**. ERA5-Land provides a homogeneous record over the whole period and the low latency needed for an operational application. A constant $f$ rescales SIF/APAR uniformly and does not alter its anomalies after standardisation (Section 2.8).

**Ratio.** SIF/APAR (Eq. 2) was computed daily for each cell. Values were not clipped at pooled percentiles, which could remove the extreme low values of a record-breaking season such as 2025. Instead, isolated spikes were removed with a per-cell Hampel filter: a value is removed if its residual to the running median of the cell's own series over ±3 days exceeds six times the cell's robust noise scale (1.4826 × median absolute residual). A persistent anomaly also shifts the running median and is therefore retained. The same filter is applied to NDVI and EVI, but not to FWI and AED, which are meteorological fields without retrieval noise and whose extreme days are genuine. Before the spike filter, SIF/APAR was set to missing on days with fPAR < 0.15, PAR < 40 W m⁻² or a TROPOSIF coverage of the cell below 0.1 equivalent full pixels. These thresholds, and the spike-filter factor of six, were derived before any fire or control series was extracted, on 1,462 unburned shrubland and heathland cells outside the analysis (no burned area in 2013–2026 and more than 10 km from any EFFIS perimeter; 3.0 million cell-days): the relative noise of SIF/APAR (absolute residual to the cell's running median, divided by the cell's median) increases gradually towards low fPAR, PAR and coverage, and each threshold is the value below which the noise exceeds twice that of the better-conditioned half of the data. They remove 0.7%, 0% and 1.3% of the summer cell-days, respectively, and the spike filter a further 0.5%. Because low fPAR may itself be part of a pre-fire signal, the analysis is repeated without the fPAR threshold (R20).

### 2.6. Optical indices

NDVI and EVI (Huete et al., 2002) were computed from daily surface reflectance of MOD09GA (Terra) and MYD09GA (Aqua), processed separately for each platform:
$$\mathrm{NDVI}=\frac{\mathrm{NIR}-R}{\mathrm{NIR}+R},\qquad
\mathrm{EVI}=2.5\,\frac{\mathrm{NIR}-R}{\mathrm{NIR}+6R-7.5B+1}. \tag{5}$$
Daily, non-BRDF-adjusted reflectance was used rather than the 16-day NBAR product (MCD43A4), whose retrieval window of about ±8 days would delay the optical response and favour SIF/APAR in a lead-time comparison. 500 m pixels were kept if flagged clear, without cloud shadow, cirrus, adjacency to clouds, snow or high aerosol (`state_1km`), with MODLAND quality ≤ 1 and sensor zenith angle ≤ 40°. Pixels with a negative reflectance in any band were discarded, and whole images with more than 10% negative pixels were rejected (Supplementary Section S1). Reflectances were aggregated to 0.05° as area-weighted means before computing the indices. EVI values outside [0, 1] were discarded. The optical reference of the main analysis combines both platforms: on each day, the mean of the Terra and Aqua indices when both are valid and the valid one otherwise, which gives about one value every 1.6 days **[TODO: compute the mean revisit over the sample cells]**. NBAR is a sensitivity analysis (R14). Terra and Aqua separately were planned as a sensitivity analysis but discarded, because a single platform rarely provides the half of valid days required by the 15-day trailing mean (valid on 10–44% of the days in May–August 2025 at the fire and control cells). The combined index is itself limited early in the window: in May and the first half of June 2025 it was valid on only 14–45% of the days, against 64–78% in July and early August.

### 2.7. Atmospheric evaporative demand and fire weather

**AED.** AED was computed as FAO-56 Penman–Monteith reference evapotranspiration (ET0; Allen et al., 1998) from ERA5-Land on its native 0.1° grid, the same source and grid as the FWI and PAR. Daily (UTC) inputs were the maximum and minimum 2 m temperature, the mean 2 m dew point (actual vapour pressure), the surface solar radiation, the mean surface pressure (psychrometric constant and, through the barometric formula, elevation for the clear-sky radiation) and the mean 10 m wind speed of the 24 hourly values, reduced to 2 m with the FAO-56 logarithmic profile (the daily mean wind components would underestimate the speed). Net radiation was computed from the solar radiation with an albedo of 0.23 and the FAO-56 net longwave radiation; the soil heat flux was neglected at the daily scale. The implementation reproduces FAO-56 Examples 8 and 18. AED was preferred over vapour pressure deficit because it integrates temperature, humidity, wind and radiation. Each 0.05° cell takes the value of the 0.1° cell that contains it. GLEAM v4.3a potential evaporation (Miralles et al., 2025; 0.1°, until 2024) is used as a check for 2018–2024 **[TODO]**.

**FWI.** The FWI of the main analysis was computed with the Canadian Fire Weather Index System (Van Wagner, 1987) from ERA5-Land on its native 0.1° grid, from noon values of temperature, relative humidity (from the 2 m dew point, Magnus formula) and 10 m wind speed and the 24 h precipitation ending at noon. Noon was taken as 12:00 UTC, within 40 min of local solar noon over the whole region (11:42 UTC at 4.5°E, 12:40 UTC at 10°W); the 24 h precipitation is the sum of the hourly ERA5-Land amounts from 13:00 UTC of the previous day to 12:00 UTC. The system was run continuously from 1 January 2017, 16 months before the TROPOMI record, with the standard start-up codes (FFMC 85, DMC 6, DC 15), without fire-season start-up and shutdown and without overwintering of the Drought Code, using the gridded implementation of xclim 1.0.0 (`xclim.compute.fire.cffwis_indices`) with the latitude day-length adjustment. On a sample of 34 cells over January–August 2025, xclim reproduced the reference R implementation of the Canadian Forest Service (package cffdrs 1.9.2) to storage precision for DMC, DC and BUI. FFMC, ISI and FWI differ slightly because xclim keeps the coefficient 147.2 of the original FFMC equations (Van Wagner, 1987) in the conversion between FFMC and fine fuel moisture content, whereas cffdrs uses 147.27723 (= 250 × 59.5/101) from the revised official code (Wang et al., 2015). The resulting FWI differences are at most 1.7 (99th percentile 0.66); with cffdrs set to 147.2 the two implementations agree to within 10⁻⁴ (Supplementary Section S1.10). xclim was used unmodified. Each 0.05° cell takes the value of the ERA5-Land cell that contains it (every 0.05° cell lies inside a single 0.1° cell). ERA5-Land downscales temperature and humidity with elevation, but its precipitation is the ERA5 precipitation interpolated to 0.1°, so the precipitation input (and the moisture codes that depend on it) has no real resolution below ~30 km; nearby burned and control cells therefore share much of their rainfall history **[discussion: limitation]**. The operational CEMS fire danger reanalysis (Vitolo et al., 2020; ERA5, 0.25°) was not used in the main analysis: with controls 10–50 km from the perimeter, 7–16% of the control cells of the 24 fires share a 0.25° FWI cell with a burned cell of the same fire (depending on whether the cell centre or any overlap is counted), and none share a 0.1° cell. Shared cells, and the smoothness of the 0.25° field, reduce the burned–control FWI difference by construction and would favour SIF/APAR. The CEMS FWI is kept as the operational reference in a sensitivity analysis (R17). FWI danger classes follow EFFIS **[TODO: class thresholds]**.

### 2.8. Anomalies

All series are masked from the masking date (the ignition date of the fire, inclusive, for its burned and control cells) **before** any statistic is computed: spike filter, climatology, trailing means and standardisation. No datum on or after the ignition date, and no fPAR composite whose compositing period ends on or after that date, enters the pre-fire window. After the last fPAR composite allowed by this rule, its value is carried forward for at most 5 days, which covers day −1 in the worst case.

**Anomalies.** For each cell and variable, the daily anomaly is the difference between the value and the median of the same cell's values within ±15 days of the same day of year, pooled over all years of the masked record (May 2018 to the day before ignition). The day-of-year median does not require a trend model, is robust to outliers in a short record of about seven seasons, and is not distorted at the end of the series, where the evaluated window lies (Supplementary Section S1.6).

**Trailing means.** Anomalies are averaged over a 15-day trailing window ending on the evaluated day (at least 8 valid days). Only trailing windows are used, so no smoothing brings post-ignition data into the pre-fire window. No spatial smoothing is applied.

**Standardisation.** The trailing-mean anomaly of each cell is divided by its standard deviation over the masked record before the epoch window (days before day −60), so that all variables are expressed in standard deviation (SD) units.

### 2.9. Burned and control cells

**Vegetation.** Vegetation was described by the FirEUrisk European fuel map (Aragoneses et al., 2023), a 1 km map of first-level fuel types built from the Copernicus Global Land Cover 2019, ESA CCI Land Cover 2020 and CORINE 2018 maps and bioclimatic models of shrub and grass fuel depth. Fuel types describe the vegetation as fuel (canopy cover, fuel-bed depth), which is closer to the question than land-use classes. The map is in an equal-area projection (ETRS89-LAEA); each 1 km pixel was split into 4 × 4 sub-points, which were assigned to the 0.05° cell containing them, giving the area fraction of each fuel type per cell. The 20 mapped types were grouped into six classes plus nonfuel: closed forest (canopy cover ≥ 70%: broadleaf deciduous, needleleaf evergreen and mixed; types 1122, 1212, 1302), open forest (canopy cover 15–70%; 1121, 1211, 1301), shrubland (fuel depth classes 21–23), heathland and wet land (wet and peat/semi-peat land with trees, shrubs or grasses; 51–53), grassland (31–33), cropland (herbaceous and woody; 41, 42) and nonfuel (urban, water, bare soil and sparse vegetation; 61, 62, 7). Broadleaf evergreen forest (holm and cork oak) is not a separate type in the European product. The dominant class of a cell is the class with the largest fraction. Results are stratified into woodland (closed and open forest), shrubland (shrubland and heathland) and grassland; grassland is a negative control, because cured grasses are dead fuel whose physiology carries no information. CORINE Land Cover 2018 (100 m), aggregated in GEE to group fractions per 0.05° cell (forest types 311–313, natural grassland 321, heathland 322, sclerophyllous vegetation 323, transitional woodland-shrub 324, agricultural areas, agro-forestry and other groups), is reported alongside as support (Table S1) and used as an alternative classification in a sensitivity analysis (R18).

**Burned cells.** The burned cells of a fire are the 0.05° cells of which at least 25% lies inside its perimeter. Cells of which at least 25% burned in any of the five years before the fire (MCD64A1, VNP64A1, EFFIS perimeters or, in Spain, ESFire30) were removed, because post-fire recovery would dominate their pre-fire anomalies; a fire was kept if it retained burned cells and excluded otherwise. This rule removed 7 of 140 burned cells (in four fires) and no fire. The fire's vegetation is the dominant class with the largest burned-fraction-weighted share among its burned cells.

**Control cells.** Three to five control cells per fire were selected once, for all variables. Each control must:
- lie between 10 km and 50 km from the perimeter: the whole cell at least 10 km away, and its centre within 50 km. The immediate strip around the fire is never used, because the position of the fire edge depends on suppression, relief and firebreaks, not only on the state of the vegetation;
- be unburned in every year from 2017 to the fire year: no burned area in EFFIS perimeters, in the MCD64A1 or VNP64A1 yearly burn history, or, in Spain, in the ESFire30 Landsat perimeters;
- have the same dominant fuel class as the fire;
- have an aridity index within ±15% (relative), and a mean elevation (SRTM 90 m) within ±200 m, of the burned-fraction-weighted mean of the burned cells. A relative aridity tolerance was preferred to an absolute one, which would be strict in the humid northwest (aridity index 1.5–2) and loose in semi-arid areas.

Valid candidates are ranked by the sum of their elevation and aridity differences, each divided by its tolerance, and the five best are kept. Fires with fewer than three valid controls are excluded and the criteria are not relaxed. Of the 53 short-listed perimeters, 37 obtained at least three controls (Table S1).

### 2.10. Superposed epoch analysis

**Fire–control differences.** For each fire, variable and day $t$ from −60 to −1 relative to ignition, the fire–control difference is
$$D_f(t) = \sum_{c \in B_f} \frac{a_c}{\sum_{c' \in B_f} a_{c'}}\, z_c(t) - \frac{1}{|C_f|}\sum_{c \in C_f} z_c(t), \tag{6}$$
where $z_c$ is the standardised anomaly of cell $c$, $B_f$ and $C_f$ are the burned and control cells of fire $f$, and $a_c$ is the burned fraction of cell $c$.

**Effect size.** Across fires, we report for each day the mean difference $\bar D(t)$ (SD units), its 95% confidence interval from a bootstrap over fires (2000 resamples, fixed seed) and the paired effect size $d_z(t) = \bar D(t)/s_D(t)$, where $s_D$ is the standard deviation of $D_f(t)$ across fires. The mean standardised anomaly of the burned cells alone is reported in the same way.

**Lead time.** The lead time of a variable is the earliest day from which the mean difference stays at least 0.5 SD in the expected direction, with a confidence interval excluding zero, on every day up to day −1. The expected direction is negative for SIF/APAR, NDVI and EVI, and positive for FWI and AED. The same threshold is used for all variables. Because carrying the last fPAR composite forward biases SIF/APAR low if canopy structure declines before ignition, a lead time of SIF/APAR is accepted only if it is also found without fPAR persistence.

**Information beyond the FWI.** In this proof of concept, the information that SIF/APAR adds to the FWI is assessed descriptively. The burned–control differences of the FWI and of SIF/APAR (Eq. 6, both standardised) are shown together in the same figure for days −60 to −1. If the FWI differs little between burned and control cells while SIF/APAR does, SIF/APAR carries information on the pre-fire state that the fire weather does not. A formal test (discrimination of burned and control cells by SIF/APAR within FWI danger classes, e.g. the area under the ROC curve per class) requires more fires and is left for the full analysis.

**Strata and decision criterion.** All results are given for all fires, by vegetation class (shrubland and heathland) and by country. The 2025 case is restricted to the shrubland stratum (Section 2.3). It is considered positive if SIF/APAR departs from the controls earlier than NDVI and EVI, and SIF/APAR differs between burned and control cells on days when the FWI difference is small; woodland is evaluated in the full analysis.

**Ignition bias.** Fire occurrence also reflects human ignition patterns. Because fires were selected among those that did burn and are compared with matched unburned cells, results describe the pre-fire state of vegetation conditional on ignition, not the probability of ignition.

### 2.11. Sensitivity and robustness analyses

The analyses in Table 2 test whether the results depend on choices of the main analysis. Their results are given in the Supplementary Material **[TODO: section numbers]**.

**Table 2.** Sensitivity and robustness analyses.

| # | Analysis | What changes | Why |
| --- | --- | --- | --- |
| R1 | No fPAR persistence | fPAR missing after the last composite allowed by the cut-off | Persistence biases SIF/APAR low before ignition, in the direction of the signal; this run validates any SIF/APAR lead time |
| R2 | VIIRS fPAR | VNP15A2H (8-day; persistence of 11 days, 8 days and none) instead of MCD15A3H | Sensor dependence of fPAR; continuity after the end of MODIS |
| R3 | 7-day trailing window | 7 instead of 15 days | The window length limits the attainable lead time |
| R4 | LOESS anomalies | Long-term LOESS trend (span 40% of the record, fitted only on data before day −60 and on the deseasonalised series) plus mean seasonal cycle, instead of the day-of-year median | Dependence on the anomaly definition |
| R5 | 0.25° grid | Burned and control cells on a 0.25° grid | Lower SIF retrieval noise; scale dependence. Requires a different control design, because nearly all 0.25° cells of NW Iberia burned after 2017 |
| R6 | 3 × 3 spatial smoothing at 0.05° | Spatial mean after masking each cell from its own burn date | Noise reduction at the cost of resolution |
| R7 | Cell-aligned epoch | Day 0 = burn date of each cell (first VIIRS detection in the cell, else MCD64A1); days between ignition and the cell's burn date flagged | Dependence on the alignment; fire spread over several days |
| R8 | Smoke days excluded | Days flagged by the fPAR aerosol bit, the TROPOMI UV aerosol index or MODIS AOD removed in burned and control cells | Smoke can lower SIF and reflectance before a cell burns |
| R9 | Pooled 1–99 percentile filter | Pooled percentile filter on SIF/APAR instead of the per-cell spike filter; fraction of pre-fire data removed by day relative to ignition | The pooled filter can remove extreme stress |
| R10 | Structural normalisation | SIF/(PAR × NIRv) and SIF/NIRv | fPAR includes non-photosynthetic material; pigment loss |
| R11 | PAR at overpass time | ERA5-Land hourly PAR at ~13:30 local solar time | SIF is an instantaneous retrieval |
| R12 | CERES PAR | CERES SYN1deg Ed4B surface PAR, with a test for the April 2022 change of inputs | Independent PAR source |
| R13 | Inverse-variance SIF weighting | Weights $w_{ij}/\sigma_i^2$ in Eq. (3) | Uneven retrieval noise |
| R14 | NBAR indices | NDVI/EVI from MCD43A4 NBAR, masked from day −8 | BRDF-adjusted reference with a 16-day window |
| ~~R15~~ | ~~Single platform~~ | Discarded (8 November 2026): with a single platform, the 15-day trailing mean rarely reaches the required half of valid days (Terra or Aqua valid on 10–44% of the days in May–August 2025 at the fire and control cells; 4–21% of the trailing means of Terra were valid) | — |
| R16 | High-confidence VIIRS | Ignition dates from high-confidence detections only | Sensitivity of the ignition date to the confidence class |
| R17 | CEMS FWI | Operational CEMS FWI (ERA5, 0.25°) instead of the FWI computed from ERA5-Land at 0.1° | Operational reference; 7–16% of controls share a 0.25° cell with burned cells, which attenuates the FWI difference |
| R18 | CORINE vegetation | Dominant CORINE 2018 group instead of the FirEUrisk fuel class for control matching and strata | Dependence on the vegetation classification |
| R19 | Single-cell fires removed | Fires with a single burned cell excluded (3 of 22) | The burned–control difference of these fires rests on one cell |
| R20 | No fPAR validity threshold | SIF/APAR without the minimum-fPAR screening | Low fPAR may be part of the pre-fire signal; the screening must not create or hide a lead time |

### 2.12. Software and reproducibility

Gridded processing was implemented in Python 3.11 (xarray, NumPy, statsmodels, earthengine-api), and the fire table, epoch statistics and figures in R 4.6 (sf, terra, dplyr, ggplot2). All parameters are stored in a single configuration file, random seeds are fixed, package versions are locked (conda and renv), and product versions are recorded in the output metadata. The absence of post-ignition leakage and the recovery of an injected pre-fire signal were verified with synthetic data (Supplementary Section S1.6). **[TODO: code and data availability statement, Zenodo DOI.]**

---

## References

- Aragoneses, E., García, M., Salis, M., Ribeiro, L.M., Chuvieco, E., 2023. Classification and mapping of European fuels using a hierarchical, multipurpose fuel classification system. Earth Syst. Sci. Data 15, 1287–1315. https://doi.org/10.5194/essd-15-1287-2023 (data: v2.0, https://doi.org/10.21950/YABYCN)
- Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998. Crop evapotranspiration: guidelines for computing crop water requirements. FAO Irrigation and Drainage Paper 56. FAO, Rome.
- Giglio, L., Boschetti, L., Roy, D.P., Humber, M.L., Justice, C.O., 2018. The Collection 6 MODIS burned area mapping algorithm and product. Remote Sens. Environ. 217, 72–85.
- Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., Moore, R., 2017. Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sens. Environ. 202, 18–27.
- Guanter, L., Bacour, C., Schneider, A., Aben, I., van Kempen, T.A., Maignan, F., Retscher, C., Köhler, P., Frankenberg, C., Joiner, J., Zhang, Y., 2021. The TROPOSIF global sun-induced fluorescence dataset from the Sentinel-5P TROPOMI mission. Earth Syst. Sci. Data 13, 5423–5440. https://doi.org/10.5194/essd-13-5423-2021
- Huete, A., Didan, K., Miura, T., Rodriguez, E.P., Gao, X., Ferreira, L.G., 2002. Overview of the radiometric and biophysical performance of the MODIS vegetation indices. Remote Sens. Environ. 83, 195–213.
- Miralles, D.G., et al., 2025. GLEAM4: global land evaporation and soil moisture dataset at 0.1° resolution from 1980 to near present. Sci. Data 12, 416. https://doi.org/10.1038/s41597-025-04610-y **[ref: verify title]**
- Muñoz-Sabater, J., et al., 2021. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth Syst. Sci. Data 13, 4349–4383.
- Myneni, R.B., et al., 2002. Global products of vegetation leaf area and fraction absorbed PAR from year one of MODIS data. Remote Sens. Environ. 83, 214–231.
- Tang, Z., Miralles, D.G., Guo, Z., Maes, W.H., 2026. Fast response of satellite fluorescence-derived plant physiology to drought stress. Nat. Commun. 17, 2886. https://doi.org/10.1038/s41467-026-70076-0
- Wang, X., Wotton, B.M., Cantin, A.S., Parisien, M.-A., Anderson, K., Moore, B., Flannigan, M.D., 2017. cffdrs: an R package for the Canadian Forest Fire Danger Rating System. Ecol. Process. 6, 5. https://doi.org/10.1186/s13717-017-0070-z
- Wang, Y., Anderson, K.R., Suddaby, R.M., 2015. Updated source code for calculating fire danger indices in the Canadian Forest Fire Weather Index System. Information Report NOR-X-424. Canadian Forest Service, Edmonton. **[ref: verify]**
- Van Wagner, C.E., 1987. Development and structure of the Canadian Forest Fire Weather Index System. Forestry Technical Report 35. Canadian Forestry Service, Ottawa.
- Vitolo, C., Di Giuseppe, F., Barnard, C., et al., 2020. ERA5-based global meteorological wildfire danger maps. Sci. Data 7, 216. https://doi.org/10.1038/s41597-020-0554-z
- Zomer, R.J., Xu, J., Trabucco, A., 2022. Version 3 of the Global Aridity Index and Potential Evapotranspiration Database. Sci. Data 9, 409. https://doi.org/10.1038/s41597-022-01493-1 (data: v3.1, https://doi.org/10.6084/m9.figshare.7504448.v7)
- **[ref]** EFFIS; FIRMS VIIRS active fires; VNP64A1; ESFire30 (Ochoa et al.); CORINE Land Cover 2018; SRTM (CGIAR-CSI); MOD09GA/MYD09GA; LSIB; PAR/shortwave ratio; CERES SYN1deg Ed4B (sensitivity).

**Data DOIs** (to be included in the data availability statement):
- TROPOSIF: via S5P-PAL **[TODO: DOI]**.
- MODIS v061: MCD15A3H, MOD09GA, MYD09GA and MCD64A1, DOIs of the form 10.5067/MODIS/<product>.061.
- CEMS fire danger: 10.24381/cds.0e89c522.
- ESFire30: 10.5281/zenodo.20257001.
- Global Aridity Index v3.1: 10.6084/m9.figshare.7504448.v7.
- FirEUrisk European fuel map v2.0: 10.21950/YABYCN.
