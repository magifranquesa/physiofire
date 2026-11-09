# Resultados de Q1b (seguimiento posterior de la pregunta 1)

**8 de noviembre de 2026.** Plan: `docs/plan_q1b.md`, fijado antes de ejecutar en el commit `d093008`.

Q1b es un análisis exploratorio diseñado después de ver el resultado de la pregunta 1, con criterio propio. No cambia el resultado negativo de la pregunta 1 (`docs/results_q1_drought.md`).

**Ficheros de salida:**
- **Tablas:** `data/processed/drought_q1b/`. Están versionadas `hypotheses_q1b.csv`, `decision_q1b.csv`, `noise_h1_replicates.csv` y `summary_*.csv`.
- **Figuras:** `figures/drought_q1b/` (`R/q1b_figures.R`).
- **Tablas resumen:** `python -m physiofire.drought_q1b_report`.

## (a) Resultado según el criterio fijado

**Matorral: resultado contrario**, frente al NDVI y frente al EVI. H3b es evaluable (141 y 145 eventos) y no se cumple.

Una precisión sobre "contrario": según la regla aprobada, es "contrario" todo caso en que H3b sea evaluable y no se cumpla. Pero las dos referencias no fallan de la misma forma:
- **frente al NDVI,** el NDVI responde *antes* (intervalo por encima de 0);
- **frente al EVI,** no hay diferencia (intervalo que incluye el 0).

Lo mismo pasa en bosque, pastizal y brezal, que no deciden.

### H3b (episodios B, censura a +90 días, anomalías de la pregunta 1)

| Estrato | Frente a | Eventos | Puntuación media [IC 95 %] | Mediana de *d* (días) | Se cumple |
| --- | --- | --- | --- | --- | --- |
| Matorral | NDVI | 141 | +0,17 [+0,06, +0,29] | +13 | no |
| Matorral | EVI | 145 | −0,04 [−0,16, +0,07] | +1 | no |
| Bosque | NDVI | 62 | +0,30 [+0,10, +0,48] | +17 | no |
| Bosque | EVI | 62 | −0,04 [−0,23, +0,15] | 0 | no |
| Pastizal | NDVI | 91 | +0,06 [−0,08, +0,22] | +3 | no |
| Pastizal | EVI | 93 | −0,14 [−0,28, +0,01] | −4 | no |

Cómo leer la tabla:
- **Puntuación:** < 0 indica que SIF/APAR responde antes.
- ***d*:** días de SIF/APAR menos días de la referencia, con la cota de +90 cuando hay censura.

Parejas en matorral frente al NDVI:
- 4463 informativas;
- 433 con censura doble;
- 4998 no observadas.

Sensibilidad (media hacia atrás y SIF/APAR corregido por el PAR): mismo signo en matorral, frente al NDVI +0,24 [+0,12, +0,36] y frente al EVI +0,02 [−0,10, +0,14].

### Análisis 1b (media hacia atrás, desfases de −15 a +60, SIF/APAR corregido por el PAR)

| Matorral | Frente al NDVI | Frente al EVI |
| --- | --- | --- |
| H1 corregido | 0,71 [0,65, 0,76], 2130 celdas: se cumple | 0,81 [0,75, 0,86], 2056 celdas: se cumple |
| H1 robusto al ruido (réplica mediana) | 0,68 [0,63, 0,73]: se cumple (5 de 5 réplicas) | 0,80 [0,75, 0,85]: se cumple (5 de 5) |
| H2b | +2 días [−1, +4], 1459 celdas (558 excluidas por extremo): no | −6 días [−8, −4], 1632 celdas (423 excluidas): se cumple |
| Sensibilidad: H1 centrada | 0,72: se cumple | 0,81: se cumple |
| Sensibilidad: H1 por correlación parcial | 0,69: se cumple | 0,79: se cumple |
| Sensibilidad: H2b centrada | +2 [0, +4]: no | −5 [−7, −3]: se cumple |

- **Bosque:** H1 solo frente al EVI (0,64, robusto); H2b no se cumple.
- **Pastizal:** ni H1 ni H2b.

Los resultados del análisis 1 de la pregunta 1 se mantienen con la corrección del PAR, la media hacia atrás y la degradación por ruido:
- la escala corta de SIF/APAR en matorral no es un efecto del ruido ni de la radiación;
- tampoco lo es su adelanto de unos 5–6 días frente al EVI.

Pero el criterio exige H3b, y H3b no se cumple.

## (b) Observaciones posteriores (marcadas como tales)

**Contraste entre estaciones** (descriptivo según el plan; el diagnóstico de la censura por la izquierda es posterior). Matorral:

| Inicio | Frente al NDVI | Frente al EVI |
| --- | --- | --- |
| Primavera (32–34 eventos) | +0,49 [+0,29, +0,68], *d* = +24 | +0,35 [+0,14, +0,55], *d* = +15 |
| Verano (109–111 eventos) | +0,08 [−0,05, +0,21], *d* = +6,5 | −0,16 [−0,29, −0,03], *d* = −4 |

- **Primavera:** los índices ópticos responden claramente antes.
- **Verano:** SIF/APAR responde antes que el EVI, aunque sin llegar a la magnitud de −5 días.

El mismo patrón aparece en el pastizal, donde en verano, frente al EVI, se cumplirían las dos condiciones (−0,28, *d* = −17). Coincide con la observación de los eventos de agosto de la pregunta 1.

**Censura por la izquierda** (`summary_posthoc_h3b_left_censored.csv`, posterior):
- **El problema:** el 30 % de las respuestas observadas del NDVI en matorral (el 34 % en verano) caen en el día −30. Es decir, el NDVI ya estaba ≤ −0,5 DE al principio de la ventana; en SIF/APAR pasa en el 6 % y en el EVI en el 15 %.
- **Por qué ocurre:** los inicios de B no parten de un estado de calma. El SPEI-90 al día −30 tiene mediana +0,28, pero el NDVI conserva anomalías de sequías anteriores (memoria estructural).
- **Cómo lo trata el diseño:** lo cuenta como "responde primero", lo que favorece a la variable más lenta y persistente.
- **Sin esas parejas:**
  - frente al NDVI: +0,10 [−0,02, +0,23] en total y −0,03 en verano;
  - frente al EVI: −0,08 [−0,19, +0,04] en total y −0,23 [−0,35, −0,10] con *d* = −19 días en verano (se cumpliría);
  - en primavera, los índices ópticos siguen respondiendo antes.

## (c) Diagnósticos del PAR y del ruido

**Pendiente del PAR** (ajustada fuera de la sequía, en la escala *z*): negativa en casi todas las celdas. Las medianas son −0,19 en matorral, −0,30 en bosque y −0,20 en pastizal. Con más luz, el rendimiento aparente baja, lo que es compatible con la saturación y con el PAR en el denominador. La corrección *sube* SIF/APAR en los días soleados y, por tanto, en los secos: es conservadora frente a la señal de sequía.

**Fracción de ruido de día a día** (mediana en matorral):

| Variable | *f* |
| --- | --- |
| SIF/APAR corregido | 0,78 |
| EVI | 0,76 |
| NDVI | 0,30 |

El EVI diario ya es casi tan ruidoso como SIF/APAR, por la banda azul y la combinación Terra + Aqua. Solo se añadió ruido al 52 % de sus celdas, frente al 99 % en el NDVI. Aun degradando el NDVI hasta el ruido de SIF/APAR, H1 apenas cambia (de 0,71 a 0,68).

## (d) Cosas raras y limitaciones

1. **Desfases en el extremo −15:** el 13–14 % de las celdas de matorral significativas a SPEI-90 tienen el desfase en −15, en el NDVI y en SIF/APAR.
   - Son celdas con una escala óptima más corta (mediana de 60–90 días, frente a 90–365 en las demás).
   - Con la escala fija en 90 días, leer el SPEI de días posteriores imita una acumulación más reciente. Ese desfase refleja el desajuste de escala, no que la vegetación se adelante al SPEI.
   - En la pregunta 1, esas mismas celdas tenían el desfase en 0.
   - H2b las excluye y lo cuenta (558 y 423 celdas).
2. **Cobertura del NDVI y del EVI:**
   - en primavera, solo el 15–18 % de los episodios de matorral tiene el NDVI o el EVI observado (≥ 50 % de días con anomalía suavizada), frente al 98–99 % de SIF/APAR;
   - es el efecto combinado de las nubes, la regla de suavizado (≥ 8 de 15 días válidos) y la regla de variable observada;
   - por eso, H3b en primavera usa solo 32–34 eventos y pocas parejas.
3. **Eventos no independientes:** 228 eventos con matorral, pero concentrados en 2022 (62), 2023 (66) y 2025 (43). Muchos son trozos vecinos de una misma sequía regional. El bootstrap por eventos lo ignora, así que los intervalos de H3b son demasiado estrechos. Esto no cambia el resultado en matorral: un intervalo más ancho no convierte en cumplida una H3b no cumplida.
4. **Definición de la respuesta:** "anomalía ≤ −0,5 DE durante 15 días" no distingue entre responder al episodio y estar ya bajo (punto (b)). Es una limitación de diseño heredada de la pregunta 1.
5. **Definición B:** la definición de sequía relámpago de Noguera et al. (2020) está por verificar con los autores.

## Conclusión

- **Según el criterio fijado, Q1b es contraria en matorral.** SIF/APAR no responde antes a los episodios de sequía que el NDVI ni que el EVI. Frente al NDVI responde después, en parte porque el NDVI ya estaba bajo antes del inicio.
- **El análisis 1 resiste las tres pruebas** (radiación, ruido y desfases con signo): SIF/APAR sigue sequías de escala más corta que el NDVI/EVI y se adelanta unos 6 días al EVI a escala de 90 días.
- **Lo que queda como hipótesis para un trabajo futuro** (posterior, no confirmado) es la dependencia estacional: los índices ópticos responden antes en primavera y SIF/APAR en verano, sobre todo frente al EVI y sin las parejas censuradas por la izquierda. Necesitaría un diseño propio fijado antes de mirar los datos: respuesta relativa al estado previo y estación como factor preespecificado.
