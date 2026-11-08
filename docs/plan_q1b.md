# Q1b: análisis de seguimiento de la pregunta 1 (declarado posterior)

**Estado:** aprobado por el investigador el 8 de noviembre de 2026, con los ajustes que recoge este texto:
- orden de recambio B → A → C;
- la estación como estrato descriptivo de H3b;
- la definición de Noguera et al., pendiente de verificar con los autores.

Fijado en git antes de ejecutar (ver "Configuración fijada antes de ejecutar", al final).

**Carácter posterior.** Q1b se diseña después de ver el resultado de la pregunta 1 (`docs/results_q1_drought.md`), que es negativo según su criterio prerregistrado. Q1b no cambia ese resultado. En el artículo se presentará como análisis exploratorio de seguimiento, con su propio criterio, fijado en git antes de ejecutar.

**Qué responde.** Las cuatro limitaciones de diseño de la pregunta 1:
- pocos eventos de sequía;
- H3 excluye las celdas sin respuesta;
- desfases censurados en 0;
- posible efecto de la radiación y del ruido sobre H1.

## Qué se mantiene de la pregunta 1

- **Datos:** las mismas celdas (6771), el mismo periodo (mayo de 2018 a 2025) y las mismas series (`drought_q1_series.nc`).
- **SPEI:** el mismo, con el recorte a ±3,09.
- **Filtros:** los mismos de validez y de picos.
- **Anomalías:** la misma climatología (mediana por día del año ±15 días) y la misma estandarización.
- **Estratos:** decide el matorral (matorral + brezal); el bosque se informa con el mismo detalle; el pastizal es la referencia.
- **Inferencia:** la misma prueba de permutación de años (199 permutaciones) y los mismos intervalos bootstrap (2000 réplicas, semilla 42; por bloques de 1° en el análisis 1, por eventos en el análisis 2).
- **Hipótesis:** cada una se evalúa frente al NDVI y frente al EVI.

## 1. H3b: tiempo hasta la respuesta, con censura

**Día de respuesta.** Igual que en la pregunta 1: primer día, entre −30 y +90 días respecto al inicio, desde el que la anomalía se mantiene ≤ −0,5 DE al menos 15 días, con la misma regla para los huecos.

**Censura.** Una variable sin respuesta en la ventana queda censurada a +90 días (respuesta "después de +90"). No se excluye.

**Comparación emparejada por celda y episodio** (SIF/APAR frente a la referencia):

| SIF/APAR | Referencia | Puntuación | Diferencia *d* (días) |
| --- | --- | --- | --- |
| Responde en *T*ₛ | Responde en *T*ᵣ | signo de *T*ₛ − *T*ᵣ | *T*ₛ − *T*ᵣ |
| Responde en *T*ₛ | Censurada | −1 (SIF/APAR antes) | *T*ₛ − 90, cota de la magnitud |
| Censurada | Responde en *T*ᵣ | +1 (SIF/APAR después) | 90 − *T*ᵣ, cota de la magnitud |
| Censurada | Censurada | no informativa | se excluye y se cuenta |

**Estadísticos por evento:** la media de las puntuaciones de sus celdas y la mediana de *d*.

**H3b** se cumple frente a una referencia si se cumplen las dos condiciones:
- **(a) dirección:** la media entre eventos de la puntuación media es < 0 y su intervalo bootstrap por eventos queda entero por debajo de 0;
- **(b) magnitud:** la mediana entre eventos de la mediana de *d* es ≤ −5 días.

**Mínimo de muestra.** H3b solo se evalúa si al menos **10 eventos** tienen alguna celda informativa del estrato. Con menos, H3b es "no evaluable".

**Descriptivos:**
- curvas de Kaplan–Meier del tiempo hasta la respuesta por variable y estrato;
- H3b por separado según la estación del inicio, como **estrato descriptivo**: primavera (marzo–mayo) y verano (junio–septiembre).
  - La estación de un evento es la del mes mediano de inicio de sus celdas.
  - No entra en el criterio de decisión.
  - Viene de la observación posterior de los eventos de agosto.

## 2. Definición de episodio válida para sequías encadenadas

En la pregunta 1, solo 161 de 6751 celdas con sequía cumplían la condición de partir de la normalidad (60 días con SPEI-90 > −0,5). Opciones:

- **A. Intensificación dentro de una sequía en curso.** Hay inicio cuando el SPEI-90 cruza a la baja un umbral de categoría (−1, −1,5 o −2), se mantiene por debajo al menos 30 días y en los 60 días anteriores estuvo al menos 0,5 por encima de ese umbral.
  - Cada cruce es un episodio.
  - Entre dos inicios de una misma celda debe haber al menos 90 días; si no, se toma el primero.
  - Mantiene la lógica de la pregunta 1 y la extiende a las sequías que se agravan.
- **B. Intensificación rápida** (por la velocidad de caída, al estilo de las sequías relámpago). Hay inicio cuando el SPEI-90 cae al menos 1,0 en 30 días o menos, termina por debajo de −1 y se mantiene por debajo al menos 30 días, sea cual sea el nivel de partida.
  - Se usa la misma separación mínima de 90 días.
  - Es una adaptación de las definiciones de sequía relámpago con el SPEI de escala corta: Noguera, Domínguez-Castro y Vicente-Serrano (2020), con una caída de ≥ 2 unidades de SPEI de 1 mes en 4 semanas que termina por debajo de −1,28 **(verificar la definición exacta; la verifica el investigador con los autores)**.
  - Es la más ligada a la pregunta, porque la fisiología debería responder antes cuando el déficit se instala deprisa.
- **C. Escala más corta para el inicio.** La regla de la pregunta 1 con el SPEI-30 en lugar del SPEI-90: 30 días previos > −0,5, por debajo de −1 al menos 20 días. Las sequías de 30 días empiezan desde la normalidad con más frecuencia, pero se separa del SPEI-90 de H2.
- **D. Relajar solo la condición previa:** 30 días > −0,5 en lugar de 60. Es el cambio mínimo, pero probablemente da pocos eventos más.

**Decisión aprobada:** orden de recambio fijado **B → A → C**.

**Regla de elección, ciega al resultado.** Antes de mirar ninguna variable de vegetación, se cuentan con el SPEI solo los eventos de ≥ 10 celdas que contienen celdas de matorral:
- si B da al menos 10 eventos, B es la principal;
- si no, A; si tampoco, C;
- si ninguna llega a 10, H3b es "no evaluable".

**Recuento** (8 de noviembre de 2026, solo SPEI; `python -m physiofire.drought_q1b count` → `data/processed/drought_q1b/event_count.csv`):

| Definición | Episodios | Celdas con episodio | Eventos (≥ 10 celdas) | Eventos con matorral | Celdas de matorral en eventos | Eventos con bosque | Eventos con pastizal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B | 18 638 | 6708 | 242 | 228 | 3632 | 154 | 159 |
| A | 21 431 | 6720 | 266 | 249 | 3633 | 169 | 174 |
| C | 2451 | 2059 | 56 | 55 | 1041 | 29 | 30 |

**Definición resultante: B**, con 228 eventos con celdas de matorral (≥ 10). A y C no se usan en la decisión.

**Comprobaciones del recuento con B** (solo SPEI):
- **Tamaño:** mediana de 25 celdas por evento; el mayor tiene 1314 celdas (marzo–abril de 2023).
- **Dispersión de inicios dentro de un evento:** mediana de 4 días, máximo de 37.
- **Eventos por año:**

  | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | 15 | 23 | 17 | 7 | 62 | 66 | 9 | 43 |
- **Independencia:** muchos eventos de un mismo año son partes vecinas de una misma sequía regional, así que no son independientes. El bootstrap por eventos no lo tiene en cuenta; es una limitación que se documentará en los resultados. Se mantienen las ventanas de inicio (marzo–septiembre y dentro del periodo con datos de vegetación) y la definición de evento (vecindad de 8, inicios a ±15 días, al menos 10 celdas).

## 3. Desfases sin censura en 0

**Principal: media hacia atrás de 15 días** (la ventana termina en el día *t*), como en el análisis de época, con desfases de −15 a +60 días.
- Un desfase negativo significaría que la vegetación se adelanta al SPEI. Físicamente no se espera, pero se admite para que el estimador no quede censurado en 0.
- La media hacia atrás retrasa unos 7 días todas las variables por igual, así que las diferencias entre variables no cambian.

**Sensibilidad:** la media centrada de la pregunta 1 con desfases de −15 a +60 días.

**H2b:** la misma regla que H2 (escala fija de SPEI-90; mediana de L(SIF/APAR) − L(ref) ≤ −5 días con el intervalo bootstrap entero por debajo de 0), con esta estimación del desfase y con el SIF/APAR corregido por el PAR (apartado 4).
- Se informa de la fracción de celdas con el desfase en un extremo (−15 o +60).
- H2b se calcula solo con las celdas en que ningún desfase cae en un extremo, y se informa del número de celdas excluidas.

## 4. Control del PAR

**Principal: SIF/APAR corregido por el PAR** con una relación estimada fuera de la sequía. Para cada celda:
- se ajusta por mínimos cuadrados la anomalía de SIF/APAR frente a la del PAR (mismo día, abril–octubre), solo en los días con SPEI-90 ≥ 0;
- la anomalía corregida es *z*(SIF/APAR) − *b* · *z*(PAR), aplicada a todos los días;
- después se repite el suavizado y la estandarización.

Motivo: con todos los días, la corrección quitaría también parte de la señal de sequía, porque los días secos son soleados (*r*(PAR, SPEI-30) ≈ −0,34). Estimada fuera de la sequía, recoge solo la saturación por la luz.

**Sensibilidad:** correlación parcial de SIF/APAR con el SPEI dado el PAR, con todos los días.

Con el SIF/APAR corregido se repiten el análisis 1 (H1 y H2b) y el análisis secundario con la AED.

## 5. Robustez de H1 frente al ruido

**Pregunta:** ¿la escala corta de SIF/APAR se debe solo a que es más ruidoso?

**Medida del ruido**, por celda y variable, sobre la anomalía diaria antes de suavizar:
- fracción de ruido *f* = var(Δx)/2 / var(x), donde Δx son las diferencias entre días consecutivos válidos. Es la parte blanca, de día a día, de la varianza, suponiendo una señal lenta;
- se calcula sin mirar ninguna correlación.

**Degradación:**
- a la anomalía diaria del NDVI y del EVI de cada celda se le añade ruido gaussiano blanco hasta que su *f* iguala la de SIF/APAR en esa celda;
- si la *f* del NDVI/EVI ya es mayor, no se añade ruido;
- no se cambia la disponibilidad de datos: el NDVI/EVI ya tiene menos días válidos (41 %) que SIF/APAR (62 %).

**Réplicas:** 5 por celda (semillas 42 a 46). En cada una se recalculan *s\**, *L\** y la permutación del NDVI y del EVI degradados (199 permutaciones). SIF/APAR se usa sin degradar y con la corrección del PAR.

**H1 robusto** se cumple frente a una referencia si H1 (≥ 60 % de celdas con la escala de SIF/APAR más corta, intervalo que excluye el 50 %) se cumple frente a la referencia degradada en la mediana de las 5 réplicas.

**Descriptivo:** desplazamiento del reparto de escalas óptimas del NDVI/EVI al degradarlos, sobre todo hacia 15–60 días.

**Coste:** unas 2–3 horas con 20 procesos (matorral, bosque y pastizal; el análisis 1 completo tardó unos 57 minutos). Si hace falta reducirlo, primero se quita el pastizal.

## 6. Criterio de decisión de Q1b (fijado antes de ejecutar)

En el estrato matorral, y frente al NDVI y frente al EVI por separado:

- **Apoyo a la hipótesis** si se cumplen las dos condiciones:
  - H3b (dirección y magnitud);
  - H1 con el SIF/APAR corregido por el PAR y robusto frente al ruido, o H2b.
- **Resultado contrario** si H3b es evaluable y no se cumple.
- **No concluyente** si H3b no es evaluable (menos de 10 eventos con celdas informativas).

Se informa igual del bosque y del pastizal, que no deciden. El caso no previsto (H3b sin apoyo del análisis 1) y el resultado global sobre las dos referencias están en "Detalles de implementación", puntos 12 y 13.

Sea cual sea el resultado de Q1b, el resultado de la pregunta 1 sigue siendo negativo según su criterio prerregistrado.

## Pasos, salidas y tiempo

1. **Recuento de eventos de B y A** (solo el SPEI), elección de la definición y commit. Minutos.
2. **Código de Q1b** en `src/physiofire/drought_q1b.py`, con tests sintéticos de:
   - la censura y la puntuación emparejada;
   - los desfases negativos;
   - la corrección del PAR;
   - la medida del ruido y la degradación.

   Sección `drought_q1b` en `config/config.yaml`, y commit antes de ejecutar.
3. **Ejecución:**
   - extraer las series de PAR, unos 15 minutos;
   - análisis 1 con la corrección del PAR y la media hacia atrás, aproximadamente 1 hora;
   - análisis 2 con H3b, unos minutos;
   - robustez frente al ruido, unas 2–3 horas.
4. **Salidas:** `data/processed/drought_q1b/`, `figures/drought_q1b/` y `docs/results_q1b.md`.

No hace falta descargar nada.

## Decisiones aprobadas (8 de noviembre de 2026)

1. **Definición de episodio:** orden de recambio B → A → C, elegido con el recuento ciego del apartado 2. Resultado: B.
2. **Estación** (primavera y verano): estrato descriptivo de H3b, fuera del criterio.
3. **Noguera et al. (2020):** el investigador verifica la definición con los autores; hasta entonces se mantiene "(verificar)".
4. **El resto, como se propuso:**
   - H3b con censura a +90 días y un mínimo de 10 eventos;
   - media hacia atrás de 15 días y desfases de −15 a +60 días;
   - corrección del PAR estimada en los días con SPEI-90 ≥ 0, con la correlación parcial como sensibilidad;
   - prueba de ruido con 5 réplicas;
   - criterio con tres salidas.

## Detalles de implementación (fijados antes de ejecutar)

Concretan puntos que el texto aprobado dejaba abiertos.
- **Código:** `src/physiofire/drought_q1b.py`.
- **Parámetros:** `config/config.yaml`, sección `drought_q1b`.
- **Tests sintéticos:** `tests/test_drought_q1b.py`.

1. **Inicio con B.** Es el primer día con SPEI-90 < −1 que cumple dos condiciones:
   - sigue por debajo de −1 al menos 30 días;
   - el máximo de los 30 días anteriores supera en ≥ 1,0 el valor de ese día.

   Si el SPEI ya estaba por debajo de −1, el inicio es el día en que se completa la caída de 1,0.
2. **Precondición de A.** La frase "en los 60 días anteriores estuvo al menos 0,5 por encima del umbral" se lee así: *al menos un día* con SPEI-90 ≥ umbral + 0,5.
   - Si se exigiera en todos los días, casi nunca habría cruces de −1,5 ni de −2 dentro de una sequía en curso, contra el propósito de A.
3. **Separación de 90 días (A y B).** Se aplica a los candidatos definidos con el SPEI, antes del filtro de mes y de ventana.
   - Así, la continuación de un episodio que empezó en febrero no cuenta como un inicio nuevo en marzo.
   - C sigue la regla de la pregunta 1, sin separación adicional.
4. **Variable observada en un episodio.** Su anomalía suavizada debe ser finita en ≥ 50 % de los días entre el −30 y el +104 (la ventana de respuesta más la duración mínima).
   - Si alguna de las dos variables no está observada, la pareja no se usa y se cuenta como "no observada".
   - Así, la censura a +90 días significa "observada y sin respuesta", no "sin datos".
5. **Anomalías de H3b.**
   - **Principal:** las de la pregunta 1 (media centrada de 15 días y SIF/APAR sin corregir), porque el apartado 1 dice "igual que en la pregunta 1" y el apartado 4 solo pide la corrección del PAR para el análisis 1.
   - **Sensibilidad:** media hacia atrás y SIF/APAR corregido.
6. **Eventos y estratos en H3b.**
   - Los eventos se construyen con todas las celdas, como en la pregunta 1.
   - Un evento cuenta para un estrato si tiene al menos una celda informativa de ese estrato.
   - El bootstrap remuestrea eventos (2000 réplicas, semilla 42).
7. **Corrección del PAR.**
   - Las anomalías diarias de SIF/APAR y del PAR, sin suavizar, se dividen por su DE de todo el periodo.
   - La pendiente *b* se ajusta por mínimos cuadrados, con intercepto, en los días de abril a octubre con SPEI-90 ≥ 0.
   - Con menos de 30 días de ajuste, la celda queda sin SIF/APAR corregido.
   - El PAR es el de la entrada de la cadena (0,48 × radiación solar descendente de ERA5-Land), extraído para las celdas en `data/processed/drought_q1b/par_series.nc`.
8. **Correlación parcial (sensibilidad).**
   - Es el máximo, sobre escalas y desfases, de la correlación parcial del SIF/APAR sin corregir con el SPEI dado el PAR del mismo día.
   - Es descriptiva, sin permutación.
   - Con esa escala se calcula H1 en las celdas en que SIF/APAR es significativo en la ejecución principal.
9. **Ruido.**
   - **Fracción de ruido:** *f* = var(Δx)/2 / var(x), donde Δx son las diferencias entre días naturales consecutivos válidos los dos. Para SIF/APAR se usa la anomalía diaria corregida.
   - **Varianza añadida:** σ² = (*f*ₛ·V − D)/(1 − *f*ₛ), con *f*ₛ limitado a 0,99; es 0 si la variable ya es más ruidosa.
   - **Aplicación:** el ruido se añade solo en los días válidos. Después se suaviza y se estandariza igual que en la ejecución principal (media hacia atrás).
   - **Semillas:** una por réplica, celda y variable.
   - **Celdas:** solo se recalculan aquellas en que SIF/APAR es significativo en la ejecución principal. H1 solo usa celdas significativas en las dos variables, así que el resultado no cambia y el coste baja.
10. **H1 robusto:** H1 en la réplica con la fracción mediana de las 5.
11. **Ejecuciones del análisis 1b.**
    - **Principal:** media hacia atrás, SIF/APAR corregido, la AED como variable secundaria y la correlación parcial.
    - **Sensibilidad con media centrada:** sin la AED, para ahorrar tiempo.
    - Las variables secundarias (SIF, SIF/PAR y fPAR) no se recalculan.
12. **Caso que el criterio no preveía.** Si H3b se cumple pero no se cumple ni H1 (corregido y robusto) ni H2b, el resultado frente a esa referencia es **no concluyente**.
13. **Resultado global del matorral:**
    - apoyo, si hay apoyo frente al NDVI y frente al EVI;
    - contrario, si es contrario frente a alguna de las dos;
    - no concluyente, en los demás casos.

## Configuración fijada antes de ejecutar

Commit: se anota tras el commit.
