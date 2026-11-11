# Comprobaciones de cierre del manuscrito

**9 de noviembre de 2026.** Respuesta a la revisión externa (`docs/reviews/CIERRE_MANUSCRITO_SIF_INSTRUCCIONES_CLAUDE_CODE.md`, versionada sin cambios; usada solo como referencia, su plan no se ha ejecutado).

Reglas de este documento:
- No se cambia ningún resultado original.
- Los puntos 1 a 4 y el 6 son lecturas de salidas existentes.
- El punto 5 es la única sensibilidad nueva y es **posterior** (declarada tras ver el resultado de H3b).
- El manuscrito no se ha tocado.

## 1. Estratos: población de §3.2, Tabla 3, Fig. 4(c) y H1

**Respuesta corta:** §3.2, la Tabla 3, la Fig. 4(c) (fila "Shrubland") y H1 usan **el estrato matorral = matorral + brezal** (`drought_q1.strata.shrubland: [shrubland, wet_heath]`), con 4169 celdas.

- Una celda cuenta como significativa para un índice si *p* < 0,05 en la prueba de permutación del máximo de *r* con el SPEI.
- H1 se calcula sobre las celdas significativas **en las dos** variables comparadas: 2267 frente al NDVI y 2171 frente al EVI. Son los mismos *n* de `hypotheses.csv`.
- Criterio de H1: fracción ≥ 0,60 y límite inferior del IC > 0,5. Los empates no cuentan como "más corta".
- Fila "Shrubland" de la Tabla 3: 0,71 [0,65–0,75] frente al NDVI y 0,80 [0,75–0,85] frente al EVI, sobre esas 2267 y 2171 celdas.
- "Heathland (descriptive)" es la clase brezal sola (`wet_heath_only`, 60 y 62 celdas).

Recuentos (celdas de la pregunta 1, sin quemar desde 2013; fuente: `analysis1_cells.csv` y `drought_q1_cells.csv`):

| Grupo | Celdas | Signif. SIF/APAR | Signif. NDVI | Signif. EVI | Signif. SIF/APAR y NDVI | Signif. SIF/APAR y EVI |
| --- | --- | --- | --- | --- | --- | --- |
| Matorral solo (`shrubland`) | 3994 | 2474 | 3361 | 3176 | 2207 | 2109 |
| Brezal solo (`wet_heath`) | 175 | 81 | 114 | 123 | 60 | 62 |
| **Matorral + brezal (estrato)** | **4169** | **2555** | **3475** | **3299** | **2267** | **2171** |
| Bosque (cerrado + abierto) | 1369 | 729 | 915 | 833 | 576 | 530 |
| Pastizal | 1233 | 744 | 1043 | 1021 | 689 | 689 |

El estrato matorral es en un 96 % matorral propiamente dicho (3994 de 4169 celdas).

### Qué es la clase "Heathland and wetland" (`wet_heath`)

Agrupa los tipos 51, 52 y 53 de FirEUrisk. La leyenda está anotada en `config.yaml` (`epoch.fuel.types`), leída del *Product User Manual* el 7 de noviembre de 2026: **"wet and peat/semi-peat land"** (zonas húmedas y turberas o semiturberas), con tres subtipos según la vegetación:

| Código | Subtipo |
| --- | --- |
| 51 | con árboles |
| 52 | con matorral |
| 53 | con pasto |

**Sí, son humedales y turberas por definición del producto, no brezales de matorral.** Composición media de las 175 celdas de la pregunta 1 con esa clase dominante (fracciones de la celda de 0,05°):

| Componente | Fracción media | Celdas en que domina entre 51–53 |
| --- | --- | --- |
| 51 (con árboles) | 0,25 | 82 |
| 52 (con matorral) | 0,05 | 17 |
| 53 (con pasto) | 0,23 | 76 |
| Suma 51–53 | 0,53 | |
| Matorral 21–23 (resto de la celda) | 0,12 | |

En las 79 celdas `wet_heath` del caso 2025 (quemadas y controles), las fracciones son 0,25, 0,04 y 0,36.

El nombre "heathland/brezal" que usamos no se corresponde con el subtipo dominante. En el noroeste ibérico esta clase coincide con matorral atlántico de brezo y tojo sobre suelos húmedos o turbosos de montaña, pero eso es una interpretación, **no algo que diga el producto**.

**Leyenda verificada** por el investigador el 11 de noviembre de 2026 en la tabla 1 de Aragoneses et al. (2023):
- 51/52/53: "Wet and peat/semi-peat land – tree / shrubland / grassland";
- 61: "Urban continuous fabric";
- 62: "Urban discontinuous fabric";
- 7: "Nonfuel".

Los comentarios de `config.yaml` (`epoch.fuel.types`) usan esos nombres.

Propuesta para el texto: "wet and peat-land fuels (FirEUrisk types 51–53; mostly Atlantic heath on wet soils in NW Iberia)" o similar.

Las 175 celdas de la pregunta 1 con esta clase son casi todas húmedas: 156 húmedas, 12 subhúmedas secas y 7 semiáridas.

### Contraste con CORINE 2018 (10 de noviembre de 2026)

Fracción media de CORINE Land Cover 2018 (100 m, agregada a 0,05° en GEE; `data/interim/gee/corine_2018_fine.nc`) en las celdas con clase dominante `wet_heath`:

| Celdas | *n* | 322 landas y brezales: media (mediana) | Celdas con 322 > 0 | Celdas con 322 como grupo dominante | Grupo de humedales y aguas (cota superior de 411 + 412): media | Máximo |
| --- | --- | --- | --- | --- | --- | --- |
| Pregunta 1 | 175 | **0,45** (0,43) | 96 % | 150 (86 %) | **0,043** | 1,00 |
| Caso 2025, quemadas | 44 | **0,61** (0,63) | 100 % | 43 | **0,000** | 0,000 |
| Caso 2025, controles | 35 | **0,53** (0,51) | 100 % | 32 | **0,002** | 0,042 |

- **411 y 412 no se pueden dar por separado con lo extraído.** El archivo de CORINE guarda grupos, y 411 (marismas interiores) y 412 (turberas) están dentro de `water_wetland` junto con 335, 421–423 y 511–523: glaciares, humedales costeros y láminas de agua.
- Por eso esa columna es una **cota superior** de 411 + 412. Para el caso 2025 es prácticamente nula, así que 411 y 412 también lo son.
- En la pregunta 1, la media de 0,043 la llevan sobre todo 8 celdas dominadas por ese grupo, probablemente embalses o costa (máximo 1,00); el 86 % de las celdas no tiene nada de él.
- Separar 411 y 412 exigiría una extracción pequeña en GEE, que no se ha hecho.
- El resto de la cobertura de CORINE en estas celdas es sobre todo frondosas (311, 0,15–0,17), seguidas de agrícola, coníferas o pastizal natural.

**Lectura:** en CORINE, la clase `wet_heath` de FirEUrisk corresponde sobre todo a **landas y brezales (322)**, no a humedales ni turberas. Esto respalda la etiqueta "heathland" en las figuras. La definición del producto FirEUrisk ("wet and peat/semi-peat land") debería citarse en Métodos como lo que es, con esta comprobación de CORINE como apoyo.

## 2. Fig. 3: SPEI de cada celda

- **Confirmado:** cada celda de 0,05° toma el SPEI de la celda de ERA5-Land de 0,1° que la contiene.
  - Las celdas de 0,05° tienen los bordes en múltiplos de 0,05°, y las de ERA5-Land están centradas en múltiplos de 0,1°, con bordes en ±0,05°. Por eso cada celda de 0,05° queda entera dentro de una sola celda de 0,1°.
  - Comprobado para las 22 celdas de la Fig. 3 y la S3: todas tienen el centro a ≤ 0,05° del centro asignado.
  - En las 4 celdas de sequía de 2022, el SPEI-90 coincide exactamente con el de la pregunta 1 (diferencia máxima 0).
- **Los dos controles de A Rúa no comparten celda de ERA5-Land:**

  | Celda | Centro de 0,05° | Celda de 0,1° |
  | --- | --- | --- |
  | Control 1 (`fine_149_62`) | 6,875° O, 42,975° N | 6,9° O, 43,0° N |
  | Control 2 (`fine_149_63`) | 6,825° O, 42,975° N | 6,8° O, 43,0° N |

  - Son celdas de ERA5-Land vecinas, de ahí que el SPEI-90 sea casi idéntico: diferencia máxima 0,11 entre abril y octubre de 2025.
  - La celda quemada (7,075° O, 42,475° N) está en otra celda (7,1° O, 42,5° N); su diferencia máxima con el control 1 es 0,58.
  - Comparten celda de ERA5-Land, por ejemplo, los dos controles de Quintas de São Bartolomeu (6,5° O, 40,5° N).

## 3. Fig. 5 / Q1b: unidades y censura

Unidades (definición B, estrato matorral = matorral + brezal; fuentes: `event_count.csv`, `analysis2b_episodes.csv` y `hypotheses_q1b.csv`):

| Concepto | Valor |
| --- | --- |
| Eventos detectados (todas las vegetaciones) | 242 |
| **Eventos con celdas de matorral** ("228 events") | **228** (59 con inicio en primavera, mar–may; 169 en verano, jun–sep) |
| Episodios celda × inicio de matorral dentro de eventos | 9894 (3760 primavera, 6134 verano) |
| Eventos con al menos una pareja informativa, frente al NDVI / EVI | **141 / 145** |
| Parejas celda–episodio informativas, frente al NDVI / EVI | **4463 / 4340** |

Las parejas informativas son las que tienen las dos variables observadas y al menos una que responde.

Reparto por estación (eventos con parejas informativas; parejas informativas):

| Frente a | Primavera | Verano | Total |
| --- | --- | --- | --- |
| NDVI | 32 eventos; 555 parejas | 109; 3908 | 141; 4463 |
| EVI | 34 eventos; 629 parejas | 111; 3711 | 145; 4340 |

- No hay inicios en otras estaciones: los meses de inicio permitidos son de marzo a septiembre.
- **"median d" es la mediana entre eventos de la mediana de *d* de cada evento** (`drought_q1b.h3b_test`). No es la mediana de todas las parejas.
- La puntuación de signo es la media entre eventos de la puntuación media de cada evento, con bootstrap por eventos.

### Fracción de parejas censuradas

Una pareja está censurada si una de las dos variables no responde en la ventana (−30 a +90 días); se le asigna la cota de +90. Las doblemente censuradas no son informativas y quedan fuera.

| Frente a | Estación | Informativas | Responden ambas | SIF/APAR censurada | Referencia censurada | **Fracción censurada** | Doble censura (excluidas) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NDVI | todas | 4463 | 2744 | 1155 (25,9 %) | 564 (12,6 %) | **38,5 %** | 433 |
| NDVI | primavera | 555 | 412 | 136 (24,5 %) | 7 (1,3 %) | **25,8 %** | 11 |
| NDVI | verano | 3908 | 2332 | 1019 (26,1 %) | 557 (14,3 %) | **40,3 %** | 422 |
| EVI | todas | 4340 | 2488 | 855 (19,7 %) | 997 (23,0 %) | **42,7 %** | 793 |
| EVI | primavera | 629 | 469 | 132 (21,0 %) | 28 (4,5 %) | **25,4 %** | 39 |
| EVI | verano | 3711 | 2019 | 723 (19,5 %) | 969 (26,1 %) | **45,6 %** | 754 |

Cuando la referencia está censurada, SIF/APAR responde y la referencia no, así que la pareja puntúa a favor de SIF/APAR. En verano frente al EVI, el 26 % de las parejas son de este tipo (punto 5).

## 4. Tabla 1: periodo disponible o extraído frente a periodo usado

| Producto | Disponible / extraído (en el proyecto) | Caso 2025 (época superpuesta) | Pregunta 1 y Q1b |
| --- | --- | --- | --- |
| TROPOSIF (SIF, 743 nm) | 1 may 2018 – 3 nov 2026 | Del 1 may 2018 al día anterior a la ignición (2025); todo enmascarado desde la ignición. Climatología con esos datos; desviación típica sobre los días anteriores al día −60 | 1 may 2018 – 31 dic 2025; análisis 1, días de abril a octubre |
| PAR = 0,48 × SSRD (ERA5-Land, GEE) | 1 may 2018 – 26 oct 2026 | Como TROPOSIF | Como TROPOSIF; corrección del PAR en Q1b ajustada en días de abril a octubre con SPEI-90 ≥ 0 |
| fPAR MCD15A3H v061 | Compuestos de 4 días del 23 abr 2018 al 28 oct 2026 | Compuestos cortados antes de la ignición; persistencia ≤ 5 días (principal sin persistencia) | 2018–2025, interpolación centrada sin persistencia |
| NDVI/EVI MOD09GA + MYD09GA v061 | 1 may 2018 – 3 nov 2026 | Como TROPOSIF | 1 may 2018 – 31 dic 2025 |
| NBAR MCD43A4 (sensibilidad) | 1 may 2018 – 29 oct 2026 | Solo sensibilidad; enmascarado desde el día −8 | No se usa |
| Precipitación ERA5-Land (balance hídrico) | Ene 1991 – dic 2025 | No se usa | SPEI: acumulación desde el 1 ene 1991; **calibración 1991–2020**; salida 2018–2025 |
| ET0 FAO-56 (ERA5-Land) para el SPEI | Entradas ene 1991 – oct 2026 | No se usa | Como la precipitación (D = P − ET0, 1991–2025) |
| AED = ET0 FAO-56 (ERA5-Land, 0,1°) | Serie diaria 1 ene 2017 – 31 oct 2026 | Desde el 1 may 2018 hasta la ignición | Análisis secundario 2018–2025 |
| FWI propio (ERA5-Land horario, 0,1°, xclim) | **Cálculo continuo desde el 1 ene 2017** (arranque FFMC 85, DMC 6, DC 15; unos 16 meses antes del primer dato usado) hasta el 31 oct 2026 | Desde el 1 may 2018 hasta la ignición | No se usa |
| FWI CEMS (EWDS, `cems-fire-historical-v1` 4_1; sensibilidad) | Agosto de 2025 | Solo comparación de agosto de 2025 | No se usa |
| Perímetros de EFFIS | Incendios de 2018–2026 (descarga del 7 nov 2026) | Selección de los incendios de 2025; controles sin quemar desde 2017 | Exclusión de lo quemado desde 2018 (dentro del criterio "desde 2013") |
| MCD64A1 / VNP64A1 | Historia de quemas 2013–2025; fechas de 2025 | Fecha de ignición (2025); controles sin quemar desde 2017; quemas previas (5 años) | Exclusión de lo quemado desde 2013 |
| ESFire30 (Ochoa et al.) | 1985–2025 | Controles sin quemar desde 2017 | Exclusión de lo quemado desde 2013 |
| FIRMS VIIRS (detecciones depuradas) | 1 ene 2018 – 7 nov 2026 | Fecha de ignición y comprobación de actividad previa (2025) | No se usa |
| FirEUrisk v2.0 (1 km, hacia 2019) | Estático | Clase dominante, estratos y emparejamiento | Clase dominante y estratos |
| Global-AI v3.1 (1970–2000) | Estático | Emparejamiento por aridez | Clases de aridez |
| SRTM 90 m | Estático | Emparejamiento por altitud | No se usa |
| CORINE 2018 | Estático | Apoyo y sensibilidad | No se usa |
| CERES SYN1deg Ed4B (sensibilidad prevista) | **No descargado** en el proyecto. Solo hay SSRD mensual de ERA5-Land remuestreada a la rejilla de 1° de CERES, may 2018 – ago 2026, para la prueba del salto de abril de 2022 | No se usa en ningún resultado | No se usa |

Notas:
- **Caso 2025:** todas las variables se enmascaran desde la ignición (incluida) en las celdas quemadas y en sus controles antes de calcular nada. La climatología (mediana por día del año ±15 días) usa los datos de 2018 hasta la ignición.
- **Pregunta 1 y Q1b:** la climatología usa 2018–2025 completo. Las anomalías se dividen por la desviación típica de la anomalía suavizada en todo el periodo.
- Lo extraído después de 2025 (2026) no entra en ningún resultado del manuscrito.

## 5. Sensibilidad posterior: solo parejas en que respondieron las dos variables

**Posterior**, declarada el 9 de noviembre de 2026 tras ver el resultado de H3b. No forma parte de ningún criterio.

- Mismo cálculo que el criterio (`drought_q1b.h3b_test`: mismos parámetros, misma semilla y bootstrap por eventos), restringido a las parejas celda–episodio en que SIF/APAR y la referencia responden dentro de la ventana, sin censura.
- Código: `src/physiofire/drought_q1b_posthoc_both.py`. Salida: `data/processed/drought_q1b/summary_posthoc_h3b_both_responded.csv`.
- Las filas "todas las parejas" reproducen exactamente los valores del criterio, como control.

| Frente a | Estación | Parejas | Eventos | Puntuación de signo [IC 95 %] | Mediana de *d* (días) | Parejas con SIF/APAR antes |
| --- | --- | --- | --- | --- | --- | --- |
| NDVI | todas: todas las parejas | 4463 | 141 | +0,17 [+0,06, +0,29] | +13 | 26 % |
| NDVI | todas: **responden ambas** | 2744 | 124 | **+0,30 [+0,19, +0,42]** | **+12,5** | 22 % |
| NDVI | primavera: responden ambas | 412 | 29 | +0,38 [+0,16, +0,60] | +13,5 | 25 % |
| NDVI | verano: responden ambas | 2332 | 95 | +0,28 [+0,14, +0,41] | +12 | 21 % |
| EVI | todas: todas las parejas | 4340 | 145 | −0,04 [−0,16, +0,07] | +1 | 41 % |
| EVI | todas: **responden ambas** | 2488 | 117 | **+0,23 [+0,11, +0,34]** | **+9** | 31 % |
| EVI | primavera: responden ambas | 469 | 31 | +0,33 [+0,10, +0,54] | +10,5 | 26 % |
| EVI | verano: responden ambas | 2019 | 86 | **+0,19 [+0,05, +0,32]** | **+8** | 32 % |

Lectura:
- Cuando las dos variables responden, **SIF/APAR responde después** que el NDVI y que el EVI, en primavera y en verano: puntuación > 0 con el IC por encima de 0 y mediana de *d* de +8 a +14 días.
- **La ventaja de SIF/APAR frente al EVI en verano** (−0,16 [−0,29, −0,03] con todas las parejas) **sale de las parejas en que el EVI no responde**, que se puntúan a favor de SIF/APAR. Son el 26 % de las parejas de verano frente al EVI (punto 3).
- Esa ventaja indica que SIF/APAR **responde más a menudo** en verano, no que **responda antes**. La observación posterior de Q1b sobre el verano debería redactarse en ese sentido.
- Los intervalos siguen siendo optimistas, porque los eventos no son independientes.

## 6. Commits de los planes fijados antes de cada análisis

| Análisis | Qué quedó fijado | Commit (fecha) |
| --- | --- | --- |
| Caso 2025: muestra de incendios | Selección por regla de los 22 incendios (`data/fires/selected_fires.csv`), registrada antes de cualquier análisis de los incendios | `47e6488` (7 nov 2026) |
| Caso 2025: configuración | Controles, umbrales, anomalías, enmascarado y criterio, antes de extraer ninguna serie de incendios | **`a7f894f`** (8 nov 2026); anotado en el borrador de métodos en `938b497`. Resultados en `0bf2d5a` |
| Pregunta 1: plan prerregistrado | Plan y criterio antes de cualquier cálculo | **`c84924c`** (8 nov 2026); concreciones aprobadas en `17685b2` |
| Pregunta 1: configuración final | Recorte del SPEI y detalles de implementación aprobados antes de extraer series | **`76ae9af`** (código y configuración fijados; anotado en `d40573e`). Resultados en `027304c` |
| Q1b | Plan aprobado y configuración fijada antes de ejecutar | **`d093008`** (8 nov 2026); hash anotado en `c219284`. Resultados en `f4f5927` |

Matiz para Métodos (caso 2025): la cadena de SIF/APAR se cerró antes de fijar la muestra.
- El 6 de noviembre (`6baf86d`) ya se había calculado SIF/APAR regional del 1 de junio al 7 de septiembre de 2025 sobre toda la Península (tarea 4, prueba de la cadena de SIF/APAR).
- La regla de selección no usa SIF/APAR, y las series de las celdas quemadas y de los controles se extrajeron solo después de `a7f894f`.
- Conviene decirlo así ("selection rule and configuration fixed before extracting any fire or control series") y no "before any SIF/APAR computation".

## 7. Versión de TROPOSIF (10 de noviembre de 2026)

- **TROPOSIF L2B**, procesador **01.00.01**, colección **03**, distribuido por S5P-PAL y producido por UPV.
  - Comprobado en los atributos `processor_version` y `collection_identifier` de los 3104 archivos diarios descargados, del 1 de mayo de 2018 al 3 de noviembre de 2026: todos son la misma versión.
  - 2018–2022 viene del reprocesado de la misión (archivos producidos en 2023) y lo posterior, del procesado continuo, con la misma versión.
- **Variable:** `SIF_Corr_743`.
- **Ajustes del algoritmo** que constan en los atributos: ventana de 743–758 nm, referencia a 740 nm, umbrales del procesador de fracción de nubes 0,8, SZA 70° y VZA 60°.
- **Huecos:** ninguno en 2018–2025. Solo faltan 5 días de octubre de 2026, fuera del periodo del estudio.
- **Cita sugerida:** el manual del producto (PUM v1.0) y Guanter et al. (2021, ESSD) **(verificar)**.

## 8. Focos activos de MODIS C6.1 (10 de noviembre de 2026)

- **Se descargaron y se depuraron, pero no entran en ningún resultado.**
  - `R/firms_clean.R` procesa la fuente FIRMS `M-C61` (configurada como "backup only"): 48 971 detecciones tras la depuración.
  - El único script que lee las detecciones, `R/fire_candidates.R`, filtra solo las fuentes VIIRS (SV-C2, J1V-C2 y J2V-C2).
- La fecha de ignición y la comprobación de actividad previa usan VIIRS (375 m, colección 2), MCD64A1, VNP64A1 y EFFIS.
- No hay que confundirlos con el área quemada MCD64A1 C6.1, que sí se usa.

## 9. Tabla 1 del manuscrito frente a lo usado (10 de noviembre de 2026)

**Las 16 filas corresponden a datasets usados.** Correcciones:
- **Perímetros de EFFIS, "Sentinel-2, 20 m":** la capa descargada es `modis.ba.poly.shp`, y en `docs/data_sources.md` consta "MODIS 250 m". **(Verificar** en la documentación de EFFIS antes de dejar Sentinel-2.)
- **MCD64A1 y VNP64A1, "2013–2026":** la historia de quemas cubre 2013–2025 y las fechas de quema, de octubre de 2024 a enero de 2026.
- **AED:** la serie diaria del análisis cubre 2017–2026. Los años 1991–2016 de ET₀ solo entran en el SPEI.
- **Versiones que faltan:**
  - FirEUrisk v2.0 (10.21950/YABYCN);
  - ESFire30 (Zenodo 10.5281/zenodo.20257001);
  - SRTM: CGIAR v4.1 (`CGIAR/SRTM90_V4`);
  - CEMS: `cems-fire-historical-v1`, versión 4_1 (EWDS).
- **TROPOSIF, resolución:** 3,5 × 7 km hasta agosto de 2019 y 3,5 × 5,5 km después.

**Se usan en los análisis y no están en la tabla:**
- máscara de tierra firme (USDOS LSIB_SIMPLE 2017, en GEE; selección de celdas con fracción de tierra ≥ 0,5);
- ERA5-Land horario (entradas del FWI a las 12:00 UTC, viento de la ET₀ y precipitación del SPEI);
- `LC_MASK` de TROPOSIF (MCD12C1 de 2018; filtro de nieve y suelo desnudo).

**Descargados pero fuera de los resultados:** NBAR de MCD43A4 y fPAR de VNP15A2H (sensibilidades), focos de MODIS C6.1 y MCD12C1 como clasificación. Natural Earth solo se usa en el mapa de la Fig. 1.

## 10. Antelación L del caso 2025: criterio conjunto, solo magnitud e intervalo bootstrap (11 de noviembre de 2026)

Fuente: `data/processed/epoch/report2025_lead_times.csv` (`R/epoch_report_2025.R`); sin cálculos nuevos.

- **L conjunto** (`lead_days`, valor puntual del manuscrito): media ≥ 0,5 DE en el signo esperado **y** intervalo diario sin el 0, todos los días hasta el día −1 (`lead_time()` en `R/epoch_lib.R`).
- **L magnitud** (`lead_mean_rule`): la misma regla sin la condición del intervalo, en la muestra completa.
- **IC 95 % bootstrap:** incendios remuestreados con reemplazo (B = `epoch.bootstrap_n`, semilla `random_seed`); en cada réplica, L con el criterio de **solo magnitud** (`lead_boot()`). Siempre es así, en todas las filas.

| Grupo | Variable | Medida | n | L conjunto | L magnitud | IC 95 % | Réplicas con L > 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Todos | FWI | celdas quemadas | 22 | 12 | 12 | [8, 17] | 100 % |
| Todos | AED | celdas quemadas | 22 | 7 | 7 | [3, 10] | 99,3 % |
| Matorral | FWI | celdas quemadas | 15 | 6 | 6 | [0, 17] | 92,8 % |
| Matorral | AED | celdas quemadas | 15 | 4 | 4 | [0, 11] | 53 % |
| Brezal | SIF/APAR (sin persistencia, principal) | celdas quemadas | 7 | 8 | 8 | [4, 11] | 99,8 % |
| Brezal | SIF/APAR (persistencia de 5 días) | celdas quemadas | 7 | 7 | 7 | [4, 11] | 100 % |
| Brezal | EVI | celdas quemadas | 7 | 17 | 17 | [1, 19] | 98,8 % |
| Brezal | FWI | celdas quemadas | 7 | 14 | 14 | [12, 60] | 100 % |
| Brezal | AED | celdas quemadas | 7 | 7 | 8 | [5, 10] | 100 % |

**Diferencia incendio–control:** L = 0 en todas las variables y grupos, con los dos criterios. El intervalo es [0, 0] salvo el FWI en brezal: [0, 5], con un 13,8 % de réplicas con L > 0.

**Resultado:**
- Los dos criterios coinciden en todos los casos menos uno: la AED en brezal (7 con el conjunto, 8 con el de magnitud).
- Ningún valor puntual del criterio conjunto cae fuera de su intervalo.
- El valor puntual y el intervalo no salen de la misma regla. Conviene decirlo en métodos: el intervalo describe la variabilidad entre incendios de la regla de magnitud.

**Notas para la redacción:**
1. **FWI en brezal, [12, 60]: límite superior censurado.** 60 es el principio de la ventana (día −60). En el 2,5 % superior de las réplicas, el FWI de las celdas quemadas está ≥ 0,5 DE durante toda la ventana, así que el límite real puede ser mayor; es una cota, no una estimación.
2. **Matorral, FWI [0, 17] y AED [0, 11]: límite inferior en 0.** Una parte de las réplicas no da ninguna antelación: el 7 % en el FWI y el 47 % en la AED. La antelación de la AED en matorral (4 días) no es robusta.

## 11. Pregunta 1: definición de H2 y celdas sin SPEI (11 de noviembre de 2026)

### H2 (`src/physiofire/drought_q1.py`, `max_corr_cell()` y `h2_test()`; config `drought_q1.analysis1`)

- **Serie de desfases:** el desfase óptimo con **SPEI-3** (`h2_scale_days: 90`).
  - Para cada celda e índice es el desfase de 0 a 60 días con la mayor correlación de Pearson con SPEI-90 (`lag_h2`). Usa los días de abril a octubre, con todos los años juntos.
  - No es el desfase del óptimo global entre escalas.
- **Celdas:** las significativas **en los dos índices a esa escala**, con p_h2 < 0,05 en SIF/APAR y en la referencia.
  - p_h2 sale de una **prueba de permutación propia de SPEI-90**: el máximo sobre los desfases, con 199 permutaciones de años enteros de la serie de vegetación.
  - No es la significación del máximo global (p) que usa H1.
  - Las celdas con valores que faltan en cualquiera de los dos índices quedan fuera.
- **Estadístico:** la mediana entre celdas de la diferencia emparejada L(SIF/APAR) − L(NDVI o EVI), en días.
- **Intervalo:** bootstrap de bloques de 1° × 1°, que remuestrea cuadrados enteros con reemplazo (B = 2000, semilla 42, percentiles 2,5–97,5).
- **Criterio:** mediana **≤ −5 días** y **límite superior del intervalo < 0** (`h2_max_median_lag_diff_days: -5`).

| Estrato | Frente a | Celdas | Mediana (días) | IC 95 % | Se cumple |
| --- | --- | --- | --- | --- | --- |
| Matorral | NDVI | 2035 | 0 | [0, 0] | no |
| Matorral | EVI | 2101 | −5 | [−7, −3] | sí |
| Bosque | NDVI | 421 | 0 | [0, 0] | no |
| Bosque | EVI | 475 | −4 | [−6, −1] | no |
| Pastizal | NDVI | 693 | 0 | [0, 0] | no |
| Pastizal | EVI | 705 | −4 | [−6, −2] | no |

Fuente: `data/processed/drought_q1/hypotheses.csv`.

### Celdas sin SPEI: 6771 seleccionadas, 6751 efectivas

- **Criterios de selección** (`R/q1_cells.R`, `select_q1_cells()` en `R/q1_lib.R`):
  - al menos un 50 % de tierra;
  - clase dominante de FirEUrisk natural: bosque cerrado o abierto, matorral, brezal o pastizal;
  - sin quemas desde 2013, por unión binaria (fracción > 0 en cualquiera de las fuentes): MCD64A1 y VNP64A1 de 2013 a 2025, EFFIS (en la práctica solo desde 2018) y ESFire30 (2013–2025, solo España).
- **La disponibilidad de SPEI no es un criterio de selección.**
- **20 celdas costeras no tienen SPEI ni AED** en todo el periodo. La celda de ERA5-Land de 0,1° que las contiene es mar.
- **Desglose por estrato:**

  | Estrato | Celdas |
  | --- | --- |
  | Matorral | 14 (una de ellas de brezal) |
  | Bosque | 5 |
  | Pastizal | 1 |

- **Cómo quedan fuera:** su correlación es NaN en todas las variables, así que no son significativas y no entran en H1, H2 ni H3.
- **Celdas efectivas: 6751.** Es la misma cifra que el "6751 de 6771" de `docs/results_q1_drought.md`.
- **Comprobación:** solo lectura de `drought_q1_series.nc` y `analysis1_cells.csv`; no cambia ningún resultado.

## 12. Q1b: inicio de sequía, eventos, signo, censura y sensibilidades (11 de noviembre de 2026)

Código: `src/physiofire/drought_q1b.py` y `drought_q1.py`; config `drought_q1b`. Resultados: `data/processed/drought_q1b/hypotheses_q1b.csv` y `decision_q1b.csv`.

### Definición B del inicio (`onsets_rapid()`)

Un día *i* es inicio candidato si cumple las tres condiciones:
1. **Umbral:** SPEI-90 del día *i* < −1,0 (estricto).
2. **Duración:** sigue por debajo de −1,0 al menos 30 días seguidos desde el día *i*, incluido.
3. **Caída:** máximo del SPEI-90 en los 30 días previos (*i* − 30 a *i* − 1) − SPEI-90 del día *i* ≥ 1,0, sin importar el nivel de partida.

Después del filtro:
- **Separación:** de dos candidatos de una celda a menos de 90 días se queda el primero.
- **Ventana:** mes de inicio de marzo a septiembre, y ventana de respuesta (día −30 a +90, más 15 días) dentro del periodo con datos.

### Estaciones (`event_season()`)

- Primavera: marzo–mayo. Verano: junio–septiembre.
- La estación es la del **evento**, no la de cada celda: la mediana, redondeada, del mes de inicio de sus celdas.
- Como los inicios solo pueden ser de marzo a septiembre, no hay eventos fuera de esas dos estaciones.

### Eventos y estrato

- **Formación de eventos** (`build_events()`, sobre todos los episodios):
  - se unen celdas vecinas (las 8 de alrededor) con inicios separados como mucho ±15 días;
  - las celdas pueden ser de **cualquier clase** (bosque, matorral, brezal o pastizal);
  - el mínimo de **≥ 10 celdas distintas** cuenta todas las clases.
- **Comparación:** usa **solo las celdas del estrato** dentro de esos eventos (`_strata_rows()`). En el estrato matorral son las de matorral y las de brezal.
- **Cuándo H3b es evaluable:** con ≥ 10 eventos que tengan al menos una pareja informativa del estrato.

### Signo y censura (`pair_scores()`, `h3b_test()`)

- **Signo:** *d* = T(SIF/APAR) − T(referencia), en días respecto al inicio. Un **valor negativo indica que SIF/APAR responde antes**.
- **Puntuación:** −1 si SIF/APAR responde antes, +1 si responde después, 0 si empatan.
- **Censura simple (una variable no responde en −30…+90):**
  - si es la referencia la que no responde: *d* = T(SIF/APAR) − 90 y puntuación −1;
  - si es SIF/APAR: *d* = 90 − T(referencia) y puntuación +1.

  Es decir, **T = +90 entra en *d* como cota**.
- **Censura doble:** la pareja se cuenta pero no se usa (no informativa).
- **Agregación:**
  - dentro de cada evento, la media de la puntuación y la mediana de *d*;
  - entre eventos, la media de las puntuaciones (bootstrap por eventos) y la mediana de las medianas.
- **Criterio:** media < 0, límite superior < 0 y mediana de *d* ≤ −5 días.

### Sensibilidades en `hypotheses_q1b.csv`

| Sensibilidad | Pruebas con resultado | Nota |
| --- | --- | --- |
| Corregida por el PAR con media centrada | H1 y H2b (`H1_centred_sens`, `H2b_centred_sens`) | **No existe para H3b.** En el análisis 1b, SIF/APAR va corregido por el PAR con los dos suavizados |
| Igualada en ruido | Solo H1 (`H1_robust_noise`; 5 réplicas, la de fracción mediana) | No existe para H2b ni para H3b |
| Correlación parcial dado el PAR | H1 (`H1_partial_sens`) | — |
| Media hacia atrás con corrección por el PAR | H3b (`H3b_backward_par_corrected_sens`) | **Es la única sensibilidad de H3b.** Cambia el suavizado y la corrección a la vez (`docs/results_q1b.md`, sección (a)) |

| Matorral | H1 corr. | H1 ruido | H1 centrada | H1 parcial | H2b | H2b centrada | H3b | H3b hacia atrás |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Frente al NDVI | sí | sí | sí | sí | no | no | no | no |
| Frente al EVI | sí | sí | sí | sí | sí (−6) | sí (−5) | no | no |

**Ninguna sensibilidad cambia el criterio.**
- H3b no se cumple en ningún caso.
- La decisión es "contraria" en todos los estratos.
- En los estratos que no deciden, la única diferencia con el análisis principal es descriptiva: en el brezal solo, frente al NDVI, se cumple H1 parcial y no H1 corregido.
