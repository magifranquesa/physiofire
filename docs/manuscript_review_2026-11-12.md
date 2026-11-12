# Revisión del manuscrito antes de enviarlo a los coautores (12 de noviembre de 2026)

Revisados: `docs/manuscript/manuscript.docx` (17:13) y `Supplementary_material.docx` (18:47), más `autores.docx`. Las versiones originales no se han tocado. Las correcciones están en dos copias con cambios controlados (autor "Claude"):

- `docs/manuscript/manuscript_rev_2026-11-12.docx`
- `docs/manuscript/Supplementary_material_rev_2026-11-12.docx`

Comprobaciones hechas: implementación del procesado de SIF frente al Product User Manual de TROPOSIF (PUM v1.0, S5P-PAL, octubre de 2022) y a los atributos de los ficheros descargados; ≈110 cifras del texto, tablas y suplemento frente a los ficheros de resultados (`docs/results_*.md`, `docs/closeout_checks.md`, `data/processed/**`); las 10 ecuaciones (OMML); citas frente a la lista de referencias y metadatos de los 35 DOI (doi.org, CSL JSON); versión de las 12 figuras insertadas frente a las cuatro últimas versiones en git; coherencia de los métodos con el código.

## 1. Veredicto

El manuscrito es coherente con el código y con los resultados en la gran mayoría de las afirmaciones. Antes de enviarlo había que corregir cuatro cifras, precisar la descripción del producto SIF, completar el cribado de MOD09GA y arreglar varias erratas. Todo eso está aplicado en las copias. Quedan pendientes del investigador los marcadores sin rellenar (sección 7).

## 2. Procesado de SIF frente al PUM

Código: `src/physiofire/download/troposif.py`, `src/physiofire/preprocess/troposif_grid.py`, sección `sif` de `config/config.yaml`.

**Corregido en la copia:**
- "SIF at 743 nm" (Tabla 1 y sección 2.2). Según el PUM (§3.1) y el atributo del fichero (`standard_name = "daylength-corr SIF@740 743-758 nm fitting window"`), la SIF se estima a **740 nm** en la **ventana de ajuste 743–758 nm**; "743" es el nombre de la ventana. La misma etiqueta imprecisa está en `config.yaml` (`sif.wavelength_nm: 743`) y en CLAUDE.md (internas, sin corregir).
- Añadido que el L2B solo contiene retrievals con `qa_value > 0.5` (PUM §3.1.1 y §4.2.3), lo que excluye VZA > 60°, SZA > 70°, radiancias fuera de rango y χ² anómalo.
- Añadido que los valores negativos de SIF se conservan (13,5 % de los sondeos en una muestra de julio de 2025; el PUM admite SIF en [−10, 10]).
- "cloud fraction" → "effective cloud fraction" (es la fracción radiométrica efectiva del producto de nubes L2, PUM §4.1.3); máscara de cobertura "MCD12C1 2018".

**Verificado y correcto:** `SIF_Corr_743` es la corrección por duración del día (`DayLength_fac`); unidades mW m⁻² sr⁻¹ nm⁻¹; fracción de nubes ≤ 0,5 conservada; `LC_MASK` con clases 15 (nieve/hielo) y 16 (suelo desnudo) excluidas; pesos de solape con los cuatro vértices (`latitude_bounds`, `longitude_bounds`) y 4 × 4 subpuntos; procesador 01.00.01 y colección 03 en los atributos de los 3104 ficheros diarios (1 de mayo de 2018 a 3 de noviembre de 2026; los 5 días que faltan son de octubre de 2026); cuando hay dos procesados del mismo día se toma el más reciente; cambio de tamaño de píxel en agosto de 2019. `SIF_ERROR_743` solo entra en `sif_sem`, que no se usa en ningún análisis. En la muestra de ficheros no hay sondeos de clase 15 ni de agua (el L2B ya es solo tierra); la máscara solo quita el 0,3 %.

## 3. Cifras corregidas

| Dónde | Decía | Fuente | Ahora |
| --- | --- | --- | --- |
| 3.2, correlaciones máximas medianas | about 0.35 / 0.65 | `data/processed/drought_q1/summary_scale_lag.csv` (celdas significativas, matorral); `results_q1_drought.md:83` | **0.39 / 0.68** |
| 3.2, desfases a SPEI-3 | 0, 1 and 10 days | mismo fichero, `lag_spei090_median`; `results_q1_drought.md:106` | **0, 1 and 11 days** |
| 3.3, sensibilidad frente al NDVI | +0.24 [+0.12, +0.36] | `hypotheses_q1b.csv`, `mean_score` = 0,23498 | **+0.23** (`results_q1b.md` imprime +0,24 por redondeo) |
| Discusión, primavera húmeda | "Spring was wet in most of the selected fires (SPEI-3 of 0 to +2 in April–May, highest in the Portuguese fires)" | no existía SPEI-3 para los 22 incendios; calculado ahora (sección 9) | frase nueva (sección 9) |

Todo lo demás coincide: muestra de incendios (53 candidatos; 8 + 5 + 4 + 7 + 2 + 5 exclusiones; 22 = 15 + 7; 19 en agosto), 133/108 celdas, 6476/5331 celdas-día, antelaciones e intervalos, diferencias de los últimos 15 días, 6771/20/6751 celdas, 4169 (96 %), Tabla 2 completa, 27 %, AED (−0,28; 11 días; 0,86; −0,22 → −0,13; 0,26 → 0,21), 228/141/145 eventos, pares, signos e intervalos, estacional y *post hoc*, Texto S1 (cffdrs, CEMS, umbrales), Tabla S2 y anomalías NIR por año.

## 4. Métodos frente al código

- **Cribado de MOD09GA (2.2), completado en la copia:** el código (`gee.py:224-246`) elimina también sombra de nube, cirros, adyacencia a nube, nieve, aerosol alto, agua y calidad MODLAND > 1, y rechaza la imagen entera si > 10 % de los píxeles cribados son negativos (lo que excluyó el 29 de marzo de 2025 citado en 2.1).
- **Texto S1.2, corregido:** el ruido se divide por la mediana de los valores **positivos** de SIF/APAR de la celda (`screening_thresholds.py:102`).
- Verificado: filtro de picos (ventana de 7 días, ≥ 3 válidos, 1,4826·MAD sobre toda la serie, k = 6); centro del compuesto de fPAR (+1,5 d = 12:00 del segundo día); hueco máximo de 12 días e interpolación a las 12:00; PAR = J m⁻²/86 400 × 0,48, bilineal; FWI (Magnus, viento × 3,6, códigos iniciales 85/6/15, desde el 1 de enero de 2017, sin invernada); FWI, AED y SPEI por celda contenedora de 0,1°; ventana de ignición [EFFIS − 30, fin + 1]; coherencia [−90, −30); regla de 7 días; tramos y factor 2 del cribado (README del run); 1462 celdas.
- Ecuaciones (1)–(10): coherentes con el texto (en (7) las dos ventanas son de 30 días; en (8) el día candidato entra en el intervalo; en (9) la censura a ±90).

## 5. Referencias

- Todas las citas tienen entrada y todas las entradas se citan (manuscrito: 38; suplemento: 6).
- Los 35 DOI resuelven y autor, año, revista, volumen y páginas coinciden. Corregidas en la copia tres entradas incompletas: Sirca et al. 2018 (563–571), Chuvieco et al. 2023 (*Fire* 6, 215) y Hu y Shi 2026 (*Front. Plant Sci.* 17, 1974112).
- **Aviso:** la bibliografía es un campo de Zotero. Si se actualiza el campo, esas tres correcciones se perderán; lo definitivo es corregir las páginas o el número de artículo en la biblioteca de Zotero.
- Chuvieco et al. 2026 (actas de Coimbra) no tiene DOI; no verificable en línea.

## 6. Figuras insertadas

Figs. 1, 3, 4, 5 y S1–S7 corresponden a la versión actual en git. En la Fig. 2 no se distingue la versión actual (`ec775d1`) de la anterior a quitar y reponer la línea de cero, porque solo difieren en el orden de capas; lo que se ve coincide con el pie. Word ha recomprimido las imágenes a ≈1430 px de ancho (≈200 ppp a 18 cm): vale para los coautores, pero al enviar a la revista habrá que subir los PNG de 300 ppp de `figures/manuscript/` y `figures/supplement/`.

## 7. Erratas y pendientes

Corregidas en las copias: paréntesis de cierre en la Tabla 1 (fila "Fire perimeters"); fila CEMS de la Tabla S3 (texto duplicado y "page:https"); línea "Contents" del suplemento (faltaba la Tabla S3).

Pendientes del investigador:
- marcadores sin rellenar: [repository URL], [Zenodo DOI] y [TODO] en contribuciones y agradecimientos;
- `autores.docx`: doble espacio en "Geography and the  Environment";
- en el suplemento hay dos líneas "Table S3." seguidas (título y pie); es una elección de formato.

## 8. Incoherencias internas (no afectan al manuscrito)

- `data/processed/screening/README.md` da 0,69 % / 0,005 % / 1,29 %; `docs/methods_equations.md` (que sigue el manuscrito) da 0,68 / 0 / 1,31 %. Probablemente distinto denominador.
- `docs/supplementary_qc.md:133` dice "26 of 33" perímetros de matorral; la lista corta tiene 35.
- `docs/results_q1b.md` imprime +0,24 y +0,14 donde el CSV da 0,235 y 0,1345.

## 9. SPEI-3 de primavera en los 22 incendios (cálculo nuevo, *post hoc*, descriptivo)

Script `R/fires_spei3_spring.R`; detalle en `docs/closeout_checks.md`, sección 14. SPEI-90 diario de 2025 en las 140 celdas de ERA5-Land de las 241 celdas del caso 2025, mismo método que la pregunta 1; por incendio, media de las celdas quemadas ponderada por la fracción quemada (como en la ecuación 3).

| Abril–mayo de 2025, celdas quemadas | España (15) | Portugal (7) |
| --- | --- | --- |
| Mediana por incendio | 0,20 a 2,13 | 1,14 a 1,79 |
| Mínimo y máximo diarios entre incendios | −0,09 y 2,35 | 0,72 y 2,03 |
| Incendios con mediana > 0 / con todos los días > 0 | 15 / 13 | 7 / 7 |
| SPEI-3 el día de la ignición | −2,67 a −0,26 | −1,87 a −1,01 |

"Highest in the Portuguese fires" no era exacto (los máximos puntuales son de Mombeltrán, Alburquerque y Cáceres); Portugal destaca por la homogeneidad. Frase puesta en la copia: "Spring was wet in all 22 fires: the SPEI-3 of their burned cells (burned-fraction-weighted mean, as in Eq. (3)) had a positive median over April–May in every fire (0.2–2.1 in Spain and 1.1–1.8 in Portugal) and remained above zero on every day of these two months in 20 of them". Dato disponible y no usado: el día de la ignición el SPEI-3 era negativo en los 22 incendios.

## 10. Cambios aplicados en las copias

Manuscrito (14 cambios controlados):
1. Tabla 1: "SIF (740 nm, 743–758 nm fitting window, day-length corrected)".
2. Tabla 1: paréntesis de cierre tras "Sentinel-2 20 m".
3. 2.2: "Daily SIF at 740 nm, retrieved in the 743–758 nm fitting window, was obtained…".
4. 2.2: "The L2B product contains only retrievals with a quality value above 0.5."
5. 2.2: "Soundings with an effective cloud fraction…".
6. 2.2: "…(derived from MODIS MCD12C1 2018) were discarded, and negative SIF retrievals were retained, since removing them would bias the daily means upwards."
7. 2.2: cribado completo de MOD09GA y regla de rechazo de imágenes.
8. 3.2: 0.39 / 0.68.
9. 3.2: 0, 1 and 11 days.
10. 3.3: +0.23.
11. Discusión: frase del SPEI-3 (sección 9).
12–14. Referencias: Sirca, Chuvieco 2023, Hu y Shi.

Suplemento (3): Texto S1.2 (mediana de los valores positivos), fila CEMS de la Tabla S3, línea "Contents".

Las copias pasan el validador OOXML del skill de Word (esquema y comprobación de que todo cambio está registrado). Se revisan y aceptan en Word con "Revisar → Aceptar todos los cambios".
