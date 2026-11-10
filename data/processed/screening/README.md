# Calibración de los umbrales de validez de SIF/APAR

Salidas de `python -m physiofire.screening_thresholds`. Los umbrales aprobados están en `config/config.yaml`, sección `sif_apar.screening`.

## `shrubland/`: la calibración que fija los umbrales aprobados

```
python -m physiofire.screening_thresholds --classes shrubland wet_heath --tag shrubland --noise-factor 2
```

- **Muestra:** 1462 celdas de matorral y brezal (FirEUrisk), sin quemar en 2013–2025 y a más de 10 km de cualquier perímetro de EFFIS de 2018–2026. Ninguna es celda quemada ni control del caso 2025.
- **Ruido relativo de SIF/APAR:** residuo absoluto respecto a la mediana móvil de ±3 días de la celda, dividido por la mediana de SIF/APAR de la celda.
- **Criterio aplicado: ruido > 2× el de referencia.**
  - El ruido de referencia es la mediana del ruido en la mitad mejor condicionada de los datos, la que está por encima de la mediana de cada variable.
  - El umbral de cada variable es el límite inferior del primer tramo a partir del cual el ruido mediano de todos los tramos siguientes es ≤ 2 veces el de referencia (columna `ratio_to_ref` de `noise_by_bin.csv`).
- **Resultado** (`proposed_thresholds.csv`, igual a la configuración aprobada):

  | Variable | Umbral | Celdas-día de junio a agosto eliminadas |
  | --- | --- | --- |
  | fPAR | 0,15 | 0,69 % |
  | PAR | 40 W m⁻² | 0,005 % |
  | Peso de TROPOSIF (píxeles equivalentes) | 0,1 | 1,29 % |

  Los tres juntos eliminan el 2,0 % de las celdas-día de junio a agosto con todas las entradas. Pasa los tres umbrales el 81,1 % de todas las celdas-día de junio a agosto (`docs/methods_equations.md`).
- **Historia:** los umbrales se aprobaron el 8 de noviembre de 2026, antes de extraer ninguna serie de incendios o controles. La primera versión de `proposed_thresholds.csv` se escribió con el factor por defecto del script (1,5) y proponía 0,3, 40 y 0,3, que no se usaron.
- **Regeneración (10 de noviembre de 2026):** se repitió con `--noise-factor 2` para que el archivo refleje el criterio aplicado. `sample_cells.csv`, `noise_by_bin.csv` y `candidates.csv` salieron idénticos byte a byte. No cambia ningún umbral ni resultado.

## Archivos de la raíz de esta carpeta (fuera de git)

Primera pasada exploratoria sobre todas las clases con vegetación, con el factor 1,5. No se usó para fijar umbrales.
