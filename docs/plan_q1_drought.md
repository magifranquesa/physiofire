# Pregunta 1: respuesta de SIF/APAR y NDVI/EVI al estrés hídrico (plan prerregistrado)

**Estado:** aprobado por el investigador el 8 de noviembre de 2026. Este plan y la sección `drought_q1` de `config/config.yaml` se fijan en git **antes** de descargar la referencia, calcular el SPEI o extraer ninguna serie para el análisis. Después no se cambia ningún parámetro: los errores se corrigen documentados como tales, y cualquier ajuste motivado por los resultados se hace como análisis adicional marcado como posterior.

## Pregunta e hipótesis

**Pregunta.** ¿SIF/APAR detecta el estrés hídrico antes y a escalas más cortas que el NDVI/EVI en la vegetación natural de la Península, con independencia de los incendios?

**Hipótesis.** SIF/APAR (fisiología) responde a escalas de déficit hídrico más cortas y con menos desfase que el NDVI y el EVI (estructura y verdor). Base conceptual: Tang et al. (2026).

## Datos y celdas

- **Periodo de vegetación:** del 1 de mayo de 2018 (inicio de TROPOMI) al 31 de diciembre de 2025.
- **Celdas:** de 0,05°, con al menos un 50 % de tierra y clase dominante de FirEUrisk natural: bosque cerrado, bosque abierto, matorral, brezal o pastizal.
- **Exclusión por incendios:** se excluye cualquier celda con superficie quemada desde 2013 según cualquier fuente (MCD64A1 y VNP64A1 desde 2013, EFFIS desde 2018, ESFire30 en España). Cultivos y celdas sin combustible quedan fuera.
- **Tamaño esperado:** recuento previo solo con MCD64A1 y VNP64A1, 9436 celdas.

| Clase | Celdas |
| --- | --- |
| Matorral | 5121 |
| Bosque cerrado | 2084 |
| Pastizal | 1507 |
| Brezal | 381 |
| Bosque abierto | 343 |

- **Estratos:**
  - **matorral** = matorral + brezal; decide el resultado. El brezal se da también por separado, solo como descriptivo;
  - **bosque** = bosque cerrado + bosque abierto; se informa con el mismo detalle, pero no decide;
  - **pastizal**, como referencia.
- **Aridez:** Global-AI v3.1 en tres clases: semiárido < 0,5, subhúmedo seco 0,5–0,65 y húmedo > 0,65.

## Variables de vegetación

Se usan las mismas fuentes y filtros que en el caso 2025, sin cortes por incendio.

- **SIF/APAR** = SIF / (PAR × fPAR):
  - PAR = 0,48 × radiación de onda corta de ERA5-Land;
  - fPAR de MCD15A3H, interpolado linealmente entre compuestos, de forma centrada y sin persistencia; no hay fecha de corte que proteger;
  - umbrales de validez del caso 2025: fPAR ≥ 0,15, PAR ≥ 40 W m⁻² y peso de TROPOSIF ≥ 0,1;
  - filtro de picos con k = 6.
- **NDVI y EVI:** combinado Terra + Aqua (media si hay los dos, el disponible si no) y el mismo filtro de picos.
- **Secundarias, solo descriptivas:** SIF sin normalizar, SIF/PAR y fPAR.
- **Anomalías:** mediana por día del año (±15 días) sobre 2018–2025, después una media centrada de 15 días (al menos la mitad de días válidos), igual para todas las variables. Se estandariza por la desviación típica de la serie suavizada de cada celda en todo el periodo.

## Variables explicativas

**SPEI diario**, con acumulación móvil.

- **Balance hídrico diario:** D = P − ET0, en la rejilla nativa de ERA5-Land (0,1°).
  - **P:** suma de las 24 imágenes horarias `total_precipitation_hourly` de ERA5-Land del día UTC (horas que terminan entre las 01 y las 24 h).
  - **ET0:** FAO-56 Penman-Monteith con el mismo código que la AED (`physiofire.preprocess.aed`).
- **Escalas:** 15, 30, 60, 90, 180 y 365 días (suma de D en los n días que terminan en el día evaluado).
- **Distribución:** log-logística, ajustada por momentos ponderados no sesgados (valores por defecto del paquete SPEI de R, versión 1.8.1), con un ajuste por día del año. El 29 de febrero se elimina.
- **Referencia:** 1991–2020. ERA5-Land diario está disponible desde 1950.
- **Paso a 0,05°:** cada celda de 0,05° toma el valor de la celda de 0,1° que la contiene.
- **Comprobación antes del cálculo:** que el paquete SPEI ajusta series de frecuencia 365 sobre un periodo de referencia, con una serie sintética. Si no lo hace, el mismo método (log-logística, momentos ponderados no sesgados, ajuste por día del año) se implementa en R y se valida contra el paquete con datos mensuales. Todo ello antes de calcular el SPEI de las celdas.

**AED (ET0) como variable explicativa secundaria.** Anomalía respecto a la mediana por día del año (2018–2025), con la misma media centrada de 15 días. Sirve para comparar con el resultado de Tang con el VPD, porque la fisiología se alinea con la demanda atmosférica.

## Análisis 1: escala y desfase de máxima correlación

- **Correlación:** para cada celda, variable de vegetación V, escala del SPEI *s* y desfase L de 0 a 60 días, correlación de Pearson entre la anomalía de V el día *t* y el SPEI-*s* el día *t* − L.
- **Estación:** abril–octubre, para el día *t* de la vegetación; todos los años juntos.
- **Resultado por celda:** la correlación positiva máxima *r\** (más agua, más actividad) y la escala *s\** y el desfase *L\** donde se alcanza.
- **AED:** lo mismo, con desfases de 0 a 60 días. Se toma la correlación más negativa (más demanda, menos actividad) y su desfase.
- **Significación:** prueba de permutación del máximo. Se permutan los años completos de la serie de vegetación respecto al SPEI (199 permutaciones, semilla 42). En cada permutación se recalcula el máximo sobre todas las escalas y desfases, y *r\** es significativa si supera el percentil 95 de esos máximos. Así se tiene en cuenta la selección del máximo entre 6 × 61 combinaciones y la autocorrelación dentro de cada año.
- **H1 (escala).** Entre las celdas con *r\** significativa en las dos variables, la escala óptima de SIF/APAR es más corta que la del NDVI en ≥ 60 % de las celdas, y también que la del EVI.
  - Los empates no cuentan como "más corta".
  - El intervalo bootstrap del porcentaje, por bloques espaciales de 1° (2000 réplicas, semilla 42), debe excluir el 50 %.
- **H2 (desfase).** A la escala fija del SPEI-90, entre las celdas con correlación significativa en las dos variables a esa escala, la mediana de L(SIF/APAR) − L(NDVI) es ≤ −5 días, y lo mismo frente al EVI. El intervalo bootstrap por bloques de 1° debe quedar entero por debajo de cero.
  - La significación a una escala fija se calcula con la misma prueba de permutación, con el máximo solo sobre los desfases.
- **Descriptivos:** mapas de *s\**, *L\** y *r\** por variable; distribuciones por estrato y clase de aridez; lo mismo para las variables secundarias y para la AED.

## Análisis 2: episodios de sequía

- **Episodio en una celda:**
  - el SPEI-90 baja de −1 y se mantiene por debajo al menos 30 días seguidos;
  - inicio = primer día por debajo de −1, entre el 1 de marzo y el 30 de septiembre;
  - los 60 días anteriores al inicio tienen SPEI-90 > −0,5;
  - el inicio y la ventana de respuesta caen dentro del periodo con datos de vegetación.
- **Día de respuesta de cada variable:** primer día, entre −30 y +90 días respecto al inicio, desde el que su anomalía suavizada se mantiene ≤ −0,5 DE al menos 15 días seguidos.
  - Si no ocurre, la celda se marca "sin respuesta".
  - La media centrada adelanta unos 7 días los días de respuesta de todas las variables por igual, así que las diferencias entre variables no cambian.
- **Eventos:** las celdas con episodio se agrupan en eventos (componentes conexas con vecindad de 8 celdas, con inicios a ±15 días). Solo cuentan los eventos con al menos 10 celdas.
- **Estadístico:**
  - para cada celda con respuesta en las dos variables, diferencia emparejada del día de respuesta (SIF/APAR − NDVI, y SIF/APAR − EVI);
  - para cada evento, la mediana de sus celdas.
- **H3.** La mediana entre eventos de esa diferencia es ≤ −5 días frente al NDVI y frente al EVI. El intervalo bootstrap por eventos (2000 réplicas, semilla 42) debe quedar entero por debajo de cero.
  - Se informa también del número de celdas sin respuesta en cada variable.

## Criterio de decisión

**Resultado positivo** si, en el estrato matorral (matorral + brezal), se cumple **H3 y además H1 o H2**. Cada hipótesis tiene que cumplirse frente al NDVI y frente al EVI.

El bosque se informa con el mismo detalle y el pastizal como referencia; ninguno de los dos decide. Un resultado negativo también se documenta y es publicable.

## Diferencias con Vicente-Serrano et al. (2013, PNAS 110:52–57)

Su método, según el texto en PMC3538253 (no se pudo leer el apéndice suplementario):
- NDVI de GIMMS (1981–2006, compuesto mensual de máximos) y MODIS (2001–2009), estandarizados con la media y la desviación típica de la serie mensual de cada píxel;
- SPEIbase mensual a 0,5°, escalas de 1 a 24 meses, interpolado a la resolución de la vegetación;
- para cada píxel, 12 series (una por mes) correlacionadas con el SPEI de 1–24 meses, 288 correlaciones;
- se conserva la máxima por estación y la escala donde se alcanza, y luego la anual;
- significación con α = 0,05, sin corrección por la selección del máximo;
- sin desfase explícito: el desfase está implícito en la escala.

| Aspecto | Vicente-Serrano et al. (2013) | Este plan | Motivo |
| --- | --- | --- | --- |
| Resolución temporal | mensual | diaria, con media centrada de 15 días | La hipótesis habla de días; Tang encuentra respuestas de 3–8 días |
| Escalas | 1–24 meses | 15–365 días | Escalas cortas para la fisiología; el registro de TROPOMI es corto |
| Desfase | implícito en la escala | explícito, 0–60 días, y aparte de la escala | Separar "cuánto tiempo integra" de "cuánto tarda" |
| Correlación por mes | 12 series por mes del año | estación abril–octubre agrupada | Con 8 temporadas, una correlación por mes tendría 8 puntos |
| Registro | 26 años (GIMMS) | 7,7 años (2018–2025) | Disponibilidad de TROPOMI |
| Significación | α = 0,05 sin corrección | permutación de años del máximo | La selección del máximo entre muchas combinaciones infla la significación |
| Vegetación | NDVI/EVI (y anillos, ANPP) | SIF/APAR frente a NDVI/EVI | Comparar fisiología con estructura |
| SPEI | SPEIbase, 0,5°, CRU | ERA5-Land, 0,1°, referencia 1991–2020 | Coherencia con el FWI, la PAR y la AED del proyecto |
| Unidades | biomas de Holdridge y balance hídrico | clases de FirEUrisk y aridez (Global-AI v3.1) | Combustible del proyecto; aridez comparable a su eje de balance hídrico |

**Implicación para la discusión.** Su resultado principal es que los biomas áridos y húmedos responden a escalas cortas (2–4 meses) y los semiáridos y subhúmedos a escalas largas, de hasta 8–10 meses cerca del balance cero. Nuestras escalas son más cortas y el registro más breve, así que la comparación será cualitativa: el gradiente de escala con la aridez.

## Datos que faltan y volumen

| Dato | Volumen y tiempo | Estado |
| --- | --- | --- |
| P diaria de ERA5-Land, 1991–2025, desde datos horarios (GEE) | ≈ 0,6 GB, ≈ 1 h | aprobado |
| Entradas de la ET0, 1991–2016 (mismo código que la AED) | ≈ 1,1 GB, ≈ 1 h | aprobado |
| Paquete SPEI 1.8.1 (CRAN) en `renv.lock` | — | pendiente |

El resto ya está: SIF a 0,05°, fPAR, PAR, MOD09GA/MYD09GA, FirEUrisk, aridez e historiales de quema.

## Pasos y salidas

1. Descargar P y las entradas de la ET0; calcular la ET0 de 1991–2016 y unirla con 2017–2025.
2. Comprobar el paquete SPEI con datos sintéticos.
3. Calcular el SPEI a 0,1° para las seis escalas y guardar los parámetros de la referencia.
4. Seleccionar las celdas (`drought_q1_cells.csv`) y extraer sus series.
5. Calcular las anomalías.
6. Análisis 1, con la prueba de permutación.
7. Análisis 2.
8. Evaluar el criterio de decisión.
9. Escribir `docs/results_q1_drought.md`.

Cada paso tiene tests con datos sintéticos antes de aplicarse a datos reales. Las salidas van a `data/processed/drought_q1/` y las figuras a `figures/drought_q1/`.

**Tiempo estimado:** 2–3 días de código y pruebas, unas 3 h de cálculo y 1 día de informe.
