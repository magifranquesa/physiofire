# PHYSIOFIRE – Prueba de concepto

> **IDIOMA: RESPONDE SIEMPRE EN CASTELLANO.** Vale para todo lo que lee el investigador: respuestas finales, mensajes intermedios entre herramientas, preguntas, opciones, resúmenes y planes. También después de leer documentación, salidas de herramientas o informes de subagentes en inglés: antes de escribir, vuelve al castellano. Solo el código, los nombres de variables, los comentarios en el código y los mensajes de commit van en inglés.

Este archivo da contexto a Claude Code sobre el proyecto. Léelo entero antes de proponer o escribir código. La sección "Objetivo de la prueba de concepto" manda sobre todo lo demás.

## Cómo trabajar conmigo

- Comunícate en español. Código, nombres de variables y comentarios en el código, en inglés.
- Soy investigador postdoctoral (doctorado en 2022) en el Instituto Pirenaico de Ecología (IPE-CSIC). Sé teledetección y Python, pero explica brevemente las decisiones metodológicas y de diseño.
- No inventes nombres de productos, versiones, variables ni URLs. Si no estás seguro de un dataset o de su acceso, dilo y propón cómo verificarlo. Varias fuentes de abajo están marcadas como **(verificar)**.
- Prioriza pasos pequeños y comprobables: descarga una muestra, inspecciona las variables y luego escala.
- Antes de descargas grandes, estima el volumen y pregúntame.
- Infraestructura mínima: construye solo lo que necesita el análisis de la prueba de concepto.
- Entorno: Windows. Miniconda en `C:\ProgramData\miniconda3` (fuera del PATH; llamarlo por ruta completa). Usar conda-forge. Entorno conda `physiofire` solo para Python. R (4.6.1 de CRAN, en `C:\Users\08856958A\AppData\Local\Programs\R\R-4.6.1`) con renv y `renv.lock`; no meter R en conda (r-terra no se mantiene en conda-forge para Windows).
- Lenguajes: el investigador trabaja habitualmente en R. Figuras y todo el código para publicar (tabla de incendios, época superpuesta, estadística) en R, salvo que otro lenguaje sea mejor o imprescindible. Python para descarga y procesado de rejillas (earthaccess, cdsapi, earthengine-api, xarray, rejillado de TROPOMI). Intercambio en NetCDF (CF) y CSV.

## Objetivo científico

Evaluar si el estado fisiológico de la vegetación observado desde satélite permite anticipar el peligro de incendio mejor y antes que los índices meteorológicos (FWI) y los índices de vegetación ópticos (NDVI, EVI).

**Hipótesis:** la anomalía de SIF/APAR (rendimiento aparente de fluorescencia) anticipa el secado del combustible vivo y aporta información sobre el peligro de incendio que no está ya contenida en el FWI y la demanda evaporativa atmosférica (AED), con antelación de días a 1–2 semanas, sobre todo en matorral y arbolado.

**Motivación:** el FWI usa solo meteorología y no observa la vegetación viva. Los productos de humedad del combustible vivo (LFMC) y los índices ópticos detectan el estrés tarde.

**Para qué sirve el resultado:** un artículo con el investigador como autor de correspondencia (envío hacia mayo–junio de 2027), resultados preliminares para una beca MSCA postdoctoral (cierre habitual en septiembre de 2027) y un resumen para la EGU (plazo habitual en enero de 2027).

## Objetivo actual: pregunta 1 cerrada (negativa); Q1b cerrada (contraria)

> ¿SIF/APAR detecta el estrés hídrico antes y a escalas más cortas que el NDVI/EVI en la vegetación natural de la Península, con independencia de los incendios?

- **Resultado de la pregunta 1 (8 de noviembre de 2026): negativo según el criterio prerregistrado.** Está en `docs/results_q1_drought.md`. En matorral:
  - **H1 se cumple:** SIF/APAR tiene una escala de SPEI más corta en el 71 % de las celdas frente al NDVI y en el 80 % frente al EVI.
  - **H2 se cumple solo frente al EVI** (−5 días).
  - **H3 no se cumple:** solo hay 6 eventos de sequía en total.
  - **Observaciones posteriores, marcadas como tales:**
    - en los eventos de agosto responde SIF/APAR y no el NDVI;
    - parte de la relación de SIF/APAR con la AED la lleva el PAR;
    - los desfases están censurados en 0.
- **Q1b (seguimiento posterior, con criterio propio):** `docs/plan_q1b.md`, aprobado el 8 de noviembre de 2026; config `drought_q1b`, código `src/physiofire/drought_q1b.py`. Incluye:
  - H3b con censura a +90 días y episodios de intensificación rápida;
  - desfases de −15 a +60 días con media hacia atrás;
  - SIF/APAR corregido por el PAR;
  - una prueba de ruido de H1.

  **Resultado de Q1b (9 de noviembre de 2026): contrario en matorral según su criterio** (plan fijado en `d093008`). Está en `docs/results_q1b.md`:
  - **H3b no se cumple** (definición B, 141–145 eventos): frente al NDVI, +0,17 [+0,06, +0,29] (el NDVI responde antes); frente al EVI, −0,04 [−0,16, +0,07] (sin diferencia).
  - **H1 corregido por el PAR y robusto al ruido se cumple** (0,68–0,81); **H2b solo frente al EVI** (−6 días).
  - **Observaciones posteriores, marcadas como tales:** el 30 % de las respuestas del NDVI caen en el día −30 (ya estaba bajo antes del inicio); en primavera responden antes los índices ópticos y en verano SIF/APAR frente al EVI. Es una hipótesis para un diseño futuro, no un resultado.

  Q1b no cambia el resultado negativo de la pregunta 1.
- Plan prerregistrado de la pregunta 1: `docs/plan_q1_drought.md` y `config.yaml` (sección `drought_q1`), fijados en git antes de calcular nada.
- Celdas de 0,05° de vegetación natural sin quemar desde 2013, en 2018–2025.
- SPEI diario de 15 a 365 días (ERA5-Land, referencia 1991–2020) y AED como variable secundaria.
- Análisis 1: escala y desfase de máxima correlación. Análisis 2: respuesta en episodios de sequía.
- Criterio de decisión: positivo si se cumplen H3 y además H1 o H2 en matorral (matorral + brezal), frente al NDVI y frente al EVI. El bosque se informa y el pastizal es referencia.
- Es una pregunta previa a la predicción de incendios: su resultado fija la escala del SPEI del modelo base de la fase predictiva (opción A, en `docs/backlog.md`).

## Prueba de concepto con incendios (caso 2025 cerrado: resultado negativo)

Resultado en `docs/results_case2025.md`: SIF/APAR no se separa de los controles. La señal previa en las celdas quemadas (FWI, AED, SIF/APAR) es regional y la comparten los controles. Pregunta original:

> ¿La anomalía de SIF/APAR se separa de lo normal antes de los incendios, con más antelación que el NDVI/EVI, y aporta información que el FWI no tiene?

**Análisis mínimo (época superpuesta):**
- Muestra de incendios de la Península Ibérica (España y Portugal) seleccionados manualmente con criterios fijados de antemano (ver "Incendios").
- Para cada incendio, anomalías de SIF/APAR, NDVI/EVI, FWI y AED en los 60 días previos a la fecha de inicio.
- Controles sin incendio emparejados por vegetación, región y fecha.

**Resultados:**
1. Días de antelación con que cada variable se separa de los controles.
2. Información más allá del FWI: en la misma figura, diferencia incendio–control del FWI y de SIF/APAR (comparación descriptiva). Si el FWI es parecido entre incendios y controles y SIF/APAR difiere, es evidencia de valor añadido. El AUC dentro de cada clase de FWI, en la prueba completa.
3. Todo estratificado por tipo de vegetación (matorral, arbolado y pasto como control negativo) y por país.

**Criterio de decisión:** seguir si SIF/APAR se adelanta al NDVI/EVI y difiere entre incendios y controles cuando la diferencia del FWI es pequeña, al menos en matorral y arbolado. El caso 2025 evalúa solo matorral; el arbolado, en la prueba completa (ver "Decisiones tomadas").

**Fuera de alcance por ahora:**
- réplica de la correlación cruzada de Tang (la pregunta 1 es un análisis propio, no una réplica);
- ESI/GLEAM (salvo el contraste de la AED, backlog 37), LFMC, bajada de escala, sistema operativo, visor y FLEX;
- modelo predictivo: registrado como fase futura (opción A, `docs/backlog.md`), que se detalla y se fija solo después del resultado de la pregunta 1.

**Hitos:**

| Hito | Contenido | Fecha |
| --- | --- | --- |
| Caso 2025 | Mapas y compuestos de los incendios seleccionados de 2025 | mediados de enero de 2027 |
| Prueba completa | Todos los incendios seleccionados y decisión de seguir o replantear | marzo de 2027 |
| Artículo | Envío como autor de correspondencia | mayo–junio de 2027 |

## Incendios

- **España:** cartografía anual de incendios de Ochoa et al. (ESFire30, publicada en Zenodo: 10.5281/zenodo.20257001). Incluye 2025 y, para 2001–2025, fechas corregidas con MODIS. Solo cubre España.
- **Alternativa y complemento: perímetros de EFFIS.** Para grandes incendios son muy precisos, cubren España y Portugal con el mismo método e incluyen fecha. Si la cartografía de Ochoa no llega a 2025, usar EFFIS. Aunque llegue, EFFIS sirve para contrastar perímetros y fechas. Ojo: la fecha de EFFIS puede ser la de detección y los perímetros de incendios cercanos pueden aparecer fusionados; contrastar con FIRMS.
- **Portugal:** cartografía de incendios disponible (fuente concreta a confirmar con el investigador).
- **Fecha de inicio:** imprescindible para el análisis. Si una cartografía no la incluye, asignarla cruzando cada perímetro con la primera detección de FIRMS VIIRS y, si es posible, con la EGIF (España) o el ICNF (Portugal) **(verificar)**.
- **Selección** (caso 2025: por regla, ver "Decisiones tomadas"). La cartografía tiene incertidumbre, así que la selección se hace con criterios escritos **antes** de mirar SIF/APAR:
  - superficie mínima (a fijar; priorizar grandes incendios por la escala de 0,25°);
  - fecha confirmada por al menos dos fuentes;
  - vegetación dominante clara;
  - sin solape con otros incendios en la ventana de 60 días.
- **Muestra equilibrada:** matorral, arbolado y pasto; España y Portugal; varias regiones y años.
- **Incendios extremos:** la base de datos de Solano-Romero et al. (preprint ESSD, 10.5194/essd-2026-236) no se usa en la prueba de concepto; línea futura en `docs/backlog.md` y `docs/literature/notes.md`.
- **Registro:** una tabla de incendios versionada (por ejemplo `data/fires/selected_fires.csv`) con identificador, país, fecha, superficie, vegetación, fuentes de la fecha y criterios que cumple. Irá como material suplementario.
- **Periodo:** TROPOMI empieza en mayo de 2018. Los incendios de 2018 solo valen si la ventana de 60 días queda dentro del periodo con datos (por ejemplo, Monchique en agosto de 2018). Incluir también 2022, 2024 y, sobre todo, 2025 (caso inicial: grandes incendios de agosto de 2025 en el noroeste de España y en Portugal, con ola de calor).
- **2026:** ensayo casi operativo, solo si hay perímetros provisionales y datos (CERES termina el 31 de agosto de 2026; usar PAR de ERA5 a partir de ahí).

## Meteorología y FWI

- **Análisis principal:** fuente homogénea para toda la Península, para que las diferencias entre países no se confundan con efectos reales. Opciones: ERA5-Land, o AEMET (España) + IPMA (Portugal) si son comparables. Decisión pendiente con el investigador.
- **Robustez:** datos de AEMET disponibles en el grupo (que trabaja con AEMET) para repetir el análisis en España con meteorología de mayor calidad.
- **AED (demanda evaporativa atmosférica):** variable atmosférica del análisis, en lugar del VPD. Integra temperatura, humedad, viento y radiación. Estimarla como evapotranspiración de referencia (ET0) con FAO-56 Penman-Monteith a partir de la fuente meteorológica elegida. Preguntar antes al investigador: su grupo (IPE, con AEMET) puede tener ya la AED calculada, y su método prevalece.
- Nota: Tang et al. usan VPD, así que la comparación con su artículo no es directa; documentarlo en la discusión.
- **FWI propio (análisis principal, decidido el 7 de noviembre de 2026):** sistema canadiense con ERA5-Land a 0,1° (valores a mediodía de temperatura, humedad relativa y viento, y precipitación de 24 h), con una implementación existente (xclim 1.0.0, aprobado el 7 de noviembre de 2026; constante del FFMC de Van Wagner, 1987, sin modificar). Motivo: con el FWI de 0,25°, el 7–16 % de los controles comparte celda con las celdas quemadas (0 % a 0,1°), lo que sesga la comparación a favor de SIF/APAR.
- **FWI de referencia:** el de EFFIS / Copernicus EMS, como referencia operativa y prueba de sensibilidad. Nombre exacto del dataset **(verificar)**.

## Base científica: Tang et al. (2026)

> **Criterio general (decidido el 7 de noviembre de 2026).** Tang et al. (2026) es la **base conceptual** (descomposición de la SIF y SIF/APAR como indicador fisiológico), **no un método a replicar**. Cada decisión se toma por lo que mejor responde a la pregunta en la Península Ibérica, no por comparabilidad con Tang. Lo que solo servía para comparar con Tang va al backlog con prioridad baja. Las diferencias con Tang se documentan en la discusión, sin intentar reducirlas.

Tang, Z., Miralles, D. G., Guo, Z. & Maes, W. H. (2026). *Fast response of satellite fluorescence-derived plant physiology to drought stress.* Nature Communications 17:2886. https://doi.org/10.1038/s41467-026-70076-0

Código y datos del artículo: https://doi.org/10.5281/zenodo.18327559 (un zip de 71 MB, licencia CC BY 4.0; citar si se reutiliza código). Revisarlo es útil pero no prioritario.

Resultados clave:
- Descomponen SIF = PAR × fPAR × SIFyield. Entonces SIF/APAR = SIF / (PAR × fPAR) aísla el rendimiento de fluorescencia (proxy fisiológico). SIF/PAR mezcla estructura y fisiología.
- Moda global del tiempo de respuesta a la sequía: SIF/APAR unos 3 días frente al VPD (unos 5 frente a la humedad del suelo), EVI unos 8 días y LAI unos 12–13 días.
- SIF sin corregir y SIF/PAR se comportan como el EVI porque conservan fPAR.
- La fisiología se alinea con el VPD; la estructura, con la humedad del suelo.
- Respuestas más rápidas en zonas húmedas, más lentas en zonas áridas. Esto es una limitación para la Península.

Pasos de Tang que sirvieron de punto de partida (la versión vigente está en `docs/methods_draft_RSE.md` y `config/config.yaml`):
1. SIF diario de TROPOMI (TROPOSIF, 743 nm, corregido por duración del día), desde el 1 de mayo de 2018.
2. Excluir datos con calidad < 0,5 y fracción de nubes > 50 %. Máscaras de nieve, agua y suelo desnudo. El artículo usa SWE de GlobSnow para la nieve; en la Península probablemente baste con la nieve de ERA5-Land (decisión pendiente).
3. PAR de CERES SYN1deg Ed4.1 en Tang. **Aquí:** PAR = 0,48 × radiación solar descendente de ERA5-Land (serie homogénea y poca latencia); CERES Ed4B, solo como prueba de sensibilidad.
4. fPAR de MODIS MCD15A3H (4 días, 500 m), remuestreado e interpolado linealmente a diario.
5. SIF/APAR = SIF / (PAR × fPAR). Tang descarta valores fuera de los percentiles 1–99; aquí, filtro de picos por celda (ver "Reglas del análisis de época").
6. Anomalías: Tang usa tendencia LOESS más ciclo estacional medio y suavizado centrado de 15 días y 3 × 3. **Aquí:** mediana por día del año (±15 días) como método principal del análisis de época, con medias hacia atrás de 15 días; LOESS (tendencia ajustada solo antes del día −60, sobre la serie desestacionalizada) como prueba de sensibilidad.

## Escala

- **Principal (decidido el 7 de noviembre de 2026): 0,05°** para toda la prueba de concepto. Con los incendios de 2025 es la única escala con celdas quemadas y controles suficientes.
- **0,25°:** al backlog, como prueba de sensibilidad con un diseño de controles propio. Casi todas las celdas de 0,25° del noroeste tienen algo quemado desde 2017; no ampliar el anillo de controles, porque perderían comparabilidad climática.

## Datos

| Variable | Fuente | Notas |
| --- | --- | --- |
| Incendios (España) | ESFire30 (Ochoa et al.; Landsat 30 m, 1985–2025; Zenodo 10.5281/zenodo.20257001, CC BY 4.0) | Solo España. Incluye 2025 y una versión con fechas corregidas con MODIS (2001–2025). Se usa para el criterio "sin quemar" de los controles |
| Incendios (España y Portugal) | Perímetros de EFFIS | Alternativa si Ochoa no llega a 2025; contraste de perímetros y fechas |
| Incendios (Portugal) | Cartografía a confirmar con el investigador | Fecha de inicio a confirmar |
| Fecha de inicio | NASA FIRMS (VIIRS); EGIF (MITECO); ICNF | Acceso a EGIF e ICNF **(verificar)** |
| SIF | TROPOSIF (TROPOMI): https://data-portal.s5p-pal.com/products/troposif.html | L2B diario global (~400 MB/día, sin cuenta), hasta noviembre de 2026; descargar, recortar y borrar con script reanudable. Detalles en docs/data_sources.md |
| PAR | 0,48 × radiación solar descendente de ERA5-Land (principal) | CERES SYN1deg Ed4B solo como prueba de sensibilidad (llega al 31 de agosto de 2026 y cambia de entradas en abril de 2022). Detalles en docs/data_sources.md |
| fPAR | MODIS MCD15A3H v061 (LP DAAC) | Fin de MODIS; VIIRS VNP15A2H como alternativa **(verificar)** |
| NDVI, EVI | MOD09GA/MYD09GA v061 diario (principal); NBAR de MCD43A4 como sensibilidad | MCD43C4 no está en GEE |
| Meteorología | ERA5-Land, AEMET (grupo), IPMA | Ver "Meteorología y FWI" |
| FWI (principal) | Propio: sistema canadiense con ERA5-Land horario a 0,1° (xclim 1.0.0) | Validado con cffdrs; ver docs/data_sources.md |
| FWI de referencia | EFFIS / Copernicus EMS en el EWDS (no en el CDS); dataset `cems-fire-historical-v1`, versión 4_1 | 0,25°, calculado con ERA5 a las 12 hora local; versión y acceso con la cuenta del CDS **(verificar)** |
| Tipos de combustible | Mapa europeo de combustibles de FirEUrisk v2.0 (Aragoneses et al., 2023, ESSD 15:1287–1315; datos 10.21950/YABYCN, 1 km, hacia 2019, 20 tipos) | Clasificación principal: clase dominante a 0,05° para la lista corta, los estratos y el emparejamiento de controles |
| Cobertura del suelo | CORINE Land Cover 2018 (GEE, 100 m) agregado a 0,05° | Apoyo y prueba de sensibilidad (R18). MCD12C1 deja de usarse (casi no asigna matorral en los incendios de 2025) |
| Aridez | Global Aridity Index v3.1 (figshare 10.6084/m9.figshare.7504448.v7) | P/ET0 de 1970–2000, 30″. La v3 (figshare v5) tenía un error en la ET0 |
| Altitud | SRTM 90 m (`CGIAR/SRTM90_V4`) | Media por celda |

Cuentas necesarias (probablemente): NASA Earthdata, Copernicus CDS y quizá el portal S5P-PAL.

Control de calidad de los datos: `docs/supplementary_qc.md` (irá como material suplementario). Pruebas de sensibilidad: `docs/backlog.md` y tabla 2 del borrador de métodos.

## Plan de trabajo

1. **Entorno y repositorio** (mínimo).
2. **Tabla de incendios:** cargar las cartografías, fijar los criterios de selección por escrito, asignar fechas y construir `selected_fires.csv`. Empezar por 2025.
3. **Verificar fuentes de satélite y meteorología:** TROPOSIF, CERES, MCD15A3H, MCD43C4, FWI de EFFIS y la fuente meteorológica elegida.
4. **Cadena de SIF/APAR de punta a punta** con un periodo de muestra (julio–agosto de 2025).
5. **Caso 2025:** anomalías de todas las variables para los incendios de 2025 y sus controles; primeras figuras de época superpuesta. Requiere la serie completa de TROPOSIF para la climatología.
6. **Prueba completa:** todos los incendios seleccionados, controles, estratificación, las dos escalas y decisión.

Después, solo si la decisión es seguir: réplica de Tang, LFMC, modelo predictivo y validación cruzada por bloques.

## Reglas metodológicas

- **Criterios antes que resultados:** la selección de incendios y controles se fija y se registra antes de analizar SIF/APAR.
- **Comparar siempre con referencias:** FWI, AED y NDVI/EVI. El resultado interesante es lo que SIF/APAR aporta más allá de ellos.
- **Peligro frente a ignición:** la ocurrencia de incendios refleja también igniciones humanas. Al trabajar con incendios seleccionados y controles emparejados, documentar este sesgo.
- **Sin fuga de información** (para la fase predictiva): cada predicción usa solo datos disponibles en esa fecha, respetando la latencia real de cada producto.
- **Reproducibilidad:** parámetros en `config/config.yaml`, semillas fijas y versiones de datos registradas.

## Reglas del análisis de época

Obligatorias en las tareas 5 y 6. Evitan una antelación artificial por fuga de datos posteriores al incendio. El suavizado centrado (15 días y 3 × 3) se mantiene solo para mapas descriptivos.

1. **Sin fuga posincendio por el suavizado.**
   - Enmascarar los datos desde la fecha de enmascarado (la ignición del incendio en el análisis principal, el día 0 de la celda en el complementario y en la climatología) *antes* de calcular tendencias, ciclos estacionales, filtros o cualquier suavizado. Esto también saca de la climatología de la celda los años posteriores al incendio.
   - En el análisis de época, usar solo ventanas hacia atrás, que terminen en el día evaluado.
   - Ningún suavizado espacial a 0,25° (3 × 3 son unos 75 km). A 0,05°, como mucho 3 × 3 y siempre después de enmascarar cada celda desde su propio día 0.
2. **Sin fuga en fPAR ni en NBAR.**
   - **fPAR:** cortar la serie de compuestos en la fecha de enmascarado *antes* de interpolar a diario, quitando todo compuesto cuyo periodo termine en o después de esa fecha.
   - **Final de la serie de fPAR:** tras el último compuesto válido, repetir su valor como máximo 5 días con MODIS y 11 con VIIRS (persistencia). La prueba sin persistencia es la referencia para validar cualquier antelación, porque la persistencia sesga SIF/APAR hacia abajo, en la dirección de la señal buscada.
   - **No suavizar el fPAR para reducir su ruido**, ni siquiera con ventanas hacia atrás. Un fPAR suavizado reacciona tarde a la pérdida de estructura: se queda más alto que el real y sesga SIF/APAR hacia abajo, igual que la persistencia. El ruido se reduce solo con filtros de calidad (SCF_QC, nubes, sombras y cirros), nunca promediando en el tiempo.
   - **NBAR de MCD43A4:** cada fecha usa 16 días de observaciones, ponderadas hacia el día 9 (de *t* − 8 a *t* + 7). Enmascarar desde el día 0 − 8.
   - **Competidor óptico diario:** añadir un NDVI/EVI diario sin ajuste BRDF (MOD09GA/MYD09GA en GEE, cada plataforma por separado, con filtro de nubes y de ángulos) como competidor principal de SIF/APAR.
   - **Deriva orbital:** documentar la deriva de Terra (hacia las ~9:00) y de Aqua (hacia las ~15:50).
   - Documentar en el borrador la ventana temporal efectiva de cada producto.
3. **Alineación por ignición en el análisis principal; día 0 por celda como complemento.**
   - El día 0 del análisis principal es la ignición de cada incendio. Todas las celdas del incendio se enmascaran desde la fecha de ignición, incluida, de modo que ningún dato de la ventana previa está afectado por ese incendio, ni por quemado ni por humo.
   - El día 0 por celda (primera detección VIIRS dentro de la celda y del perímetro o, si no la hay, MCD64A1) sirve para dos cosas:
     - (a) enmascarar las celdas quemadas en la climatología y en los controles, solo si su fracción quemada supera un umbral propio de cada escala, para que un incendio pequeño no elimine una celda de 0,25° entera;
     - (b) un análisis complementario alineado por celda, marcando los días con humo entre la ignición y el día 0 de la celda.
   - **Criterios de selección añadidos:**
     - un mínimo de temporadas válidas antes del incendio en sus celdas, para que la climatología esté definida;
     - ninguna celda quemada en los 5 años anteriores (recuperación posincendio, incluidos los grandes incendios de 2017).
4. **Sin filtro de percentiles global.**
   - No usar el filtro de percentiles 1–99 calculado sobre todas las celdas y días, porque puede eliminar justo el estrés extremo de 2025.
   - Usarlo en su lugar: filtros de validez de las entradas (fPAR, PAR y número de píxeles mínimos) más un filtro robusto por celda que solo quite picos aislados.
   - No recortar los valores bajos: la SIF negativa es ruido sin sesgo.
   - Mantener el filtro global solo como prueba de sensibilidad, con un diagnóstico: fracción de datos de las ventanas previas a incendios (y de los controles) que el filtro global habría eliminado, según el día relativo al día 0.

## Riesgos conocidos

- Señal SIF débil en vegetación dispersa (zonas semiáridas). Estratificar y centrarse en matorral y arbolado.
- Pastos y cereal curados son combustible muerto, así que su fisiología no informa.
- Respuesta fisiológica más lenta en zonas áridas, según el propio artículo.
- Nubosidad y ruido diario de SIF; el suavizado de 15 días reduce la ventaja temporal.
- Desajuste de escala entre píxel e incendio.
- Climatología corta para las anomalías.
- Muestra de incendios pequeña y seleccionada a mano.
- Fin de MODIS.

## Estructura de repositorio

```
physiofire/
├── CLAUDE.md
├── README.md
├── environment.yml
├── config/config.yaml        # región, periodo, rutas, parámetros, criterios de selección
├── docs/                     # versionado; borradores personales excluidos de git
├── data/                     # fuera de git, salvo data/fires/selected_fires.csv
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── fires/
├── src/physiofire/
│   ├── download/             # un módulo por fuente
│   ├── preprocess/           # recorte, rejilla común, máscaras, QC
│   ├── indices.py            # SIF/APAR, EVI, AED, FWI
│   ├── anomalies.py
│   └── anomalies.py
├── R/                        # tabla de incendios (fechas, selección, controles),
│                             # época superpuesta, estratificación y figuras (renv)
├── notebooks/                # exploración, numerados
├── figures/
└── tests/
```

Stack: Python 3.11 (`environment.yml`) con xarray, dask, rioxarray, zarr, netCDF4, pandas, geopandas, scipy, statsmodels, scikit-learn, matplotlib (solo vistas rápidas), cdsapi, earthaccess y earthengine-api; R 4.6 (`renv.lock`) con yaml, sf, terra, dplyr, tidyr, readr, ggplot2 y patchwork. Añadir una implementación del FWI canadiense solo tras verificar cuál usar.

## Decisiones tomadas (7 de noviembre de 2026)

- **Caso 2025:** en lugar de una selección manual, todos los incendios de la lista corta de EFFIS > 2000 ha del estrato matorral (matorral y brezal) con fecha de ignición válida, sin marca de coherencia y con ≥ 3 controles (`Rscript R/select_fires.R` → `data/fires/selected_fires.csv`). Regla general de exclusión: ignición más de 7 días antes de la fecha de EFFIS sin confirmación independiente (`epoch.selection.max_days_before_effis`). Muestra final: 22 incendios (24 menos Oímbra y Murias de Paredes); exclusiones a mano solo con motivo registrado.
- **Fecha de ignición:** la más temprana entre EFFIS, VIIRS, MCD64A1 y VNP64A1 (el error peligroso es una fecha tardía).
- **Escala:** 0,05°. **Anomalías:** mediana por día del año; LOESS como sensibilidad.
- **Umbrales** (en `config.yaml`, sección `epoch`): celda quemada ≥ 25 %; controles 3–5 por incendio, a 10–50 km, 0 % quemado desde 2017 (EFFIS, MCD64A1, VNP64A1 y ESFire30), misma clase dominante de FirEUrisk, aridez ±15 % (relativa al índice de las celdas quemadas) y altitud ±200 m; antelación = primer día desde el que el efecto se mantiene ≥ 0,5 DE hasta el día −1.
- **Vegetación:** mapa de combustibles de FirEUrisk agrupado en bosque cerrado, bosque abierto, matorral, brezal y zonas húmedas, pastizal, cultivos y sin combustible (`config.yaml`, `epoch.fuel.classes`); estratos: arbolado = bosque cerrado o abierto, matorral = matorral o brezal, pasto = pastizal. CORINE 2018 como apoyo. **Aridez:** Global-AI v3.1. **PAR:** ERA5-Land. **LOESS:** tendencia ajustada antes del día −60, como sensibilidad. **ESFire30:** desde 2017 hasta el año del incendio.
- **Información más allá del FWI:** comparación descriptiva (diferencia incendio–control del FWI y de SIF/APAR en la misma figura); el AUC por clase de FWI, a la prueba completa.
- **Arbolado:** pasa a la prueba completa (backlog 35); en 2025 solo 2 de los 5 incendios de arbolado tenían controles. El caso 2025 se centra en el estrato matorral.
- **FWI:** el propio (ERA5-Land, 0,1°) pasa al análisis principal; el de EFFIS/CEMS, a sensibilidad (R17).
- **Celdas quemadas con quemas previas:** se quitan las que tienen ≥ 25 % quemado en los 5 años anteriores (MCD64A1, VNP64A1, EFFIS o ESFire30); el incendio se mantiene si le quedan celdas (`epoch.prior_burn`). En 2025 quita 7 de 140 celdas y ningún incendio.
- **NDVI/EVI:** competidor principal = combinado Terra + Aqua (media si hay ambos, el disponible si no); Terra y Aqua por separado y NBAR, como sensibilidad.
- **AED:** ET0 FAO-56 con ERA5-Land (0,1°, misma fuente que FWI y PAR); GLEAM v4.3a como contraste para 2018–2024 (backlog). Si el grupo aporta una AED propia, se valora.
- **Umbrales de validez de SIF/APAR:** derivados de celdas no quemadas ajenas al análisis, pendientes de aprobación antes de extraer series de incendios.
- **Nieve:** sin máscara específica en el caso 2025 (ventanas de junio a agosto); GlobSnow, al backlog.

## Decisiones pendientes con el investigador

- Fuente de la cartografía de Portugal, o EFFIS para ambos países.
- Fuente meteorológica del análisis principal (ERA5-Land, o AEMET + IPMA).
- Arbolado en el caso 2025 (ver "Decisiones tomadas").

## Contexto adicional

- Colaboradores potenciales: Sergio Vicente-Serrano (IPE-CSIC, sequía y demanda evaporativa atmosférica), Wouter H. Maes (UAV Research Centre, Universidad de Gante, fluorescencia), Diego G. Miralles (H-CEL, Universidad de Gante, GLEAM) y el equipo de EFFIS en el JRC.
- La misión FLEX de la ESA (lanzada en septiembre de 2026) podrá usarse más adelante para bajar de escala.
- En `docs/` están la hoja de ruta 2026–2028 y el artículo de Tang et al.
