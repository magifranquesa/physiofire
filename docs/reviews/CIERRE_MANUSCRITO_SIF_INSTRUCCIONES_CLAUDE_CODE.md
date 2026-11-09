# Revisión científica y plan de cierre del manuscrito SIF–incendios

**Documento de trabajo para Claude Code**  
**Idioma de la revisión:** español. **Idioma del manuscrito:** inglés británico.  
**Documento examinado en esta revisión:** `Does satellite chlorophyll fluorescence anticipate fire-prone fuel conditions Ev (1)(1).docx` (**15 páginas, Figuras 1–5 incrustadas**). Para este cierre, esta versión gráfica sustituye al borrador textual anterior como referencia de revisión; comprobar en el repositorio cuál es la fuente maestra editable.  
**Título actual del manuscrito:** *Does satellite chlorophyll fluorescence anticipate fire-prone fuel conditions? Evidence from the Iberian Peninsula, 2018–2025*.  
**Estado de esta revisión (actualización con figuras):** se han revisado el **texto, las tres tablas y las cinco figuras incrustadas** del DOCX actualizado, incluida la legibilidad de ejes, leyendas y etiquetas de tamaños muestrales. **No se ha inspeccionado el repositorio, ejecutado código ni comprobado datos originales.** Las figuras se han examinado visualmente, no regenerado. Las observaciones que siguen distinguen incoherencias visibles de hipótesis técnicas pendientes de verificación. El documento conserva marcadores `[Insert: figures/manuscript/...]` en los pies pese a que las imágenes ya están embebidas; limpiar estos marcadores en la versión de envío después de cotejar originales y trazabilidad.

## Actualización v2 — hallazgos nuevos al examinar las figuras

**Conservar la valoración científica general del documento v1**, pero considerar los siguientes puntos como nuevas prioridades antes de cerrar el manuscrito:

1. **Figura 4 / §3.2:** la cifra de 2.555 celdas SIF significativas presentada en el texto como matorral equivale a 2.474 celdas *shrubland* + 81 *heathland* representadas por separado en Fig. 4(a). La misma igualdad se da para NDVI y EVI. Comprobar si la categoría del texto es agregada y cómo se definió H1.
2. **Figura 5:** separar 228 episodios detectados, 141/145 eventos de comparación y 4.463/4.340 pares celda–episodio; auditar la fuerte censura visible, especialmente el pico en +120 días.
3. **Figura 3:** las tres series SPEI-90 parecen coincidir exactamente aunque las coordenadas difieren; confirmar si se usa deliberadamente una serie meteorológica regional común o hay un problema en extracción/gráfico.
4. **Figura 2:** los *n* ópticos cambian notablemente según fecha y estrato; verificar composición de muestras y explicar que no hubo **separación sostenida al umbral prerregistrado**, no ausencia de cualquier diferencia puntual.
5. **Figura 1:** revisar la clase de leyenda «Heathland and wetland» frente a la clase «heathland» analizada.
6. **Edición:** las figuras ya están incrustadas; eliminar los marcadores `[Insert: ...]` de sus pies cuando las fuentes se hayan identificado.

**Estos hallazgos no autorizan por sí mismos a cambiar ninguna cifra:** primero comprobar scripts y outputs; después corregir estratos, cifras o etiquetas según corresponda.

---

## 0. Instrucción principal para Claude Code

**Objetivo:** ayudar a cerrar y dejar listo para envío el manuscrito existente, conservando sus tres análisis y evitando convertirlo en un nuevo estudio. Primero auditar los métodos y resultados fundamentales; después, y solo en función de lo comprobado, introducir correcciones de redacción y preparar materiales reproducibles.

**No hacer:**

- No sustituir resultados negativos por una narrativa favorable a SIF.
- No inventar cifras, significaciones, tamaños muestrales, citas, fechas, figuras, repositorios, DOI ni versiones de productos.
- No cambiar silenciosamente umbrales, filtros, ventanas, hipótesis o criterios prerregistrados. Distinguir claramente **análisis originales**, **comprobaciones de sensibilidad posteriores** y **análisis exploratorios**.
- No modificar resultados del manuscrito si no se han regenerado desde el código o comprobado en los outputs de origen.
- No ampliar el objetivo a predicción regional de incendios, carga de combustible o productividad antecedente. Eso se reservará para un artículo distinto.
- No tratar un nulo de discriminación local como demostración de falta general de capacidad predictiva del FWI o de SIF.
- No confundir **escala temporal de acumulación óptima del SPEI**, **desfase de máxima correlación** y **día de detección de un episodio de sequía**: son estimandos diferentes.

**Método de trabajo:** localizar primero el código, los datos derivados, los planes/commits prerregistrados y los outputs de los tres análisis; elaborar un inventario de evidencias. Ejecutar solo comprobaciones concretas que respondan a los puntos críticos. Si falta alguna fuente, registrar el bloqueo y no improvisar su contenido.

---

## 1. Valoración científica general

### Fortalezas

1. El manuscrito plantea una pregunta pertinente: si la sensibilidad fisiológica de SIF/APAR a balances hídricos recientes se convierte en una ventaja práctica para anticipar condiciones vinculadas al peligro de incendios.
2. Articula **tres pruebas distintas y complementarias**: discriminación local previa a incendios, escalas temporales de respuesta al SPEI y momento de respuesta al inicio de sequías.
3. Presenta resultados negativos informativos. No demostrar anticipación no invalida el trabajo si el alcance inferencial y las limitaciones se expresan con precisión.
4. Declara protocolos y criterios fijados en control de versiones antes de ejecutar los análisis; esa fortaleza debe poder verificarse y documentarse.
5. Incluye controles de radiación, ruido y distintos productos; la Figura 4 muestra asociaciones a escalas de SPEI más cortas para SIF/APAR que para NDVI/EVI. **Antes de presentar esa robustez como específica del matorral debe resolverse la inconsistencia aparente entre las etiquetas de estratos y los recuentos de matorral + brezal (véase P0.5).**

### Principal contribución que recomiendo defender

> **Una asociación de SIF/APAR con escalas de déficit hídrico más cortas no implica necesariamente una detección más temprana de episodios de sequía ni una mayor discriminación espacial local de las zonas que acabarán quemándose.**

Este es el mensaje conceptual más sólido e interesante. Evitar presentar el artículo como «la fluorescencia no sirve para el peligro de incendios», porque los análisis no sustentan una conclusión de alcance tan general.

### Juicio editorial

El manuscrito **tiene una línea publicable y coherente**, sujeta a comprobar las cuestiones metodológicas críticas descritas más abajo. Recomiendo **cerrarlo como artículo independiente**, con modificaciones selectivas y sin añadir un cuarto análisis de productividad o combustible. No es una evaluación definitiva de publicabilidad ni una revisión por pares: falta examinar la implementación y las figuras.

---

## 2. Resultados del borrador que deben preservarse y verificarse

Estos números se transcriben del manuscrito recibido; son **declaraciones del borrador**, no números recalculados en esta revisión.

| Análisis | Resultado declarado | Interpretación permitida |
|---|---|---|
| 1. Incendios agosto 2025 | 22 incendios (15 España, 7 Portugal); 133 celdas quemadas; 108 controles; distancia de controles 10–50 km | Evaluación de **discriminación local** antes de ignición; no de predicción regional o temporal |
| 1. Anticipación quemadas–controles | Tiempo de separación = **0 días** para SIF/APAR, NDVI, EVI, FWI y AED conforme al umbral fijado; SIF/APAR última quincena +0,13 DE, no significativo; FWI +0,00 DE | No se ha demostrado separación bajo el criterio adoptado; no equivale a demostrar igualdad fisiológica exacta ni capacidad predictiva nula |
| 1. Anomalía relativa a climatología | FWI se apartó de lo habitual ~12 días antes y AED ~7 días antes en las celdas quemadas, pero también en controles | Señal regional compartida, no específica de los lugares quemados |
| 2. Escalas de sequía | El texto declara 6.771 celdas vegetadas y 4.169 «de matorral», con escalas medianas de **60/180/365 días** (SIF/APAR/NDVI/EVI). **Verificar si la categoría de 4.169 y los resultados citados mezclan shrubland + heathland:** en Fig. 4(a), 2.474 + 81 = 2.555 celdas SIF significativas | Asociación con balance hídrico más reciente; **estrato y denominador pendientes de auditoría P0.5** |
| 2. Comparación por celdas | Escala SIF/APAR más corta en **71 %** frente a NDVI y **80 %** frente a EVI para la fila «Shrubland» (Tabla 3; Fig. 4c) | Resultado central de H1; verificar si Fig. 4(b), Fig. 4(c) y Tabla 3 usan exactamente el mismo estrato, además de denominadores y bootstrap espacial |
| 2. Bosques | Tabla 3: 0,62 vs NDVI y 0,70 vs EVI; tras corrección PAR: 0,52 vs NDVI y 0,64 vs EVI | **No** afirmar igual robustez que en matorral para la comparación forestal frente a NDVI |
| 3. Inicio de sequía | El texto presenta 228 eventos; Fig. 5(a) muestra **141 eventos** con NDVI y **145 eventos** con EVI, mientras Fig. 5(b) muestra **4.463 y 4.340 pares celda–episodio**, respectivamente | No llamar «141/145 pares» a lo que la figura rotula como eventos; documentar filtros, unidades de análisis, censura y agregación |
| 3. Anticipación | Sign score +0,17 [0,06; 0,29] vs NDVI; −0,04 [−0,16; 0,07] vs EVI. Mediana de diferencia SIF/APAR − índice: **+13 días** vs NDVI; **+1 día** vs EVI | No hay ventaja general de SIF/APAR; con NDVI el índice óptico aparece primero en la comparación principal |
| 3. Estacionalidad | En verano SIF/APAR aparece antes que EVI en un análisis **exploratorio** (sign score −0,16 [−0,29; −0,03]) | Hipótesis a investigar, no confirmación ni criterio original de éxito |

Notas: en el análisis 2, el desfase a escala SPEI-90 es otra medida y no debe mezclarse con la mediana de días del análisis 3. El resultado de no separación del análisis 1 depende de una definición concreta de *lead time* (diferencia quemada–control ≥ 0,5 DE, sostenida hasta la víspera de la ignición).

---

## 3. Comprobaciones que considero imprescindibles antes de enviar

### P0.1 — Auditar filtrado temporal y uso de información futura

**Por qué:** el apartado 2.7 indica una **media centrada de 15 días** para correlacionar índices con SPEI. Esto incluye días posteriores a la fecha representada. Es admisible para un estudio retrospectivo de sensibilidad si está declarado, pero no constituye una señal de alerta disponible en tiempo real. El apartado 2.8 exige **15 días consecutivos de anomalía** para definir una respuesta; hay que distinguir el primer día al que retrospectivamente se atribuye la respuesta del día en que se puede confirmar.

**Acciones:**

1. Localizar en el código las ventanas y filtros utilizados **por separado** en los análisis 1, 2 y 3. El análisis 1 declara media retrospectiva de 15 días, mientras que el 2 declara media centrada; **no asumir** que el 3 aplica la misma media sin comprobarlo.
2. Crear una tabla con: indicador, análisis, operación temporal, ventana, si incorpora observaciones futuras, tratamiento de NA, fecha asignada, criterio de persistencia y fecha real de confirmación.
3. Si los resultados originales permiten una interpretación de anticipación **retrospectiva**, etiquetarla como tal. Si el texto utiliza «early warning» en sentido **operativo**, realizar una comprobación de sensibilidad con ventanas causales/retrospectivas, sin sobrescribir el análisis prerregistrado.
4. Para el inicio de sequía, mostrar en un ejemplo reproducible cómo se define el primer día y cómo se trata la confirmación de persistencia (15 días). Una detección que se valida 14 días después no debe describirse como alerta disponible el primer día.

**Salida esperada:** `audit_temporal_windows.md` y, si procede, sensibilidad documentada sobre la interpretación de anticipación.

**Condición de cierre:** no queda en el resumen, discusión ni conclusiones ninguna afirmación de alerta operativa que dependa de datos futuros sin explicitarlo.

### P0.2 — Auditar el análisis de inicio de sequía y la comparación justa entre sensores

**Por qué:** el manuscrito reconoce que el **30 %** de casos tenían NDVI ya anómalo en el día −30, frente al **6 %** para SIF/APAR; que los episodios de sequía están encadenados y que en primavera la cobertura óptica alcanza solo **15–18 %** de episodios frente a **98 %** en SIF/APAR. Estos hechos pueden afectar el orden de respuesta observado.

**Acciones:**

1. Verificar la definición del evento de inicio: SPEI-90 cae al menos 1 unidad en 30 días y pasa por debajo de −1, sin mirar los datos de vegetación; ventana de respuesta de −30 a +90 días; anomalía ≤ −0,5 DE persistente durante 15 días.
2. Documentar los casos con respuesta antes de −30, respuesta ya presente al abrir la ventana, ausencia de respuesta y **censura en +90**. Explicar cómo se computan diferencias emparejadas cuando uno o ambos índices están censurados.
3. Revisar el denominador de los **228 eventos**, los **141 eventos** del contraste NDVI y **145 eventos** del contraste EVI, y sus respectivos **4.463/4.340 pares celda–episodio** representados en Fig. 5; aclarar los filtros y las unidades efectivas de cada resultado.
4. Ejecutar una sensibilidad **posterior y etiquetada** que excluya o estratifique los casos en los que el índice ya estaba anómalo al principio de la ventana. No seleccionar únicamente resultados favorables a SIF.
5. Explorar sensibilidad a faltantes y cobertura por estación; si una comparación equilibrada hace inviable el análisis primaveral, **declararlo** en vez de forzar una conclusión.
6. Auditar el `sign score`, el signo, los empates y el bootstrap. Evaluar la dependencia temporal entre episodios de 2022, 2023 y 2025; los intervalos bootstrap por evento pueden ser demasiado optimistas. Considerar validación descriptiva por año o por bloque espacio-temporal si la muestra lo permite; **no prometer intervalos robustos con solo tres años de eventos**.

**Salida esperada:** `audit_drought_onset.md`, tabla de disponibilidad y censura, figura o tabla de sensibilidad y resumen de si cambian signo, magnitud y alcance de la conclusión.

**Condición de cierre:** la conclusión principal sobre no anticipación se expresa con cautela adecuada respecto a episodios encadenados, cobertura y censura. Si la conclusión cambia al corregir un error de implementación, documentar el error, regenerar resultados y reescribir todas las secciones afectadas.

**Comprobaciones adicionales motivadas por la Figura 5:**

- Verificar que el texto distingue **228 eventos detectados**, **141/145 eventos evaluables** en los dos contrastes y **4.463/4.340 pares celda–episodio** visualizados en los histogramas; documentar cómo se obtienen esos recuentos (primavera/verano: NDVI 32 + 109 eventos y 555 + 3.908 pares; EVI 34 + 111 eventos y 629 + 3.711 pares).
- Inspeccionar la gran masa en el extremo derecho de los histogramas (~+120 días): el pie atribuye el pico a un índice óptico ya anómalo a −30 y SIF/APAR censurado en +90. **La diferencia +120 es un límite impuesto por la ventana, no un tiempo de respuesta observado.** Cuantificar la fracción de pares censurados por estación e índice, y su impacto sobre medianas y *sign scores*.
- Comprobar el cálculo de los intervalos bootstrap: la unidad de remuestreo debe reflejar la dependencia de pares dentro de eventos (y en lo posible año/región); advertir que 4.463 pares no equivalen a 4.463 eventos independientes.
- Comparar las conclusiones con el subconjunto «ambos respondieron», o utilizar un análisis adecuado para censura como **sensibilidad exploratoria**, manteniendo intacto el criterio original. Reportar sensibilidad de las medianas +13/+1 a la codificación de observaciones censuradas.
- En la Fig. 5(b) se indica «median d (median over events)». Verificar que el texto y el método describen esa agregación y no una mediana directa de todos los pares.

### P0.3 — Verificar la inferencia del análisis de escalas de sequía

**Por qué:** la señal favorable a SIF/APAR en escalas temporales es el principal hallazgo positivo. Debe quedar claro **qué significa** y bajo qué comparaciones se sostiene.

**Acciones:**

1. Revisar el método exacto de correlación usado en el código (el borrador utiliza `r` pero no especifica aquí inequívocamente Pearson/Spearman), escalas SPEI de 15/30/60/90/180/365 días y desfases 0–60 días.
2. Comprobar la selección del máximo en la búsqueda múltiple escala × desfase y las **199 permutaciones de años completos** que recomputan ese máximo; verificar cómo se deriva la significación y qué celdas entran en las proporciones comparadas.
3. Confirmar el procedimiento de intervalos bootstrap por bloques espaciales de 1° y sensibilidad a agrupación espacial; verificar empates y celdas no significativas.
4. Reproducir la Tabla 3, especialmente los resultados tras corrección PAR y *noise matching*.
5. Comprobar cómo se corrige la radiación, dado que PAR está en el denominador de SIF/APAR y está muy correlacionada con AED en el registro estudiado (el borrador declara r = 0,86). Revisar que la corrección no utilice información de días de sequía cuando se afirma que se estimó sobre días sin sequía.
6. Distinguir en el texto: **escala SPEI más corta** ≠ **respuesta instantánea más rápida** ≠ **menor número de días para detectar una anomalía**. Evitar extrapolar una correlación más corta a una medida directa de estrés hídrico o humedad del combustible.

**Salida esperada:** `audit_timescales.md`, verificación trazable de Tabla 3 y anotación de las frases que requieren matices.

**Condición de cierre:** el resultado de matorrales se reproduce y se interpreta como asociación a escalas de balance hídrico; la robustez forestal se formula de acuerdo con la Tabla 3.

### P0.4 — Acotar correctamente el experimento de incendios

**Por qué:** los controles se seleccionaron a 10–50 km, con combustible dominante similar, aridez dentro de ±15 % y altitud dentro de ±200 m, para **compartir aproximadamente el contexto meteorológico**. El diseño está concebido para detectar diferencias locales, no la habilidad del FWI o SIF para distinguir regiones o periodos de peligro.

**Acciones:**

1. Reproducir la selección de los 22 incendios, los 133 píxeles quemados y 108 controles; verificar las fechas de ignición (primera detección VIIRS/MODIS/VIIRS burned day/EFFIS), exclusiones y la máscara estrictamente preincendio.
2. Confirmar que las comparaciones se computan de forma consistente a nivel de incendio y no dan falsa precisión por tratar píxeles vecinos como independientes.
3. Reproducir la Tabla 2 y comprobar que el valor de 0 días significa **no alcanzar el criterio prerregistrado de separación sostenida ≥ 0,5 DE**. Evitar interpretar el intervalo `[0,0]` como prueba de igualdad exacta.
4. Revisar si la formulación «no variable separated ... at any point» debe matizarse a «no sustained separation meeting the prespecified criterion»; comprobar las curvas y sus intervalos.
5. Mantener explícita la distinción entre **anomalías en quemadas frente a su propia climatología** y **diferencia quemadas–controles**. El FWI y AED pueden señalar anomalía regional aunque no discriminen el perímetro final.

**Salida esperada:** `audit_fire_matching.md`, reproducibilidad de Tabla 2 y textos corregidos según el alcance real.

**Condición de cierre:** el artículo no concluye que «FWI no anticipa incendios» ni que «SIF carece de utilidad regional» sobre la base de este experimento local.

---

### P0.5 — Resolver la incoherencia aparente entre shrubland, heathland y recuentos (Figura 4)

**Hallazgo visual concreto (muy importante):** en la Figura 4(a) los encabezados presentan tamaños muestrales **n = SIF/APAR / NDVI / EVI** por clase:

| Clase rotulada en Fig. 4(a) | SIF/APAR | NDVI | EVI |
|---|---:|---:|---:|
| Shrubland | 2.474 | 3.361 | 3.176 |
| Heathland | 81 | 114 | 123 |
| **Suma shrubland + heathland** | **2.555** | **3.475** | **3.299** |

Los valores de la **suma** coinciden exactamente con los que el apartado **3.2** atribuye a «shrubland» (2.555, 3.475 y 3.299). Además, la Figura 4(b), titulada *“Shrubland and heathland, by aridity class”*, muestra 1.776 + 311 + 468 = **2.555** celdas significativas para SIF/APAR; 2.415 + 469 + 591 = **3.475** para NDVI; y 2.262 + 441 + 596 = **3.299** para EVI. **Es una coincidencia aritmética comprobada en las figuras, no prueba todavía de un error de código.**

**Acciones obligatorias:**

1. Auditar en los scripts y outputs la reclasificación de combustibles y los nombres exactos de conjuntos empleados en **§3.2, Fig. 4(a), Fig. 4(b), Fig. 4(c), Tabla 3 y H1**. Distinguir «shrubland estrictamente», «heathland» y «shrubland + heathland»; verificar también si las **4.169 celdas** del texto corresponden a la suma de esas dos clases o solo a una.
2. Documentar para cada figura y tabla los recuentos **totales**, **significativos por indicador** y **significativos para ambos indicadores** en las comparaciones pareadas. No sustituir en bloque la etiqueta de matorral sin comprobar qué población sostiene realmente los porcentajes 0,71 y 0,80.
3. Revisar la Fig. 1: su leyenda usa la categoría **“Heathland and wetland”**, mientras el manuscrito trata “heathland” como clase de combustible. Verificar qué incluye, cómo se ha reclasificado y si hay humedales mezclados en los estratos de incendios y de sequía.
4. Corregir texto, pies, encabezados, nombres de clases y, si procede, reproducir tablas y figuras, pero **solo** con evidencia de los outputs originales o ejecución trazable.

**Salida esperada:** `audit_strata_counts.md` con tabla de correspondencias, operaciones de suma, denominadores y correcciones propuestas.

**Condición de cierre:** todas las afirmaciones sobre «matorral» se basan en un estrato explícito y consistente con la Figura 4 y la Tabla 3. Si la distinción cambia el resultado confirmatorio de H1, aplicar la regla de parada y consultar antes de rehacer narrativa.

### P0.6 — Auditoría visual y trazabilidad de Figuras 1–5

**No reconstruir los gráficos a ojo.** Para cada figura, localizar código, archivo fuente y datos derivados; comprobar que los 5 gráficos incrustados corresponden a los outputs en el repositorio y que se exportaron con las versiones correctas. Revisar visualmente al menos estos puntos:

| Figura | Observación que aporta la figura | Verificación o cambio solicitado |
|---|---|---|
| **1. Distribución de incendios y controles** | Se representan 22 incendios, clases FirEUrisk y celdas quemadas/controles en el noroeste | Verificar clase **“Heathland and wetland”** frente a “heathland”; confirmar número de puntos/celdas, leyenda, resolución y criterios espaciales. No deducir balances de muestra contando símbolos superpuestos. |
| **2. Composites preincendio** | Las curvas de diferencia quemada–control oscilan cerca de cero; FWI/AED y otros indicadores muestran anomalías compartidas; **n varía de 8–22 incendios para NDVI y 9–22 para EVI**, y menos en heathland | Validar composición con muestras que varían por fecha, intervalo de confianza por incendio, umbral ±0,5 DE y que una excursión puntual no se confunda con separación **sostenida**. Inspeccionar si huecos ópticos introducen diferencias de composición de incendios por día. |
| **3. Series A Rúa** | Se ven anomalías de EVI positivas a comienzos de verano en quemada y controles; la celda quemada está enmascarada después de ignición; **las tres curvas SPEI-90 parecen exactamente iguales** pese a coordenadas diferentes | Verificar si SPEI-90 se ha representado intencionadamente como **serie meteorológica común al incendio**, si hay una agregación regional justificada o si existe reutilización accidental de una misma serie / error de extracción. Si es un producto común, etiquetarlo explícitamente en gráfico y pie; si debía ser específico de celda, depurarlo. No afirmar error de datos sin comprobación. |
| **4. Escalas SPEI** | SIF/APAR domina visualmente escalas más cortas; índices ópticos se concentran en 365 días; tamaños por estrato y aridez permiten verificar sumas | Ejecutar **P0.5**. Comprobar que panel (b) rotulado “shrubland and heathland” no se presenta como solo “shrubland”; que los `n` se definen; que panel (c) y Tabla 3 comparten estratos y criterios de significación. |
| **5. Inicio de sequía** | Hay abundancia de pares censurados en extremos y diferencias acusadas de observaciones primavera/verano; muestra conteos por **evento** y por **par celda–episodio** | Ejecutar el bloque específico de **P0.2**: interpretación del extremo ~+120 días, reglas de censura y agregación de medianas; mostrar fracciones censuradas. El resultado estival frente a EVI continúa siendo **exploratorio**. |

Comprobar además el esquema de colores y las bandas de incertidumbre, rotulación de eje temporal, símbolos, *n* variables, texto de subtítulos y pies. Los cinco pies aún contienen la coletilla `[Insert: figures/manuscript/...]` aunque las figuras ya están embebidas: retirar solo cuando se confirme su fuente. Las figuras principales deben mantenerse salvo que se detecte un error o una mejora necesaria de legibilidad o interpretación.

**Salida esperada:** `audit_figures.md`, con matriz **figura → script → datos → output → versión → afirmaciones del manuscrito**, incidencias clasificadas como `confirmed mismatch`, `needs source check` o `editorial only` y capturas/archivos originales cuando existan.

**Condición de cierre:** ninguna figura contradice cifras o estratos declarados y todas las aparentes anomalías quedan explicadas o corregidas trazablemente.

---

## 4. Mejoras importantes, pero no necesariamente bloqueantes (P1)

### P1.1 — Referencias temporales y climatología

El borrador calcula anomalías por celda con medianas por día del año (±15 días) para **2018–2025**, mientras que el SPEI utiliza referencia **1991–2020**. Explicar que las anomalías del índice vegetal y el SPEI no comparten periodo de referencia y describir el posible efecto en comparaciones. Si es sencillo, explorar una sensibilidad *leave-one-year-out* de la climatología de índices vegetales; etiquetarla como adicional y no reemplazar automáticamente los resultados originales.

### P1.2 — Coherencia de cobertura de datos de la Tabla 1

El texto declara estudio **2018–2025**, pero la columna titulada **“Period used”** de la Tabla 1 contiene varios periodos que llegan a **2026** (por ejemplo TROPOSIF «May 2018–Nov 2026», PAR 2018–2026, etc.). Esto resulta ambiguo.

**Comprobar con logs y outputs** si esos intervalos indican disponibilidad o extracción total y cuáles son realmente los periodos utilizados en cada análisis. Corregir el encabezado, separar “dataset availability/extracted” y “analytical period” o ajustar los valores, según corresponda. No imponer 2025 a todos los datos: AED y SPEI necesitan periodos de calibración anteriores, y FWI necesita una fase previa de inicialización.

Revisar también los metadatos reales y la versión concreta de TROPOSIF, pendiente en el manuscrito.

### P1.3 — Terminología y mecanismos fisiológicos

- SIF/APAR es un **proxy** de rendimiento de fluorescencia, no medición directa del contenido de humedad del combustible vivo (LFMC), del cierre estomático ni del agua disponible.
- Verificar unidades, normalización temporal y consistencia del cálculo SIF/(PAR × fPAR), incluyendo tratamiento de baja fPAR, PAR y peso por observación TROPOMI. No afirmar que la razón es adimensional si las unidades del producto no lo permiten.
- La variación de iluminación, extinción y disipación no fotoquímica puede influir en la SIF. La sección de «light saturation» debe conservarse, evitando atribuir cada descenso de verano exclusivamente a sequía.
- Comparar con Tang et al. (2026) con prudencia: sus «días de respuesta» y la «escala SPEI óptima» o el criterio de persistencia de este trabajo **no son métricas directamente equivalentes**.

### P1.4 — Moderar la interpretación de la primavera/verano de 2025

La sección **4.4, “The 2025 season: abundant fuel and extreme weather”**, infiere combustible abundante a partir de anomalías positivas de verdor y primavera húmeda. El manuscrito **no presenta una estimación directa de carga, continuidad o combustibilidad del combustible**. Recomiendo cambiar título y texto a una interpretación más cautelosa:

- Confirmado según las series exploratorias descritas: primavera húmeda, anomalías positivas de EVI a comienzos de verano y condiciones extremas en agosto.
- Hipótesis compatible pero no probada: mayor crecimiento vegetal antecedente pudo contribuir a la disponibilidad o continuidad del combustible.
- No afirmar causalmente que estos incendios «burned abundant fuel rather than previously stressed vegetation» sin datos de biomasa/humedad específicos.
- Mantener este punto **breve** como explicación plausible y trabajo futuro, sin incluir nuevas figuras de productividad ni análisis de carga de combustible.

### P1.5 — Novedad y alcance de las conclusiones

Reformular «fluorescence does not add early warning of fire-prone conditions in the Iberian Peninsula» por una frase ligada a **estas condiciones de observación, años, ecosistemas, métricas y diseño**. El texto sí permite concluir que **no se encontró una ventaja sistemática en la detección de estos inicios de sequía** ni **discriminación local sostenida antes de los grandes incendios de agosto de 2025**. No permite excluir cualquier beneficio en escalas regionales, otros ecosistemas, otros sensores o estrategias multivariables.

### P1.6 — Ajustar frases concretas del borrador

| Ubicación | Problema | Propuesta |
|---|---|---|
| §3.2 | “Across aridity classes, In shrubland” y recuentos que aparentemente suman shrubland + heathland | Eliminar duplicación **después** de resolver P0.5; corregir clasificación y tamaños muestrales según outputs |
| §3.2 / §4.2 / conclusiones | A veces se presenta «shrubland and forest» como resultado igualmente robusto | Precisar que la robustez más fuerte es para matorral; en bosque, frente a NDVI, la proporción cae bajo el umbral 0,60 tras correcciones |
| §3.3 y Fig. 5 | 228 eventos, 141/145 **eventos** de comparación y 4.463/4.340 **pares celda–episodio** | Definir la unidad de cada estadístico, filtros, dependencia y censura; evitar llamarlos todos «pares» |
| §4.1 | “Where fires burn is not decided by vegetation state at regional scale” | El análisis prueba diferencias locales **dentro** de un contexto regional compartido; evitar usar «at regional scale» para una conclusión que en realidad es local |
| Fig. 3 / §4.4 | Las tres curvas de SPEI-90 parecen idénticas y se afirma “abundant fuel” | Verificar fuente de SPEI por celda o referencia común; sustituir combustible supuesto por «high pre-fire greenness / potential fuel accumulation» |
| §4.6 | «FLEX mission, launched in 2026» | Verificar **estado real de lanzamiento, fecha, resolución y capacidades** con fuentes de ESA antes de fijarlo; el borrador no acredita por sí solo esos datos |
| Abstract / conclusiones | «no early warning» sin calificador | Especificar TROPOMI, metodología retrospectiva, discriminación local y muestra 2025 |

---

## 5. Recomendación de narrativa y estructura del manuscrito

No cambiar el orden de los tres análisis. La mejor narrativa es una **secuencia de hipótesis cada vez más exigentes**:

1. **Sensibilidad:** SIF/APAR se asocia a escalas de SPEI más cortas que NDVI/EVI. Esto aporta información fisiológica diferente.
2. **Anticipación:** la escala óptima más corta no se convierte, en el registro evaluado, en una ventaja consistente en detección de inicio de sequía.
3. **Aplicación a incendios:** tampoco se obtiene discriminación espacial local de los perímetros finales bajo meteorología extrema.

El orden de presentación de resultados puede mantenerse como ahora (incendios, escalas, inicios); la síntesis del abstract/discusión debe hacer explícita esta cadena sin fingir que se han demostrado vínculos causales entre los tres resultados.

### Discusión sugerida

- **4.1. What the local fire comparison can and cannot establish.** Distinguir anomalía climática regional y diferencias en el perímetro final.
- **4.2. Shorter drought timescales do not imply earlier detectable responses.** Convertirlo en la contribución conceptual principal.
- **4.3. Seasonality, illumination and detectability.** Radiación/NPQ, ruido, diferencia de cobertura, episodios encadenados; separar evidencia confirmatoria de verano exploratorio.
- **4.4. The 2025 context and fuel-related hypotheses.** Resumen prudente de EVI/SPEI y potencial acumulación de biomasa no comprobada.
- **4.5. Limitations.** Separar limitaciones de observación, del diseño local, de período y de inferencia.
- **4.6. Implications.** Necesidad de integrar escalas de sequía/estado vegetal y de evaluar sensores de mayor resolución como hipótesis futura; no prometer que FLEX resolverá por sí mismo el problema.

### Título

El título actual es legítimo, pero “fire-prone fuel conditions” puede sugerir una medida directa del estado físico del combustible. Alternativa editorial (opcional, **no cambiar sin elección de los autores**):

> *Does satellite chlorophyll fluorescence provide earlier warning of drought-related wildfire conditions? Evidence from the Iberian Peninsula*

Si se conserva el título original, aclarar en el resumen y en la introducción que la variable principal es SIF/APAR y que no se mide directamente LFMC o carga de combustible.

---

## 6. Borradores orientativos en inglés británico (NO sustituir automáticamente)

Los siguientes textos solo son válidos **si las comprobaciones mantienen los resultados declarados**. Son propuestas de enfoque, no resultados recalculados ni instrucciones para ocultar limitaciones.

### 6.1. Abstract propuesto

> Solar-induced chlorophyll fluorescence normalised by absorbed photosynthetically active radiation (SIF/APAR) is associated with plant physiological responses to water limitation, but it remains unclear whether this sensitivity provides earlier warning of drought-related wildfire conditions. We evaluated daily TROPOMI SIF/APAR alongside MODIS NDVI and EVI, fire weather, atmospheric evaporative demand and multi-scale SPEI across the Iberian Peninsula during 2018–2025. Three analyses tested local pre-fire discrimination, the drought accumulation timescales associated with vegetation indices, and response timing at drought onset. For 22 large shrubland and heathland fires in August 2025, none of the indicators achieved the prespecified sustained separation between burned cells and comparable unburned controls located 10–50 km away. Across 6,771 vegetated cells, SIF/APAR was associated with shorter SPEI accumulation timescales than greenness indices, particularly in shrubland (median 60 days, compared with 180 days for NDVI and 365 days for EVI). However, across 228 identified drought-onset events, SIF/APAR did not consistently respond earlier than either optical index. An exploratory summer comparison suggested an earlier response than EVI, but this requires further testing and careful treatment of illumination effects. Thus, sensitivity to shorter water-balance timescales did not translate into earlier detectable drought responses or local pre-fire discrimination in the analyses considered. These findings clarify the limits of interpreting satellite fluorescence as an operational early-warning indicator at TROPOMI resolution.

**Comprobar tras la auditoría:** si el análisis de inicio usa información futura, el último sintagma “operational early-warning” debe limitarse a la interpretación metodológica de lo que **no está demostrado**, evitando atribuir una validación operativa no realizada. Mantener estilo y longitud de la revista elegida.

### 6.2. Conclusiones propuestas

> 1. In the 22 large August 2025 fires examined, SIF/APAR, NDVI, EVI and meteorological indicators did not achieve the prespecified sustained discrimination between burned cells and nearby matched controls. This finding concerns local spatial discrimination under broadly shared weather conditions, not regional fire-danger prediction.
> 2. SIF/APAR was associated with shorter drought accumulation timescales than NDVI and EVI, particularly in shrubland. This indicates that fluorescence normalised by absorbed radiation contains information related to more recent water-balance variability, but does not by itself demonstrate earlier event detection.
> 3. At the identified drought onsets, SIF/APAR showed no consistent lead over the optical indices. Chained drought episodes, uneven observation coverage and illumination-related effects limit interpretation of seasonal differences; the apparent summer advantage over EVI remains exploratory.
> 4. At the resolution and noise levels of TROPOMI, the analyses did not establish an early-warning advantage for SIF/APAR. Further work should explicitly assess operational detection latency and evaluate whether fluorescence adds information at other spatial scales or alongside independent fuel and drought indicators.

### 6.3. Sustitución prudente para §4.4

> The exploratory 2025 time series indicate a wet spring and unusually high greenness in early summer, followed by extreme fire-weather conditions in August. This sequence is consistent with the possibility that antecedent vegetation growth affected fuel availability, but neither fuel load nor continuity was quantified here. Consequently, the data do not establish whether antecedent productivity contributed to the extent of the fires. Testing such fuel-mediated pathways would require a separate analysis combining productivity, fuel structure and subsequent drying.

---

## 7. Preparación para envío: consistencia editorial y reproducibilidad (P1–P2)

### Manuscrito, figuras y tablas

- El DOCX actualizado contiene **tres tablas y las cinco figuras incrustadas** (Figuras 1–5), aunque los pies aún incluyen `[Insert: ...]`. Identificar archivos originales y scripts de creación; verificar que reproducen los gráficos incluidos, que las figuras no son versiones antiguas y que los pies coinciden con ejes, estratos, muestras, umbrales y unidades. **Auditoría visual detallada: P0.6.**
- Verificar consistencia de cifras entre abstract, texto, Tabla 2, Tabla 3, Figuras 2/4/5 y suplementos. En particular, 22/15/7 incendios; 133/108 celdas; 6.771/4.169 celdas; **2.474 + 81 = 2.555** y sumas equivalentes para NDVI/EVI; **228 eventos**, **141/145 eventos evaluables**, **4.463/4.340 pares celda–episodio**; 71/80 %; 60/180/365 días; sign scores; intervalos y el umbral 0,60.
- No insertar gráficos o figuras regeneradas con otra versión de datos sin actualización simultánea de texto, tablas y suplemento.
- Comprobar nomenclatura homogénea: shrubland/heathland/forest; SIF, SIF/PAR y SIF/APAR; AED/ET0; r/ρ; SPEI-90; FFMC/FWI; `lead time` versus `lag`.
- Revisar unidades, redondeo, signos, número efectivo de muestras y tratamiento de fechas en todas las figuras.

### Bibliografía

Hay citas marcadas `[ref]`, referencias incompletas y `[TODO]`. Resolverlas con fuentes primarias antes del envío. Comprobar DOI, autores, título, año, volumen, páginas, contexto y correspondencia de la afirmación citada. En particular: estudios de 2026, Tang et al., fuentes de SIF, FWI, ESFire30 y afirmaciones sobre FLEX. **No completar una referencia por conjetura.**

### Trazabilidad y preregistro

- Localizar hash/fecha de los commits de los tres planes previos; comprobar que anteceden a los análisis relevantes; incorporar ubicación o identificador verificable en métodos o suplemento.
- Documentar cada corrección posterior como error de código, aclaración o sensibilidad exploratoria. No presentar nuevas pruebas como prerregistradas.
- Completar la sección de disponibilidad de datos y código con URL, licencia y DOI de archivo **solo si existen o han sido efectivamente creados**.
- Completar autoría, agradecimientos y revista objetivo con indicaciones reales del equipo; no inventar personas o contribuciones.
- Comprobar que los resultados finales se ejecutan a partir de comandos documentados, con entorno y dependencias reproducibles.

---

## 8. Secuencia operativa propuesta para Claude Code

### Paso A — Inventario y auditoría sin cambios

1. Identificar estructura del repositorio y su estado (`git status`, rama, último commit) sin modificar ni descartar cambios ajenos.
2. Encontrar fuente editable del manuscrito, scripts de los análisis 1–3, outputs tabulares, figuras, pruebas y documentos de prerregistro.
3. Producir `reports/manuscript_closeout/inventory.md` con rutas reales, fechas/hash disponibles, dependencia entre scripts y resultados; usar otra ruta si el repositorio ya tiene convención distinta.
4. Marcar cuáles de las cifras de la sección 2 están confirmadas por outputs existentes y cuáles aún no.

### Paso B — Seis auditorías P0

Ejecutar P0.1–P0.6, priorizando de inmediato **P0.5 (estratos)** y **P0.2 (censura)** si existe riesgo de inconsistencia sustantiva, con cambios mínimos. Mantener intactos los outputs originales; guardar sensibilidades en directorio separado y con nombres inequívocos. Si hay errores, describir causa, impacto en tablas/figuras y criterio original afectado.

### Paso C — Informe de decisión

Crear `reports/manuscript_closeout/decision_memo.md` con esta estructura:

- **Conclusions retained / modified / unresolved**.
- Tabla de resultados originales frente a nuevas comprobaciones (si existen), con tamaños muestrales e incertidumbre.
- Lista de cambios imprescindibles en el manuscrito y justificación.
- Limitaciones que solo pueden declararse, no resolverse con datos actuales.
- Recomendación: **ready to revise**, **needs reanalysis**, o **blocked by missing inputs** (no afirmar `ready for submission` sin cumplir los criterios finales).

### Paso D — Revisión editorial trazable

Solo tras el informe de decisión, generar una versión editada del manuscrito o un parche, según el formato fuente disponible. Mantener un registro `CHANGELOG_MANUSCRIPT.md` que diga **sección / frase anterior / cambio / razón / resultado o fuente que lo respalda**. Conservar original sin sobreescribir a menos que el usuario lo haya autorizado explícitamente.

### Paso E — Entrega final

Entregar como mínimo:

1. `inventory.md`: qué existe, dónde y qué se ha ejecutado.
2. Seis auditorías (`audit_temporal_windows.md`, `audit_drought_onset.md`, `audit_timescales.md`, `audit_fire_matching.md`, `audit_strata_counts.md`, `audit_figures.md`) o explicación precisa de bloqueos.
3. `decision_memo.md` y tabla comparativa de cifras.
4. Manuscrito revisado **en formato disponible**, con cambios visibles o registro de cambios.
5. Figuras/tablas verificadas y lista de citas/TODO aún pendientes, si las hay.
6. Comandos exactos para reproducir cada comprobación.

**Importante:** los nombres de ruta anteriores son convenciones sugeridas; no presumir que existen de antemano.

---

## 9. Criterios de aceptación y reglas de parada

El artículo podrá considerarse metodológicamente listo para edición final cuando:

- [ ] Se haya reconstruido la cronología de datos, medias y ventanas, y no haya ambigüedad sobre uso de información futura.
- [ ] Se reproduzcan o reconcilien las Tablas 2 y 3, la **Figura 4 (estratos)**, la **Figura 5 (censura)** y los resultados del análisis 3.
- [ ] Queden documentados los casos de inicio de sequía previamente anómalos, cobertura desigual y censura, distinguiendo **eventos** de **pares celda–episodio** y el extremo artificial de +120 días.
- [ ] Se distinga explícitamente discriminación local de predicción regional; el resultado de 0 días se interprete según el criterio original.
- [ ] Las conclusiones diferencien **escalas SPEI**, **lag estadístico** y **detección de inicio**; las poblaciones *shrubland* y *heathland* estén explícita y consistentemente delimitadas.
- [ ] Las cinco figuras incrustadas correspondan a la misma versión de resultados que el texto y tengan archivos fuente trazables; quede explicada la aparente **identidad de SPEI-90 entre celdas en Figura 3**.
- [ ] La Tabla 1 distinga correctamente periodos de disponibilidad, procesamiento, calibración y análisis.
- [ ] La discusión de 2025 no afirme carga de combustible medida o demostración causal sin evidencias.
- [ ] Se resuelvan referencias, versiones de datos, TODO y afirmaciones externas verificables.
- [ ] Se documente la trazabilidad de planes originales, sensibilidades y correcciones.

**Regla de parada por cambios sustantivos:** si una auditoría detecta que los recuentos de Fig. 4 alteran la población de H1, invalida el resultado principal del análisis 2 o cambia la conclusión sobre inicio de sequía del análisis 3, **detener la edición narrativa**, informar los hallazgos y reconstruir primero métodos/resultados completos. Nunca ajustar el texto para encajar con la conclusión prevista.

**Regla de alcance:** si para responder una sugerencia hiciera falta montar un estudio nuevo sobre productividad, biomasa, continuidad del combustible o predicción regional, anotarlo como propuesta futura. **No implementarlo dentro de este cierre**.

---

## 10. Primer mensaje operativo sugerido para ejecutar en Claude Code

> Lee `CIERRE_MANUSCRITO_SIF_INSTRUCCIONES_CLAUDE_CODE_v2.md` y la **versión de 15 páginas del manuscrito con Figuras 1–5 incrustadas**. Examina el repositorio y localiza los tres análisis, sus planes de ejecución, resultados, figuras y tablas. **Antes de editar el texto**, verifica la aparente suma de *shrubland + heathland* en Fig. 4 y §3.2, los 141/145 eventos frente a los 4.463/4.340 pares y la censura de Fig. 5, y la aparente identidad de SPEI-90 en las tres celdas de Fig. 3. Empieza por el inventario y las seis auditorías P0, sin modificar el manuscrito ni sobrescribir resultados originales. Identifica qué afirmaciones están reproducidas, cuáles requieren matiz y cuáles no pueden verificarse con el material disponible. Produce un informe de decisión trazable y, solo después, propone un parche editorial en inglés británico. No inventes resultados, citas ni rutas; distingue prerregistro de sensibilidades nuevas. El objetivo es cerrar el artículo de SIF, no abrir el estudio de productividad y combustible.

---

### Nota de procedencia

Esta evaluación parte del **DOCX actualizado con cinco figuras incrustadas**. Los números del texto son los **reportados en el borrador** y los recuentos de Figuras 4/5 son **lecturas visuales de las etiquetas de dichas figuras**, no comprobaciones de código. Las sumas aritméticas de recuentos visibles en Figura 4 están verificadas; la identidad aparente de SPEI-90 en Figura 3 y las consecuencias de la censura en Figura 5 son **alertas para investigar**, no errores de implementación demostrados. Las propuestas metodológicas y editoriales deben contrastarse con el repositorio antes de adoptarse.
