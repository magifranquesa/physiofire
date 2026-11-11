# Diagnóstico: EVI diario frente a NBAR en las celdas de la Fig. 3 y las S3_1 a S3_5

**11 de noviembre de 2026.** Es un diagnóstico posterior: no forma parte de ningún análisis ni figura y todavía no está en el manuscrito.

**Archivos:**
- Script: `docs/diagnostics/evi_nbar_fig3.py`.
- Tablas: `evi_nbar_fig3_cells.csv` (por celda y mes) y `evi_nbar_fig3_nir_june.csv` (NIR de junio por año).

## Pregunta

En la Fig. 3 (A Rúa) el EVI diario empieza muy alto a finales de junio (+2 a +3,6 DE) y baja en julio, mientras que el NDVI se queda moderado y sube. El diagnóstico previo mostró que el exceso del EVI viene del infrarrojo cercano (NIR), no de la banda azul.

¿Es un efecto de la geometría de observación? El producto diario MOD09GA/MYD09GA no tiene corrección BRDF.

## Método

- **Celdas:** las 18 de los seis incendios (una quemada y dos controles por incendio), de `data/interim/explore/explore_cells.csv`.
- **NBAR:** MCD43A4 v061, bandas 1, 2 y 3 (rojo, NIR y azul), calidad obligatoria ≤ 1. Es la misma agregación a 0,05° que la del análisis (`data/interim/gee/series/nbar_fine_*.nc`).
- **Diario:** MOD09GA y MYD09GA, combinados Terra + Aqua como en los análisis.
- **Índices:** el mismo código (`epoch._optical`, con el EVI fuera de [0, 1] descartado) y el mismo filtro de picos.
- **Anomalías:** mediana por día del año de 2018–2025 (±15 días), igual que en la Fig. 3.
  - La DE es la de la media de 15 días hacia atrás de la anomalía, en 2018–2025.
  - La celda quemada se enmascara desde la ignición; el NBAR, desde el día −8, porque usa observaciones hasta *t* + 7.
- **Tabla:** medias mensuales de los valores diarios de junio y julio de 2025, sin suavizar.

**Diferencia de partida entre los dos productos:** cada fecha del NBAR combina 16 días de observaciones (*t* − 8 a *t* + 7). Es una serie más suave y con más datos (30 de 30 días en junio, frente a unos 8–15 en el diario).

## Resultados

### 1. El exceso del EVI de junio se mantiene con NBAR

| Media de las 18 celdas, junio de 2025 | Diario: anomalía (bruta) | Diario: anomalía (DE) | NBAR: anomalía (bruta) | NBAR: anomalía (DE) |
| --- | --- | --- | --- | --- |
| NDVI | +0,018 | +0,52 | +0,022 | +0,58 |
| EVI | **+0,041** | **+2,08** | **+0,035** | **+1,69** |
| NIR | +0,036 | +2,73 | +0,024 | +1,63 |

- Con NBAR, el EVI de junio está por encima de +1 DE en 17 de las 18 celdas; con el diario, en las 18.
- En unidades brutas, el NBAR conserva de media el **88 %** de la anomalía del EVI diario.
- Del NIR conserva unas dos terceras partes (+0,024 frente a +0,036). Es decir, en torno a un tercio del exceso del NIR diario puede deberse a la geometría o al muestreo, y el resto no.

**Dónde baja más el exceso con NBAR** (EVI de junio, en DE, diario → NBAR):

| Celda | Diario | NBAR |
| --- | --- | --- |
| Benuza, quemada | 2,56 | 1,51 |
| Benuza, control 1 | 3,06 | 1,31 |
| A Rúa, control 1 | 2,93 | 2,07 |
| Uña de Quintana, control 1 | 1,99 | 1,11 |

En la quemada de A Rúa casi no cambia (2,57 → 2,40).

**A Rúa, junio y julio de 2025** (anomalía en DE):

| Celda | Mes | NDVI diario | NDVI NBAR | EVI diario | EVI NBAR | NIR diario | NIR NBAR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Quemada | junio | +0,35 | +0,87 | +2,57 | +2,40 | +3,13 | +1,29 |
| | julio | +1,27 | +0,35 | +0,70 | +1,58 | +0,47 | +1,19 |
| Control 1 | junio | −0,29 | +0,13 | +2,93 | +2,07 | +3,63 | +1,23 |
| | julio | +1,70 | +0,13 | +0,22 | +1,32 | −0,03 | +0,82 |
| Control 2 | junio | −0,17 | +0,16 | +2,13 | +2,35 | +2,63 | +1,75 |
| | julio | +1,23 | +0,20 | +0,41 | +1,21 | +0,34 | +0,92 |

La tabla completa de las 18 celdas, con valor bruto, climatología, anomalía bruta, anomalía en DE y número de días, está en `evi_nbar_fig3_cells.csv`.

### 2. Las tendencias opuestas de julio no se ven con NBAR

- **EVI:** con NBAR baja mucho menos de junio a julio. En A Rúa pasa de +2,1 a +2,4 en junio a +1,2 a +1,6 en julio. En el diario cae a +0,2 a +0,7.
- **NDVI:** con NBAR no sube en julio. En A Rúa queda en +0,1 a +0,35, frente a +1,2 a +1,7 en el diario.
- **NIR:** con NBAR sigue alto en julio (+0,8 a +1,2 DE en A Rúa); en el diario cae a ~0.

Así que la caída del EVI y la subida del NDVI en julio del producto diario dependen en buena parte del producto: geometría, días observados o el suavizado propio del NBAR. El exceso de junio, en cambio, no.

### 3. NIR de junio por año: no hay una tendencia compatible con la deriva orbital

Anomalía media de las 18 celdas respecto a la mediana por día del año de 2018–2025 (reflectancia):

| Año | Terra | Aqua | Combinado | NBAR |
| --- | --- | --- | --- | --- |
| 2018 | −0,003 | +0,005 | +0,001 | −0,003 |
| 2019 | +0,007 | −0,004 | +0,002 | +0,002 |
| 2020 | +0,013 | +0,017 | +0,015 | +0,011 |
| 2021 | −0,003 | −0,001 | −0,003 | −0,007 |
| 2022 | −0,017 | −0,004 | −0,016 | −0,009 |
| 2023 | +0,003 | −0,005 | −0,015 | −0,013 |
| 2024 | +0,011 | +0,018 | +0,014 | +0,007 |
| **2025** | **+0,039** | **+0,040** | **+0,035** | **+0,024** |

- **2025 es el año con el NIR de junio más alto** en los cuatro productos.
- No hay una tendencia monótona: 2020 y 2024 son positivos, y 2022 y 2023, negativos.
- **Terra y Aqua dan la misma anomalía en 2025** (+0,039 y +0,040), aunque sus órbitas derivan en sentidos opuestos: Terra hacia las ~9:00 y Aqua hacia las ~15:50. Con la deriva como causa, lo esperable serían anomalías de signo o tamaño distintos en cada plataforma.
- NBAR, que corrige la geometría, también da el máximo en 2025 (+0,024).
- **Matiz:** la climatología solo tiene 8 años e incluye 2025. Si la mediana excluyera 2025, la anomalía de 2025 sería algo mayor.

## Conclusión

- **El exceso del EVI de junio de 2025 no es un artefacto de la geometría:** con NBAR se mantiene en el 88 % de la anomalía bruta y en 17 de las 18 celdas.
- **Tampoco viene de la deriva orbital:** Terra, Aqua y NBAR coinciden en que junio de 2025 tiene el NIR más alto de 2018–2025.
- **Lo más probable:** un aumento real del NIR, compatible con más vegetación tras la primavera húmeda (SPEI-3 positivo en abril y mayo). No está verificado.
- **Lo que depende del producto diario:**
  - una parte del exceso del NIR (en torno a un tercio);
  - y, sobre todo, las tendencias opuestas de julio (EVI que baja, NDVI que sube), que con NBAR casi desaparecen.
- Si el texto comenta la evolución de julio del EVI y el NDVI en la Fig. 3, conviene matizarlo o apoyarlo en NBAR.

**Limitaciones:**
- NBAR suaviza 16 días y tiene más datos. Parte de la diferencia en julio puede deberse a ese suavizado y no a la geometría.
- Son 18 celdas de seis incendios del noroeste y del centro-norte de Portugal. No es una muestra regional.
