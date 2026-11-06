# Fuentes de datos: verificación (tarea 3)

Verificado el 6 de noviembre de 2026 a partir de documentación oficial, catálogos STAC/CMR y metadatos. **No se ha descargado ningún dato.** Etiquetas: ✅ verificado en esta revisión · ⚠️ verificado con matices · ❓ pendiente (se resuelve con un archivo de muestra o con el portal).

Volúmenes: tamaño de los archivos tal como se descargan, antes de recortar a la Península. Periodo completo = mayo de 2018 a finales de 2026 (unos 3100 días).

## Resumen

| Producto | Estado | Acceso | Volumen julio 2022 | Volumen periodo completo | Problema principal |
| --- | --- | --- | --- | --- | --- |
| TROPOSIF L2B | ✅ | STAC S5P-PAL, sin cuenta | 12,3 GB | ~1,2 TB | Archivos diarios globales de ~400 MB; sin rejillar |
| CERES SYN1deg-Day Ed4B | ⚠️ | ASDC / herramienta de pedidos, cuenta | <0,1 GB recortado | <1 GB recortado | Ed4.1 sustituida; cambio de entradas en abril de 2022 |
| MCD15A3H v061 | ✅ | LP DAAC (Earthdata) | 0,19 GB | ~19 GB | Ninguno grave; sigue produciéndose |
| MCD43C4 v061 | ✅ | LP DAAC (Earthdata) | 2,8 GB | ~280 GB | Archivos diarios globales de ~91 MB |
| FWI CEMS | ⚠️ | EWDS (no CDS) | pequeño | pequeño | Versión vigente y nombres de API por confirmar |
| ERA5-Land | ❓ | CDS | pequeño | pequeño | Pendiente de revisar en el CDS |
| FIRMS VIIRS | ✅ | Archivo histórico (Earthdata o correo) o API con MAP_KEY | pequeño | pequeño | API limitada a 5 días por petición |

## TROPOSIF (SIF de TROPOMI)

Fuentes: manual de producto (PUM v1.0, `S5P_PUM_PAL_NOV_UPV_SIF_v10.pdf`), página del producto y catálogo STAC `https://data-portal.s5p-pal.com/api/s5p-l2`.

- **Colecciones STAC** ✅: `L2__SIF___` (L2, por órbita) y `L2B_SIF___` (L2B, diario). Ambas empiezan el 30 de abril de 2018. No hay producto L3 rejillado (el catálogo `s5p-l3` devuelve 404).
- **Versión del procesador** ✅: v01.00.01 (14 de julio de 2023), reprocesada para toda la misión. Ejemplo de identificador: `S5P_PAL__L2B_SIF____20220701T010600_20220702T004657_20230913T084229`.
- **Cobertura y latencia** ✅: 365 archivos L2B en 2025; en 2026 hay 302 hasta el 3 de noviembre (latencia de unos 3 días). El portal avisa de que faltan algunas órbitas.
- **Acceso** ✅: STAC con descarga HTTPS directa (asset `product`). Ni el portal ni la documentación de la API mencionan registro, y los ejemplos usan peticiones sin autenticación. No hay recorte espacial en el servidor.
- **Formato** ✅: NetCDF-4/HDF5 con grupos. **El L2B no está rejillado**: es una lista de píxeles (`n_elem`) de todas las órbitas del día.
- **Variables del L2B** ✅ (grupo `PRODUCT` y subgrupos):
  - `SIF_743` (SIF instantánea) y `SIF_Corr_743` (corregida por duración del día, la que usa Tang); también `SIF_ERROR_743`. Las mismas para la ventana de 735 nm.
  - `latitude`, `longitude`, `latitude_bounds` y `longitude_bounds` (4 esquinas), `delta_time`.
  - Geometría: `solar_zenith_angle`, `viewing_zenith_angle`, `relative_azimuth_angle`.
  - `SUPPORT_DATA/INPUT_DATA`: `cloud_fraction_L2` (fracción de nubes radiométrica efectiva) y `LC_MASK` (MODIS MCD12C1 de 2018, clases 1–16).
- **Calidad** ✅:
  - `qa_value` va de 0 a 1 y se calcula restando penalizaciones de 0,5 o 1,0 (VZA > 60°, SZA > 70°, radiancia fuera de rango, χ² fuera de 0,6–2, SIF fuera de ±10).
  - El L2B **ya incluye solo los píxeles con qa > 0,5**, así que no trae la variable de calidad.
  - Las nubes **no** entran en `qa_value`, así que el filtro de fracción de nubes ≤ 0,5 de Tang se aplica con `cloud_fraction_L2`.
- **Diferencia con Tang** ⚠️: Tang excluye la calidad < 0,5 (conserva qa = 0,5), mientras que el L2B exige qa > 0,5. Las penalizaciones son múltiplos de 0,5, así que el L2B descarta además los píxeles con una sola penalización (sobre todo bordes de pasada con VZA > 60°). Es una diferencia menor; para reproducir exactamente el criterio habría que usar el L2.
- **Resolución** ✅: el atributo `summary` del L2 indica 7,0 × 3,5 km. El paso a 5,5 × 3,5 km desde agosto de 2019 es conocimiento general de TROPOMI, no está en el manual. Con píxeles de ese tamaño, la rejilla de 0,05° (~4,5 × 5,5 km) tendrá muchas celdas sin observación cada día: el rejillado fino es viable, pero con mucho ruido.
- **Volumen** ✅: 31 archivos L2B en julio de 2022 suman **12,3 GB** (398 MB de media). El periodo completo serían **~1,2 TB de descarga**. El L2 no ahorra nada: unos 266 MB por órbita, con varias órbitas al día sobre la Península.
- **Implicación**: descargar cada día, recortar a la Península en cuanto llega y borrar el original. Lo que se guarda recortado es mucho menor (orden de unos pocos MB al día, por confirmar con la muestra). Se puede preguntar a support@s5p-pal.com si existe algún servicio de recorte.

## CERES SYN1deg (PAR)

Fuentes: página de datos de CERES, herramienta de pedidos y resumen de calidad (DQS) de SYN1deg Ed4A (versión del 8 de mayo de 2025), y CMR.

- **Ed4.1 ya no se ofrece** ⚠️: la herramienta `SYN1degEd41Selection.jsp` devuelve 404 y la web enlaza `SYN1degEd42Selection.jsp`.
  - El DQS indica: "SYN1deg Edition4B (Edition4.2 on the ordering tool)", publicada el 7 de mayo de 2025.
  - Por tanto, el "Ed4.1" de la herramienta corresponde a Ed4A (Terra-Aqua), que es la que usó Tang.
- **Colección en CMR** ✅: `CER_SYN1deg-Day_Terra-Aqua-NOAA20` `Edition4B` (proveedor LARC_CLOUD). Datos desde el 1 de marzo de 2000 hasta el **31 de agosto de 2026** (latencia de unos 2 meses). Un día global ocupa ~95 MB.
  - En CMR no aparece la serie diaria Ed4A; si sigue disponible en otro sitio ❓.
- **Discontinuidad en 2022** ⚠️: desde **abril de 2022**, Ed4B deja de usar Terra y Aqua (solo NOAA-20) y pasa a usar el reanálisis MERRA-2 para nubes y flujos. Es un cambio de entradas justo en la temporada del caso de estudio.
  - El propio DQS advierte de que los cambios de entradas pueden introducir saltos espurios.
  - Hay que comprobar si existe un salto en el PAR sobre la Península en marzo–abril de 2022 antes de calcular anomalías.
- **Variables PAR** ❓: la página de datos lista "PAR Direct/Diffuse Fluxes" entre los flujos de superficie calculados.
  - Los nombres exactos de las variables de cielo real no están en la web ni en CMR (la colección no tiene metadatos de variables).
  - Se confirman con el catálogo de producto de SYN1deg-Day o con un archivo de muestra.
- **Herramienta de pedidos** ✅: permite recortar por caja de coordenadas sobre la rejilla de 1°, elegir resolución diaria y descargar NetCDF3 (hasta 2 GB por pedido).
  - Requiere iniciar sesión, pero no consta que sea con la cuenta de Earthdata ❓.
  - En octubre de 2026 tenía un aviso de mantenimiento con posibles retrasos.
- **Alternativa**: descargar los gránulos diarios globales de CMR (~95 MB/día, ~300 GB el periodo completo) con earthaccess y recortar. Solo compensa si la herramienta de pedidos no funciona.
- **Comprobación de robustez** ❓: ERA5 (niveles únicos, no ERA5-Land) tiene un parámetro de PAR en superficie. Habría que verificarlo; serviría para detectar el posible salto de 2022.

## MODIS MCD15A3H v061 (fPAR)

Fuente: CMR (consultas con earthaccess, solo metadatos).

- **Colección** ✅: `MCD15A3H` v061, "MODIS/Terra+Aqua Leaf Area Index/FPAR 4-Day L4 Global 500m SIN Grid V061", proveedor LPCLOUD, concepto `C2343110937-LPCLOUD`. Datos desde el 4 de julio de 2002.
- **Teselas que cubren la Península** ✅: h17v04, h17v05, h18v04 y h18v05. En julio de 2022: 32 gránulos, **190 MB** (de 2,5 a 12 MB cada uno). El periodo completo serían ~19 GB.
- **Continuidad** ✅: gránulos hasta el **28 de octubre de 2026**; el producto sigue generándose.
- **Formato** ✅: HDF4-EOS. Se lee con el plugin `libgdal-hdf4` (instalado en el entorno) y con terra en R.
- **Capas de calidad** ❓: se confirmarán con un archivo de muestra; no he encontrado la lista exacta en esta revisión.
- **Alternativa VIIRS** ✅: `VNP15A2H` v002, "VIIRS/NPP Leaf Area Index/FPAR 8-Day L4 Global 500m SIN Grid V002", desde 2012. Es **8-diario**, no 4-diario, lo que reduce la resolución temporal del fPAR. En julio de 2022: 16 gránulos, 96 MB.
- **Acceso**: LP DAAC (cuenta de NASA Earthdata).

## MODIS MCD43C4 v061 (NDVI, EVI)

- **Colección** ✅: `MCD43C4` v061, "MODIS/Terra+Aqua BRDF/Albedo Nadir BRDF-Adjusted Ref Daily L3 Global 0.05Deg CMG V061", concepto `C2532449179-LPCLOUD`. Datos desde el 16 de febrero de 2000 hasta el 28 de octubre de 2026.
- **Volumen** ✅: archivos globales de ~91 MB por día. Julio de 2022 son unos 2,8 GB y el periodo completo **~280 GB**, de los que solo se conserva la Península.
- **Alternativa VIIRS** ✅: `VNP43C4` v002, desde el 19 de enero de 2012.
- **Bandas de reflectancia y calidad** ❓: se confirmarán con un archivo de muestra.

## FWI de referencia (Copernicus EMS)

Fuentes: página del dataset en el EWDS y guía de usuario de ECMWF (Confluence, actualizada en febrero de 2024).

- **Dataset** ✅: "Fire danger indices historical data from the Copernicus Emergency Management Service", identificador `cems-fire-historical-v1`, DOI 10.24381/cds.0e89c522, licencia CC-BY.
- **Plataforma** ⚠️: está en el **EWDS** (Early Warning Data Store, `ewds.climate.copernicus.eu`), **no en el CDS**.
  - No he podido confirmar si basta la cuenta y la clave del CDS ni cuál es la URL de la API ❓.
  - Los ejemplos de la guía usan `cdsapi`.
- **Contenido** ✅: datos diarios desde 1940, actualizados a diario. Reanálisis a 0,25° (rejilla regular interpolada desde N320) y miembros del conjunto a 0,5°. NetCDF solo en la rejilla interpolada, GRIB2 en todas.
- **Base meteorológica** ✅: ERA5, no ERA5-Land. Las entradas se toman a las **12 hora local**.
- **Variables** ⚠️: FWI y sus subíndices (FFMC, DMC, DC, ISI, BUI), entre otras variables.
  - En la API solo está confirmado `fire_weather_index`.
  - El ejemplo de la guía usa `system_version: '4_1'` y `dataset_type: 'consolidated_dataset'`; la versión vigente está por confirmar ❓.
- **Discrepancia** ❓: la guía pide `grid: '0.5/0.5'` en un ejemplo, mientras que la ficha indica 0,25° para el reanálisis. Se resuelve en la pestaña de descarga.

## Meteorología: ERA5-Land

❓ **No revisado en esta ronda.** Queda pendiente de verificar en el CDS: el identificador (`reanalysis-era5-land`, según el uso habitual), las variables horarias necesarias, el formato de la precipitación acumulada y la latencia.

- **Variables necesarias:** temperatura a 2 m, punto de rocío a 2 m, viento a 10 m (u, v), precipitación total y nieve (para la máscara).
- **Para el FWI propio** hay dos detalles conocidos que hay que confirmar:
  - la precipitación de ERA5-Land se acumula desde las 00 UTC, así que hay que desacumularla para obtener la de 24 h;
  - el mediodía solar en la Península queda entre unos 11:20 y 12:40 UTC.

## Fecha de inicio: NASA FIRMS (VIIRS)

Fuentes: páginas oficiales de FIRMS (`/api/`, `/api/map_key/`, `/api/area/`, `/download/`).

- **Productos** ✅:
  - `VIIRS_SNPP_SP` / `_NRT`: S-NPP de 375 m, del 20 de enero de 2012 al 2 de noviembre de 2026.
  - `VIIRS_NOAA20_SP` / `_NRT`: desde el 1 de abril de 2018.
  - `VIIRS_NOAA21_SP` / `_NRT`: desde el 1 de marzo de 2023.
  - Los datos NRT se sustituyen por los de calidad científica (SP) con unos 5 meses de retraso.
- **Archivo histórico** ✅: descarga de detecciones de más de 7 días en SHP, CSV o JSON. Requiere identificarse con **Earthdata o con un código enviado por correo**; el enlace de descarga llega por correo.
- **API por área** ✅: `/api/area/csv/[MAP_KEY]/[SOURCE]/[west,south,east,north]/[DAY_RANGE]/[DATE]`, con **DAY_RANGE de 1 a 5 días** por petición.
  - La MAP_KEY es gratuita y se pide con el correo.
  - Límite de 5000 transacciones cada 10 minutos.
- **Lista de campos** ❓: la API no la documenta (está en las tablas de atributos enlazadas); se confirmará con una descarga de prueba.
- **Recomendación**: para 2018–2024, pedir el archivo histórico por región de una sola vez (VIIRS S-NPP y NOAA-20). La API exigiría cientos de peticiones de 5 días.

## Cuentas y credenciales

| Cuenta | Para qué | Estado |
| --- | --- | --- |
| NASA Earthdata | MCD15A3H, MCD43C4 (LP DAAC); probablemente CERES; archivo de FIRMS | En creación |
| Copernicus CDS | ERA5-Land | En creación |
| Copernicus EWDS | FWI de CEMS | ❓ comprobar si sirve la cuenta de ECMWF/CDS y qué clave de API usa |
| CERES ordering tool | PAR recortado | ❓ comprobar si usa Earthdata |
| FIRMS MAP_KEY | API por área (opcional) | Solo si se usa la API |
| S5P-PAL | TROPOSIF | No parece necesaria |

## Actualización del 6 de noviembre de 2026 (tarea 4)

- **Google Earth Engine** ✅: proyecto `ee-magifranquesa`.
  - El cliente por defecto de `earthengine authenticate` (y el de gcloud) los bloquea Google.
  - Se usan credenciales de gcloud (application-default) con un cliente OAuth propio de escritorio; los pasos están en el README.
  - `ee.Initialize` necesita que se le pasen esas credenciales de forma explícita (`physiofire.download.gee.initialize`).
- **MCD43C4 no está en el catálogo de GEE** ✅. Se usa `MODIS/061/MCD43A4` (NBAR de 500 m, diario, de 2000 al 28 de octubre de 2026), agregado en GEE a 0,05°.
  - Agregación: media ponderada por área de los píxeles válidos.
  - Calidad: `BRDF_Albedo_Band_Mandatory_Quality_BandN` ≤ 1 (0 = inversión completa, 1 = inversión de magnitud).
  - Es equivalente a MCD43C4, que también se obtiene agregando MCD43A4.
- **MCD15A3H en GEE** ✅: `MODIS/061/MCD15A3H`, con las bandas `Fpar`, `Lai`, `FparLai_QC`, `FparExtra_QC`, `FparStdDev` y `LaiStdDev`.
  - Filtro: SCF_QC (bits 5–7 de `FparLai_QC`) ≤ 1, es decir, solo el algoritmo principal. Los bits están **(verificar)** con la guía de usuario de MOD15.
- **MCD12C1 en GEE** ✅: `MODIS/061/MCD12C1`, de 2001 a 2025, con el porcentaje de cada clase IGBP (`Land_Cover_Type_1_Percent_Class_0..16`) en la rejilla nativa de 0,05°.
  - ⚠️ **Pendiente:** contrastarlo con CORINE o ESA WorldCover (`ESA/WorldCover/v200` está en GEE), porque las clases IGBP pueden confundir matorral y arbolado mediterráneos (sabanas leñosas, matorral abierto).
- **ERA5-Land en GEE** ✅:
  - `ECMWF/ERA5_LAND/DAILY_AGGR` (de 1950 al 26 de octubre de 2026) trae todo lo que necesita la AED con FAO-56: `temperature_2m_min`/`_max`, `dewpoint_temperature_2m`, viento a 10 m, `surface_solar_radiation_downwards_sum`, `surface_net_solar_radiation_sum`, `surface_net_thermal_radiation_sum` y `surface_pressure`. Trae también `snow_cover` y `snow_depth_water_equivalent`.
  - `ECMWF/ERA5_LAND/HOURLY` sirve para el FWI a mediodía.
- **El ERA5 de GEE no tiene PAR** ✅: ninguna de las 292 bandas de `ECMWF/ERA5/HOURLY` es PAR.
- **PAR provisional**: PAR = 0,48 × radiación solar descendente diaria de ERA5-Land (media diaria en W/m²), interpolada bilinealmente desde 0,1°.
  - El valor 0,48 está dentro del rango habitual de la fracción energética PAR/global (0,45–0,50); falta citar la referencia.
  - Al ser un factor constante, reescala SIF/APAR de forma uniforme: no cambia la forma ni el momento de sus anomalías, pero los valores absolutos no son comparables con los de Tang.
  - Queda marcado como provisional en `config.yaml` (`par.provisional: true`) y en los atributos de los archivos de salida.
- **CERES Ed4B, volúmenes** ✅ (CMR): el diario de mayo de 2018 a agosto de 2026 son 2770 gránulos, 280 GB; el mensual, 91 gránulos, 9,6 GB (~105 MB cada uno).
  - La prueba del salto de abril de 2022 se hace con el **mensual**, frente a la radiación solar descendente mensual de ERA5-Land en la rejilla de 1° de CERES.
  - La descarga necesita Earthdata (los enlaces apuntan a `data.asdc.earthdata.nasa.gov/asdc-prod-protected/`).
- **MCD64A1 en GEE** ✅: de 2000 a agosto de 2026. Solo se usa para mantener los puntos genéricos de control lejos de celdas quemadas.

## fPAR de VIIRS (prueba de sensibilidad; verificado el 6 de noviembre de 2026)

- **VNP15A2H (S-NPP) en GEE** ✅: el asset vigente es `NASA/VIIRS/002/VNP15A2H` (colección 2), de 500 m, con datos del 17 de enero de 2012 al 24 de octubre de 2026 (679 compuestos).
  - El asset antiguo `NOAA/VIIRS/001/VNP15A2H` está **obsoleto**; GEE avisa de que lo sustituye `NASA/VIIRS/002/VNP15A2H`.
  - Existe también una versión `_RAW` (sin procesar por GEE); se usa la normal.
  - En CMR: `VNP15A2H` v002, "VIIRS/NPP Leaf Area Index/FPAR 8-Day L4 Global 500m SIN Grid V002" (LP DAAC).
- **Bandas** ✅: `Fpar`, `Lai`, `FparLai_QC`, `FparExtra_QC`, `FparStdDev` y `LaiStdDev`; los mismos nombres que en MCD15A3H.
  - `Fpar`: entero sin signo de 8 bits, rango válido 0–100, relleno 249–255, factor de escala 0,01 (guía de usuario, tabla 3).
- **Compuestos de 8 días** ✅:
  - En GEE, `system:time_end` = `system:time_start` + 8 días, así que cada compuesto cubre del inicio al inicio + 7.
  - Calendario fijo por día del año (en el periodo de muestra empiezan el 2 y el 10 de junio, etc.).
  - El producto compone retrievals diarios (PGE533) en 8 días (PGE534); guía de usuario, sección 3.3.
- **Bits de calidad: distintos de MODIS** ✅ ([VNP15 User Guide v1.1](https://lpdaac.usgs.gov/documents/126/VNP15_User_Guide.pdf), tablas 4 y 5).
  - **`FparLai_QC`:**
    - **SCF_QC en los bits 0–2:** 0 = método principal (RT) sin saturación; 1 = RT con saturación ("good, very usable"); 2 = empírico por mala geometría; 3 = empírico por otras causas; 4 = sin dato.
    - Bit 3: detector muerto.
    - Bits 4–7: tipo de bioma.
    - En **MCD15A3H**, SCF_QC está en los bits 5–7 (por verificar con la guía de MOD15). **No se puede reutilizar la máscara de MODIS tal cual.**
  - **`FparExtra_QC`:** bits 0–1 nubes (0 despejado seguro, 1 probablemente despejado, 2 probablemente nuboso, 3 nuboso seguro), bit 2 sombra de nube, bit 3 cirro fino, bits 4–5 cantidad de aerosol, bit 6 nieve o hielo.
  - ⚠️ La guía es la v1.1 (para la colección 1). No he encontrado una guía específica de la colección 2; el asset de GEE describe la misma disposición de bits.
- **NOAA-20 (VJ115A2H)** ⚠️: **no está en GEE**. Existe en LP DAAC (CMR: `VJ115A2H` v002, "VIIRS/JPSS1 Leaf Area Index/FPAR 8-Day L4 Global 500m SIN Grid V002", desde el 1 de enero de 2018).
  - Para usarlo habría que descargar las teselas con Earthdata (como MCD15A3H: 4 teselas por compuesto) y agregarlas aquí.
- **NOAA-21 (VJ215A2H)** ✅ en GEE: `NASA/VIIRS/002/VJ215A2H`, desde el 10 de febrero de 2023. No cubre la climatología desde 2018.
- **¿Aumenta la frecuencia si se combinan?** ❌ No.
  - Los compuestos de S-NPP y NOAA-21 empiezan en las mismas fechas (calendario fijo de 8 días, comprobado en junio–septiembre de 2025); NOAA-20 sigue presumiblemente el mismo calendario.
  - Combinarlos no da más de un compuesto cada 8 días. Solo mejora la cobertura y la calidad dentro de cada compuesto (más observaciones sin nubes): menos huecos, no más resolución temporal.
- **Uso:** prueba de sensibilidad al sensor de fPAR y base para una futura versión operativa tras el fin de MODIS. MCD15A3H sigue siendo la fuente principal.
- ⚠️ **Escala distinta entre los assets de GEE de MODIS y de VIIRS** (comprobado el 6 de noviembre de 2026, compuesto del 4 al 12 de julio de 2025):

  | Asset | Tipo de `Fpar` | Valores | Relleno | Tratamiento |
  | --- | --- | --- | --- | --- |
  | `MODIS/061/MCD15A3H` | entero | 0–100 | 249–255 | × 0,01; válido ≤ 100 |
  | `NASA/VIIRS/002/VNP15A2H` | real (double) | 0–1 (ya escalado) | 2,49–2,55 | **sin factor**; válido ≤ 1,0 |
  | `NASA/VIIRS/002/VNP15A2H_RAW` | entero | 0–100 | 249–255 | como MODIS (no se usa) |

  - Con el factor de la guía aplicado al asset ya escalado, el fPAR medio salía 0,004 en lugar de 0,36–0,40.
  - Lo recogen `config.yaml` (`gee.fpar_viirs.scale: 1.0`) y los metadatos de los archivos (`asset_prescaled`, `scale_factor_applied`).
  - **Comprobación automática:** `gee.py` detiene la descarga con un error que nombra el producto y la fecha si la mediana de un compuesto o día queda fuera de un rango plausible (`gee.plausible_median`: fPAR 0,05–0,95; rojo 0,01–0,40; NIR 0,05–0,60; azul 0,005–0,30). Se aplica a MCD15A3H, VNP15A2H, MCD43A4, MOD09GA y MYD09GA. `python -m physiofire.download.gee check --file ...` vuelve a comprobar archivos ya descargados.
- **Comparación con MCD15A3H** (junio–septiembre de 2025, fPAR diario interpolado; `figures/qc/qc_fpar_viirs_vs_modis.csv`):
  - **Toda la Península, a 0,25°:** sesgo mediano por celda de −0,010 (−2,4 %) y correlación mediana de 0,67. SIF/APAR con VIIRS es un 4 % mayor (mediana).
  - **Matorral:** diferencias del −2 al −5 %. La correlación de las medias de 15 días de SIF/APAR es de 0,96 a 1,00.
  - **Arbolado** (País Vasco y Girona): VIIRS es un 9–16 % más alto y SIF/APAR un 10–14 % más bajo. La forma de la serie se conserva (r de 0,90 a 0,98).
  - **Caídas de MCD15A3H en arbolado:** el fPAR de MODIS tiene caídas de 0,2 a 0,5 entre compuestos consecutivos (probablemente nubes o sombras no marcadas), que crean picos artificiales de SIF/APAR. VIIRS, de 8 días, es mucho más estable. **[TODO]** Valorar el filtro de nubes de `FparExtra_QC` en MCD15A3H.

## Diferencias con Tang et al. (2026) que hay que documentar

- CERES Ed4B (Ed4.2) en lugar de Ed4.1/Ed4A, con el cambio de entradas de abril de 2022.
- TROPOSIF L2B (qa > 0,5) en lugar de qa ≥ 0,5, si no se usa el L2.
- VPD y meteorología de ERA5-Land en lugar de AIRS.
- Nieve de ERA5-Land en lugar de GlobSnow (decisión pendiente).
- NBAR de MCD43A4 agregado en GEE en lugar de MCD43C4; LAI y fPAR agregados en GEE, como en el artículo.
- AED en lugar de VPD como variable atmosférica.
- PAR provisional a partir de ERA5-Land hasta la prueba con CERES.
