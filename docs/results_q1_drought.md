# Resultados de la pregunta 1: respuesta de SIF/APAR y NDVI/EVI al estrés hídrico

**Fecha de ejecución:** 8 de noviembre de 2026.

**Plan prerregistrado:** `docs/plan_q1_drought.md` y `config/config.yaml` (sección `drought_q1`).

**Configuración:** fijada antes de extraer las series en el commit `76ae9af`. No se ha cambiado ningún parámetro después de ver los resultados.

**Correcciones de código antes de extraer las series** (todas documentadas como errores, ninguna después de ver resultados):
- recorte del SPEI a ±3,09 de todos los valores, no solo de los infinitos (`76ae9af`);
- lectura del SPEI por nombre de eje (`103ecc8`);
- celdas costeras sin datos de tierra en ERA5-Land (`843847a`);
- arranque de los procesos paralelos de R (`813f906`).

**Muestra:** 6771 celdas de 0,05° de vegetación natural sin quemar desde 2013, en 2018–2025:

| Estrato | Celdas | Semiárido | Subhúmedo seco | Húmedo |
| --- | --- | --- | --- | --- |
| Matorral (matorral + brezal) | 4169 | 2888 | 575 | 706 |
| Bosque | 1369 | 291 | 311 | 767 |
| Pastizal | 1233 | 821 | 116 | 296 |

- 20 celdas costeras caen en celdas de ERA5-Land sin datos de tierra y no tienen SPEI ni AED.
- Una de ellas, de matorral junto al Mar Menor (−0,825 E, 37,625 N), tampoco tiene PAR a 0,05°. Por eso no tiene SIF/APAR ni SIF: el filtro de validez exige PAR. Hay SIF de TROPOSIF en esa celda; el hueco no es un fallo del rejillado.

**Recorte del SPEI a ±3,09**, en 2018–2025 (tabla completa en `summary_spei_clip.csv`). Afecta al 0,06–0,56 % de las celdas-día según la escala, con muchos más recortes en la cola seca que en la húmeda.

**Ejecución:**

```
Rscript R/q1_cells.R
python -m physiofire.download.era5land_precip          # y entradas de ET0 1991-2016
python -m physiofire.preprocess.water_balance
Rscript R/q1_spei.R 16
python -m physiofire.drought_q1 series
python -m physiofire.drought_q1 analysis --workers 20
python -m physiofire.drought_q1_report
Rscript R/q1_figures.R
```

**Salidas versionadas** (`data/processed/drought_q1/`):
- `hypotheses.csv`, `decision.json`, `analysis2_episodes.csv`;
- `summary_*.csv`;
- `posthoc_*.csv`, excepto `posthoc_par_cells.csv`.

Las tablas por celda (`analysis1_cells.csv`, 9,6 MB) y las series quedan fuera de git. Las figuras están en `figures/drought_q1/`.

---

## (a) Resultado según el criterio prerregistrado

> **Resultado positivo** si, en el estrato matorral (matorral + brezal), se cumple **H3 y además H1 o H2**, cada una frente al NDVI y frente al EVI.

**Resultado: negativo.** H3 no se cumple en matorral frente a ninguna de las dos referencias. H1 sí se cumple frente a las dos, y H2 solo frente al EVI.

Intervalos bootstrap del 95 % (2000 réplicas, semilla 42): por bloques espaciales de 1° en H1 y H2, por eventos en H3.

| Estrato | Frente a | H1: fracción con escala de SIF/APAR más corta [IC] (n celdas) | H2: mediana L(SIF/APAR) − L(ref) a SPEI-90, días [IC] (n) | H3: mediana entre eventos, días [IC] (celdas; eventos) |
| --- | --- | --- | --- | --- |
| **Matorral** | NDVI | **0,71 [0,65; 0,75] — se cumple** (2267) | 0 [0; 0] — no (2035) | −17,3 [−50; +15,5] — no (21; 2) |
| **Matorral** | EVI | **0,80 [0,75; 0,85] — se cumple** (2171) | **−5 [−7; −3] — se cumple** (2101) | +14,5 [+14,5; +14,5] — no (18; 1) |
| Bosque | NDVI | 0,62 [0,53; 0,70] — se cumple (576) | 0 [0; 0] — no (421) | −17,5 — "se cumple"* (2; 1) |
| Bosque | EVI | 0,70 [0,64; 0,76] — se cumple (530) | −4 [−6; −1] — no (475) | −18,5 — "se cumple"* (2; 1) |
| Pastizal | NDVI | 0,42 [0,33; 0,55] — no (689) | 0 [0; 0] — no (693) | +16,5 [+11; +22] — no (4; 2) |
| Pastizal | EVI | 0,50 [0,40; 0,63] — no (689) | −4 [−6; −2] — no (705) | +17,5 — no (2; 1) |
| Brezal solo (descriptivo) | NDVI | 0,60 [0,47; 0,73] — no (60) | 0 [0; 0] — no (37) | sin eventos |
| Brezal solo (descriptivo) | EVI | 0,79 [0,67; 0,89] — se cumple (62) | −0,5 [−7; 0] — no (44) | sin eventos |

\* Con un solo evento de 2 celdas, el intervalo tiene anchura cero y el "se cumple" es degenerado. No es interpretable. El bosque no decide.

Figura: `figures/drought_q1/q1_hypotheses.png`.

### Celdas con correlación significativa

Prueba de permutación de años, p < 0,05:

| Estrato | SIF/APAR | NDVI | EVI | SIF/APAR y NDVI | SIF/APAR y EVI |
| --- | --- | --- | --- | --- | --- |
| Matorral (4169) | 2555 | 3475 | 3299 | 2267 | 2171 |
| Bosque (1369) | 729 | 915 | 833 | 576 | 530 |
| Pastizal (1233) | 744 | 1043 | 1021 | 689 | 689 |

La correlación máxima típica de SIF/APAR (*r\** ≈ 0,39 en las celdas significativas) es bastante menor que la del NDVI y el EVI (≈ 0,68): SIF/APAR es mucho más ruidoso.

### Episodios y eventos

- 178 episodios en 161 celdas.
- 6 eventos de al menos 10 celdas.
- Eventos con celdas de cada estrato: matorral 5, pastizal 5, bosque 1.
- Eventos que entran en H3 (alguna celda del estrato con respuesta en las dos variables):

| Estrato | Frente al NDVI | Frente al EVI |
| --- | --- | --- |
| Matorral | 2 | 1 |
| Bosque | 1 | 1 |
| Pastizal | 2 | 1 |

### Escala y desfase óptimos

Medianas, con la moda entre paréntesis. SIF/APAR, NDVI y EVI: celdas con *r\** significativa. SIF, SIF/PAR y fPAR: todas las celdas, solo descriptivo. Tabla completa por estrato y clase de aridez en `summary_scale_lag.csv`; reparto por escalas en `summary_scale_share.csv`.

| Estrato | Variable | Escala *s\** (días) | Desfase *L\** (días) | Desfase a SPEI-90 (días) |
| --- | --- | --- | --- | --- |
| Matorral | SIF/APAR | 60 (90) | 0 (0) | 0 (0) |
| Matorral | NDVI | 180 (365) | 0 (0) | 1 (0) |
| Matorral | EVI | 365 (365) | 0 (0) | 11 (0) |
| Matorral | SIF | 90 (90) | 5 (0) | 5 (0) |
| Matorral | SIF/PAR | 90 (90) | 1 (0) | 0 (0) |
| Matorral | fPAR | 180 (365) | 8 (0) | 10 (8) |
| Bosque | SIF/APAR | 60 (90) | 0 | 0 |
| Bosque | NDVI | 180 (365) | 0 | 0 |
| Bosque | EVI | 180 (365) | 4 | 9 |
| Bosque | SIF | 90 (90) | 6 | 4 |
| Bosque | SIF/PAR | 90 (60) | 0 | 0 |
| Bosque | fPAR | 180 (365) | 12 | 12 |
| Pastizal | SIF/APAR | 90 (90) | 1 | 0 |
| Pastizal | NDVI | 90 (90) | 1 | 1 |
| Pastizal | EVI | 90 (90) | 6 | 7 |
| Pastizal | SIF | 90 (90) | 5 | 3 |
| Pastizal | SIF/PAR | 90 (90) | 1 | 0 |
| Pastizal | fPAR | 90 (90) | 6 | 6 |

**Escalas en matorral.** La escala de SIF/APAR se reparte así: 15–30 días, 23 %; 60–90 días, 65 %; 180–365 días, 12 %. En el NDVI, el 68 % de las celdas está en 180–365 días, y en el EVI, el 75 %. Figuras: `q1_scale_share.png` y `q1_scale_maps.png`.

**Por clase de aridez:**
- SIF/APAR (mediana, con la moda entre paréntesis):
  - en las celdas húmedas responde a 60 días en todos los estratos;
  - en las semiáridas, a 90 días;
  - en las subhúmedas secas, a 60 días en matorral (moda 90; 311 celdas) y a 90 días en bosque y pastizal.

  En matorral: semiárido 90 (90), 1776 celdas; subhúmedo seco 60 (90), 311 celdas; húmedo 60 (60), 468 celdas. *Corregido el 9 de noviembre de 2026: la versión anterior decía 90 días también en el matorral subhúmedo seco, contra `summary_scale_lag.csv`. Error de redacción; los datos no cambian.*
- El NDVI y el EVI de matorral y bosque responden a 180–365 días en las clases semiárida y subhúmeda seca, y a 90–180 días en las húmedas.
- En el pastizal, todo responde a unos 90 días.

**Variables secundarias.** El orden es el que predice la descomposición de Tang et al. (2026):
- SIF/APAR, a la escala más corta;
- SIF/PAR y SIF, a escalas intermedias (90 días), con la SIF algo más retrasada;
- el fPAR, como la estructura (180–365 días, con 8–12 días de desfase).

### Análisis secundario con la AED

Desfases de 0 a 60 días; se toma la correlación más negativa. Tabla completa en `summary_aed.csv`.

| Estrato | Variable | Celdas significativas | *r* (mediana) | Desfase: mediana (moda), días | Celdas donde la AED supera al SPEI |
| --- | --- | --- | --- | --- | --- |
| Matorral | SIF/APAR | 3035 | −0,28 | 11 (0) | 20 % |
| Matorral | NDVI | 3096 | −0,46 | 14 (13) | 7 % |
| Matorral | EVI | 2700 | −0,41 | 19 (60) | 4 % |
| Bosque | SIF/APAR | 1000 | −0,32 | 1 (0) | 41 % |
| Bosque | NDVI | 601 | −0,43 | 13 (60) | 7 % |
| Bosque | EVI | 574 | −0,42 | 37 (60) | 7 % |
| Pastizal | SIF/APAR | 866 | −0,29 | 12 (0) | 18 % |
| Pastizal | NDVI | 957 | −0,51 | 15 (14) | 14 % |
| Pastizal | EVI | 830 | −0,44 | 17 (17) | 5 % |

SIF/APAR se relaciona con la AED sin desfase, y el NDVI y el EVI, con 2–3 semanas de retraso. El diagnóstico del apartado (c) indica que buena parte de esa relación de SIF/APAR pasa por la radiación.

Según la nota de interpretación del plan, el SPEI de 15–60 días en verano está dominado por la ET0. Por tanto, la respuesta de SIF/APAR a escalas cortas debe leerse junto a este análisis y al apartado (c).

---

## (b) Observación posterior: eventos de agosto

> **Análisis posterior**, declarado después de ver el resultado. No modifica el criterio ni el resultado de (a).

Hay 5 eventos con celdas de matorral (tabla `posthoc_events.csv`, figura `q1_posthoc_events.png`):

| Evento | Inicio | Celdas de matorral | SIF/APAR responde | NDVI responde | EVI responde |
| --- | --- | --- | --- | --- | --- |
| 44 | marzo de 2023 | 7 | 3 | 7 | 2 |
| 52 | marzo de 2023 | 25 | 18 | 25 | 25 |
| 139 | agosto de 2022 | 11 | 9 | 0 | 0 |
| 145 | agosto de 2022 | 17 | 6 | 1 | 0 |
| 123 | agosto de 2025 | 7 | 4 | 0 | 0 |

- **En los eventos de agosto**, SIF/APAR responde en **19 de 35** celdas de matorral y el NDVI en **1 de 35**. El EVI no responde en ninguna.
  - H3 solo usa celdas con respuesta en las dos variables, así que estos eventos no entran en H3.
  - Lo que muestran es que SIF/APAR detecta la sequía que empieza en pleno verano, y el NDVI/EVI no, dentro de los 90 días siguientes.
- **En los eventos de marzo de 2023 ocurre lo contrario:** el NDVI responde en todas las celdas (32 de 32) y SIF/APAR en 21 de 32.
- **Lectura prudente.** El patrón depende de la época:
  - en primavera, la sequía corta el crecimiento y se ve en el verdor;
  - en agosto, el matorral ya está en su mínimo estacional de verdor y la respuesta se ve en la fisiología.
- **Alcance:** solo son 3 eventos en dos veranos, con celdas vecinas que no son independientes. Es una hipótesis para Q1b, no un resultado.

---

## (c) Diagnóstico del PAR

> **Análisis posterior.** No modifica el criterio ni el resultado de (a).

**Motivo.** El PAR está en el denominador de SIF/APAR, y la radiación es una de las entradas principales de la ET0. Una correlación de SIF/APAR con la AED, o con el SPEI de verano dominado por la ET0, podría reflejar la caída del rendimiento de fluorescencia con mucha luz (saturación), no estrés hídrico.

**Método:**
- anomalías estandarizadas como en el análisis, de abril a octubre, con desfase 0;
- PAR leído de la misma entrada que la serie;
- correlaciones por celda y correlaciones parciales dado el PAR;
- tablas `posthoc_par_diagnostic.csv` (por estrato) y `posthoc_par_cells.csv` (por celda, fuera de git); figura `q1_posthoc_par.png`.

**Medianas en las celdas de matorral** (bosque y pastizal, parecidos):

| Correlación | Bruta | Parcial, dado el PAR |
| --- | --- | --- |
| SIF/APAR – PAR | −0,18 | — |
| PAR – AED | +0,86 | — |
| SIF/APAR – AED | −0,22 | **−0,13** |
| SIF/APAR – SPEI-30 | +0,26 | **+0,21** |
| NDVI – AED | −0,32 | −0,44 |
| NDVI – SPEI-30 | +0,43 | +0,42 |

**Lectura:**
- Algo menos de la mitad de la relación de SIF/APAR con la AED desaparece al controlar por el PAR. Lo que queda es débil (−0,13).
- La relación de SIF/APAR con el SPEI se mantiene en su mayor parte (+0,26 → +0,21).
- En el NDVI pasa lo contrario: la parte de la AED que no es radiación (temperatura, déficit de presión de vapor y viento) se relaciona más con el NDVI, no menos.
- La alineación de SIF/APAR con la demanda atmosférica (como en Tang, con el VPD) debe interpretarse con cuidado en la Península, porque aquí la AED está dominada por la radiación.
- Las escalas cortas de SIF/APAR frente al SPEI no parecen explicarse solo por la radiación. Comprobarlo exige repetir el análisis 1 con control del PAR (Q1b).

Un sondeo previo con 400 celdas y el PAR reconstruido como SIF/(SIF/APAR × fPAR) daba valores parecidos: −0,22 → −0,11 y +0,26 → +0,22. Los de la tabla, con el PAR de la entrada y todas las celdas, son los válidos.

---

## (d) Limitaciones de diseño

1. **Eventos insuficientes en el análisis 2.**
   - El 99,7 % de las celdas (6751 de 6771) tiene alguna racha de ≥ 30 días con SPEI-90 < −1 en el periodo con datos de vegetación.
   - Pero solo 161 celdas cumplen la definición de inicio: 60 días previos > −0,5, inicio entre marzo y septiembre y ventanas dentro del periodo con datos.
   - Las sequías de 2019 y 2022–2023 fueron largas y encadenadas: el 28–30 % de las celdas-día de esos años tiene SPEI-90 < −1. Pocas empiezan desde la normalidad.
   - Resultado: 6 eventos en total y 1–2 por estrato en H3. **H3 falla por falta de muestra, no porque los datos la contradigan.**
2. **H3 excluye las celdas sin respuesta en alguna de las dos variables.** Una variable que no responde no cuenta como más lenta: la celda desaparece. En los eventos de agosto, eso deja fuera justo los casos en que SIF/APAR responde y el NDVI/EVI no (apartado b). La falta de respuesta debería tratarse como censura, no como exclusión.
3. **Desfases censurados en 0 y en 60 días.**
   - Los desfases van de 0 a 60 días sobre una media centrada de 15 días, que incluye 7 días posteriores.
   - Si la vegetación responde casi a la vez que el SPEI, el máximo cae en 0, y el desfase real puede ser negativo en la serie suavizada.
   - Frente al NDVI, en el 27 % de las celdas de matorral los dos desfases a SPEI-90 valen 0, y en otro 1 % la diferencia es 0 con desfases iguales distintos de 0. Por eso H2 frente al NDVI da mediana 0 con intervalo [0; 0]: el diseño no puede separar las dos variables.
   - En el otro extremo, el NDVI, el EVI y el fPAR acumulan celdas en 60 días, sobre todo frente a la AED.
   - Figura: `q1_lag_spei090.png`; tabla: `summary_h2_lag_diff.csv`.
4. **Ruido distinto entre variables.** SIF/APAR tiene correlaciones mucho más bajas que el NDVI/EVI. No se ha comprobado si el ruido por sí solo desplaza la escala óptima hacia escalas cortas. H1 debe leerse con esa reserva hasta hacer la prueba de robustez de Q1b.
5. **Radiación** (apartado c). La relación de SIF/APAR con la AED, y en parte con el SPEI de escalas cortas, puede incluir saturación por la luz.
6. **Periodo corto y más seco que la referencia.** Son ocho estaciones (2018–2025), las anomalías se calculan respecto a la mediana de ese mismo periodo, y 2018–2025 es más seco que 1991–2020: los recortes del SPEI se concentran en la cola seca.

## Conclusión

- **Según el criterio prerregistrado, la pregunta 1 da un resultado negativo.**
- El análisis 1 muestra que la escala óptima de SIF/APAR es más corta que la del NDVI y la del EVI en matorral y bosque, aunque no en pastizal. Esto es coherente con la hipótesis fisiológica, con dos reservas pendientes: el ruido y la radiación.
  - *Resueltas en Q1b (`docs/results_q1b.md`; nota del 9 de noviembre de 2026):* con SIF/APAR corregido por el PAR y con el ruido igualado, H1 se mantiene **en matorral** frente al NDVI y frente al EVI (0,71 / 0,81 y 0,68 / 0,80). **En bosque solo se mantiene frente al EVI** (0,64 y 0,63); frente al NDVI baja a 0,52 y 0,50, por debajo de 0,60.
- El desfase no separa SIF/APAR del NDVI, por la censura en 0.
- La prueba de episodios (H3) no tiene muestra suficiente para decidir.
- El análisis de seguimiento Q1b (`docs/plan_q1b.md`) se declara posterior y se evaluará con su propio criterio. No cambia este resultado.
