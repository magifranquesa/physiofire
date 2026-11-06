# Backlog: pruebas de sensibilidad y comprobaciones para más adelante

**Regla (desde el 6 de noviembre de 2026):** prioridad absoluta al caso 2025. Cualquier comprobación nueva que no cambie una decisión del caso 2025 se apunta aquí y no se hace ahora.

Cada entrada indica qué se prueba, contra qué referencia y dónde está descrita en el borrador de métodos (`docs/methods_draft_RSE.md`). Al hacer una, se mueve a "Hechas" con la fecha, el resultado y el commit.

## Fuentes y preprocesado

| # | Prueba | Referencia | Borrador |
| --- | --- | --- | --- |
| 1 | SIF/APAR con fPAR de VIIRS (VNP15A2H, 8 días; persistencia de 11 días, 8 días y sin persistencia) | SIF/APAR con MCD15A3H | 2.5 |
| 2 | Comparación Aqua − Terra del NDVI diario (MYD09GA − MOD09GA) por año, para detectar la deriva orbital; informar de la hora media de paso por año | — | 2.5 |
| 3 | Fuente de PAR: CERES SYN1deg Ed4B frente a ERA5-Land, y prueba del salto de abril de 2022 (mensual, rejilla de 1°) | PAR provisional de ERA5-Land | 2.6 |
| 4 | PAR a la hora del paso de TROPOMI (~13:30) frente al PAR medio diario | PAR medio diario | 2.7 |
| 5 | SIF/(PAR × NIRv) y SIF/NIRv, por la pérdida de pigmentos | SIF/APAR | 2.7 |
| 6 | Ponderación de la SIF por el inverso de la varianza de cada píxel | ponderación por huella | 2.7 |
| 7 | Filtro de percentiles 1–99 global de Tang, con el diagnóstico de la fracción eliminada por día relativo a la ignición en incendios y controles | filtro por celda | 2.7 |
| 8 | Máscara de nieve: ERA5-Land frente a GlobSnow (irrelevante en verano) | — | 2.4 |
| 9 | Contraste de MCD12C1 (IGBP) con CORINE o ESA WorldCover para la clase de vegetación | MCD12C1 2017 | 2.12 |

## Anomalías y época

| # | Prueba | Referencia | Borrador |
| --- | --- | --- | --- |
| 10 | Ventana hacia atrás de 7 días | 15 días | 2.8 |
| 11 | Suavizado espacial 3 × 3 a 0,05° (tras enmascarar) | sin suavizado espacial | 2.8 |
| 12 | Exclusión de los días con aerosoles marcados (MODIS medio o alto; VIIRS alto) | sin excluir; marcado como humo | 2.5, 2.11 |
| 13 | Indicador de humo del índice de aerosoles UV de TROPOMI o AOD de MODIS | — | 2.11 |
| 14 | fPAR sin persistencia (MODIS) y con 8 días o sin persistencia (VIIRS); diagnóstico de la diferencia por días antes de la ignición | **la prueba sin persistencia es la referencia para validar la antelación** | 2.5 |
| 15 | Análisis alineado por celda (día 0 = fecha de quemado de la celda), con los días de humo marcados | alineado por ignición | 2.11 |
| 16 | Umbral del efecto distinto de 0,5 desviaciones típicas | 0,5 DE | 2.11 |
| 17 | Cobertura del suelo del año anterior a cada incendio | mapa fijo de 2017 | 2.12 |
| 18 | FWI propio con ERA5-Land a mediodía a 0,05° | FWI de CEMS a 0,25° | 2.9 |

## Versión operativa (después de la prueba de concepto)

| # | Tarea | Motivo | Borrador |
| --- | --- | --- | --- |
| 19 | Filtro de picos solo hacia atrás (mediana de los días anteriores) en lugar del centrado de ±3 días | El filtro centrado usa hasta 3 días posteriores al evaluado: vale en el análisis retrospectivo (siempre antes del corte), pero no en tiempo real | 2.7 |

## Hechas

| Fecha | Prueba | Resultado | Commit |
| --- | --- | --- | --- |
| 2026-11-06 | Filtro de nubes de `FparExtra_QC` en MCD15A3H y VNP15A2H | Aplicado; elimina un 8,6 % (MODIS) y un 13,5 % (VIIRS) de los píxeles; reduce pero no elimina las caídas de MODIS en arbolado | `87fda42` |
| 2026-11-06 | Estado de nubes de MOD09 en MCD15A3H | Aplicado; elimina un 2,2 % más y apenas reduce las caídas | `e4c51a6` |
| 2026-11-06 | Ruido en SIF/APAR según la fuente de fPAR | VIIRS reduce un ≈ 10 % el ruido en arbolado a 0,25° y menos en el resto; MODIS se mantiene como principal | `e4c51a6` |
