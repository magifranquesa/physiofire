# Resultados del caso 2025 (análisis de época superpuesta, estrato matorral)

**Fecha de ejecución:** 8 de noviembre de 2026.
**Configuración:** fijada antes de extraer series de incendios en el commit `a7f894f`. No se ha cambiado ningún parámetro del análisis principal después de ver los resultados.
**Corrección de código posterior:** `R/epoch_analysis.R` duplicaba la ruta del directorio de figuras y se detenía al guardarlas. Se corrigió como error de código. No afecta a ningún resultado numérico.

**Muestra:** 22 incendios de 2025 (15 en España y 7 en Portugal; 15 de matorral y 7 de brezal) con 133 celdas quemadas y 108 controles (229 celdas distintas).

**Serie principal:** anomalía respecto a la mediana por día del año, media de los 15 días anteriores, estandarizada por celda. Intervalos bootstrap del 95 % por incendios (2000 réplicas, semilla 42).

**Ejecución:**

```
python -m physiofire.epoch --grid fine
Rscript R/epoch_analysis.R data/processed/epoch/epoch_series_fine.csv
Rscript R/epoch_report_2025.R
python -m physiofire.report_valid_days
```

## Criterio de decisión

Criterio tal como está escrito en CLAUDE.md y en el borrador (sección 2.10), aplicado al caso 2025 (estrato matorral: matorral y brezal):

> Seguir si SIF/APAR se adelanta al NDVI/EVI y difiere entre incendios y controles cuando la diferencia del FWI es pequeña.

**Resultado: no se cumple.**

- **SIF/APAR no se separa de los controles en ningún día de la ventana.** No puede adelantarse al NDVI/EVI, que tampoco se separan.
- **La diferencia incendio–control del FWI es prácticamente nula** (media de los últimos 15 días: +0,00 DE), así que la condición de "FWI parecido" se cumple.
- **Pero SIF/APAR tampoco difiere:** la diferencia es ligeramente positiva (+0,13 DE de media en los últimos 15 días), en sentido contrario al esperado, y su intervalo incluye el cero casi todos los días.
- **El resultado es negativo en matorral y en brezal por separado.**
- **Matiz en brezal:** la diferencia incendio–control del FWI es positiva al final de la ventana. La media de los últimos 15 días es +0,15 DE, y el intervalo excluye el cero en 7 de esos 15 días (tabla de abajo). La antelación sigue siendo 0 [0, 5] y SIF/APAR tampoco difiere ahí (+0,06 DE). *Precisión añadida el 9 de noviembre de 2026; los datos no cambian.*

Según CLAUDE.md, corresponde replantear (otra resolución, SIF/PAR, otra región) antes de invertir más. Un resultado negativo también es publicable. No se ha lanzado ninguna prueba de sensibilidad ni análisis adicional.

## Antelación de cada variable

Antelación de la diferencia incendio–control, en días antes de la ignición (0 = no se separa). La estimación puntual sigue la regla del borrador: diferencia media ≥ 0,5 DE en el sentido esperado, con intervalo que excluye el cero, todos los días hasta el día −1. Entre corchetes, el percentil 2,5–97,5 de la antelación en 2000 remuestreos de incendios; dentro de cada réplica no se exige la condición del intervalo.

| Variable | Conjunto (22) | Matorral (15) | Brezal (7) |
| --- | --- | --- | --- |
| SIF/APAR sin persistencia del fPAR | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| SIF/APAR con persistencia de 5 días | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| NDVI (Terra + Aqua) | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| EVI (Terra + Aqua) | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| FWI (ERA5-Land, 0,1°) | 0 [0, 0] | 0 [0, 0] | 0 [0, 5] |
| AED (ET0, ERA5-Land) | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |

Tabla completa: `data/processed/epoch/report2025_lead_times.csv`.

## Señal regional en las celdas quemadas

Si se miden solo las celdas quemadas, sin restar los controles, varias variables sí se separan de lo normal antes de la ignición:

| Variable | Conjunto | Matorral | Brezal |
| --- | --- | --- | --- |
| FWI | 12 días [8, 17] | 6 [0, 17] | 14 [12, 60] |
| AED | 7 [3, 10] | 4 [0, 11] | 7 [5, 10] |
| SIF/APAR sin persistencia | 0 [0, 4] | 0 [0, 0] | 8 [4, 11] |
| EVI | 0 [0, 4] | 0 [0, 0] | 17 [1, 19] |

En las celdas quemadas del conjunto:

- **FWI y AED:** anomalías positivas de +1 a +1,5 DE al final de la ventana. Es la ola de calor de agosto de 2025.
- **SIF/APAR:** pasa de +0,9 DE al principio de la ventana a −0,3 DE el día −1.
- **EVI:** pasa de +1,9 DE a −0,2 DE, partiendo de una primavera muy verde.

Los controles, a 10–50 km, siguen la misma evolución, de modo que la diferencia es nula. Es una señal regional de la sequía y el calor, no una señal propia de los lugares que ardieron. En el brezal, el FWI de las celdas quemadas se separa antes (14 días) que SIF/APAR (8 días).

## FWI frente a SIF/APAR

Diferencia incendio–control de las dos variables en la misma figura:

| Grupo | FWI: media de los últimos 15 días | Días con IC sin cero | SIF/APAR sin persistencia: media de los últimos 15 días | Días con IC sin cero |
| --- | --- | --- | --- | --- |
| Conjunto | 0,00 | 0 | +0,13 | 0 |
| Matorral | −0,07 | 0 | +0,16 | 0 |
| Brezal | +0,15 | 7 | +0,06 | 0 |

## Figuras

- `figures/epoch/report2025_epoch_all.png`: conjunto; SIF/APAR sin persistencia, NDVI y EVI combinados, FWI y AED; diferencia incendio–control y celdas quemadas solas.
- `figures/epoch/report2025_epoch_shrubland.png` y `report2025_epoch_heathland.png`: lo mismo por clase.
- `figures/epoch/report2025_fwi_vs_sifapar.png`: diferencia incendio–control del FWI y de SIF/APAR.
- `figures/epoch/epoch_*_fine.png`: figuras generales de `R/epoch_analysis.R`, con todas las variables y series.

## Celdas-día válidas de SIF/APAR en la ventana de 60 días

SIF/APAR sin persistencia, tras el corte en la ignición, los umbrales de validez (fPAR ≥ 0,15, PAR ≥ 40 W m⁻², peso de TROPOSIF ≥ 0,1) y el filtro de picos (k = 6). Se cuentan los valores diarios, antes de la media de 15 días.

| Incendio | Clase | Celdas quemadas | Válidas en celdas quemadas | Válidas en controles |
| --- | --- | --- | --- | --- |
| Uña de Quintana (Zamora) | matorral | 22 | 1123 (85 %) | 246 (82 %) |
| A Rúa (Ourense) | brezal | 17 | 827 (81 %) | 244 (81 %) |
| Quintas de São Bartolomeu | matorral | 13 | 662 (85 %) | 261 (87 %) |
| Benuza (León) | brezal | 12 | 470 (65 %) | 218 (73 %) |
| Burón (León) | brezal | 11 | 503 (76 %) | 216 (72 %) |
| Navaconcejo (Cáceres) | matorral | 10 | 507 (84 %) | 255 (85 %) |
| Carviçais (Douro) | matorral | 8 | 430 (90 %) | 267 (89 %) |
| Peranzanes (León) | brezal | 6 | 263 (73 %) | 225 (75 %) |
| Alverca da Beira/Bouça Cova | matorral | 5 | 258 (86 %) | 266 (89 %) |
| Frechas (Trás-os-Montes) | matorral | 4 | 210 (88 %) | 262 (87 %) |
| Maceda (Ourense) | brezal | 3 | 141 (78 %) | 235 (78 %) |
| Gallegos del Río (Zamora) | matorral | 3 | 156 (87 %) | 259 (86 %) |
| Villablino (León) | brezal | 3 | 135 (75 %) | 222 (74 %) |
| Cáceres (Cáceres) | matorral | 3 | 153 (85 %) | 255 (85 %) |
| Alfara de Carles (Tarragona) | matorral | 2 | 93 (78 %) | 237 (79 %) |
| Mombeltrán (Ávila) | matorral | 2 | 94 (78 %) | 237 (79 %) |
| Mata de Lobos (Beiras) | matorral | 2 | 104 (87 %) | 253 (84 %) |
| Carballeda de Avia (Ourense) | brezal | 2 | 95 (79 %) | 244 (81 %) |
| Vale das Fontes (Trás-os-Montes) | matorral | 2 | 105 (88 %) | 268 (89 %) |
| Riofrío de Aliste (Zamora) | matorral | 1 | 53 (88 %) | 265 (88 %) |
| Alburquerque (Badajoz) | matorral | 1 | 47 (78 %) | 259 (86 %) |
| Lazarim (Douro) | matorral | 1 | 47 (78 %) | 137 (76 %), 3 controles |

En total hay 6476 celdas-día válidas en celdas quemadas y 5331 en controles, de 7980 y 6480 posibles. Con persistencia del fPAR son 6904 y 5646. La disponibilidad de SIF/APAR no limita el resultado. Tabla: `data/processed/epoch/report2025_valid_days.csv`.

## Lo investigado (sin cambiar nada)

1. **Pocos incendios con NDVI/EVI válido al principio de la ventana** (8–11 de 22 el día −60). No es un error.
   - En las celdas de incendios y controles, MOD09GA y MYD09GA combinados tienen un dato válido solo el 14–45 % de los días en mayo y la primera quincena de junio de 2025, frente al 64–78 % en julio y la primera quincena de agosto.
   - La media de 15 días exige la mitad de días válidos.
   - Consecuencias:
     - la prueba con una sola plataforma (R15) queda descartada, porque Terra tiene un dato válido el 10–44 % de los días y solo el 4–21 % de sus medias de 15 días son válidas;
     - la frecuencia "~1 dato cada 1,6 días" del índice combinado solo se cumple en julio–agosto.
2. **La diferencia de SIF/APAR en sentido contrario (positiva) no es significativa y se concentra en pocos incendios:**
   - Alverca da Beira (+1,34 DE de media en los últimos 10 días), Carviçais (+0,40) y Quintas de São Bartolomeu (+0,24), los tres portugueses con ignición el 14 de agosto;
   - Mata de Lobos (+0,48);
   - Lazarim (+1,64, una sola celda).

   Se comprobó si podía deberse al humo o a la cercanía de incendios que habían empezado antes. Los controles suelen estar algo más cerca de esos incendios que las celdas quemadas, pero la relación entre esa diferencia de distancia y la diferencia de SIF/APAR tiene el signo contrario al que daría el humo (r = 0,4). No se atribuye a ello.

## Independencia de la muestra

15 de los 22 incendios empezaron entre el 7 y el 15 de agosto de 2025, casi todos en el noroeste, con la misma situación meteorológica. Algunos comparten controles: 229 celdas distintas para 241 asignaciones. El bootstrap por incendios trata los 22 como independientes, así que los intervalos son algo optimistas. Esto no cambia la conclusión, que es negativa.

## Pendiente

No se ha lanzado ninguna prueba de sensibilidad (R1–R20) ni análisis adicional. Se esperan instrucciones del investigador.
