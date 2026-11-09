# Comprobaciones de cierre del manuscrito

**9 de noviembre de 2026.** Respuesta a la revisión externa (`docs/chatgpt/CIERRE_MANUSCRITO_SIF_INSTRUCCIONES_CLAUDE_CODE.md`, usado solo como referencia; su plan no se ha ejecutado).

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

Hay que verificar en el *Product User Manual* (`data/raw/fireurisk_fuel/yabycn_v2/PUM_FirEUrisk_European_fuel_map.pdf`, tabla de tipos) la redacción exacta de la leyenda. No he podido extraer el texto del PDF en este equipo.

Propuesta para el texto: "wet and peat-land fuels (FirEUrisk types 51–53; mostly Atlantic heath on wet soils in NW Iberia)" o similar, después de verificarlo.

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
