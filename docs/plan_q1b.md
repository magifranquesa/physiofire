# Q1b: análisis de seguimiento de la pregunta 1 (declarado posterior)

**Estado:** borrador pendiente de aprobación, 8 de noviembre de 2026. No se ha ejecutado nada de Q1b.

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
- H3b por separado según la estación del inicio: primavera (marzo–mayo) y verano (junio–septiembre). Esta separación es solo descriptiva y viene de la observación posterior de los eventos de agosto.

## 2. Definición de episodio válida para sequías encadenadas

En la pregunta 1, solo 161 de 6751 celdas con sequía cumplían la condición de partir de la normalidad (60 días con SPEI-90 > −0,5). Opciones:

- **A. Intensificación dentro de una sequía en curso.** Hay inicio cuando el SPEI-90 cruza a la baja un umbral de categoría (−1, −1,5 o −2), se mantiene por debajo al menos 30 días y en los 60 días anteriores estuvo al menos 0,5 por encima de ese umbral.
  - Cada cruce es un episodio.
  - Entre dos inicios de una misma celda debe haber al menos 90 días; si no, se toma el primero.
  - Mantiene la lógica de la pregunta 1 y la extiende a las sequías que se agravan.
- **B. Intensificación rápida** (por la velocidad de caída, al estilo de las sequías relámpago). Hay inicio cuando el SPEI-90 cae al menos 1,0 en 30 días o menos, termina por debajo de −1 y se mantiene por debajo al menos 30 días, sea cual sea el nivel de partida.
  - Se usa la misma separación mínima de 90 días.
  - Es una adaptación de las definiciones de sequía relámpago con el SPEI de escala corta: Noguera, Domínguez-Castro y Vicente-Serrano (2020), con una caída de ≥ 2 unidades de SPEI de 1 mes en 4 semanas que termina por debajo de −1,28 **(verificar la definición exacta)**.
  - Es la más ligada a la pregunta, porque la fisiología debería responder antes cuando el déficit se instala deprisa.
- **C. Escala más corta para el inicio.** La regla de la pregunta 1 con el SPEI-30 en lugar del SPEI-90: 30 días previos > −0,5, por debajo de −1 al menos 20 días. Las sequías de 30 días empiezan desde la normalidad con más frecuencia, pero se separa del SPEI-90 de H2.
- **D. Relajar solo la condición previa:** 30 días > −0,5 en lugar de 60. Es el cambio mínimo, pero probablemente da pocos eventos más.

**Propuesta:** B como definición principal y A como sensibilidad.

**Regla de elección, ciega al resultado.** Antes de mirar ninguna variable de vegetación, se cuentan los eventos de ≥ 10 celdas con celdas de matorral que dan B y A, usando solo el SPEI:
- si B da al menos 10 eventos, B es la principal;
- si no, se usa A;
- si ninguna llega a 10, H3b es "no evaluable" con las dos.

El recuento se registra en git antes de calcular respuestas. Se mantienen las ventanas de inicio (marzo–septiembre y dentro del periodo con datos de vegetación) y la definición de evento (vecindad de 8, inicios a ±15 días, al menos 10 celdas).

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

Se informa igual del bosque y del pastizal, que no deciden.

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

## Decisiones pendientes con el investigador

1. **Definición de episodio:** B como principal y A como sensibilidad, con la regla de elección ciega al resultado del apartado 2.
2. **Mínimo de 10 eventos** para que H3b sea evaluable.
3. **Desfases de −15 a +60 días** con la media hacia atrás como principal.
4. **Corrección del PAR** estimada en los días con SPEI-90 ≥ 0, como principal.
5. **Ruido:** fracción de ruido por diferencias de días consecutivos, 5 réplicas, y "H1 robusto" en la mediana de las réplicas.
6. **Criterio de decisión** del apartado 6, con tres salidas: apoyo, contrario y no concluyente.
