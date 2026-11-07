# Lista corta de grandes incendios de 2025 (perímetros de EFFIS > 2.000 ha)

Generada el 07/11/2026 con `Rscript R/fire_shortlist.R` a partir de `data/interim/fires/fire_candidates_2025.csv`. Solo información estática: no se ha extraído ninguna serie de vegetación ni de meteorología.

**Columnas**

- **Fechas** (día/mes, UTC): primera fecha de cada fuente dentro del perímetro, entre FIREDATE − 30 días y FINALDATE + 1 día. VIIRS: detecciones `type = 0` sin confianza baja.
- **Ignición**: la más temprana de las cuatro fuentes; entre paréntesis, la fuente o fuentes que la fijan.
- **Vegetación (mapa de combustibles de FirEUrisk, 1 km, hacia 2019; agregado a 0,05°)**: porcentaje de cada clase, medio ponderado por la superficie del perímetro en cada celda de 0,05°. B. cerr. = bosque cerrado (cubierta de copas ≥ 70 %; tipos 1122, 1212, 1302), B. ab. = bosque abierto (15–70 %; 1121, 1211, 1301), Mator. = matorral (21–23), Brezal = brezal y zonas húmedas (51–53), Pastiz. = pastizal (31–33), Cult. = cultivos herbáceos y leñosos (41, 42), Sin comb. = urbano, agua, suelo desnudo y vegetación escasa (61, 62, 7). "Dominante" es la clase con más superficie en las celdas quemadas (≥ 25 % dentro del perímetro, ponderadas por su fracción quemada), la que se usa para emparejar los controles y estratificar; † = distinta de la dominante en todo el perímetro (la de los porcentajes). Estrato: arbolado = bosque cerrado o abierto, matorral = matorral o brezal, pasto = pastizal. **CORINE**: grupo dominante de CORINE 2018 (apoyo; porcentajes de todos los grupos en el CSV).
- **Celdas / Controles**: celdas de 0,05° con al menos un 25 % dentro del perímetro, y celdas de control válidas (se usan como máximo 5; hacen falta 3) con los criterios de `config.yaml` (`epoch.controls`): sin quemar desde 2017 (EFFIS, MCD64A1, VNP64A1 y ESFire30), misma clase dominante de FirEUrisk que las celdas quemadas, aridez ±15 % (relativa), altitud ±200 m y a 10–50 km del perímetro. Solo información estática.
- **Coherencia**: actividad VIIRS o MCD64A1/VNP64A1 dentro del perímetro entre 90 y 30 días antes de FIREDATE; entre paréntesis, detecciones previas y su fracción del total.
- **Revisar**: ignición más de 3 días antes de FIREDATE sin marca de coherencia (posible fusión de perímetros).

| # | ID EFFIS | Municipio (provincia) | País | ha | EFFIS | VIIRS | MCD64A1 | VNP64A1 | Ignición (fuente) | B. cerr. % | B. ab. % | Mator. % | Brezal % | Pastiz. % | Cult. % | Sin comb. % | Dominante (estrato) | CORINE | Celdas | Controles | Coherencia | Revisar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 277926 | Trancoso (São Pedro e Santa Maria) e Souto Maior (Beiras e Serra da Estrela) | PT | 62.104 | 10/08 | 10/08 | 09/08 | 09/08 | **09/08** (mcd64a1, vnp64a1) | 0 | 0 | 59 | 18 | 6 | 16 | 1 | matorral (matorral) | agrícola | 33 | 5 | **sí** (3 VIIRS, 0,1 %) | no |
| 2 | 277940 | Uña de Quintana (Zamora) | ES | 40.081 | 10/08 | 10/08 | 09/08 | 08/08 | **08/08** (vnp64a1) | 1 | 1 | 54 | 0 | 10 | 33 | 0 | matorral (matorral) | agrícola | 22 | 5 | no | no |
| 3 | 277927 | Sobral de São Miguel (Beiras e Serra da Estrela) | PT | 37.619 | 10/08 | 10/08 | 10/08 | 11/08 | **10/08** (effis, viirs, mcd64a1) | 30 | 3 | 23 | 22 | 16 | 4 | 2 | bosque cerrado (arbolado) | transición bosque-matorral | 21 | 1 | no | no |
| 4 | 278475 | Rúa, A (Ourense) | ES | 37.179 | 14/08 | 14/08 | 13/08 | 13/08 | **13/08** (mcd64a1, vnp64a1) | 16 | 2 | 18 | 56 | 5 | 1 | 2 | brezal y zonas húmedas (matorral) | landas y brezales | 20 | 5 | no | no |
| 5 | 278350 | Piódão (Região de Coimbra) | PT | 30.455 | 11/08 | 13/08 | 11/08 | 12/08 | **11/08** (effis, mcd64a1) | 11 | 1 | 21 | 24 | 43 | 0 | 1 | pastizal (pasto) | transición bosque-matorral | 18 | 0 | no | no |
| 6 | 277944 | Benuza (León) | ES | 26.241 | 09/08 | 09/08 | 09/08 | 08/08 | **08/08** (vnp64a1) | 13 | 1 | 19 | 55 | 12 | 0 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 14 | 5 | no | no |
| 7 | 278477 | Veiga, A (Ourense) | ES | 25.953 | 15/08 | 15/08 | 14/08 | 13/08 | **13/08** (vnp64a1) | 8 | 0 | 18 | 8 | 66 | 0 | 0 | pastizal (pasto) | pastizal natural | 14 | 0 | **sí** (8 VIIRS, 0,1 %) | no |
| 8 | 278504 | Manzaneda (Ourense) | ES | 24.583 | 08/08 | 08/08 | 09/08 | 08/08 | **08/08** (effis, viirs, vnp64a1) | 10 | 0 | 8 | 69 | 10 | 1 | 1 | brezal y zonas húmedas (matorral) | landas y brezales | 15 | 2 | **sí** (3 VIIRS, 0,1 %) | no |
| 9 | 278348 | Oímbra (Ourense) | ES | 24.471 | 13/08 | 24/07 | 11/08 | 11/08 | **24/07** (viirs) | 13 | 1 | 38 | 34 | 7 | 6 | 1 | matorral (matorral) | landas y brezales | 14 | 4 | no | **sí** |
| 10 | 278492 | Quintas de São Bartolomeu (Beiras e Serra da Estrela) | PT | 23.594 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 0 | 0 | 59 | 30 | 7 | 4 | 0 | matorral (matorral) | transición bosque-matorral | 14 | 5 | no | no |
| 11 | 278481 | Burón (León) | ES | 19.112 | 14/08 | 14/08 | 12/08 | 12/08 | **12/08** (mcd64a1, vnp64a1) | 9 | 2 | 2 | 56 | 30 | 0 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 11 | 5 | no | no |
| 12 | 279768 | Navaconcejo (Cáceres) | ES | 17.317 | 13/08 | 13/08 | 11/08 | 11/08 | **11/08** (mcd64a1, vnp64a1) | 7 | 6 | 39 | 7 | 20 | 21 | 1 | matorral (matorral) | matorral esclerófilo | 10 | 5 | no | no |
| 13 | 278349 | Ferreira de Aves (Viseu Dão Lafões) | PT | 13.903 | 10/08 | 13/08 | 10/08 | 12/08 | **10/08** (effis, mcd64a1) | 3 | 1 | 79 | 7 | 6 | 3 | 1 | matorral (matorral) | transición bosque-matorral | 9 | 1 | no | no |
| 14 | 278347 | Mezquita, A (Ourense) | ES | 12.026 | 12/08 | 12/08 | 11/08 | 11/08 | **11/08** (mcd64a1, vnp64a1) | 12 | 1 | 28 | 43 | 13 | 1 | 1 | brezal y zonas húmedas (matorral) | landas y brezales | 9 | 2 | no | no |
| 15 | 278497 | Carviçais (Douro) | PT | 11.932 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 1 | 0 | 58 | 17 | 15 | 8 | 1 | matorral (matorral) | transición bosque-matorral | 8 | 5 | no | no |
| 16 | 278498 | Puertas (Salamanca) | ES | 10.823 | 13/08 | 13/08 | 13/08 | 15/08 | **13/08** (effis, viirs, mcd64a1) | 0 | 0 | 18 | 0 | 65 | 17 | 0 | pastizal (pasto) | agroforestal | 7 | 5 | no | no |
| 17 | 278493 | Alverca da Beira/Bouça Cova (Beiras e Serra da Estrela) | PT | 9.523 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 0 | 0 | 66 | 6 | 0 | 27 | 1 | matorral (matorral) | agrícola | 5 | 5 | no | no |
| 18 | 279404 | Peranzanes (León) | ES | 7.821 | 10/08 | 10/08 | 11/08 | 10/08 | **10/08** (effis, viirs, vnp64a1) | 15 | 1 | 3 | 65 | 16 | 0 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 6 | 5 | no | no |
| 19 | 276834 | Entre Ambos-os-Rios, Ermida e Germil (Alto Minho) | PT | 7.225 | 26/07 | 12/07 | 27/07 | 28/07 | **12/07** (viirs) | 3 | 1 | 17 | 69 | 8 | 0 | 1 | brezal y zonas húmedas (matorral) | landas y brezales | 4 | 3 | **sí** (11 VIIRS, 0,7 %) | **sí** |
| 20 | 277955 | Murias de Paredes (León) | ES | 7.070 | 21/08 | 09/08 | 10/08 | 09/08 | **09/08** (viirs, vnp64a1) | 20 | 3 | 11 | 57 | 9 | 0 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 4 | 5 | no | **sí** |
| 21 | 278483 | Guardo (Palencia) | ES | 6.862 | 16/08 | 16/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 54 | 0 | 29 | 3 | 2 | 11 | 0 | bosque cerrado (arbolado) | coníferas | 4 | 5 | no | no |
| 22 | 276659 | Real (Tâmega e Sousa) | PT | 6.555 | 28/07 | 30/06 | 27/07 | 29/07 | **30/06** (viirs) | 33 | 1 | 21 | 0 | 40 | 1 | 3 | pastizal (pasto) | transición bosque-matorral | 5 | 1 | no | **sí** |
| 23 | 277291 | Pena, Quintã e Vila Cova (Douro) | PT | 6.087 | 03/08 | 03/08 | 02/08 | 03/08 | **02/08** (mcd64a1) | 7 | 3 | 27 | 40 | 17 | 2 | 3 | brezal y zonas húmedas (matorral) | landas y brezales | 4 | 0 | **sí** (3 VIIRS, 0,3 %) | no |
| 24 | 278485 | Llerena (Badajoz) | ES | 5.829 | 14/08 | 14/08 | 13/08 | 14/08 | **13/08** (mcd64a1) | 0 | 14 | 16 | 0 | 24 | 46 | 0 | cultivos (otro) | agroforestal | 4 | 5 | no | no |
| 25 | 273143 | Oliola (Lleida) | ES | 5.247 | 01/07 | 02/07 | 02/07 | 01/07 | **01/07** (effis, vnp64a1) | 0 | 0 | 0 | 0 | 0 | 99 | 0 | cultivos (otro) | agrícola | 3 | 5 | no | no |
| 26 | 277918 | Maceda (Ourense) | ES | 4.725 | 10/08 | 10/08 | 09/08 | 09/08 | **09/08** (mcd64a1, vnp64a1) | 16 | 5 | 13 | 47 | 12 | 8 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 3 | 5 | no | no |
| 27 | 277945 | Carucedo (León) | ES | 4.416 | 09/08 | 10/08 | 09/08 | 10/08 | **09/08** (effis, mcd64a1) | 20 | 1 | 35 | 34 | 8 | 1 | 2 | brezal y zonas húmedas† (matorral) | frondosas | 3 | 2 | no | no |
| 28 | 277936 | Gallegos del Río (Zamora) | ES | 4.317 | 12/08 | 12/08 | 11/08 | 09/08 | **09/08** (vnp64a1) | 0 | 0 | 79 | 0 | 3 | 17 | 0 | matorral (matorral) | matorral esclerófilo | 3 | 5 | no | no |
| 29 | 277953 | Villablino (León) | ES | 4.285 | 09/08 | 09/08 | 09/08 | 10/08 | **09/08** (effis, viirs, mcd64a1) | 13 | 1 | 0 | 79 | 7 | 0 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 3 | 5 | no | no |
| 30 | 278500 | Frechas (Terras de Trás-os-Montes) | PT | 3.752 | 18/08 | 18/08 | 17/08 | 15/08 | **15/08** (vnp64a1) | 0 | 0 | 74 | 9 | 3 | 15 | 0 | matorral (matorral) | agrícola | 4 | 5 | no | no |
| 31 | 278488 | Cáceres (Cáceres) | ES | 3.739 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 0 | 2 | 58 | 0 | 25 | 15 | 0 | matorral (matorral) | agroforestal | 3 | 5 | no | no |
| 32 | 278489 | Casar de Cáceres (Cáceres) | ES | 3.614 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 0 | 0 | 10 | 0 | 87 | 3 | 0 | pastizal (pasto) | pastizal natural | 2 | 5 | no | no |
| 33 | 278748 | Ervededo (Alto Tâmega) | PT | 3.493 | 19/08 | 14/08 | 17/08 | 14/08 | **14/08** (viirs, vnp64a1) | 0 | 0 | 66 | 9 | 1 | 16 | 8 | matorral (matorral) | mosaico agrícola-natural | 3 | 0 | no | **sí** |
| 34 | 279526 | Vale das Fontes (Terras de Trás-os-Montes) | PT | 3.405 | 28/08 | 28/08 | 27/08 | 28/08 | **27/08** (mcd64a1) | 3 | 5 | 72 | 1 | 5 | 13 | 0 | matorral (matorral) | transición bosque-matorral | 2 | 5 | no | no |
| 35 | 278495 | Lousã e Vilarinho (Região de Coimbra) | PT | 3.388 | 14/08 | 14/08 | 11/08 | 15/08 | **11/08** (mcd64a1) | 63 | 2 | 14 | 9 | 10 | 0 | 3 | bosque cerrado (arbolado) | bosque mixto | 2 | 0 | no | no |
| 36 | 274755 | Valmojado (Toledo) | ES | 3.247 | 17/07 | 17/07 | 17/07 | 18/07 | **17/07** (effis, viirs, mcd64a1) | 0 | 2 | 25 | 0 | 1 | 66 | 6 | cultivos (otro) | agrícola | 2 | 5 | no | no |
| 37 | 278478 | Carballeda de Avia (Ourense) | ES | 3.096 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 38 | 1 | 3 | 37 | 18 | 2 | 1 | brezal y zonas húmedas† (matorral) | landas y brezales | 2 | 5 | no | no |
| 38 | 278334 | Villar del Pedroso (Cáceres) | ES | 3.084 | 12/08 | 12/08 | 11/08 | 11/08 | **11/08** (mcd64a1, vnp64a1) | 0 | 1 | 43 | 0 | 43 | 12 | 2 | pastizal† (pasto) | pastizal natural | 2 | 5 | no | no |
| 39 | 275866 | Medelim (Beira Baixa) | PT | 3.019 | 28/07 | 29/07 | 27/07 | 29/07 | **27/07** (mcd64a1) | 0 | 0 | 37 | 0 | 7 | 56 | 0 | cultivos (otro) | agrícola | 2 | 5 | no | no |
| 40 | 278753 | Ávila (Ávila) | ES | 2.942 | 15/08 | 15/08 | 13/08 | 15/08 | **13/08** (mcd64a1) | 0 | 0 | 29 | 0 | 68 | 1 | 2 | pastizal (pasto) | pastizal natural | 3 | 5 | no | no |
| 41 | 277665 | Mata de Lobos (Beiras e Serra da Estrela) | PT | 2.774 | 08/08 | 08/08 | 07/08 | 08/08 | **07/08** (mcd64a1) | 0 | 0 | 46 | 19 | 7 | 27 | 0 | matorral (matorral) | agrícola | 2 | 5 | no | no |
| 42 | 281635 | Cardoso de la Sierra, El (Guadalajara) | ES | 2.740 | 21/09 | 21/09 | 21/09 | 19/09 | **19/09** (vnp64a1) | 32 | 3 | 20 | 43 | 1 | 0 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 1 | 0 | no | no |
| 43 | 278949 | Cinco Vilas e Reigada (Beiras e Serra da Estrela) | PT | 2.708 | 20/08 | 20/08 | 17/08 | 20/08 | **17/08** (mcd64a1) | 0 | 0 | 27 | 42 | 6 | 25 | 0 | brezal y zonas húmedas (matorral) | landas y brezales | 1 | 0 | no | no |
| 44 | 276078 | Caminomorisco (Cáceres) | ES | 2.694 | 29/07 | 29/07 | 28/07 | 29/07 | **28/07** (mcd64a1) | 51 | 7 | 25 | 10 | 0 | 7 | 0 | bosque cerrado (arbolado) | matorral esclerófilo | 1 | 5 | no | no |
| 45 | 274252 | Alfara de Carles (Tarragona) | ES | 2.650 | 07/07 | 07/07 | 07/07 | 06/07 | **06/07** (vnp64a1) | 10 | 0 | 55 | 0 | 0 | 32 | 3 | matorral (matorral) | agrícola | 2 | 5 | no | no |
| 46 | 275045 | Castilblanco (Badajoz) | ES | 2.418 | 19/07 | 19/07 | 19/07 | 19/07 | **19/07** (effis, viirs, mcd64a1, vnp64a1) | 0 | 0 | 24 | 0 | 38 | 37 | 2 | cultivos† (otro) | agroforestal | 2 | 5 | no | no |
| 47 | 278487 | Alburquerque (Badajoz) | ES | 2.346 | 14/08 | 14/08 | 13/08 | 14/08 | **13/08** (mcd64a1) | 0 | 0 | 72 | 0 | 12 | 17 | 0 | matorral (matorral) | agroforestal | 1 | 5 | no | no |
| 48 | 281915 | Bensafrim e Barão de São João (Algarve) | PT | 2.332 | 21/09 | 21/09 | 20/09 | 20/09 | **20/09** (mcd64a1, vnp64a1) | 20 | 4 | 68 | 0 | 2 | 6 | 0 | bosque cerrado† (arbolado) | transición bosque-matorral | 2 | 0 | no | no |
| 49 | 275869 | Mombeltrán (Ávila) | ES | 2.231 | 29/07 | 29/07 | 28/07 | 29/07 | **28/07** (mcd64a1) | 10 | 1 | 64 | 0 | 2 | 23 | 0 | matorral (matorral) | transición bosque-matorral | 2 | 5 | no | no |
| 50 | 278425 | Riofrío de Aliste (Zamora) | ES | 2.142 | 13/08 | 13/08 | 13/08 | 10/08 | **10/08** (vnp64a1) | 10 | 0 | 70 | 0 | 7 | 14 | 0 | matorral (matorral) | agrícola | 2 | 5 | no | no |
| 51 | 277662 | Leomil (Douro) | PT | 2.131 | 08/08 | 08/08 | 09/08 | 07/08 | **07/08** (vnp64a1) | 0 | 0 | 38 | 42 | 4 | 15 | 1 | brezal y zonas húmedas (matorral) | landas y brezales | 2 | 0 | no | no |
| 52 | 281621 | Lazarim (Douro) | PT | 2.067 | 19/09 | 19/09 | 17/09 | 17/09 | **17/09** (mcd64a1, vnp64a1) | 6 | 0 | 47 | 38 | 3 | 5 | 0 | matorral (matorral) | landas y brezales | 1 | 3 | no | no |
| 53 | 278333 | Madrid (Madrid) | ES | 2.037 | 12/08 | 12/08 | 12/08 | 12/08 | **12/08** (effis, viirs, mcd64a1, vnp64a1) | 0 | 0 | 21 | 0 | 48 | 17 | 14 | pastizal (pasto) | pastizal natural | 1 | 1 | no | no |

## Selección

Marcar aquí los 10–15 incendios elegidos (ID EFFIS), con la fecha de ignición contrastada y la fecha de la selección, antes de analizar nada.

