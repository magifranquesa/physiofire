# Resultados de la pregunta 1 (respuesta de SIF/APAR y NDVI/EVI a la sequía)

- **Plan prerregistrado:** `docs/plan_q1_drought.md`; configuración en `config.yaml`, sección `drought_q1`.
- **Resultados:** `docs/results_q1_drought.md`.
- **Código:** `src/physiofire/drought_q1.py` y `drought_q1_report.py`; selección de celdas en `R/q1_cells.R`.

## Archivos versionados

| Archivo | Contenido |
| --- | --- |
| `hypotheses.csv` | H1, H2 y H3 por estrato y referencia |
| `decision.json` | Decisión según el criterio prerregistrado |
| `analysis2_episodes.csv` | Episodios de sequía y días de respuesta |
| `summary_*.csv` | Tablas resumen |
| `posthoc_*.csv` | Diagnósticos posteriores, marcados como tales |

El resto (series diarias y tablas por celda) se puede regenerar y queda fuera de git.

## Celdas y clases de aridez

6771 celdas de 0,05° con al menos un 50 % de tierra, clase dominante de FirEUrisk natural (bosque cerrado o abierto, matorral, brezal o pastizal) y sin quemar desde 2013 (`drought_q1_cells.csv`).

Clases de aridez del Global-AI v3.1 (P/ET₀, media de los píxeles de 30″ de la celda), en intervalos [inferior, superior):

| Clase | Intervalo | Celdas |
| --- | --- | --- |
| `semiarid` | AI < 0,5 | 4000 |
| `dry_subhumid` | 0,5 ≤ AI < 0,65 | 1002 |
| `humid` | AI ≥ 0,65 | 1769 |

**La primera clase (`semiarid`, AI < 0,5) incluye 53 celdas áridas (AI < 0,2): 39 de matorral y 14 de pastizal.** El valor mínimo del índice es 0,150 (pastizal); el de matorral, 0,165. Ninguna celda de bosque ni de brezal baja de 0,2. Por eso las figuras del manuscrito llaman a esta clase "Arid to semi-arid" (Fig. 4b y S4b; nota del 11 de noviembre de 2026). Ni las clases ni los resultados cambian.
