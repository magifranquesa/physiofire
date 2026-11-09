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
  - **Caídas de MCD15A3H en arbolado:** el fPAR de MODIS tiene caídas de 0,2 a 0,5 entre compuestos consecutivos (probablemente nubes o sombras no marcadas), que crean picos artificiales de SIF/APAR. VIIRS, de 8 días, es mucho más estable. (Antes del filtro de nubes; ver abajo).

## Filtro de nubes de `FparExtra_QC` (aplicado el 6 de noviembre de 2026)

**Bits verificados en las guías de usuario.** MODIS: [MOD15 C6.1 User Guide](https://lpdaac.usgs.gov/documents/926/MOD15_User_Guide_V61.pdf), tabla 5. VIIRS: VNP15 User Guide v1.1, tabla 5.

| Indicador | MCD15A3H | VNP15A2H | Filtro aplicado |
| --- | --- | --- | --- |
| Nubes | bit 5, máscara interna (0 = sin nubes) | bits 0–1, confianza (0 despejado seguro, 1 probablemente despejado, 2 probablemente nuboso, 3 nuboso seguro) | MODIS = 0; VIIRS ≤ 1 |
| Sombra de nube | bit 6 | bit 2 | = 0 |
| Cirros | bit 4 | bit 3 | = 0 |
| Aerosoles | bit 3: 0 ninguno o bajo, 1 medio o alto | bits 4–5: 0 climatología, 1 bajo, 2 medio, 3 alto | **no se aplica**; se guarda la fracción por celda (MODIS ≥ 1, VIIRS = 3) |
| Nieve o hielo | bit 2 | bit 6 | no se aplica (verano); pendiente para la serie completa |

MODIS tiene además el estado de nubes heredado de MOD09 en `FparLai_QC` (bits 3–4: 0 despejado, 1 nubes, 2 mixto, 3 no definido); de momento no se aplica.

**Efecto en junio–septiembre de 2025** (`figures/qc/qc_fpar_cloud_filter_*.csv`):

| Píxeles válidos eliminados | MODIS | VIIRS |
| --- | --- | --- |
| Total | 8,6 % | 13,5 % |
| Arbolado | 17 % | 18,5 % |
| Matorral | 7,5 % | 11,8 % |
| Cultivos | 6,5 % | 11,2 % |

- Septiembre es el mes en que más elimina (13 % en MODIS, 23 % en VIIRS).
- **Frecuencia de compuestos válidos por celda:** apenas cambia (≥ 99,3 % de celda-compuesto con dato).
- **Antigüedad del último compuesto válido antes de un posible día de ignición:** no cambia. MODIS: mediana de 3 días y percentil 90 de 5. VIIRS: mediana de 7 días y percentil 90 de 11. Los límites de persistencia (5 y 11 días) siguen siendo adecuados.
- **Aerosoles:** si se aplicara el bit de MODIS, eliminaría un 16 % adicional (30 % en arbolado; 44 % en arbolado en agosto de 2025). El indicador "alto" de VIIRS marca un 3,2 % (7 % en agosto). Por eso no se usa como máscara: el de MODIS mezcla aerosol medio y alto.
- **Caídas en los puntos de arbolado (MODIS):** se reducen pero no desaparecen. En el País Vasco, la desviación típica entre compuestos consecutivos pasa de 0,16 a 0,11, el mínimo de 0,30 a 0,54 y los cambios > 0,1 de 15 a 9. **[TODO]** Probar a añadir el estado de nubes de MOD09 (bits 3–4 de `FparLai_QC`).

## Estado de nubes de MOD09 en MCD15A3H y ruido en SIF/APAR (6 de noviembre de 2026)

**Estado de nubes de MOD09** (bits 3–4 de `FparLai_QC`; se excluyen 1 = nubes significativas y 2 = mixto; `qc_fpar_cloud_filter_mod09cs_*.csv`):
- Elimina un 2,2 % más de píxeles que el filtro de `FparExtra_QC` (1,9 % en arbolado, 1,7 % en matorral; 4,1 % en septiembre).
- La frecuencia de compuestos y la antigüedad antes de la ignición no cambian (mediana de 3 días, percentil 90 de 5).
- Las caídas en arbolado apenas cambian. País Vasco: desviación típica entre compuestos de 0,110 a 0,109 y cambios > 0,1 de 9 a 7. Girona: 0,104 y de 7 a 6.

**Ruido que llega a SIF/APAR con cada fuente de fPAR** (`qc_sif_apar_noise_by_fpar_*.csv`; mediana por celda en los días en que las tres fuentes tienen dato):

| Vegetación (0,25°) | DE de Δ log fPAR diario: MODIS / VIIRS | DE relativa de Δ de SIF/APAR, media de 7 días hacia atrás: MODIS / VIIRS | Saltos > 10 %: MODIS / VIIRS |
| --- | --- | --- | --- |
| Arbolado | 0,036 / 0,008 | 0,080 / 0,072 | 14 / 13 |
| Matorral | 0,022 / 0,009 | 0,088 / 0,087 | 18 / 18 |
| Sabanas | 0,027 / 0,008 | 0,075 / 0,072 | 12 / 10 |
| Total | 0,023 / 0,009 | 0,084 / 0,082 | 15 / 14 |

- A 0,05° las diferencias en SIF/APAR son menores del 3 %.
- Las dos versiones de MODIS (con y sin estado de nubes) dan prácticamente lo mismo.
- **Conclusión:** VIIRS da un fPAR mucho más estable, pero en SIF/APAR la mejora es modesta (≈ 10 % en arbolado a 0,25° y menos en el resto), porque domina el ruido de la SIF.

## Reflectancia diaria MOD09GA/MYD09GA: píxeles negativos e imágenes rechazadas (7 de noviembre de 2026)

**Qué pasó.** La descarga de la serie completa se detuvo en Terra (MOD09GA) el 29 de marzo de 2025. La mediana del azul en la Península era 0,0049, por debajo del límite de 0,005.

**El fallo era del día, no de escala.** Las tres bandas eran anormalmente bajas en la mitad occidental de la Península, la única despejada ese día:

| Día (Terra) | Rojo | IRC | Azul | Píxeles despejados con alguna banda negativa |
| --- | --- | --- | --- | --- |
| 28/03/2025 | 0,085 | 0,288 | 0,041 | 0,01 % |
| **29/03/2025** | **0,037** | **0,183** | **0,006** | **25,7 %** |
| 30/03/2025 | 0,096 | 0,310 | 0,046 | 0,0 % |

- Es probablemente una sobrecorrección atmosférica (la mediana del 29 de marzo está calculada ya sin los píxeles negativos).
- Si se aceptara, daría un NDVI falsamente alto (≈ 0,68 frente a ≈ 0,54).

**Frecuencia de píxeles negativos en toda la serie** (mayo de 2018 – noviembre de 2026, recuadro de la región, a 1 km, calculado en GEE con un script exploratorio no versionado):

| | MOD09GA (Terra) | MYD09GA (Aqua) |
| --- | --- | --- |
| Imágenes | 3097 | 3093 |
| Percentil 99 de la fracción de píxeles negativos | 0,3 % | 1,0 % |
| Imágenes > 10 % | 3 | 2 |

- El 29 de marzo de 2025 es el único caso con cobertura apreciable: 25,7 % de 1,16 millones de píxeles de 500 m despejados.
- Las otras imágenes por encima del 10 % tienen menos de 350 km² despejados (invierno).
- La siguiente imagen con cobertura amplia es Aqua del 2 de noviembre de 2026, con un 4,1 %.

**Filtros aplicados** (`config.yaml`, sección `gee`):
1. **Píxel** (`sr_reject_negative`): se descarta el píxel de 500 m con reflectancia negativa en cualquier banda.
2. **Imagen** (`sr_max_negative_fraction`, `sr_negative_min_pixels`): se rechaza la imagen entera si más del 10 % de sus píxeles despejados tiene alguna banda negativa, siempre que tenga al menos 10 000 píxeles despejados (unos 2500 km²).
   - El filtro de píxel por sí solo no basta: sin los negativos, el 29 de marzo pasa la comprobación de medianas (azul 0,0062), pero el día sigue sesgado.
   - Los archivos guardan la fracción de negativos por celda (variable `neg`; `neg_count` = píxeles despejados).
3. **Rangos plausibles de la mediana** (`plausible_median`): sin cambios.

**Imágenes rechazadas** (`series_rejection`):
- Una imagen que no pasa los filtros 2 o 3 se anota en `data/interim/gee/series/rejected_images.csv` (producto, fecha, variable, valor, número de celdas y motivo).
- Se excluye: no aparece como paso de tiempo en el archivo anual.
- La descarga sigue. Solo se detiene con 3 rechazos seguidos o más de 5 en un mismo producto y año, porque eso indicaría un problema sistemático (escala).
- **Rechazada hasta ahora:** MOD09GA, 29 de marzo de 2025.

**Serie homogénea.** MOD09GA 2018–2024 se descarga de nuevo con los mismos filtros. Los archivos anteriores, sin el filtro de negativos, están en `data/interim/gee/series/backup_mod09ga_nofilter/` hasta comprobar los nuevos; luego se borran.

## FIRMS: archivo descargado y limpieza (7 de noviembre de 2026)

**Descarga.** Petición en https://firms.modaps.eosdis.nasa.gov/download/ con la cuenta de Earthdata, una por país (España y Portugal; el formulario no admite varios a la vez).
- Parámetros: buffer de 0 km, del 1 de enero de 2018 al 7 de noviembre de 2026, CSV.
- Fuentes: VIIRS S-NPP (`SV-C2`), NOAA-20 (`J1V-C2`), NOAA-21 (`J2V-C2`) y MODIS C6.1 (`M-C61`).
- Cada fuente viene en dos partes: estándar (`fire_archive_*`, hasta el 31 de julio de 2026; MODIS, hasta finales de agosto) y tiempo casi real (`fire_nrt_*`, hasta el 2–7 de noviembre de 2026). Las dos partes empalman sin huecos.
- La selección por país incluye las islas: Canarias y Baleares en España, Azores y Madeira en Portugal.
- En `data/raw/firms/{spain,portugal}/`, 45 MB.

**Campos.** `latitude`, `longitude`, `brightness`, `scan`, `track`, `acq_date`, `acq_time` (UTC, HHMM), `satellite`, `instrument`, `confidence`, `version`, `bright_t31`, `frp`, `daynight` y, solo en la parte estándar, `type`.
- `type`: 0 = presunto incendio de vegetación, 2 = otra fuente terrestre estática, 3 = en el mar.
- `confidence`: en VIIRS, clases `l`, `n` y `h` (baja, nominal y alta); en MODIS, de 0 a 100.

**Limpieza** ([R/firms_clean.R](../R/firms_clean.R), sección `firms` de `config.yaml`):
1. **Solo la Península:** se conservan las celdas de la máscara peninsular con `land_fraction > 0`, lo que deja fuera las islas.
2. **Parte estándar:** se conserva solo `type = 0`.
3. **Parte en tiempo casi real (sin `type`):** se eliminan las detecciones a menos de 500 m (VIIRS) o 1000 m (MODIS) de alguna detección `type = 2` del archivo estándar de 2018–2026. Elimina un 15–16 %, una proporción parecida a la de `type = 2` en el archivo estándar (≈ 18 %). La validación fuera de muestra está en el backlog (21).
4. **Confianza:** en VIIRS se quita solo la baja; en MODIS, los valores < 30. La prueba solo con confianza alta está en el backlog (20).

**Resultado:** `data/interim/firms/firms_iberia_clean.csv`, con 425 154 detecciones (VIIRS más MODIS), y su resumen por fuente.

**Agosto de 2025, comprobación cualitativa.** En el noroeste (lat > 41,5°, lon < −6°) las detecciones VIIRS diarias pasan de ≈ 40 el 7–8 de agosto a > 1100 desde el 10, con un máximo de 7244 el 17 de agosto.

## Perímetros de EFFIS (verificado el 7 de noviembre de 2026)

**Acceso.** Hay dos vías, según la página https://forest-fire.emergency.copernicus.eu/applications/data-and-services:
- **Descarga pública directa** de la base de datos de áreas quemadas, actualizada en tiempo real:
  - Shapefile: https://forest-fire.emergency.copernicus.eu/downloads/data.request.form/effis_layer.zip (262 MB; descargado el 7 de noviembre de 2026, versión de las 03:46 UTC).
  - SpatiaLite: `effis_layer.db.zip`.
- **Formulario de solicitud** (https://forest-fire.emergency.copernicus.eu/apps/data.request.form) para "datos históricos, extractos de la base de datos o perímetros brutos". No ha hecho falta: la descarga directa trae todos los años.

**Licencia.** © Unión Europea, 1995–2026. Se permite la reutilización citando la fuente (Decisión de la Comisión de 12 de diciembre de 2011).

**Contenido** (`effis_layer/modis.ba.poly.shp`, WGS84). 109 262 perímetros de toda el área de EFFIS.
- **Fechas:** `FIREDATE` (fecha y hora de inicio, UTC), `FINALDATE` y `LASTUPDATE`.
- **Localización y superficie:** `COUNTRY` (ES, PT…), `PROVINCE`, `COMMUNE` y `AREA_HA`.
- **Cobertura afectada:** porcentajes de CORINE en `BROADLEA`, `CONIFER`, `MIXED`, `SCLEROPH`, `TRANSIT`, `OTHERNATLC`, `AGRIAREAS`, `ARTIFSURF` y `OTHERLC`.
- **Otros:** `PERCNA2K` (porcentaje en Natura 2000) y `CLASS` (`FireSeason`, `30DAYS` o `7DAYS`).

**Advertencias del readme:**
- Los perímetros salen de MODIS a 250 m y se dibujan para incendios de unas 30 ha o más, aunque hay perímetros más pequeños.
- Pueden incluir quemas agrícolas o prescritas.
- Incendios distintos entre dos actualizaciones pueden quedar fusionados en un solo perímetro.
- "Las fechas de inicio y de última actualización pueden no corresponder a la ignición y la extinción del incendio".

**Recorte** ([R/effis_firms_dates.R](../R/effis_firms_dates.R)). España y Portugal, año de `FIREDATE` de 2018 a 2026, con el punto interior del perímetro dentro de la máscara peninsular.

| Año | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ES | 102 | 418 | 466 | 897 | 1484 | 1389 | 758 | 1355 | 2149 |
| PT | 86 | 217 | 462 | 746 | 1230 | 921 | 737 | 998 | 1434 |

- Superficie total de 2025: España ≈ 399 000 ha y Portugal ≈ 283 000 ha.
- Salida en `data/interim/fires/effis_iberia_2018_2026.gpkg`.

**Fecha de EFFIS frente a la primera detección VIIRS** (2025; `data/interim/fires/effis_2025_firms_dates.csv` y su resumen):
- **Método:** para cada perímetro, se toma la primera detección VIIRS (`type = 0`, confianza no baja) dentro del perímetro, entre `FIREDATE` − 30 días y `FINALDATE` + 1 día. La ventana es exploratoria, no un criterio de selección.
- **Cobertura de VIIRS:** el 100 % de los perímetros de ≥ 500 ha tiene detecciones VIIRS dentro; los de < 100 ha, solo el 33 %.
- **Coincidencia:** la mediana de la diferencia es 0 días en todas las clases de tamaño.
  - En el 60 % de los perímetros con VIIRS, la hora de inicio de EFFIS coincide con la primera detección VIIRS con menos de 10 minutos de diferencia (63 de 108 en los de ≥ 500 ha).
  - **Por tanto, la fecha de inicio de EFFIS se deriva de las detecciones activas: EFFIS y FIRMS no son dos fuentes independientes de la fecha.**
- **Discrepancias de más de 1 día:** 14 de los 108 perímetros de ≥ 500 ha tienen VIIRS antes y 4 después.
  - VIIRS antes (hasta 28 días): probablemente un incendio anterior dentro del mismo perímetro o perímetros fusionados (por ejemplo, Oímbra, Ourense: VIIRS el 24 de julio y EFFIS el 13 de agosto).
  - VIIRS después (2–3 días): por ejemplo, Piódão y Ferreira de Aves (Portugal). Las horas de EFFIS acaban en :00 en el 18 % de los perímetros y se repiten en lotes (2025-03-31 00:00 en 58 perímetros; 2025-08-10 02:00 en varios grandes), lo que apunta a fechas asignadas por lote y no observadas.

**Consecuencia (decidido el 7 de noviembre de 2026).** Ya no se exigen dos fuentes independientes. La fecha de ignición es la más temprana entre EFFIS, VIIRS, MCD64A1 y VNP64A1, porque el error peligroso es una fecha tardía. La regla y su justificación están en el borrador de métodos (2.10); la validación con la EGIF (ESFire30, 2018–2021) queda en el backlog (22).

## Área quemada para la fecha de ignición: MCD64A1 y VNP64A1 (7 de noviembre de 2026)

- **VNP64A1 está en GEE** ✅: `NASA/VIIRS/002/VNP64A1` (colección 2), mensual, 500 m, 175 imágenes de marzo de 2012 a septiembre de 2026.
  - Bandas: `Burn_Date` (día del año), `Burn_Date_Uncertainty`, `QA`, `First_Day` y `Last_Day`.
  - No hay versión 001 en GEE.
- **MCD64A1:** `MODIS/061/MCD64A1`, de noviembre de 2000 a agosto de 2026. Bandas: `BurnDate`, `Uncertainty`, `QA`, `FirstDay` y `LastDay`.
- **Descarga** (`python -m physiofire.download.gee burn_dates --burn-product {mcd64a1,vnp64a1} --start --end`):
  - Fecha de quemado por píxel, por vecino más próximo en una rejilla de 0,005° (≈ 500 m), sin agregar.
  - En `data/interim/gee/burndate/`. Descargado de octubre de 2024 a enero de 2026 para los candidatos de 2025.
- **Comprobación:** en agosto de 2025 hay ≈ 25 000 celdas quemadas en cada producto (≈ 570 000 ha), del mismo orden que la superficie de EFFIS de ese mes.

**Tabla de candidatos de 2025** ([R/fire_candidates.R](../R/fire_candidates.R); `data/interim/fires/fire_candidates_2025.csv`):

| Tamaño | Perímetros | Fecha más temprana anterior a EFFIS | Más de 1 día antes | Con marca de coherencia | Para revisar (> 3 días antes, sin marca) |
| --- | --- | --- | --- | --- | --- |
| < 100 ha | 2093 | 24 | 19 | 16 | 18 |
| 100–500 ha | 152 | 36 | 19 | 3 | 9 |
| 500–1000 ha | 29 | 15 | 10 | 2 | 3 |
| 1000–5000 ha | 54 | 38 | 20 | 0 | 8 |
| ≥ 5000 ha | 25 | 18 | 9 | 5 | 4 |

- **Diferencia con EFFIS por fuente** (mediana, perímetros de ≥ 500 ha): VIIRS 0 días, MCD64A1 −1 día, VNP64A1 0 días.
- **Marcados de ≥ 500 ha:** los 7 lo están por entre 1 y 11 detecciones VIIRS entre 90 y 30 días antes, frente a cientos o miles dentro del incendio. Ninguno por MCD64A1 ni VNP64A1.

## Campos estáticos para los controles (7 de noviembre de 2026)

**Script:** `python -m physiofire.download.gee static`. Escribe `data/interim/gee/static_{base,fine}.nc`.
- **Altitud media:** `CGIAR/SRTM90_V4`, banda `elevation`, media por área. SRTM a 30 m (`USGS/SRTMGL1_003`) agota la memoria de usuario de GEE al agregar a 0,05°.
- **Índice de aridez:** P / |PET| con `ECMWF/ERA5_LAND/MONTHLY_AGGR` (`total_precipitation_sum` y `potential_evaporation_sum`, esta negativa por convención), sumas medias anuales de 1991–2020, interpolación bilineal desde 0,1°.
  - **PROVISIONAL:** la PET de ERA5-Land está sobrestimada, así que los valores son bajos (Madrid ≈ 0,22, Galicia ≈ 0,95, sureste ≈ 0,16).
  - Solo se usa para comparar celdas cercanas; cuando haya AED se puede sustituir.
  - **Sustituido** el mismo día por el Global Aridity Index v3.1 (ver abajo). El campo sigue en `static_*.nc`, pero no se usa.

## Fuentes nuevas para emparejar controles (7 de noviembre de 2026)

**Índice de aridez: Global Aridity Index v3.1** ✅
- figshare 7504448. La DOI que se pidió (v5, 10.6084/m9.figshare.7504448.v5) es la **versión 3**. La **v7 (versión 3.1, 17 de julio de 2025)** corrige un error de la v3: en el término de Stefan-Boltzmann se usaba la temperatura en °C en lugar de K, lo que sobrestimaba la ET0 y daba un índice demasiado árido. El readme recomienda migrar a la 3.1. **Se usa la v3.1.**
- Archivo: `Global-AI_ET0__annual_v3_1.zip` (646 MB), de él solo `ai_v31_yr.tif`. GeoTIFF uint16 de 30″ (rejilla global con origen −180, 90), valores × 10 000 (multiplicar por 0,0001), 1970–2000. El mar vale 0 en esta zona.
- En `data/raw/global_ai/figshare_7504448_v7/`. Agregado con `python -m physiofire.preprocess.aridity` a `data/interim/static/aridity_gai_{base,fine}.nc` (media de 6 × 6 píxeles por celda de 0,05°, sin remuestreo).
- Valores: Almería 0,22, Madrid 0,34, Santiago 1,87; percentiles 5–95 de la Península 0,26–1,47. Frente al índice provisional de ERA5-Land: r = 0,82 y 1,63 veces mayor (mediana).

**CORINE Land Cover 2018** ✅
- GEE: `COPERNICUS/CORINE/V20/100m/2018`, banda `landcover`, códigos de nivel 3 (111–523), 100 m en EPSG:3035. Cubre España y Portugal.
- `python -m physiofire.download.gee corine`: fracción de cada grupo de `epoch.corine.groups` por celda (media por área del indicador de clase). Hay que pedirlo en 16 teselas, porque en una sola petición supera el límite de reproyección de GEE (13 726 × 11 884 píxeles).
- Grupos: los siete pedidos (311, 312, 313, 321, 322, 323, 324) más cultivos y prados (211–242), mosaico agrícola con vegetación natural (243), agroforestal, dehesas y montados (244), vegetación escasa (331–333), zonas quemadas (334), artificial y agua. El grupo agrícola se separó en tres porque, con uno solo, dominaba en 20 de los 53 incendios de la lista corta y mezclaba cultivos con mosaicos y dehesas.
- Las fracciones suman 1 (± 0,001) en el 99,9 % de las 34 399 celdas de 0,05° con datos. Comprobado que R (terra) y Python leen las capas en el mismo orden.

**ESFire30 (cartografía de Ochoa et al.)** ✅
- Zenodo 20257001 (DOI 10.5281/zenodo.20257001, 26 de mayo de 2026, CC BY 4.0). Autores: Clara Ochoa, Amin Khairoun, José Antonio Rodado Coello y Emilio Chuvieco. Landsat 30 m, algoritmo BAMT.
- Dos productos: `ESFire30_1985_2025.zip` (perímetros anuales `BA_{año}.shp`, campo `area_ha` o `value1`) y `ESFire30_2001_2025.zip` (`burned_areas_{año}_MODIS.shp`, con `date`, `julian_day` y `area_ha`: fechas corregidas con MODIS). 33 MB en total, en `data/raw/esfire30/zenodo_20257001/`. El CRS cambia según el año (WGS84 o ETRS89 UTM 30N).
- **Solo España:** coincide con los 33 incendios españoles de la lista corta y con 1 de los 20 portugueses.
- **Incluye 2025** (2428 polígonos). Resuelve la pregunta pendiente de CLAUDE.md sobre si la cartografía de Ochoa llega a 2025.
- Uso actual: criterio "sin quemar desde 2017" de los controles. La versión fechada puede servir para validar la fecha de ignición en España (backlog 22). En Zenodo hay además "ESFire30 Causes" (18449006, 93 MB) y "Validation ESFire30" (18646713, 1 GB); no se han descargado.

**Mapa europeo de combustibles de FirEUrisk** ✅ (clasificación principal de la vegetación desde el 7 de noviembre de 2026)
- e-cienciaDatos, DOI 10.21950/YABYCN, versión 2.0 (27 de mayo de 2022, actualizada el 29 de junio de 2022), CC BY 4.0. Artículo: Aragoneses et al. (2023), ESSD 15:1287–1315.
- Archivos, en `data/raw/fireurisk_fuel/yabycn_v2/`:
  - `FirEUrisk_Europe_fuel_map.tif` (1,7 MB; MD5 25a021569fb63b4d9088a032c81bd932);
  - manual de usuario (PUM, con la leyenda en la tabla 1);
  - `readme-en.txt`.
  - Descarga directa por la API de Dataverse: `https://edatos.consorciomadrono.es/api/access/datafile/{9603, 9685, 9684}`.
- GeoTIFF de una banda (float32, NaN como sin datos), 1 km, EPSG:3035. Datos de entrada de 2018–2020.
- Tipos presentes en la Península (los 20 del mapa europeo): 1121, 1122, 1211, 1212, 1301, 1302, 21–23, 31–33, 41, 42, 51–53, 61, 62 y 7. El mar se codifica como 7. No hay frondosas perennifolias (1111/1112).
- `python -m physiofire.preprocess.fuel` escribe `data/interim/static/fuel_fireurisk_{base,fine}.nc` (`type_fraction` por tipo, con 4 × 4 subpuntos por píxel). La agrupación en clases se hace al leer (`epoch.fuel.classes`), así que se puede cambiar sin volver a agregar.
- Concordancia con CORINE y reparto por clase: ver `docs/supplementary_qc.md`, S1.8.

**Historial de quemas de VNP64A1** ✅
- `python -m physiofire.download.gee burn_history --burn-product vnp64a1` escribe `burn_history_vnp64a1_{grid}_2013_2025.nc`, con las mismas variables que el de MCD64A1.

## Serie diaria MOD09GA/MYD09GA completada (7 de noviembre de 2026)

- **Orden de descarga:** MOD09GA 2025–2026, MYD09GA 2018–2026 y MOD09GA 2018–2024 de nuevo con el filtro de negativos. Ningún aviso de límite de peticiones.
- **Imágenes rechazadas:** solo una en toda la serie (MOD09GA, 29 de marzo de 2025).
- **Comprobación de los nuevos MOD09GA 2018–2024 frente a la copia:**
  - Mismos pasos de tiempo y `neg` presente.
  - Ninguna reflectancia negativa.
  - Cambia el 0,5–0,8 % de las celdas de 0,05° y se pierden de 35 a 84 celdas-día por año.
- **Copia de seguridad:** borrada tras la comprobación.

## Pendiente para la serie completa

- Repetir por año la comparación Aqua − Terra del NDVI diario (MYD09GA − MOD09GA), para detectar efectos de la deriva orbital. En la muestra de 2025 la diferencia mediana es −0,001.

## Diferencias con Tang et al. (2026), para la discusión

Tang es la base conceptual, no un método a replicar (CLAUDE.md, 7 de noviembre de 2026). Estas diferencias se documentan, no se intentan reducir.

- PAR de ERA5-Land (0,48 × radiación de onda corta) en lugar de CERES SYN1deg; CERES Ed4B, como sensibilidad.
- TROPOSIF L2B (qa > 0,5) en lugar de qa ≥ 0,5.
- AED (FAO-56, ERA5-Land) en lugar de VPD como variable atmosférica.
- Sin máscara de nieve en el caso 2025 (ventanas de verano), en lugar de GlobSnow.
- NDVI/EVI diario de MOD09GA/MYD09GA en lugar de NBAR de MCD43C4.
- Anomalías respecto a la mediana por día del año, con medias hacia atrás, en lugar de LOESS más ciclo medio y suavizado centrado.
- Filtro de picos por celda en lugar del filtro de percentiles 1–99 global.
- Rejilla de 0,05° en lugar de 0,25°.
- Vegetación del mapa de combustibles de FirEUrisk (con CORINE 2018 como apoyo) en lugar de MCD12C1.

## FWI propio (ERA5-Land) y FWI de CEMS (7 de noviembre de 2026)

**FWI del análisis principal: ERA5-Land horario** ✅
- GEE `ECMWF/ERA5_LAND/HOURLY`. Bandas: `temperature_2m`, `dewpoint_temperature_2m`, `u_component_of_wind_10m`, `v_component_of_wind_10m` (a las 12:00 UTC) y `total_precipitation_hourly` (lluvia de la hora que termina en la marca de tiempo; comprobado con la banda acumulada).
- Rejilla nativa de 0,1° con centros en múltiplos de 0,1° (`crs_transform` [0,1, 0, −360,05, 0, −0,1, 90,05]): 146 × 91 celdas, 7814 de tierra.
- `python -m physiofire.download.era5land_fwi --start ... --end ...`: una petición por mes, un archivo por mes en `data/interim/era5land_fwi/fwi_inputs_YYYYMM.nc` (≈ 2,4 MB). Es reanudable.
- `python -m physiofire.preprocess.fwi --start ... --end ...`: aplica xclim 1.0.0 (`xclim.compute.fire.cffwis_indices`; en xclim 1.0 el módulo pasó de `xclim.indices.fire` a `xclim.compute.fire`).
- Validado con cffdrs 1.9.2 (`R/check_fwi_cffdrs.R`). La única diferencia es la constante del FFMC (147,2 frente a 147,27723); ver `docs/supplementary_qc.md`, S1.10.

**FWI de CEMS (referencia operativa, sensibilidad R17)** ✅
- EWDS, dataset `cems-fire-historical-v1` (`product_type` reanalysis, `system_version` 4_1, `dataset_type` consolidated_dataset; intermediate_dataset para lo más reciente), `grid` 0.25/0.25, NetCDF.
- Variables en el archivo: `fwinx`, `ffmcode`, `dufmcode` y `drtcode`. Coordenadas `valid_time`, `latitude` (de 44,75 a 35,25) y `longitude` (de −10,25 a 4,75).
- La misma clave del CDS sirve en el EWDS (URL `https://ewds.climate.copernicus.eu/api`). Hay que aceptar una vez las condiciones de uso del EWDS (aceptadas el 7 de noviembre de 2026).
- `python -m physiofire.download.cems_fwi --year 2025 --months 8` → `data/raw/cems_fwi/cems_fwi_YYYYMM.nc`.

## Límites de países: Natural Earth admin-0 1:10m (9 de noviembre de 2026)

Solo para la cartografía de la figura 1 (costa, fronteras y mapa de situación de Europa); no entra en ningún cálculo. ✅
- Natural Earth, *Admin 0 – Countries*, escala 1:10m, versión 5.1.1 (`ne_10m_admin_0_countries.VERSION.txt`). Dominio público.
- Descarga: `https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip` (4,9 MB; SHA-256 `ce1ac7036499a0edd641fbc093cd209a98f96a49d2eca8480aaacad35138a7f6`), descomprimido en `data/raw/naturalearth/ne_10m_admin_0_countries/` (fuera de git).
- La usa `R/manuscript_figures/fig1_study_area.R` (España y Portugal: `ADM0_A3` ESP y PRT).
