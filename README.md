
# Práctica 1: Web scraping

## Descripció

Practica 1 de l'assignatura Tipologia i cicle de vida de les dades del Master de cienca de dades de la UOC.

En aquesta primera pràctica de l’assignatura Tipologia i cicle de vida de les dades s’ha
implementat una tènica de web scraping mitjançant una web crawler o aranya, per a generar
una base de dades d’enfonsaments de vaixells a tot el món al llarg de la història a partir de la
pàgina “List of shipwrecks” de Wikipedia. La font original es pot consultar en aquest enllaç:
https://en.wikipedia.org/wiki/Lists_of_shipwrecks

## Equip

Activitat realitzada per **Oriol Caravaca Müller** i **Pau Casanova Pedrol**.

## Dataset

 https://doi.org/10.5281/zenodo.7347768
 
## Codi font rellevant

* **source/requirements.txt**: conte la informació dels requeriments de l'entorn.
* **source/main.py**: punt de entrada del programa. Inicia el process de webscraping.
* **source/shipWrecks/spiders/shipwreck.py**: conte la implementacio de la classe que s'encarga de fer el webscraping
* **source/shipWrecks/settings.py**: conte  la configuració especifica per a les bones practiques del webscaping. Com per exemple el User-agent.
* **source/postprocess/cleaning.py**: conte la implementacio de funcions per netejar les dades.
* **source/visualitzacio/shipwreckPlot.py**: conte la implementacio de funcio que s'encarrega de generar la visualitzacio.

