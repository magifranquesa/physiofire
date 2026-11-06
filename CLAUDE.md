# PHYSIOFIRE – Prueba de concepto

Este archivo da contexto a Claude Code sobre el proyecto. Léelo entero antes de proponer o escribir código. La sección "Objetivo de la prueba de concepto" manda sobre todo lo demás.

## Cómo trabajar conmigo

- Comunícate en español. Código, nombres de variables y comentarios en el código, en inglés.
- Soy investigador postdoctoral (doctorado en 2022) en el Instituto Pirenaico de Ecología (IPE-CSIC). Sé teledetección y Python, pero explica brevemente las decisiones metodológicas y de diseño.
- No inventes nombres de productos, versiones, variables ni URLs. Si no estás seguro de un dataset o de su acceso, dilo y propón cómo verificarlo. Varias fuentes de abajo están marcadas como **(verificar)**.
- Prioriza pasos pequeños y comprobables: descarga una muestra, inspecciona las variables y luego escala.
- Antes de descargas grandes, estima el volumen y pregúntame.
- Infraestructura mínima: construye solo lo que necesita el análisis de la prueba de concepto.
- Entorno: Windows. Miniconda en `C:\ProgramData\miniconda3` (fuera del PATH; llamarlo por ruta completa). Usar conda-forge. Entorno conda `physiofire` solo para Python. R (versión actual de CRAN, binarios de CRAN) con renv y `renv.lock`; no meter R en conda (r-terra no se mantiene en conda-forge para Windows).
- Lenguajes: el investigador trabaja habitualmente en R. Figuras y todo el código para publicar (tabla de incendios, época superpuesta, estadística) en R, salvo que otro lenguaje sea mejor o imprescindible. Python para descarga y procesado de rejillas (earthaccess, cdsapi, xarray, rejillado de TROPOMI). Intercambio en NetCDF (CF) y CSV.

## Objetivo científico

Evaluar si el estado fisiológico de la vegetación observado desde satélite permite anticipar el peligro de incendio mejor y antes que los índices meteorológicos (FWI) y los índices de vegetación ópticos (NDVI, EVI).

**Hipótesis:** la anomalía de SIF/APAR (rendimiento aparente de fluorescencia) anticipa el secado del combustible vivo y aporta información sobre el peligro de incendio que no está ya contenida en el FWI y el VPD, con antelación de días a 1–2 semanas, sobre todo en matorral y arbolado.

**Motivación:** el FWI usa solo meteorología y no observa la vegetación viva. Los productos de humedad del combustible vivo (LFMC) y los índices ópticos detectan el estrés tarde.

**Para qué sirve el resultado:** un artículo con el investigador como autor de correspondencia (envío hacia mayo–junio de 2027), resultados preliminares para una beca MSCA postdoctoral (cierre habitual en septiembre de 2027) y un resumen para la EGU (plazo habitual en enero de 2027).

## Objetivo de la prueba de concepto (prioridad absoluta)

Responder a una pregunta para decidir si seguir:

> ¿La anomalía de SIF/APAR se separa de lo normal antes de los incendios, con más antelación que el NDVI/EVI, y aporta información que el FWI no tiene?

**Análisis mínimo (época superpuesta):**
- Muestra de incendios de la Península Ibérica (España y Portugal) seleccionados manualmente con criterios fijados de antemano (ver "Incendios").
- Para cada incendio, anomalías de SIF/APAR, NDVI/EVI, FWI y VPD en los 60 días previos a la fecha de inicio.
- Controles sin incendio emparejados por vegetación, región y fecha.

**Resultados:**
1. Días de antelación con que cada variable se separa de los controles.
2. Capacidad de SIF/APAR para distinguir incendio de no incendio dentro de cada clase de FWI.
3. Todo estratificado por tipo de vegetación (matorral, arbolado y pasto como control negativo) y por país.

**Criterio de decisión:** seguir si SIF/APAR se adelanta al NDVI/EVI y discrimina dentro de las clases de FWI, al menos en matorral y arbolado. Si no, replantear (otra resolución, SIF/PAR, otra región) antes de invertir más. Un resultado negativo también es publicable.

**Fuera de alcance por ahora:** réplica de la correlación cruzada de Tang, ESI/GLEAM, LFMC, modelo predictivo, bajada de escala, sistema operativo, visor y FLEX.

**Hitos:**

| Hito | Contenido | Fecha |
| --- | --- | --- |
| Caso 2022 | Mapas y compuestos de los incendios seleccionados de 2022 | mediados de enero de 2027 |
| Prueba completa | Todos los incendios seleccionados y decisión de seguir o replantear | marzo de 2027 |
| Artículo | Envío como autor de correspondencia | mayo–junio de 2027 |

## Incendios

- **España:** cartografía anual de incendios de Ochoa et al. El investigador es colaborador y los datos están disponibles en el grupo.
- **Portugal:** cartografía de incendios disponible (fuente concreta a confirmar con el investigador).
- **Fecha de inicio:** imprescindible para el análisis. Si una cartografía no la incluye, asignarla cruzando cada perímetro con la primera detección de FIRMS VIIRS y, si es posible, con la EGIF (España) o el ICNF (Portugal) **(verificar)**.
- **Selección manual.** La cartografía tiene incertidumbre, así que se seleccionan incendios a mano, pero con criterios escritos **antes** de mirar SIF/APAR:
  - superficie mínima (a fijar; priorizar grandes incendios por la escala de 0,25°);
  - fecha confirmada por al menos dos fuentes;
  - vegetación dominante clara;
  - sin solape con otros incendios en la ventana de 60 días.
- **Muestra equilibrada:** matorral, arbolado y pasto; España y Portugal; varias regiones y años.
- **Registro:** una tabla de incendios versionada (por ejemplo `data/fires/selected_fires.csv`) con identificador, país, fecha, superficie, vegetación, fuentes de la fecha y criterios que cumple. Irá como material suplementario.
- **Periodo:** TROPOMI empieza en mayo de 2018. Los incendios de 2018 solo valen si la ventana de 60 días queda dentro del periodo con datos (por ejemplo, Monchique en agosto de 2018). Incluir también 2022 y 2024 (grandes incendios en ambos países).

## Meteorología y FWI

- **Análisis principal:** fuente homogénea para toda la Península, para que las diferencias entre países no se confundan con efectos reales. Opciones: ERA5-Land, o AEMET (España) + IPMA (Portugal) si son comparables. Decisión pendiente con el investigador.
- **Robustez:** datos de AEMET disponibles en el grupo (que trabaja con AEMET) para repetir el análisis en España con meteorología de mayor calidad.
- **VPD:** calcularlo a partir de temperatura y humedad (o punto de rocío).
- **FWI propio:** calcularlo con el sistema canadiense. Verificar que los datos tienen valores a mediodía de temperatura, humedad relativa y viento, y precipitación de 24 h.
- **FWI de referencia:** el de EFFIS / Copernicus EMS, porque es la referencia operativa que el índice tendría que mejorar. Nombre exacto del dataset **(verificar)**.

## Base científica: Tang et al. (2026)

Tang, Z., Miralles, D. G., Guo, Z. & Maes, W. H. (2026). *Fast response of satellite fluorescence-derived plant physiology to drought stress.* Nature Communications 17:2886. https://doi.org/10.1038/s41467-026-70076-0

Código y datos del artículo: https://doi.org/10.5281/zenodo.18327559 (un zip de 71 MB, licencia CC BY 4.0; citar si se reutiliza código). Revisarlo es útil pero no prioritario.

Resultados clave:
- Descomponen SIF = PAR × fPAR × SIFyield. Entonces SIF/APAR = SIF / (PAR × fPAR) aísla el rendimiento de fluorescencia (proxy fisiológico). SIF/PAR mezcla estructura y fisiología.
- Moda global del tiempo de respuesta a la sequía: SIF/APAR unos 3 días frente al VPD (unos 5 frente a la humedad del suelo), EVI unos 8 días y LAI unos 12–13 días.
- SIF sin corregir y SIF/PAR se comportan como el EVI porque conservan fPAR.
- La fisiología se alinea con el VPD; la estructura, con la humedad del suelo.
- Respuestas más rápidas en zonas húmedas, más lentas en zonas áridas. Esto es una limitación para la Península.

Pasos del método que se usan en la prueba de concepto:
1. SIF diario de TROPOMI (TROPOSIF, 743 nm, corregido por duración del día), desde el 1 de mayo de 2018.
2. Excluir datos con calidad < 0,5 y fracción de nubes > 50 %. Máscaras de nieve, agua y suelo desnudo. El artículo usa SWE de GlobSnow para la nieve; en la Península probablemente baste con la nieve de ERA5-Land (decisión pendiente).
3. PAR de CERES SYN1deg Ed4.1 (suma de PAR directa y difusa, cielo real), diario, 1°, interpolado a la rejilla de trabajo.
4. fPAR de MODIS MCD15A3H (4 días, 500 m), remuestreado e interpolado linealmente a diario.
5. SIF/APAR = SIF / (PAR × fPAR); descartar valores fuera de los percentiles 1–99.
6. Anomalías: tendencia con LOESS (ventana del 40 % del periodo) y resta del ciclo estacional medio diario. Suavizado de 15 días y 3 × 3 píxeles. La climatología es corta (desde 2018): documentarlo y probar una alternativa, por ejemplo anomalías respecto a la mediana del periodo.

## Escala

- **Base:** 0,25°, como el artículo. Un píxel mide unos 25 × 25 km, mucho más que la mayoría de incendios.
- **Alternativa:** rejillado más fino de TROPOMI (en torno a 0,05°), con más ruido.
- Probar las dos con los mismos incendios.

## Datos

| Variable | Fuente | Notas |
| --- | --- | --- |
| Incendios (España) | Cartografía anual de Ochoa et al. (datos del grupo) | Fecha de inicio a confirmar |
| Incendios (Portugal) | Cartografía a confirmar con el investigador | Fecha de inicio a confirmar |
| Fecha de inicio | NASA FIRMS (VIIRS); EGIF (MITECO); ICNF | Acceso a EGIF e ICNF **(verificar)** |
| SIF | TROPOSIF (TROPOMI): https://data-portal.s5p-pal.com/products/troposif.html | Producto rejillado o L2 por órbita, cobertura y latencia **(verificar)** |
| PAR | CERES SYN1deg Ed4.1: https://ceres-tool.larc.nasa.gov/ord-tool/jsp/SYN1degEd41Selection.jsp | Diario, 1°; fecha final disponible **(verificar)** |
| fPAR | MODIS MCD15A3H v061 (LP DAAC) | Fin de MODIS; VIIRS VNP15A2H como alternativa **(verificar)** |
| NDVI, EVI | MODIS MCD43C4 v061 (diario, 0,05°) | Fórmula de EVI en el artículo |
| Meteorología | ERA5-Land, AEMET (grupo), IPMA | Ver "Meteorología y FWI" |
| FWI de referencia | EFFIS / Copernicus EMS en el CDS | **(verificar)** |
| Cobertura del suelo | CORINE o ESA WorldCover; MODIS MCD12C1 como en el artículo | Para estratificar y emparejar controles |

Cuentas necesarias (probablemente): NASA Earthdata, Copernicus CDS y quizá el portal S5P-PAL.

## Plan de trabajo

1. **Entorno y repositorio** (mínimo).
2. **Tabla de incendios:** cargar las cartografías, fijar los criterios de selección por escrito, asignar fechas y construir `selected_fires.csv`. Empezar por 2022.
3. **Verificar fuentes de satélite y meteorología:** TROPOSIF, CERES, MCD15A3H, MCD43C4, FWI de EFFIS y la fuente meteorológica elegida.
4. **Cadena de SIF/APAR de punta a punta** con un mes de muestra (julio de 2022).
5. **Caso 2022:** anomalías de todas las variables para los incendios de 2022 y sus controles; primeras figuras de época superpuesta.
6. **Prueba completa:** todos los incendios seleccionados, controles, estratificación, las dos escalas y decisión.

Después, solo si la decisión es seguir: réplica de Tang, LFMC, modelo predictivo y validación cruzada por bloques.

## Reglas metodológicas

- **Criterios antes que resultados:** la selección de incendios y controles se fija y se registra antes de analizar SIF/APAR.
- **Comparar siempre con referencias:** FWI, VPD y NDVI/EVI. El resultado interesante es lo que SIF/APAR aporta más allá de ellos.
- **Peligro frente a ignición:** la ocurrencia de incendios refleja también igniciones humanas. Al trabajar con incendios seleccionados y controles emparejados, documentar este sesgo.
- **Sin fuga de información** (para la fase predictiva): cada predicción usa solo datos disponibles en esa fecha, respetando la latencia real de cada producto.
- **Reproducibilidad:** parámetros en `config/config.yaml`, semillas fijas y versiones de datos registradas.

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
│   ├── indices.py            # SIF/APAR, EVI, VPD, FWI
│   ├── anomalies.py
│   └── anomalies.py
├── R/                        # tabla de incendios (fechas, selección, controles),
│                             # época superpuesta, estratificación y figuras
├── notebooks/                # exploración, numerados
├── figures/
└── tests/
```

Stack: Python 3.11 (`environment.yml`) con xarray, dask, rioxarray, zarr, netCDF4, pandas, geopandas, scipy, statsmodels, scikit-learn, matplotlib (solo vistas rápidas), cdsapi y earthaccess; R actual (`renv.lock`) con yaml, sf, terra, dplyr, tidyr, readr, ggplot2 y patchwork. Añadir una implementación del FWI canadiense solo tras verificar cuál usar.

## Decisiones pendientes con el investigador

- Fuente de la cartografía de Portugal.
- Si las cartografías incluyen la fecha de inicio de cada incendio.
- Fuente meteorológica del análisis principal (ERA5-Land, o AEMET + IPMA).
- Superficie mínima y resto de umbrales de selección.
- Máscara de nieve (ERA5-Land o GlobSnow).

## Contexto adicional

- Colaboradores potenciales: Sergio Vicente-Serrano (IPE-CSIC, sequía y VPD), Wouter H. Maes (UAV Research Centre, Universidad de Gante, fluorescencia), Diego G. Miralles (H-CEL, Universidad de Gante, GLEAM) y el equipo de EFFIS en el JRC.
- La misión FLEX de la ESA (lanzada en septiembre de 2026) podrá usarse más adelante para bajar de escala.
- En `docs/` están la hoja de ruta 2026–2028 y el artículo de Tang et al.
