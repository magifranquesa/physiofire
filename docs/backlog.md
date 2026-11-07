# Backlog: pruebas de sensibilidad y comprobaciones para más adelante

**Regla (desde el 6 de noviembre de 2026):** prioridad absoluta al caso 2025. Cualquier comprobación nueva que no cambie una decisión del caso 2025 se apunta aquí y no se hace ahora.

**Criterio (desde el 7 de noviembre de 2026):** Tang et al. (2026) es la base conceptual (SIF/APAR), no un método a replicar. Lo que solo servía para comparar con Tang queda aquí con prioridad baja.

Cada entrada indica qué se prueba, contra qué referencia y su código en la tabla de pruebas de sensibilidad del borrador de métodos (`docs/methods_draft_RSE.md`, sección 2.11, tabla 2). Al hacer una, se mueve a "Hechas" con la fecha, el resultado y el commit.

## Pruebas de sensibilidad del caso 2025 (tabla 2 del borrador)

| # | Prueba | Referencia | Tabla 2 |
| --- | --- | --- | --- |
| 14 | fPAR sin persistencia (MODIS); diagnóstico de la diferencia por días antes de la ignición. **Obligatoria antes de dar por buena cualquier antelación de SIF/APAR** | persistencia de 5 días | R1 |
| 1 | SIF/APAR con fPAR de VIIRS (VNP15A2H, 8 días; persistencia de 11 días, 8 días y sin persistencia) | MCD15A3H | R2 |
| 10 | Ventana hacia atrás de 7 días | 15 días | R3 |
| 24 | Anomalías LOESS con la tendencia ajustada solo antes del día −60 (sobre la serie desestacionalizada) | mediana por día del año | R4 |
| 25 | Rejilla de 0,25°, con un diseño de controles propio (casi todas las celdas de 0,25° del noroeste tienen algo quemado desde 2017; no ampliar el anillo de 10–50 km) | 0,05° | R5 |
| 11 | Suavizado espacial 3 × 3 a 0,05° (tras enmascarar) | sin suavizado espacial | R6 |
| 15 | Análisis alineado por celda (día 0 = fecha de quemado de la celda), con los días de humo marcados | alineado por ignición | R7 |
| 12, 13 | Exclusión de los días con humo: bit de aerosoles del fPAR (MODIS medio o alto; VIIRS alto), índice de aerosoles UV de TROPOMI o AOD de MODIS | sin excluir | R8 |
| 7 | Filtro de percentiles 1–99 global, con el diagnóstico de la fracción eliminada por día relativo a la ignición en incendios y controles | filtro de picos por celda | R9 |
| 5 | SIF/(PAR × NIRv) y SIF/NIRv, por la pérdida de pigmentos | SIF/APAR | R10 |
| 4 | PAR a la hora del paso de TROPOMI (~13:30) | PAR medio diario | R11 |
| 3 | PAR de CERES SYN1deg Ed4B y prueba del salto de abril de 2022 (mensual, rejilla de 1°). Ya no condiciona el análisis principal, que usa ERA5-Land | PAR de ERA5-Land | R12 |
| 6 | Ponderación de la SIF por el inverso de la varianza de cada píxel | ponderación por huella | R13 |
| 26 | NDVI/EVI de NBAR (MCD43A4), enmascarado desde el día −8 | NDVI/EVI diario de MOD09GA/MYD09GA | R14 |
| 2 | Terra y Aqua por separado; diferencia Aqua − Terra del NDVI diario por año y hora media de paso por año (deriva orbital) | — | R15 |
| 20 | Fecha de ignición con detecciones VIIRS de confianza alta solamente | confianza nominal y alta | R16 |
| 18 | FWI operativo de CEMS (ERA5, 0,25°) como referencia. El 7–16 % de los controles de los 24 incendios comparte celda de 0,25° con alguna celda quemada (0 % a 0,1°), lo que reduce por construcción la diferencia incendio–control del FWI. Desde el 7 de noviembre de 2026, el FWI propio con ERA5-Land a 0,1° es el del análisis principal | FWI propio con ERA5-Land a 0,1° | R17 |
| 31 | Vegetación de CORINE 2018 (grupo dominante) para emparejar controles y estratificar. Diagnóstico ya hecho con la lista corta: 35 de 53 incendios con controles (1 de arbolado), frente a 37 (2 de arbolado) con FirEUrisk | clase dominante de FirEUrisk | R18 |
| 16 | Umbral del efecto distinto de 0,5 desviaciones típicas | 0,5 DE | — |
| 36 | Sin los incendios con una sola celda quemada (Alburquerque, 278487, y Lazarim, 281621, en 2025) | los 22 incendios | R19 |

## Comprobaciones de datos

| # | Prueba | Referencia | Dónde |
| --- | --- | --- | --- |
| 21 | Validación de la máscara de fuentes estáticas: construida con `type = 2` de 2018–2024 y evaluada con el archivo estándar de 2025–2026 (aciertos y detecciones `type = 0` eliminadas por error) | — | QC S1.7 |
| 22 | Validación de la fecha de ignición con ESFire30 (versión con fechas corregidas con MODIS, 2001–2025, solo España) y con la EGIF (registro "ESFire30 Causes", Zenodo 18449006) | regla de la fecha más temprana | métodos 2.3 |
| 27 | Clase de FirEUrisk (hacia 2019) frente a un mapa más reciente (p. ej., ESA WorldCover 2021) y frente a las zonas quemadas en 2017–2024: un píxel quemado poco antes de 2019 puede figurar como matorral o pastizal | FirEUrisk | métodos 2.9 |
| 33 | Bosque de frondosas perennifolias (encinares, alcornocales): el mapa europeo de FirEUrisk no tiene los tipos 1111/1112; comprobar en qué clase caen (bosque abierto, matorral, cultivo leñoso) con CORINE 311 y el Mapa Forestal de España **(verificar acceso)** | FirEUrisk | métodos 2.9 |

## Prueba completa (después del caso 2025)

| # | Tarea | Motivo | Borrador |
| --- | --- | --- | --- |
| 23 | Reglas automáticas de selección de incendios: superficie mínima, marca de coherencia con un mínimo de actividad previa (p. ej. ≥ 5 % de las detecciones VIIRS o algún píxel quemado de MCD64A1/VNP64A1), vegetación dominante, solape, temporadas válidas y sin quemas en los 5 años anteriores | El caso 2025 usa una selección manual (decidido el 7 de noviembre de 2026) | 2.3 |
| 28 | Regresión logística condicional (FWI + AED + NDVI frente a + SIF/APAR) con conjuntos caso-control emparejados y bootstrap por episodios | Información más allá del FWI con más incendios | — |
| 35 | Estrato de arbolado: incendios de arbolado de otros años (2018–2024) o de menos de 2000 ha, con el mismo diseño de controles | En 2025 solo 2 de los 5 incendios de arbolado de la lista corta tenían controles; el caso 2025 se limita a matorral (decidido el 7 de noviembre de 2026) | 2.3, 2.10 |
| 32 | Discriminación incendio–control de SIF/APAR dentro de cada clase de peligro del FWI (AUC por clase, umbrales de clase de EFFIS) | Sustituida en el caso 2025 por la comparación descriptiva FWI frente a SIF/APAR (decidido el 7 de noviembre de 2026); hacen falta más incendios por clase | 2.10 |

## Líneas futuras (fuera de la prueba de concepto)

| # | Tarea | Motivo |
| --- | --- | --- |
| 34 | Señal de SIF/APAR antes de incendios extremos y no extremos (2018–2022) con la base de datos de incendios extremos de Solano-Romero et al. (preprint ESSD, 10.5194/essd-2026-236; 0,25°, mensual, 2003–2022, celdas-mes extremas por anomalías regionales de área quemada de FireCCI51 y de FRP de MCD14ML). Notas en `docs/literature/notes.md` | ¿Es la anomalía fisiológica previa mayor o más temprana en los incendios extremos? |

## Solo comparabilidad con Tang et al. (prioridad baja)

| # | Prueba | Motivo |
| --- | --- | --- |
| 8 | Máscara de nieve: ERA5-Land frente a GlobSnow | Irrelevante para las ventanas de junio–agosto del caso 2025 |
| 29 | Réplica de la correlación cruzada de Tang (tiempos de respuesta frente a VPD y humedad del suelo) | Ya fuera de alcance en CLAUDE.md |
| 30 | Media móvil centrada de 15 días × 3 × 3 de Tang en los mapas descriptivos | Solo para figuras comparables con el artículo |

## Versión operativa (después de la prueba de concepto)

| # | Tarea | Motivo |
| --- | --- | --- |
| 19 | Filtro de picos solo hacia atrás (mediana de los días anteriores) en lugar del centrado de ±3 días | El filtro centrado usa hasta 3 días posteriores al evaluado: vale en el análisis retrospectivo (siempre antes del corte), pero no en tiempo real |

## Descartadas

| Fecha | Prueba | Motivo |
| --- | --- | --- |
| 2026-11-07 | 9: contraste de MCD12C1 con CORINE o WorldCover | MCD12C1 deja de usarse; la vegetación sale de CORINE 2018 |
| 2026-11-07 | 17: cobertura del suelo del año anterior a cada incendio (MCD12C1) | Igual; CORINE 2018 es un mapa único anterior a los incendios de 2025 (ver 27) |

## Hechas

| Fecha | Prueba | Resultado | Commit |
| --- | --- | --- | --- |
| 2026-11-06 | Filtro de nubes de `FparExtra_QC` en MCD15A3H y VNP15A2H | Aplicado; elimina un 8,6 % (MODIS) y un 13,5 % (VIIRS) de los píxeles; reduce pero no elimina las caídas de MODIS en arbolado | `87fda42` |
| 2026-11-06 | Estado de nubes de MOD09 en MCD15A3H | Aplicado; elimina un 2,2 % más y apenas reduce las caídas | `e4c51a6` |
| 2026-11-06 | Ruido en SIF/APAR según la fuente de fPAR | VIIRS reduce un ≈ 10 % el ruido en arbolado a 0,25° y menos en el resto; MODIS se mantiene como principal | `e4c51a6` |
