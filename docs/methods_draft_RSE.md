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

**fPAR.** fPAR from MCD15A3H (Myneni et al., 2002) was retained only for retrievals of the main (radiative transfer) algorithm (SCF_QC, bits 5–7 of `FparLai_QC`, ≤ 1) and valid range (≤ 100 before scaling).

**[Implemented] Cloud screening.** Pixels flagged in `FparExtra_QC` were additionally removed: internal cloud mask (bit 5), cirrus (bit 4) and cloud shadow (bit 6) (MOD15 C6.1 User Guide, Table 5). In June–September 2025 this removed:

| Vegetation type | Valid 500 m pixels removed |
| --- | --- |
| All land | 8.6% |
| Woodland | 17% (25% in September) |
| Shrubland | 7.5% |
| Cropland | 6.5% |

Because each grid cell aggregates many pixels, the fraction of cell-composites with data hardly changed (≥ 99.3%), and neither did the age of the last valid composite before a potential ignition day (median 3 days, 90th percentile 5 days). The persistence limit is therefore unaffected. At generic woodland points, the filter removed the deepest composite-to-composite fPAR drops (for example, minimum fPAR 0.30 → 0.54 and number of changes > 0.1 between consecutive composites 15 → 9), but residual variability remains.

**MOD09 cloud state.** We also removed pixels whose MOD09 cloud state, inherited in `FparLai_QC` bits 3–4, is "significant clouds" or "mixed". This removed a further 2.2% of pixels (1.9% in woodland) and had almost no effect on the woodland drops (standard deviation between consecutive composites 0.110 → 0.109) **[TODO: keep or drop; negligible effect]**. The residual variability of MCD15A3H in woodland is therefore not explained by flagged clouds.

**[Rule] No temporal smoothing of fPAR.** fPAR is never smoothed to reduce noise, not even with trailing windows. A smoothed fPAR reacts late to structural loss, stays higher than the true value and biases SIF/APAR low, like persistence. Noise is reduced only through quality screening.

**[Implemented] Aerosol flag not used as a mask.** The aerosol bit of MCD15A3H (`FparExtra_QC` bit 3) only distinguishes "no or low" from "average or high" aerosol. Applying it would remove 16% of the retained pixels (30% in woodland; 44% in woodland in August 2025), including many smoke-free summer days, and it is not comparable with VIIRS, which flags high aerosol separately. Its per-cell fraction is stored instead and used as one of the smoke indicators (Section 2.11). Excluding flagged days is a sensitivity test, consistent with the smoke control applied to fires and controls alike. Each 4-day composite was assigned to its central time (start + 1.5 days). Daily values were obtained by linear interpolation between composite centres, bridging gaps of up to 12 days, as in Tang et al. (2026).

**[Planned] VIIRS fPAR as a sensitivity test.** MCD15A3H remains the main fPAR source, because its 4-day compositing matches Tang et al. (2026). As a sensitivity test to the fPAR sensor, and as the basis for a future operational version after the end of MODIS, SIF/APAR is also computed with VIIRS S-NPP fPAR (VNP15A2H, collection 2, 500 m, 8-day composites; GEE asset `NASA/VIIRS/002/VNP15A2H`) as a separate variable.
- **Quality filter:** equivalent to MCD15A3H (main radiative-transfer algorithm, SCF_QC ≤ 1). In VNP15A2H the SCF_QC field occupies bits 0–2 of `FparLai_QC` (VNP15 User Guide v1.1, Table 4), not bits 5–7 as in MCD15A3H.
- **Cloud screening:** the equivalent of the MODIS filter, with VIIRS bit positions (`FparExtra_QC`, User Guide Table 5).
  - Clouds: bits 0–1; "probably cloudy" and "confident cloudy" removed, "probably clear" kept.
  - Cloud shadow: bit 2. Cirrus: bit 3.
  - Effect: 13.5% of valid pixels removed (18.5% in woodland), with no change in the frequency of valid cell-composites.
- **Aerosol flag:** the VIIRS flag is graded, and only "high" (value 3 of bits 4–5) is stored. It flagged 3.2% of retained pixels (7% in August 2025, 14% in woodland). It is not used as a mask, but it serves as a smoke indicator.
- **Units:** the GEE asset is distributed already scaled (fraction 0–1, fill values 2.49–2.55), so no scale factor is applied and the valid range is fPAR ≤ 1.0.
- **Empirical check:** we compared the distribution of SCF_QC and the fraction of valid pixels with MCD15A3H over the study region in June–September 2025, and found them nearly identical (main algorithm without saturation: 93.0% vs 93.6%; valid: 97.3% vs 96.9%).
- **Processing:** composites are assigned to their centre (start + 3.5 days) and interpolated linearly to daily values, bridging gaps of up to 16 days (one missing composite).
- **NOAA-20 and NOAA-21:** NOAA-20 (VJ115A2H) is not in GEE, and NOAA-21 (VJ215A2H) only starts in 2023. Because all VIIRS LAI/FPAR products share the same fixed 8-day calendar, combining platforms would reduce gaps but would not increase the temporal frequency.

**Noise passed on to SIF/APAR (June–September 2025).**
- **fPAR noise:** VNP15A2H injects 3–5 times less day-to-day noise into the fPAR series than MCD15A3H. The median standard deviation of daily changes in log fPAR is 0.008–0.010 for VIIRS and 0.022–0.036 for MODIS, with the largest difference in woodland.
- **SIF/APAR noise:** it is dominated by SIF retrieval noise. With 7-day trailing means, the median relative standard deviation of day-to-day changes in woodland is 0.072 with VIIRS and 0.080 with MODIS at 0.25°, i.e. about 10% lower. It is 0.089 vs 0.091 at 0.05°, and the difference is ≤ 4% in other vegetation types.
- **Interpretation:** part of VIIRS's stability comes from its 8-day compositing, which is itself a form of temporal averaging, with the delay discussed below.

The lower temporal frequency matters most for the days just before ignition. With an 8-day product, the latest composite allowed by the cut-off rule (below) has its centre 4.5–11.5 days before ignition, against 2.5–5.5 days for MCD15A3H. Late structural changes are therefore captured later, or not at all.

**[Planned] Cut-off for fPAR (epoch analysis).** For the epoch analysis, the fPAR series of each fire cell is cut at the masking date (the fire ignition $d_f$ in the main analysis, $d_c$ in the per-cell analysis; Section 2.11) *before* interpolation. Any composite whose compositing period ends on or after that date (start + 3 days ≥ cut-off) is removed, so that no post-fire composite enters the daily values of the pre-fire window. After the last valid composite centre, the last value is carried forward for a limited number of days (persistence of the last available datum). This uses no future information and mimics what an operational system would do; leaving those days missing would remove SIF/APAR precisely on the days closest to the fire. The uncut series is used only for descriptive maps.

**Persistence limit.** The limit is the longest possible distance between the centre of the latest allowed composite and day −1: 4.5 days for MCD15A3H (persistence of 5 days) and 10.5 days for VNP15A2H (11 days). Sensitivity runs use 8 days for VIIRS, and no persistence for both products.

**Direction of the persistence bias.** If canopy structure declines in the days before ignition, a carried-forward fPAR is older and higher than the true value. SIF/APAR is then artificially *low*, in the same direction as the signal sought, and persistence could create a spurious lead time. The **no-persistence runs are therefore the reference for validating any lead time**, for both MODIS and VIIRS. As a diagnostic, we report the difference in the fire–control effect size between the persistence and no-persistence runs as a function of day before ignition. A difference concentrated in the last days before ignition would indicate that persistence drives the result.

**Optical indices.** MCD43C4, used by Tang et al. (2026), is not available in GEE. We therefore aggregated its 500 m counterpart, MCD43A4 nadir BRDF-adjusted reflectance (NBAR; Schaaf et al., 2002), to 0.05°. MCD43C4 is itself derived from this aggregation. We kept reflectances with mandatory quality ≤ 1 (full or magnitude BRDF inversion). NDVI and EVI (Huete et al., 2002) were computed at 0.05° from cell-mean red ($R$), near-infrared (NIR) and blue ($B$) reflectances, using the EVI formulation of Tang et al. (2026):
$$\mathrm{NDVI}=\frac{\mathrm{NIR}-R}{\mathrm{NIR}+R},\qquad
\mathrm{EVI}=2.5\,\frac{\mathrm{NIR}-R}{\mathrm{NIR}+6R-7.5B+1}. \tag{4}$$
EVI values outside [0, 1] were discarded. 0.25° indices were obtained as count-weighted means of the 0.05° indices, mirroring the resampling of indices from 0.05° to 0.25° in Tang et al. (2026).

**[Planned] Temporal footprint of NBAR and a daily optical competitor.** MCD43A4 v061 NBAR for a nominal date is retrieved from 16 days of Terra and Aqua observations, temporally weighted to the ninth day of the period, which is the date of the product. A value dated $t$ therefore uses observations from $t-8$ to $t+7$ (LP DAAC product description **[TODO: cite MCD43 C6.1 user guide]**). This has two consequences for the epoch analysis:
- NBAR dates within about 8 days before a burn date contain post-fire observations; in the epoch analysis they are masked ($t \ge d_c - 8$).
- The window delays and smooths the optical response, which would artificially favour SIF/APAR in a lead-time comparison.

We therefore add a daily, non-BRDF-adjusted NDVI/EVI from MODIS surface reflectance (MOD09GA, Terra, and MYD09GA, Aqua; collection 6.1, in GEE), processed separately for each platform.
- **Screening:** `state_1km` flags for clear sky, no cloud shadow, no cirrus, no internal cloud, not adjacent to cloud, no snow and not high aerosol **[TODO: verify bit definitions in the MOD09 user guide]**; `QC_500m` MODLAND quality ≤ 1; sensor zenith ≤ 40°.
- **Aggregation:** to the same grids.
- **Role:** main optical competitor in the lead-time analysis, with MCD43A4 as a secondary reference.

**Orbital drift.** Both platforms have drifted freely since their last manoeuvres (Terra in February 2020, Aqua in December 2021). Terra's local overpass time moves earlier, to about 09:00 by late 2025, from a nominal 10:30. Aqua's moves later, to about 15:50 by August 2026, from a nominal 13:30. During the 2025 case, Aqua no longer overpasses at the TROPOMI time (~13:30), and illumination geometry changes along the record, which can introduce trends in non-BRDF-adjusted indices. The LOESS detrending (Section 2.8) partly absorbs these trends. The mean overpass time per year over the region will be reported from `SolarZenith`/granule times **[TODO]**, and the platforms' end-of-mission status will be confirmed **[TODO: GEE holds MOD09GA/MYD09GA up to November 2026]**.

In the 2025 sample, NDVI from the two platforms agreed when both observed the same cell on the same day (median Aqua − Terra difference −0.001; interquartile range −0.011 to 0.009), and combining them gave a valid observation on 62% of days per cell (Terra 39%, Aqua 35%). **[TODO: with the full record, repeat the Aqua − Terra NDVI comparison by year to detect effects of orbital drift.]**

**[Planned] Effective temporal window of each product.** The temporal support of each input (Table 2) is reported, because it bounds the lead time that each variable can show.

**Table 2.** Effective temporal window of each input (**[TODO: verify entries marked *]**).

| Variable | Product | Temporal support of one daily value |
| --- | --- | --- |
| SIF | TROPOSIF L2B | single overpass (~13:30 local solar time), day-length corrected |
| fPAR | MCD15A3H | 4-day composite* (best retrieval within the period), linearly interpolated between composite centres |
| fPAR (sensitivity) | VNP15A2H | 8-day composite, linearly interpolated between composite centres |
| NBAR NDVI/EVI | MCD43A4 | 16-day multi-angular retrieval window* |
| Daily NDVI/EVI | MOD09GA/MYD09GA | single overpass; nominal Terra 10:30 / Aqua 13:30, drifted to about 09:00 / 15:30–15:50 by 2025–2026 |
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

**[Planned] Sensitivity to the structural normalisation.** MCD15A3H fPAR is the fraction absorbed by the whole canopy, not by chlorophyll. In Mediterranean summers part of a decrease in SIF/APAR can therefore reflect pigment loss rather than a change in fluorescence yield. As a sensitivity test, we also compute SIF/(PAR × NIRv) and SIF/NIRv, with NIRv = (NDVI − 0.08) × NIR as in Tang et al. (2026), Eq. 2, where 0.08 removes the soil background contribution. NIRv values outside [0, 1] are discarded.

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
1. **Masking before any statistic.** Data are masked from the masking date onwards *before* computing trends, seasonal cycles, filters or any smoothing (Section 2.11). The masking date is the fire's ignition date $d_f$ for the cells of a fire in the main analysis, and the cell's burn date $d_c$ in the per-cell analysis and for the climatology of any cell burned above $f_\mathrm{clim}$. This also keeps the post-fire recovery years of a cell out of its climatology.
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
- no overlap with other fires within the 60-day pre-fire window;
- **[Planned]** a minimum number of valid seasons before the fire in each of its cells, so that the climatology is defined **[TODO: number, e.g. 3 seasons with ≥ x% valid days]**;
- **[Planned]** no cell burned in the five years before the fire (post-fire recovery). This includes the large 2017 fires in Portugal and Galicia; burn history from MCD64A1 (from 2000) and the national maps.

The sample will be balanced across vegetation types (shrubland, woodland, and grassland as a negative control, since cured grasses are dead fuel), countries, regions and years. The selected fires and the criteria each meets will be provided as supplementary material.

### 2.11. Superposed epoch analysis **[Planned]**

**Main alignment: fire ignition date.** In the main analysis, day 0 is the ignition date $d_f$ of each fire. All cells attributed to the fire are masked from $d_f$ (inclusive) onwards, so no datum in the pre-fire window is affected by that fire, either through burning or through its smoke. A cell is attributed to a fire if the burned fraction of the cell (from the perimeter) is at least $f_\mathrm{min}$ **[TODO: threshold at 0.25° and 0.05°]**. The epoch series of each fire is the burned-area-weighted mean over its cells **[TODO: or the cells treated individually with grouping by fire]**, for days $-60$ to $-1$, after applying the masking and trailing-window rules of Section 2.8.

**Burn date per cell.** The burn date of each cell, $d_c$, is:
- the earliest VIIRS 375 m active-fire detection (S-NPP and NOAA-20, nominal and high confidence **[TODO: confidence rule]**) falling inside both the cell and the fire perimeter;
- if no such detection exists, the earliest MCD64A1 burn date in the cell.

It is used for two purposes:
1. **Climatology and controls.** Every cell whose burned fraction exceeds a scale-dependent threshold $f_\mathrm{clim}$ **[TODO: e.g. 10% at 0.25° and 30% at 0.05°]** is masked from $d_c$ onwards when computing climatologies and filters, and is excluded from the control pool. This applies to all fires in the record, not only the selected ones. The threshold prevents a small fire from removing a whole 0.25° cell.
2. **Complementary analysis aligned per cell**, with day 0 at $d_c$. Days between $d_f$ and $d_c$, when the fire is already active nearby, are flagged as smoke- or heat-affected.

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
