# SOA U8 - Cauzele inundatiilor in Europa (10 lucrari)

| # | Lucrare | Date | Metoda | Rezultat relevant U8 |
|---|---|---|---|---|
| 1 | Bloschl et al. (2017), Science, https://doi.org/10.1126/science.aan2506 | 4262 statii, 38 tari europene | analiza continentala a sezonalitatii inundatiilor | schimbari regionale clare ale momentului inundatiilor (timing), legate de mecanisme hidrometeo |
| 2 | Berghuijs et al. (2019), WRR, https://doi.org/10.1029/2019WR024841 | serii pan-europene AMAX | atribuire mecanisme (ploi extreme, umiditate antecedenta, snowmelt) | multe evenimente apar prin combinatia ploaie + umiditate antecedenta ridicata |
| 3 | Hundecha et al. (2020), HSJ, https://doi.org/10.1080/02626667.2020.1782413 | 614 statii Europa, 1961-2010 | clasificare flood process types | trend descrescator pentru snowmelt floods, trend crescator pentru long-rain floods |
| 4 | Jiang et al. (2022), HESS, https://doi.org/10.5194/hess-26-6339-2022 | 55,828 evenimente, >1000 bazine | explainable ML + clustering mecanisme | multe bazine sunt controlate de combinatii de mecanisme, nu de un singur driver |
| 5 | Tarasova et al. (2023), Communications Earth & Environment, https://doi.org/10.1038/s43247-023-00714-8 | Europa 1960-2010 | flood-rich / flood-poor periods + proces changes | schimbari mici in mixul proceselor pot amplifica perioade regionale flood-rich |
| 6 | Kemter et al. (2020), GRL, https://doi.org/10.1029/2020GL087464 | 3872 statii Europa | trenduri magnitudine + extindere spatiala | coevolutie a trendurilor de magnitudine si extindere spatiala a inundatiilor |
| 7 | Bertola et al. (2020), HESS, https://doi.org/10.5194/hess-24-1805-2020 | 2370 serii (>=40 ani) | modelare non-stationara a flood quantiles | trenduri diferite pentru flooduri mici vs mari, dependente de regiune/scara |
| 8 | Brunner & Fischer (2022), ERL, https://doi.org/10.1088/1748-9326/ac948f | bazine europene | clasificare eveniment + conectivitate spatiala | floodurile influentate de zapada au conectivitate spatiala mai puternica |
| 9 | Stein et al. (2019), Hydrological Processes, https://doi.org/10.1002/hyp.13678 | 113,635 evenimente, 4155 bazine | clasificare event-based in 5 procese | schema robusta de separare: short-rain, long-rain, excess-rain, snowmelt, rain-on-snow |
| 10 | Turkington et al. (2016), Weather and Climate Extremes, https://doi.org/10.1016/j.wace.2016.10.001 | bazine alpine | weather generator + model hidrologic + clustering | tipizarea pe procese este reproductibila si utila pentru climate-impact studies |

## Concluzie SOA pentru CP1

Literatura sustine clar ideea U8: tipurile de inundatii se separa mai bine cand combinam:

- informatia de eveniment (activare/loc/timp),
- precipitatii si temperatura,
- starea antecedenta a solului,
- componenta nivala.

Aceasta este exact ipoteza operationalizata in pipeline-ul CP1 din acest folder.
