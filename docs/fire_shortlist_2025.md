# Lista corta de grandes incendios de 2025 (perímetros de EFFIS > 2.000 ha)

Generada el 07/11/2026 con `Rscript R/fire_shortlist.R` a partir de `data/interim/fires/fire_candidates_2025.csv`. Solo información estática: no se ha extraído ninguna serie de vegetación ni de meteorología.

**Columnas**

- **Fechas** (día/mes, UTC): primera fecha de cada fuente dentro del perímetro, entre FIREDATE − 30 días y FINALDATE + 1 día. VIIRS: detecciones `type = 0` sin confianza baja.
- **Ignición**: la más temprana de las cuatro fuentes; entre paréntesis, la fuente o fuentes que la fijan.
- **Vegetación (CORINE Land Cover 2018, 100 m, agregado a 0,05°)**: porcentaje de cada grupo, medio ponderado por la superficie del perímetro en cada celda de 0,05°. Frond. = frondosas (311), Conif. = coníferas (312), Mixto = bosque mixto (313), Pastizal = pastizal natural (321), Landas = landas y brezales (322), Escler. = matorral esclerófilo (323), Trans. = transición bosque-matorral (324), Agríc. = cultivos y prados (211–242), Mosaico = mosaico agrícola con vegetación natural (243), Agrofor. = sistemas agroforestales, dehesas y montados (244); Otro = vegetación escasa, zonas quemadas (334, sobre todo de 2017), artificial y agua. "Dominante" es el grupo con más superficie, el que se usa para emparejar los controles. Estrato: arbolado = 311–313, matorral = 322–324, pasto = 321.
- **Celdas / Controles**: celdas de 0,05° con al menos un 25 % dentro del perímetro, y celdas de control válidas (se usan como máximo 5; hacen falta 3) con los criterios de `config.yaml` (`epoch.controls`): sin quemar desde 2017 (EFFIS, MCD64A1, VNP64A1 y ESFire30), mismo grupo dominante de CORINE, aridez ±0,1, altitud ±200 m y a 10–50 km del perímetro. Solo información estática.
- **Coherencia**: actividad VIIRS o MCD64A1/VNP64A1 dentro del perímetro entre 90 y 30 días antes de FIREDATE; entre paréntesis, detecciones previas y su fracción del total.
- **Revisar**: ignición más de 3 días antes de FIREDATE sin marca de coherencia (posible fusión de perímetros).

| # | ID EFFIS | Municipio (provincia) | País | ha | EFFIS | VIIRS | MCD64A1 | VNP64A1 | Ignición (fuente) | Frond. % | Conif. % | Mixto % | Pastizal % | Landas % | Escler. % | Trans. % | Agríc. % | Mosaico % | Agrofor. % | Otro % | Dominante (estrato) | Celdas | Controles | Coherencia | Revisar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 277926 | Trancoso (São Pedro e Santa Maria) e Souto Maior (Beiras e Serra da Estrela) | PT | 62.104 | 10/08 | 10/08 | 09/08 | 09/08 | **09/08** (mcd64a1, vnp64a1) | 1 | 5 | 1 | 0 | 23 | 1 | 25 | 28 | 12 | 0 | 4 | agrícola (otro) | 33 | 0 | **sí** (3 VIIRS, 0,1 %) | no |
| 2 | 277940 | Uña de Quintana (Zamora) | ES | 40.081 | 10/08 | 10/08 | 09/08 | 08/08 | **08/08** (vnp64a1) | 16 | 3 | 0 | 4 | 0 | 19 | 12 | 40 | 3 | 0 | 3 | agrícola (otro) | 22 | 5 | no | no |
| 3 | 277927 | Sobral de São Miguel (Beiras e Serra da Estrela) | PT | 37.619 | 10/08 | 10/08 | 10/08 | 11/08 | **10/08** (effis, viirs, mcd64a1) | 1 | 15 | 0 | 0 | 21 | 0 | 47 | 10 | 3 | 0 | 2 | transición bosque-matorral (matorral) | 21 | 1 | no | no |
| 4 | 278475 | Rúa, A (Ourense) | ES | 37.179 | 14/08 | 14/08 | 13/08 | 13/08 | **13/08** (mcd64a1, vnp64a1) | 15 | 8 | 2 | 3 | 50 | 0 | 10 | 4 | 5 | 0 | 2 | landas y brezales (matorral) | 20 | 5 | no | no |
| 5 | 278350 | Piódão (Região de Coimbra) | PT | 30.455 | 11/08 | 13/08 | 11/08 | 12/08 | **11/08** (effis, mcd64a1) | 2 | 14 | 7 | 0 | 25 | 0 | 35 | 5 | 5 | 0 | 6 | transición bosque-matorral (matorral) | 18 | 0 | no | no |
| 6 | 277944 | Benuza (León) | ES | 26.241 | 09/08 | 09/08 | 09/08 | 08/08 | **08/08** (vnp64a1) | 18 | 2 | 1 | 8 | 55 | 0 | 8 | 1 | 0 | 0 | 8 | landas y brezales (matorral) | 14 | 4 | no | no |
| 7 | 278477 | Veiga, A (Ourense) | ES | 25.953 | 15/08 | 15/08 | 14/08 | 13/08 | **13/08** (vnp64a1) | 5 | 0 | 0 | 56 | 11 | 0 | 2 | 1 | 0 | 0 | 25 | pastizal natural (pasto) | 14 | 0 | **sí** (8 VIIRS, 0,1 %) | no |
| 8 | 278504 | Manzaneda (Ourense) | ES | 24.583 | 08/08 | 08/08 | 09/08 | 08/08 | **08/08** (effis, viirs, vnp64a1) | 11 | 5 | 0 | 2 | 63 | 0 | 4 | 3 | 7 | 0 | 5 | landas y brezales (matorral) | 15 | 0 | **sí** (3 VIIRS, 0,1 %) | no |
| 9 | 278348 | Oímbra (Ourense) | ES | 24.471 | 13/08 | 24/07 | 11/08 | 11/08 | **24/07** (viirs) | 5 | 10 | 1 | 0 | 37 | 0 | 13 | 8 | 22 | 0 | 4 | landas y brezales (matorral) | 14 | 5 | no | **sí** |
| 10 | 278492 | Quintas de São Bartolomeu (Beiras e Serra da Estrela) | PT | 23.594 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 1 | 0 | 2 | 1 | 30 | 0 | 32 | 13 | 15 | 1 | 4 | transición bosque-matorral (matorral) | 14 | 5 | no | no |
| 11 | 278481 | Burón (León) | ES | 19.112 | 14/08 | 14/08 | 12/08 | 12/08 | **12/08** (mcd64a1, vnp64a1) | 18 | 1 | 0 | 4 | 54 | 0 | 1 | 0 | 0 | 0 | 21 | landas y brezales (matorral) | 11 | 5 | no | no |
| 12 | 279768 | Navaconcejo (Cáceres) | ES | 17.317 | 13/08 | 13/08 | 11/08 | 11/08 | **11/08** (mcd64a1, vnp64a1) | 14 | 1 | 0 | 16 | 6 | 23 | 6 | 11 | 3 | 6 | 13 | matorral esclerófilo (matorral) | 10 | 0 | no | no |
| 13 | 278349 | Ferreira de Aves (Viseu Dão Lafões) | PT | 13.903 | 10/08 | 13/08 | 10/08 | 12/08 | **10/08** (effis, mcd64a1) | 0 | 17 | 2 | 0 | 11 | 0 | 31 | 20 | 11 | 0 | 8 | transición bosque-matorral (matorral) | 9 | 0 | no | no |
| 14 | 278347 | Mezquita, A (Ourense) | ES | 12.026 | 12/08 | 12/08 | 11/08 | 11/08 | **11/08** (mcd64a1, vnp64a1) | 9 | 9 | 0 | 0 | 46 | 0 | 9 | 4 | 16 | 0 | 5 | landas y brezales (matorral) | 9 | 3 | no | no |
| 15 | 278497 | Carviçais (Douro) | PT | 11.932 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 1 | 1 | 0 | 2 | 18 | 4 | 32 | 15 | 19 | 0 | 8 | transición bosque-matorral (matorral) | 8 | 5 | no | no |
| 16 | 278498 | Puertas (Salamanca) | ES | 10.823 | 13/08 | 13/08 | 13/08 | 15/08 | **13/08** (effis, viirs, mcd64a1) | 3 | 0 | 0 | 28 | 0 | 2 | 5 | 9 | 2 | 49 | 1 | agroforestal (otro) | 7 | 5 | no | no |
| 17 | 278493 | Alverca da Beira/Bouça Cova (Beiras e Serra da Estrela) | PT | 9.523 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 0 | 2 | 1 | 1 | 11 | 0 | 26 | 40 | 17 | 0 | 2 | agrícola (otro) | 5 | 5 | no | no |
| 18 | 279404 | Peranzanes (León) | ES | 7.821 | 10/08 | 10/08 | 11/08 | 10/08 | **10/08** (effis, viirs, vnp64a1) | 22 | 3 | 0 | 4 | 56 | 0 | 3 | 2 | 0 | 0 | 9 | landas y brezales (matorral) | 6 | 3 | no | no |
| 19 | 276834 | Entre Ambos-os-Rios, Ermida e Germil (Alto Minho) | PT | 7.225 | 26/07 | 12/07 | 27/07 | 28/07 | **12/07** (viirs) | 4 | 1 | 3 | 0 | 66 | 0 | 12 | 3 | 3 | 0 | 8 | landas y brezales (matorral) | 4 | 2 | **sí** (11 VIIRS, 0,7 %) | **sí** |
| 20 | 277955 | Murias de Paredes (León) | ES | 7.070 | 21/08 | 09/08 | 10/08 | 09/08 | **09/08** (viirs, vnp64a1) | 28 | 0 | 1 | 5 | 53 | 0 | 6 | 1 | 2 | 0 | 5 | landas y brezales (matorral) | 4 | 5 | no | **sí** |
| 21 | 278483 | Guardo (Palencia) | ES | 6.862 | 16/08 | 16/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 24 | 33 | 11 | 3 | 7 | 1 | 5 | 15 | 1 | 0 | 1 | coníferas (arbolado) | 4 | 0 | no | no |
| 22 | 276659 | Real (Tâmega e Sousa) | PT | 6.555 | 28/07 | 30/06 | 27/07 | 29/07 | **30/06** (viirs) | 23 | 0 | 6 | 0 | 0 | 0 | 55 | 10 | 5 | 0 | 1 | transición bosque-matorral (matorral) | 5 | 1 | no | **sí** |
| 23 | 277291 | Pena, Quintã e Vila Cova (Douro) | PT | 6.087 | 03/08 | 03/08 | 02/08 | 03/08 | **02/08** (mcd64a1) | 1 | 4 | 7 | 3 | 40 | 0 | 18 | 8 | 10 | 0 | 9 | landas y brezales (matorral) | 4 | 1 | **sí** (3 VIIRS, 0,3 %) | no |
| 24 | 278485 | Llerena (Badajoz) | ES | 5.829 | 14/08 | 14/08 | 13/08 | 14/08 | **13/08** (mcd64a1) | 8 | 1 | 0 | 2 | 0 | 3 | 12 | 29 | 1 | 44 | 0 | agroforestal (otro) | 4 | 5 | no | no |
| 25 | 273143 | Oliola (Lleida) | ES | 5.247 | 01/07 | 02/07 | 02/07 | 01/07 | **01/07** (effis, vnp64a1) | 9 | 0 | 0 | 0 | 0 | 5 | 0 | 86 | 0 | 0 | 0 | agrícola (otro) | 3 | 5 | no | no |
| 26 | 277918 | Maceda (Ourense) | ES | 4.725 | 10/08 | 10/08 | 09/08 | 09/08 | **09/08** (mcd64a1, vnp64a1) | 21 | 5 | 0 | 6 | 37 | 0 | 13 | 2 | 16 | 0 | 0 | landas y brezales (matorral) | 3 | 4 | no | no |
| 27 | 277945 | Carucedo (León) | ES | 4.416 | 09/08 | 10/08 | 09/08 | 10/08 | **09/08** (effis, mcd64a1) | 42 | 0 | 1 | 9 | 33 | 0 | 7 | 3 | 1 | 0 | 2 | frondosas (arbolado) | 3 | 1 | no | no |
| 28 | 277936 | Gallegos del Río (Zamora) | ES | 4.317 | 12/08 | 12/08 | 11/08 | 09/08 | **09/08** (vnp64a1) | 1 | 0 | 0 | 11 | 0 | 44 | 4 | 30 | 11 | 0 | 1 | matorral esclerófilo (matorral) | 3 | 5 | no | no |
| 29 | 277953 | Villablino (León) | ES | 4.285 | 09/08 | 09/08 | 09/08 | 10/08 | **09/08** (effis, viirs, mcd64a1) | 14 | 1 | 0 | 3 | 71 | 0 | 2 | 5 | 0 | 0 | 3 | landas y brezales (matorral) | 3 | 2 | no | no |
| 30 | 278500 | Frechas (Terras de Trás-os-Montes) | PT | 3.752 | 18/08 | 18/08 | 17/08 | 15/08 | **15/08** (vnp64a1) | 2 | 0 | 1 | 1 | 15 | 0 | 18 | 33 | 25 | 0 | 3 | agrícola (otro) | 4 | 5 | no | no |
| 31 | 278488 | Cáceres (Cáceres) | ES | 3.739 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 2 | 0 | 0 | 2 | 0 | 34 | 1 | 8 | 0 | 53 | 1 | agroforestal (otro) | 3 | 5 | no | no |
| 32 | 278489 | Casar de Cáceres (Cáceres) | ES | 3.614 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 0 | 0 | 0 | 64 | 0 | 10 | 2 | 12 | 3 | 8 | 1 | pastizal natural (pasto) | 2 | 5 | no | no |
| 33 | 278748 | Ervededo (Alto Tâmega) | PT | 3.493 | 19/08 | 14/08 | 17/08 | 14/08 | **14/08** (viirs, vnp64a1) | 2 | 1 | 2 | 1 | 16 | 0 | 17 | 23 | 31 | 0 | 8 | mosaico agrícola-natural (otro) | 3 | 0 | no | **sí** |
| 34 | 279526 | Vale das Fontes (Terras de Trás-os-Montes) | PT | 3.405 | 28/08 | 28/08 | 27/08 | 28/08 | **27/08** (mcd64a1) | 2 | 3 | 3 | 0 | 11 | 0 | 35 | 21 | 23 | 0 | 2 | transición bosque-matorral (matorral) | 2 | 3 | no | no |
| 35 | 278495 | Lousã e Vilarinho (Região de Coimbra) | PT | 3.388 | 14/08 | 14/08 | 11/08 | 15/08 | **11/08** (mcd64a1) | 5 | 23 | 29 | 0 | 8 | 0 | 25 | 5 | 3 | 0 | 1 | bosque mixto (arbolado) | 2 | 0 | no | no |
| 36 | 274755 | Valmojado (Toledo) | ES | 3.247 | 17/07 | 17/07 | 17/07 | 18/07 | **17/07** (effis, viirs, mcd64a1) | 1 | 0 | 0 | 12 | 0 | 8 | 1 | 62 | 8 | 1 | 6 | agrícola (otro) | 2 | 5 | no | no |
| 37 | 278478 | Carballeda de Avia (Ourense) | ES | 3.096 | 15/08 | 15/08 | 14/08 | 15/08 | **14/08** (mcd64a1) | 26 | 10 | 6 | 0 | 33 | 0 | 5 | 7 | 1 | 0 | 12 | landas y brezales (matorral) | 2 | 2 | no | no |
| 38 | 278334 | Villar del Pedroso (Cáceres) | ES | 3.084 | 12/08 | 12/08 | 11/08 | 11/08 | **11/08** (mcd64a1, vnp64a1) | 7 | 1 | 2 | 30 | 0 | 2 | 5 | 21 | 7 | 23 | 1 | pastizal natural (pasto) | 2 | 5 | no | no |
| 39 | 275866 | Medelim (Beira Baixa) | PT | 3.019 | 28/07 | 29/07 | 27/07 | 29/07 | **27/07** (mcd64a1) | 1 | 0 | 0 | 0 | 0 | 8 | 32 | 37 | 19 | 2 | 1 | agrícola (otro) | 2 | 5 | no | no |
| 40 | 278753 | Ávila (Ávila) | ES | 2.942 | 15/08 | 15/08 | 13/08 | 15/08 | **13/08** (mcd64a1) | 2 | 0 | 1 | 63 | 0 | 23 | 2 | 1 | 3 | 1 | 5 | pastizal natural (pasto) | 3 | 5 | no | no |
| 41 | 277665 | Mata de Lobos (Beiras e Serra da Estrela) | PT | 2.774 | 08/08 | 08/08 | 07/08 | 08/08 | **07/08** (mcd64a1) | 5 | 0 | 1 | 2 | 19 | 6 | 25 | 27 | 13 | 0 | 1 | agrícola (otro) | 2 | 2 | no | no |
| 42 | 281635 | Cardoso de la Sierra, El (Guadalajara) | ES | 2.740 | 21/09 | 21/09 | 21/09 | 19/09 | **19/09** (vnp64a1) | 11 | 21 | 9 | 15 | 39 | 1 | 1 | 0 | 1 | 0 | 2 | landas y brezales (matorral) | 1 | 0 | no | no |
| 43 | 278949 | Cinco Vilas e Reigada (Beiras e Serra da Estrela) | PT | 2.708 | 20/08 | 20/08 | 17/08 | 20/08 | **17/08** (mcd64a1) | 0 | 0 | 0 | 3 | 46 | 0 | 15 | 18 | 13 | 0 | 5 | landas y brezales (matorral) | 1 | 1 | no | no |
| 44 | 276078 | Caminomorisco (Cáceres) | ES | 2.694 | 29/07 | 29/07 | 28/07 | 29/07 | **28/07** (mcd64a1) | 0 | 10 | 16 | 3 | 13 | 27 | 20 | 9 | 1 | 0 | 1 | matorral esclerófilo (matorral) | 1 | 1 | no | no |
| 45 | 274252 | Alfara de Carles (Tarragona) | ES | 2.650 | 07/07 | 07/07 | 07/07 | 06/07 | **06/07** (vnp64a1) | 1 | 19 | 1 | 0 | 0 | 32 | 9 | 33 | 1 | 0 | 3 | agrícola (otro) | 2 | 5 | no | no |
| 46 | 275045 | Castilblanco (Badajoz) | ES | 2.418 | 19/07 | 19/07 | 19/07 | 19/07 | **19/07** (effis, viirs, mcd64a1, vnp64a1) | 2 | 0 | 0 | 13 | 0 | 4 | 9 | 19 | 1 | 48 | 3 | agroforestal (otro) | 2 | 5 | no | no |
| 47 | 278487 | Alburquerque (Badajoz) | ES | 2.346 | 14/08 | 14/08 | 13/08 | 14/08 | **13/08** (mcd64a1) | 4 | 5 | 0 | 19 | 0 | 24 | 5 | 3 | 0 | 41 | 0 | agroforestal (otro) | 1 | 5 | no | no |
| 48 | 281915 | Bensafrim e Barão de São João (Algarve) | PT | 2.332 | 21/09 | 21/09 | 20/09 | 20/09 | **20/09** (mcd64a1, vnp64a1) | 26 | 8 | 0 | 0 | 0 | 14 | 38 | 10 | 3 | 0 | 0 | transición bosque-matorral (matorral) | 2 | 5 | no | no |
| 49 | 275869 | Mombeltrán (Ávila) | ES | 2.231 | 29/07 | 29/07 | 28/07 | 29/07 | **28/07** (mcd64a1) | 2 | 17 | 6 | 3 | 0 | 11 | 33 | 20 | 2 | 0 | 6 | transición bosque-matorral (matorral) | 2 | 4 | no | no |
| 50 | 278425 | Riofrío de Aliste (Zamora) | ES | 2.142 | 13/08 | 13/08 | 13/08 | 10/08 | **10/08** (vnp64a1) | 2 | 8 | 0 | 5 | 0 | 34 | 3 | 35 | 12 | 0 | 1 | agrícola (otro) | 2 | 5 | no | no |
| 51 | 277662 | Leomil (Douro) | PT | 2.131 | 08/08 | 08/08 | 09/08 | 07/08 | **07/08** (vnp64a1) | 1 | 6 | 0 | 0 | 43 | 0 | 10 | 28 | 5 | 0 | 6 | landas y brezales (matorral) | 2 | 0 | no | no |
| 52 | 281621 | Lazarim (Douro) | PT | 2.067 | 19/09 | 19/09 | 17/09 | 17/09 | **17/09** (mcd64a1, vnp64a1) | 1 | 4 | 2 | 0 | 43 | 0 | 13 | 20 | 17 | 0 | 1 | landas y brezales (matorral) | 1 | 0 | no | no |
| 53 | 278333 | Madrid (Madrid) | ES | 2.037 | 12/08 | 12/08 | 12/08 | 12/08 | **12/08** (effis, viirs, mcd64a1, vnp64a1) | 19 | 0 | 0 | 38 | 0 | 1 | 0 | 9 | 0 | 21 | 11 | pastizal natural (pasto) | 1 | 1 | no | no |

## Selección

Marcar aquí los 10–15 incendios elegidos (ID EFFIS), con la fecha de ignición contrastada y la fecha de la selección, antes de analizar nada.

