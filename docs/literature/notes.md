# Notas de literatura

Notas breves sobre artículos y datos relevantes para PHYSIOFIRE: qué aportan, cómo se usan (o por qué no) y qué queda por verificar.

## Aragoneses et al. (2023): mapa europeo de combustibles de FirEUrisk

Aragoneses, E., García, M., Salis, M., Ribeiro, L. M. y Chuvieco, E. (2023). Classification and mapping of European fuels using a hierarchical, multipurpose fuel classification system. *Earth System Science Data* 15, 1287–1315. https://doi.org/10.5194/essd-15-1287-2023

- **Datos:** FirEUrisk_Europe_fuel_map v2.0, e-cienciaDatos, https://doi.org/10.21950/YABYCN (CC BY 4.0). GeoTIFF de una banda, 1 km, ETRS89-LAEA (EPSG:3035). Periodo de los datos de entrada: 2018–2020 (Copernicus Global Land Cover 2019, ESA CCI Land Cover 2020, CORINE 2018 y modelos bioclimáticos de la altura del matorral y del pasto).
- **Leyenda:** 20 de los 24 tipos de primer nivel (tabla 1 del manual de usuario, PUM). No se cartografían las frondosas perennifolias (1111 y 1112), algo relevante en la Península por encinares y alcornocales (backlog 33).
- **Validación (PUM):** acierto global del 88,4 % en los tipos principales (LUCAS 2018) y del 81,2 % en todos los tipos. El matorral es el tipo principal con más error (62 % de comisión y 41 % de omisión).
- **Uso en PHYSIOFIRE:** clasificación principal desde el 7 de noviembre de 2026, con la clase dominante a 0,05° para la lista corta, los estratos y el emparejamiento de controles (`config.yaml`, `epoch.fuel`). Agrupación en `epoch.fuel.classes`.

## Solano-Romero et al. (preprint ESSD, 2026): base de datos de incendios extremos

Solano-Romero, E., Segura-Garcia, C., Pettinari, M. L., Khairoun, A., Torres-Vázquez, M. Á. y Chuvieco, E. A global database of extreme fire events from satellite data from 2003 to 2022. *Earth System Science Data Discussions*, https://doi.org/10.5194/essd-2026-236 (recibido el 28 de marzo de 2026; discusión desde el 11 de mayo de 2026; versión revisada en evaluación según la página consultada el 7 de noviembre de 2026).

- **Contenido (resumen del preprint):** rejillas mensuales globales en NetCDF, 0,25°, 2003–2022. La unidad es la celda-mes. Una celda-mes es extrema si tiene a la vez anomalías estandarizadas de área quemada (FireCCI51) y de FRP (MCD14ML), según umbrales regionales en 55 regiones. Además, indica si se solapa con un perímetro de FRY v2.0 extremo por superficie, duración, FRP media, velocidad de propagación o severidad. Contiene 19 951 eventos extremos.
- **Versión revisada:** según la respuesta de los autores, cambian los nombres (celdas-mes de incendio, FCM; celdas-mes extremas, EFCM). Usar los nombres de la versión final al citarla.
- **Repositorio de datos:** probablemente e-cienciaDatos, doi:10.21950/TK9BXK **(verificar: sale de un resumen automático de la página, no del texto literal)**. Licencia de los datos por confirmar.
- **Uso en PHYSIOFIRE:** no se usa en la prueba de concepto. Es una línea futura (backlog 34): comparar la señal de SIF/APAR antes de incendios extremos y no extremos en el periodo común con TROPOMI (mayo de 2018–2022). Limitaciones: es mensual y a 0,25°, así que habría que llevar la etiqueta de extremo de la celda-mes a los perímetros y fechas de ignición; y no cubre 2025.
