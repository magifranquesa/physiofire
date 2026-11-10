# Ecuaciones de los métodos, comprobadas contra el código

**10 de noviembre de 2026.** Cada ecuación propuesta para el manuscrito, comprobada contra el código que produjo los resultados. No se ha cambiado código ni resultados.

Para cada punto se da el veredicto:
- **coincide**;
- **coincide, con precisiones**: la ecuación es correcta, pero faltan detalles necesarios para reproducirla;
- **no coincide**: se da la versión correcta.

Notación: $c$ = celda de 0,05°; $t$ = día; $\tau$ = día relativo a la ignición o al inicio de la sequía.

---

## (1) PAR y APAR: coincide, con precisiones

$$
\mathrm{PAR}_{c,t} = 0.48\,\overline{SW\!\downarrow}_{c,t},\qquad
\overline{SW\!\downarrow}_{c,t} = \frac{SSRD^{\mathrm{day}}_{t}}{86\,400}\ \ [\mathrm{W\,m^{-2}}],\qquad
\mathrm{APAR}_{c,t} = \mathrm{PAR}_{c,t}\,\mathrm{fPAR}_{c,t}
$$

- **SW↓:** `surface_solar_radiation_downwards_sum` de ERA5-Land diario (GEE `ECMWF/ERA5_LAND/DAILY_AGGR`; suma del día UTC en J m⁻²) dividida por 86 400. Es, por tanto, la **media diaria en W m⁻²**. Código: `download/gee.py::run_shortwave` y `_series_fetch_one`.
  - Paso a 0,05° por **remuestreo bilineal** desde 0,1° (`_reproject_bilinear`). No se usa la celda contenedora, a diferencia del FWI, la AED y el SPEI.
  - El factor 0,48 y la exclusión de SW ≤ 0 están en `epoch.py::open_inputs` (`par_fraction`).
- **fPAR:** MCD15A3H v061, solo píxeles del algoritmo principal (SCF_QC ≤ 1) sin nubes, cirros ni sombra, y sin estado de nubes de MOD09 1 o 2. Se agrega a 0,05° como media de los píxeles de 500 m válidos (`gee.py::fpar_images`).
  - El compuesto de 4 días se sitúa en su centro (inicio + 1,5 días) y se interpola **linealmente entre centros de compuestos**, evaluado a las 12:00 de cada día, rellenando huecos de hasta 12 días (`sif_apar.fpar_max_gap_days`).
- **Caso 2025** (`indices.py::composites_to_daily_cut`, llamado por `epoch.py::sif_apar_causal`):
  - antes de interpolar se quitan los compuestos cuyo periodo termina en la ignición o después;
  - tras el último compuesto válido se repite su valor **como máximo 5 días contados desde el centro del compuesto**;
  - todo se anula desde la ignición.
  - Hay dos versiones: con persistencia (`sif_apar`) y **sin persistencia** (`sif_apar_nopersist`). **La Fig. 2 y las antelaciones del texto usan la versión sin persistencia.**
- **Pregunta 1 y Q1b** (`indices.py::composites_to_daily`, llamado por `drought_q1.py::build_series`): interpolación lineal centrada, sin persistencia y sin corte.

## (2) SIF/APAR: coincide, con precisiones

$$
\left(\frac{\mathrm{SIF}}{\mathrm{APAR}}\right)_{c,t} = \frac{\mathrm{SIF}_{c,t}}{\mathrm{PAR}_{c,t}\,\mathrm{fPAR}_{c,t}}
$$

- **Sin ningún factor de unidades** (`indices.py::sif_apar`). Unidades: (mW m⁻² sr⁻¹ nm⁻¹) / (W m⁻²). Como todo se analiza en anomalías estandarizadas, ni el factor 0,48 ni las unidades afectan a los resultados.
- **SIF:** `SIF_Corr_743` de TROPOSIF L2B, corregida por la duración del día (configuración `sif.variable`). La definición exacta de la corrección conviene citarla del ATBD de TROPOSIF **(verificar)**.
- **Rejillado** (`preprocess/troposif_grid.py`): media diaria ponderada por la huella de cada píxel en la celda, con 4 × 4 subpuntos por píxel:

  $$
  \mathrm{SIF}_{c,t}=\frac{\sum_i w_{i,c}\,s_i}{\sum_i w_{i,c}}
  $$

  - Filtros de píxel: `cloud_fraction_L2` ≤ 0,5; `LC_MASK` > 0 y distinto de 15 (nieve) y 16 (suelo desnudo). El producto L2B ya trae solo píxeles con calidad > 0,5.
- **Validez de SIF/APAR**, aplicada antes de las anomalías (`epoch.py::screening_mask`): fPAR ≥ 0,15, PAR ≥ 40 W m⁻² y $\sum_i w_{i,c}$ ≥ 0,1 píxeles equivalentes.
- **Filtro de picos** (Hampel; `anomalies.py::spike_filter`), sobre la serie diaria antes de las anomalías:
  - quita $x_t$ si $|x_t-\mathrm{med}(x_{t-3..t+3})| > 6 \cdot 1.4826\,\mathrm{MAD}_c$, siendo $\mathrm{MAD}_c$ la mediana de los residuos absolutos de toda la serie de la celda;
  - se aplica a SIF/APAR, NDVI y EVI (y a SIF y SIF/PAR en la pregunta 1), no al FWI ni a la AED.

## (3) NDVI y EVI: coincide, con precisiones

$$
\mathrm{NDVI}=\frac{\rho_{NIR}-\rho_R}{\rho_{NIR}+\rho_R},\qquad
\mathrm{EVI}=2.5\,\frac{\rho_{NIR}-\rho_R}{\rho_{NIR}+6\rho_R-7.5\rho_B+1}
$$

(`indices.py::ndvi`, `indices.py::evi`.)

- **Bandas de MOD09GA/MYD09GA v061:** R = `sur_refl_b01`, NIR = `sur_refl_b02` y B = `sur_refl_b03`, con escala 10⁻⁴ (configuración `gee.sr_bands`).
- **Filtros por píxel de 500 m** (`gee.py::sr_images`):
  - `state_1km`: despejado, sin sombra, sin cirros, sin adyacencia, sin nieve, aerosol no alto y tierra;
  - `QC_500m` ≤ 1;
  - ángulo cenital de observación ≤ 40°;
  - ninguna banda negativa.
  - Además se rechaza la imagen entera si más del 10 % de los píxeles filtrados son negativos.
- **El índice se calcula después de agregar:** primero se promedian a 0,05° las reflectancias de cada banda sobre los píxeles válidos (`reduceResolution`, media) y después se calculan NDVI y EVI (`epoch.py::_optical`). Es una diferencia respecto a calcular el índice por píxel.
- El **EVI fuera de [0, 1] se anula**; el NDVI no tiene límite de rango.
- **Terra + Aqua** (`epoch.py::combine_platforms`), cada plataforma por separado:

  $$
  I_{c,t}=\begin{cases}\tfrac12\,(I^{T}_{c,t}+I^{A}_{c,t}) & \text{si los dos son válidos}\\ \text{el válido} & \text{si solo hay uno}\end{cases}
  $$

## (4) ET0 FAO-56 Penman–Monteith: coincide, con precisiones

$$
ET_0=\frac{0.408\,\Delta\,(R_n-G)+\gamma\,\dfrac{900}{T+273}\,u_2\,(e_s-e_a)}{\Delta+\gamma\,(1+0.34\,u_2)},\qquad ET_0\leftarrow\max(ET_0,0)
$$

(`preprocess/aed.py::et0_fao56`, con entradas de `download/era5land_aed.py`.)

| Término | Implementación |
| --- | --- |
| Paso temporal | **Diario**, con $T=(T_{max}+T_{min})/2$ de ERA5-Land `DAILY_AGGR` |
| $e_s$ | $[e^0(T_{max})+e^0(T_{min})]/2$, con $e^0(T)=0.6108\exp\!\big(\tfrac{17.27T}{T+237.3}\big)$ (Ec. 11–12) |
| $e_a$ | $e^0(T_{dew})$ desde el **punto de rocío medio diario** (Ec. 14) |
| $\Delta$ | $4098\,e^0(T)/(T+237.3)^2$, con la $T$ media |
| $\gamma$ | $0.000665\,P$ con la **presión superficial media diaria** de ERA5-Land (Ec. 8) |
| $u_2$ | $u_{10}\cdot 4.87/\ln(67.8\cdot10-5.42)$ (Ec. 47), con $u_{10}$ = **media de las 24 velocidades horarias** $\sqrt{u^2+v^2}$ de ERA5-Land horario. Si falta alguna hora, el día queda sin dato |
| $R_n$ | **Estimación FAO-56**, no los flujos netos de ERA5-Land: $R_n=(1-0.23)R_s-R_{nl}$, con $R_s$ = SSRD diaria (MJ m⁻²) |
| $R_{nl}$ | $\sigma\,\frac{T_{max,K}^4+T_{min,K}^4}{2}\,(0.34-0.14\sqrt{e_a})\,(1.35\,R_s/R_{so}-0.35)$, con $T_K=T+273.16$ y $R_s/R_{so}$ limitado a [0,25; 1] (Ec. 39) |
| $R_{so}$ | $(0.75+2\cdot10^{-5}z)\,R_a$ (Ec. 37), con $z$ obtenida de la presión superficial (Ec. 7 invertida) y $R_a$ de la latitud y el día del año (Ec. 21) |
| $G$ | **0** (escala diaria) |

## (5) SPEI: coincide, con precisiones

$$
D_t=P_t-ET_{0,t},\qquad
D^{(k)}_t=\sum_{j=0}^{k-1}D_{t-j},\quad k\in\{15,30,60,90,180,365\}\ \text{días}
$$

$$
\mathrm{SPEI}^{(k)}_t=\min\!\Big(3.09,\ \max\!\big(-3.09,\ \Phi^{-1}\!\big[F_{\mathrm{doy}(t)}\big(D^{(k)}_t\big)\big]\big)\Big)
$$

(`R/spei_lib.R::spei_daily`, `R/q1_spei.R`, `preprocess/water_balance.py`.)

- **$P_t$:** suma de las 24 imágenes horarias de ERA5-Land del día UTC, de las 01:00 del día $t$ a las 00:00 del día $t+1$ (cada imagen guarda la hora que termina en su marca). **$ET_{0,t}$:** el mismo código que la AED.
- **El 29 de febrero se elimina antes de acumular**: cada ventana suma $k$ días de un calendario de 365 días. Al final se le asigna NA.
- La suma exige los $k$ días válidos (`roll_sum`). La serie empieza el 1 de enero de 1991, así que los primeros $k-1$ días de 1991 quedan sin dato.
- **$F_{\mathrm{doy}}$:** log-logística de tres parámetros, ajustada por momentos ponderados no sesgados (`SPEI::spei`, `distribution = "log-Logistic"`, `fit = "ub-pwm"`, SPEI 1.8.1). Hay **un ajuste por cada uno de los 365 días del año** (serie con frecuencia 365, `scale = 1` sobre la acumulación ya calculada), con referencia **1991–2020**.
- **Recorte:** todo valor fuera de ±3,09 se lleva a ±3,09, incluidos los ±∞ que aparecen fuera del soporte de la distribución.
- **Rejilla:** se calcula en la rejilla nativa de ERA5-Land de 0,1°. Cada celda de 0,05° toma el SPEI de la celda de 0,1° **que la contiene**, extraído en el centro de esa celda (`lon01`, `lat01`). Cada celda de 0,05° cae entera dentro de una de 0,1°.

## (6) Anomalía estandarizada: no coincide en σ ni en el orden de las operaciones

El código no estandariza la anomalía diaria y luego la suaviza. **Calcula la anomalía, la suaviza y divide por la desviación típica de la anomalía suavizada.** Versión correcta:

$$
a_{c,t}=x_{c,t}-\tilde x_c\big(\mathrm{doy}(t)\big),\qquad
\tilde x_c(d)=\operatorname*{mediana}\{x_{c,s}: |\mathrm{doy}(s)-d|_{366}\le 15\}
$$

$$
\bar a_{c,t}=\mathcal{S}_{15}\big(a_{c,\cdot}\big)_t\quad\text{(ec. 7)},\qquad
\bar z_{c,t}=\frac{\bar a_{c,t}}{\sigma_c},\qquad \sigma_c=\operatorname{sd}\{\bar a_{c,s}: s\in\mathcal{R}\}
$$

Como σ es constante para cada celda, $\bar z = \mathcal S_{15}(a)/\sigma_c$ equivale a suavizar $a/\sigma_c$. Pero **σ_c es la desviación típica de la anomalía suavizada, no la de $x$ ni la de la anomalía diaria.**

- **Día del año:** se usa el ordinal del calendario (1–366), con distancia circular módulo 366 (`anomalies.py::_doy_pooled`). La mediana agrupa todos los años disponibles en el periodo $\mathcal{R}$ de cada análisis.

| Análisis | Datos de la mediana $\tilde x_c$ | $\sigma_c$: periodo $\mathcal{R}$ | Código |
| --- | --- | --- | --- |
| Caso 2025 | 1 may 2018 – día anterior a la ignición (todo se anula desde la ignición en las celdas quemadas **y en los controles** de ese incendio) | Todos los días **anteriores al día −60** (desde mayo de 2018) | `epoch.py::fire_series`, `standardize(…, win_start)` |
| Pregunta 1 (análisis 1 y H3/H3b) | 1 may 2018 – 31 dic 2025 | **Todo el periodo**, todos los meses | `drought_q1.py::standardised_anomaly` |
| Q1b, análisis 1b | Igual | Todo el periodo (de la serie suavizada hacia atrás) | `drought_q1b.py::smooth_standardise` |

Variables meteorológicas:
- **FWI y AED en el caso 2025:** la misma cadena (mediana por día del año, media hacia atrás y σ anterior al día −60), sin filtro de picos.
- **AED en la pregunta 1:** igual que la vegetación (mediana por día del año, media centrada y σ de todo el periodo).
- **El SPEI no se reestandariza:** entra tal cual.
- El FWI no se usa en la pregunta 1.

## (7) Medias móviles: coincide en la fórmula; H3b usa la media centrada

$$
\mathcal{S}^{\leftarrow}_{15}(a)_t=\frac{1}{n_t}\sum_{j=0}^{14}a_{t-j}\,\mathbb{1}[a_{t-j}\ \text{válido}],\qquad
\mathcal{S}^{\leftrightarrow}_{15}(a)_t=\frac{1}{n_t}\sum_{j=-7}^{7}a_{t+j}\,\mathbb{1}[\cdot]
$$

**Mínimo exacto: $n_t\ge 8$ días válidos de 15.** En el código de la media hacia atrás del caso 2025 es $\lceil 0.5\cdot15\rceil=8$; en la centrada y en la hacia atrás de Q1b es $n_t\ge 7.5$. Si no se llega, el valor queda sin dato.

| Análisis | Media | Código |
| --- | --- | --- |
| Caso 2025 | Hacia atrás | `anomalies.py::trailing_mean` |
| Pregunta 1, análisis 1 y 2 | Centrada | `drought_q1.py::centred_mean` |
| Q1b, análisis 1b (escala, desfase y H1 corregidos) | Hacia atrás | `drought_q1b.py::backward_mean` |
| **Q1b, H3b (el criterio) y Fig. 5** | **Centrada**: las anomalías de la pregunta 1 | `drought_q1b.py::main` (paso `analysis2`) |
| Q1b, H3b de sensibilidad | Hacia atrás, con SIF/APAR corregido por el PAR | íd. (`bwcorr_`) |

**Lo que propone el borrador ("hacia atrás en Q1b") no es exacto para H3b.** El día de respuesta del criterio y de la Fig. 5 se calcula con la media centrada, que usa datos de hasta 7 días después de cada día.

## (8) Caso 2025: Δ, antelación e intervalos: coincide el orden, no la regla de antelación

**Orden de promedios** (`R/epoch_lib.R::fire_day_table`, `effect_table`): celdas → incendio → conjunto.

$$
B_{f,\tau}=\frac{\sum_{c\in\mathcal{B}_f} w_c\,\bar z_{c,\tau}}{\sum_{c\in\mathcal{B}_f} w_c},\qquad
C_{f,\tau}=\frac{1}{|\mathcal{C}_f|}\sum_{c\in\mathcal{C}_f}\bar z_{c,\tau},\qquad
\Delta_{f,\tau}=B_{f,\tau}-C_{f,\tau}
$$

$$
\Delta_\tau=\frac{1}{|\mathcal{F}_\tau|}\sum_{f\in\mathcal{F}_\tau}\Delta_{f,\tau}
$$

- **Las celdas quemadas se ponderan por su fracción quemada** ($w_c$ = `burned_fraction`). Los controles entran con peso 1.
- Solo cuentan las celdas con valor ese día. $\mathcal{F}_\tau$ son los incendios con $\Delta_{f,\tau}$ válido, de ahí que el número de incendios varíe con el día (Fig. 2).

**El umbral se aplica con signo.** El signo esperado es $s_v$ = −1 para SIF/APAR, NDVI y EVI, y +1 para FWI y AED (`epoch.expected_sign`). En la estimación puntual se exige, además, que el intervalo excluya el 0:

$$
M_\tau=\mathbb{1}\big[s_v\,\Delta_\tau\ge 0.5\big]\cdot\mathbb{1}\big[\mathrm{IC}_{95}(\Delta_\tau)\ \text{excluye 0 en la dirección de } s_v\big]
$$

$$
L=\max\{\,m\ge0:\ M_\tau=1\ \ \forall\,\tau\in\{-m,\dots,-1\}\,\}
$$

(`R/epoch_lib.R::lead_time`.) $L$ es la longitud de la racha que acaba en el día −1, y $L=0$ si $M_{-1}=0$. La antelación de las celdas quemadas solas usa la misma regla con $B_\tau=\tfrac{1}{|\mathcal F_\tau|}\sum_f B_{f,\tau}$.

**Hay dos bootstraps distintos** (B = 2000, semilla 42, remuestreo de incendios con reemplazo):
1. **Intervalo de $\Delta_\tau$ (bandas de la Fig. 2):** para cada día por separado, cuantiles 2,5 y 97,5 % de la media de $\Delta_{f,\tau}$ sobre incendios remuestreados (`R/epoch_lib.R::.boot_ci`).
2. **Intervalo de $L$ (Tabla 2):** se remuestrean incendios (filas completas de la matriz incendio × día), se recalcula la curva media $\Delta^{*}_\tau$ y $L^{*}$ con la regla **solo del umbral con signo, sin la condición del intervalo**, y se toman los cuantiles 2,5 y 97,5 % de $L^{*}$ (`R/epoch_report_2025.R::lead_boot`).

   La estimación puntual de la Tabla 2 sí incluye la condición del intervalo. Como todos los valores son 0 [0, 0] o casi, no cambia nada en el caso 2025, pero conviene describirlo así.

Las bandas de los controles de la Fig. 2 son un cálculo descriptivo hecho para la figura, con el mismo bootstrap (`R/manuscript_figures/fig2_epoch.R`).

## (9) Pregunta 1: correlación y permutaciones: coincide, con precisiones

$$
r_c(k,\ell)=\operatorname{corr}_{\text{Pearson}}\Big(\bar z_{c,t},\ \mathrm{SPEI}^{(k)}_{c,t-\ell}\Big),\quad t\in\{\text{abril–octubre, todos los años}\},\ \ \ell\in\{0,\dots,60\}
$$

$$
(k^*,\ell^*)=\arg\max_{k,\ell}\, r_c(k,\ell)
$$

(`drought_q1.py::max_corr_cell`, `lagged_season`, `pooled_corr`.)

- **Máximo de $r$ con signo**, no de $|r|$. Para la AED se toma el mínimo (la correlación más negativa).
- $\mathrm{SPEI}_{t-\ell}$ se desplaza en la serie diaria completa, así que para los días de abril se usan valores de marzo o anteriores.
- Los días se alinean por mes y día del calendario. Las parejas de días con dato se agrupan entre años, y se exigen al menos 30.
- **Permutaciones:** 199 (`analysis1.permutations`).
  - Se permutan **años completos de vegetación**: la temporada de abril a octubre del año $\pi(b)$ de la vegetación se empareja con la del año $b$ del SPEI. Se descarta la permutación identidad.
  - En cada permutación se recalcula el máximo sobre **todas** las escalas y desfases.

  $$
  p=\frac{1+\#\{\pi:\ \max_{k,\ell} r^{\pi}(k,\ell)\ge r_c(k^*,\ell^*)\}}{1+199}
  $$

- Una celda es significativa si $p<0.05$.
- Hay un generador aleatorio por celda (semilla [42, c]), compartido entre variables, así que el resultado es reproducible en cualquier orden.
- El desfase a escala fija (SPEI-90, H2) se calcula igual con $k=90$ y su propio $p$.
- **Q1b, análisis 1b:** desfases de −15 a +60 días con la media hacia atrás y SIF/APAR corregido por el PAR (`drought_q1b.py::lagged_season_signed`).

## (10) H1: coincide

$$
f=\frac{1}{N}\sum_{c=1}^{N}\mathbb{1}\big[k^*_{c,\mathrm{SIF/APAR}}<k^*_{c,\mathrm{ref}}\big],\qquad
N=\#\{c:\ p_{c,\mathrm{SIF/APAR}}<0.05\ \wedge\ p_{c,\mathrm{ref}}<0.05\}
$$

(`drought_q1.py::h1_test`.)

- Los empates no cuentan como "más corta".
- **Bootstrap por bloques de 1°:** bloque = $(\lfloor \mathrm{lat}\rfloor,\lfloor \mathrm{lon}\rfloor)$. Se remuestrean bloques completos con reemplazo, B = 2000, semilla 42, intervalo percentil del 95 % (`block_bootstrap`, `one_degree_block`).
- **Criterio:** $f\ge 0.60$ **y** límite inferior del IC > 0,5. El borrador debería mencionar también esta segunda condición.
- En Q1b se usa el mismo cálculo con SIF/APAR corregido por el PAR (`H1_par_corrected`) y en la réplica de ruido mediana (`H1_robust_noise`).

## (11) Q1b: inicio, respuesta, censura y agregación: no coincide la definición del inicio

**Inicio del episodio, definición B** (`drought_q1b.py::onsets_rapid`, `separate` y `window_ok`; configuración `drought_q1b.episodes.B`). Sobre el SPEI-90 diario de la celda, el día $i$ es candidato si:

$$
\mathrm{SPEI}_i<-1,\qquad \mathrm{SPEI}_{j}<-1\ \ \forall j\in[i,\,i+29],\qquad
\max_{j\in[i-30,\,i-1]}\mathrm{SPEI}_j-\mathrm{SPEI}_i\ \ge\ 1.0
$$

- La caída se mide **desde el máximo de los 30 días anteriores hasta el día del inicio**, partiendo de cualquier nivel. No hace falta que $i$ sea el primer día por debajo de −1: basta con que se cumplan las tres condiciones.
- De los candidatos de una celda **se queda el primero y se descartan los que caen a menos de 90 días** del último conservado.
- Después se exige que el inicio sea de **marzo a septiembre** y que la ventana [−30, +104] días quede dentro de los datos.
- **Eventos:** celdas vecinas (8 vecinos) con inicios a ±15 días como mucho, unidas en componentes conexas, con al menos 10 celdas (de cualquier vegetación) (`drought_q1.py::build_events`).
- La estación del evento sale de la **mediana del mes de inicio de todas sus celdas** (primavera, marzo–mayo; verano, junio–septiembre).

**Día de respuesta** (`drought_q1.py::response_day`), con $\bar z$ = **media centrada** de la pregunta 1:

$$
r_v=\min\Big\{d\in[-30,90]:\ \bar z_{o+d}\ \text{válido},\ \bar z_{o+d}\le-0.5,\ 
\#\{j\in[0,14]: \bar z_{o+d+j}\ \text{válido}\}\ge 8,\ \bar z_{o+d+j}\le-0.5\ \ \forall\,j\ \text{válido}\Big\}
$$

- Los huecos no cortan la racha ni cuentan como respuesta.
- La racha tiene que empezar en un día válido.
- Sin respuesta en la ventana, $r_v$ queda censurada.

**Variable observada** (`drought_q1b.py::observed`): $\bar z$ válida en al menos el 50 % de los días de [−30, +104]. Una pareja solo se usa si las **dos** variables están observadas.

**Diferencia y puntuación de signo por pareja** (`drought_q1b.py::pair_scores`):

$$
(d,S)=\begin{cases}
(r_a-r_b,\ \operatorname{sgn}(r_a-r_b)) & \text{responden las dos}\\
(r_a-90,\ -1) & \text{solo responde SIF/APAR (}b\text{ censurada)}\\
(90-r_b,\ +1) & \text{solo responde la referencia}\\
\text{no informativa (excluida)} & \text{no responde ninguna}
\end{cases}
$$

- $\operatorname{sgn}(0)=0$: un empate puntúa 0.
- Con una sola censurada, $d$ es una **cota**, no una diferencia observada.

**Agregación** (`drought_q1b.py::h3b_test`). Para cada evento $e$, sobre sus parejas informativas de matorral:

$$
\bar S_e=\frac{1}{n_e}\sum_{i\in e}S_i,\qquad \tilde d_e=\operatorname*{mediana}_{i\in e} d_i
$$

Entre eventos:

$$
\hat S=\frac{1}{E}\sum_e\bar S_e,\qquad \hat d=\operatorname*{mediana}_e\ \tilde d_e
$$

- El IC del 95 % de $\hat S$ se obtiene por bootstrap percentil sobre eventos (B = 2000, semilla 42).
- **Criterio:** al menos 10 eventos, $\hat S<0$ con el IC entero por debajo de 0 y $\hat d\le-5$ días.

## (12) FWI: coincide, con precisiones

- **Implementación:** `xclim` **1.0.0**, función `xclim.compute.fire.cffwis_indices` (`preprocess/fwi.py::compute`).
  - Sin temporada (`season_method=None`), sin arrastre invernal (`overwintering=False`) e `initial_start_up=True`.
  - Valores de arranque por defecto de xclim, comprobados en el código instalado: **FFMC 85, DMC 6 y DC 15**.
  - Cálculo continuo **desde el 1 de enero de 2017** (`fwi.start`), sobre la rejilla nativa de ERA5-Land de 0,1°.
  - Se pasa la latitud de cada celda para los factores de duración del día del DMC y el DC.
  - Validado con cffdrs (R): `R/check_fwi_cffdrs.R`.
- **Entradas** (`download/era5land_fwi.py`; ERA5-Land horario en GEE):

| Entrada | Implementación |
| --- | --- |
| Temperatura | $T_{2m}$ **instantánea a las 12:00 UTC** (`fwi.noon_utc_hour`). El mediodía solar va de las 11:42 a las 12:40 UTC según la longitud |
| Humedad relativa | De $T_{2m}$ y $T_{d}$ a las 12:00 UTC, con Magnus sobre agua: $\mathrm{HR}=100\,e(T_d)/e(T)$, $e(T)=6.1094\exp\!\big(\tfrac{17.625T}{T+243.04}\big)$, limitada a 100 % (`relative_humidity`) |
| Viento | $\sqrt{u_{10}^2+v_{10}^2}$ a las 12:00 UTC, en km h⁻¹ (× 3,6) |
| Precipitación | Suma de 24 h **hasta las 12:00 UTC**, de la imagen horaria de las 13:00 UTC del día anterior a la de las 12:00 del día, en mm, con negativos a 0 |

- En los análisis, cada celda de 0,05° toma el FWI de la celda de 0,1° que la contiene (`epoch.py::_extract`, vecino más cercano).

---

## Detalles que afectan a la reproducibilidad y no estaban en el borrador

1. **σ es la desviación típica de la anomalía suavizada** (punto 6), calculada sobre periodos distintos en cada análisis: en el caso 2025, solo los días anteriores al día −60.
2. **H3b y la Fig. 5 usan la media centrada** (punto 7), no la media hacia atrás.
3. **Antelación del caso 2025** (punto 8): la estimación puntual exige además que el intervalo excluya el 0, mientras que el bootstrap de $L$ no lo exige. Las celdas quemadas se ponderan por su fracción quemada.
4. **Inicio B** (punto 11): candidato a cualquier día con caída ≥ 1,0 desde el máximo de los 30 días anteriores, que se mantiene 30 días por debajo de −1; separación de 90 días. No es una caída "en 30 días o menos hasta cruzar −1".
5. **El PAR se remuestrea por bilineal** desde 0,1°. El FWI, la AED y el SPEI toman, en cambio, la celda de 0,1° que contiene a la de 0,05°.
6. **NDVI y EVI se calculan con reflectancias ya agregadas a 0,05°**, no por píxel, y el EVI fuera de [0, 1] se anula.
7. **Filtros anteriores a las anomalías:**
   - validez de SIF/APAR (fPAR ≥ 0,15, PAR ≥ 40 W m⁻² y peso ≥ 0,1);
   - filtro de picos de Hampel (±3 días, $k=6$), solo en variables de satélite.
8. **H1 tiene dos condiciones:** $f\ge0.60$ y límite inferior del IC > 0,5.
9. **Calendario:** el día del año usa el ordinal 1–366 con distancia circular. El SPEI elimina el 29 de febrero antes de acumular.
10. **Caso 2025:** el enmascarado desde la ignición se aplica también a los controles de cada incendio, así que su climatología termina en la misma fecha.

---

## Precisiones de fPAR y de los filtros de SIF/APAR (10 de noviembre de 2026)

Lecturas del código y un cálculo descriptivo hecho para el texto. No cambia ningún resultado.

**Centro de los compuestos de MCD15A3H.**
- Se fija en $t_{\mathrm{inicio}}+1.5$ días (`gee.fpar.composite_center_days`; `download/gee.py`). El inicio del compuesto es a las 00:00 UTC, así que el centro cae a las **12:00 del segundo día** del compuesto.
- El fPAR diario se evalúa a las 12:00 de cada día.
- El punto medio exacto de los 4 días sería $t_{\mathrm{inicio}}+2.0$ días; la convención usada lo adelanta medio día.

**Huecos.**
- Se interpola linealmente entre los centros de dos compuestos válidos si están a **12 días o menos**. Si están más separados, los días intermedios quedan sin dato (`xarray.interpolate_na`, `max_gap = 12` días).
- Comprobado con una serie sintética: con 1 o 2 compuestos perdidos (centros a 8 y 12 días) se rellena; con 3 (16 días), no.
- No se extrapola antes del primer compuesto válido ni después del último.

**Días sin fPAR antes de la ignición** (caso 2025, versión sin persistencia, 22 incendios):
- El último compuesto cuyo periodo termina antes de la ignición tiene su centro entre 2,5 y 5,5 días antes de ella. Desde ese centro hasta el día −1, fPAR y SIF/APAR quedan sin dato.
- Todas las celdas de un mismo incendio tienen el mismo hueco.

  | Días sin dato al final (hasta el día −1) | Incendios |
  | --- | --- |
  | 2 | 6 |
  | 3 | 7 |
  | 4 | 5 |
  | 5 | 4 |

- La mediana es 3 días.
- La media hacia atrás de 15 días (con al menos 8 válidos) sigue definida en el día −1, pero solo con datos hasta 2–5 días antes de la ignición.

**Peso de TROPOSIF** (umbral 0,1):

$$
W_{c,t}=\sum_{i}w_{i,c}
$$

- La suma recorre todos los píxeles de todas las órbitas del día $t$. $w_{i,c}$ es la **fracción de la huella del píxel $i$ que cae en la celda $c$**, estimada con 4 × 4 subpuntos por píxel, de 1/16 cada uno (`preprocess/troposif_grid.py`).
- Unidades: **píxeles completos equivalentes** (adimensional). $W\ge0.1$ equivale a una décima de la huella de un píxel (unos 2 km² con píxeles de 3,5 × 5,5 km) dentro de la celda ese día.

**Filtro de Hampel** (`anomalies.py::spike_filter`):

$$
r_t=x_t-\operatorname*{mediana}_{|j|\le3}x_{t+j},\qquad s=1.4826\,\operatorname*{mediana}_t|r_t|,\qquad x_t\leftarrow\text{NA si }|r_t|>6s
$$

- **Ventana:** centrada de 7 días; la mediana móvil incluye el propio día. Exige **al menos 3 valores válidos** en la ventana; si no los hay, no hay mediana y el valor se conserva.
- **Escala $s$:** se calcula sobre **toda la serie de la celda**. En el caso 2025 es la serie hasta la ignición, porque el filtro se aplica después del corte; en la pregunta 1 y Q1b, la de 2018–2025. Solo se aplica si $s>0$.
- **Una sola pasada.** Los valores marcados pasan a faltantes. Se aplica después de los umbrales de validez.
- **Variables:**
  - caso 2025: SIF/APAR, con y sin persistencia; NDVI; EVI (y sus variantes de sensibilidad Terra, Aqua y NBAR);
  - pregunta 1 y Q1b: SIF/APAR, NDVI, EVI, SIF y SIF/PAR;
  - nunca a fPAR, PAR, FWI, AED ni SPEI.

**Umbrales de validez en las celdas de calibración** (1462 celdas de matorral y brezal, junio a agosto de 2018–2026, 1 210 536 celdas-día; `data/processed/screening/`):

| Celdas-día de junio a agosto | Fracción |
| --- | --- |
| Con SIF observada | 82,9 % |
| Con todas las entradas (SIF, PAR, fPAR y peso) | 82,8 % |
| Que pasan los tres umbrales | **81,1 %** |

- Los tres umbrales juntos eliminan el **2,0 %** de las celdas-día con todas las entradas: fPAR < 0,15, el 0,68 %; PAR < 40 W m⁻², el 0 %; $W$ < 0,1, el 1,31 %. Casi no se solapan.
- En todas las estaciones eliminan el 5,3 %.
- **Criterio de los umbrales:** el ruido relativo de SIF/APAR en el tramo es mayor que 2× el de la mitad mejor condicionada (`noise_by_bin.csv`).

  | Variable | Último tramo por encima de 2× (cociente) | Primer tramo por debajo de 2× (cociente) |
  | --- | --- | --- |
  | fPAR | 0,10–0,15 (2,39) | 0,15–0,20 (1,96) |
  | PAR | 20–40 (2,83) | 40–60 (1,40) |
  | Peso | 0–0,1 (2,005) | 0,1–0,2 (1,83) |

**TROPOSIF.**
- Versión: L2B, procesador **01.00.01**, colección **03** (S5P-PAL/UPV). Comprobado en los atributos de los 3104 archivos diarios del 1 de mayo de 2018 al 3 de noviembre de 2026; no hay ninguna otra versión.
- Sin días perdidos en 2018–2025.
