from shipWrecks.spiders.shipwreck import ShipWreckSpider
from postprocess import cleaning
from visualitzacio import shipwreckPlot
from scrapy.crawler import CrawlerProcess
from concurrent.futures import process
import pandas as pd


ruta_csv='../dataset/shipWrecks.csv'
ruta_visualitzacio='../dataset/shipWrecks.png'

#fem corre el process
process =CrawlerProcess()
process.crawl(ShipWreckSpider)
process.start()


#un cop acabat el process anexem totes les taules trobades i guardem el dataset amb les columnes desitjades
df=pd.concat(ShipWreckSpider.taules, axis=0)

#netejem, guardem i generem plot
df=cleaning.clean_data(df)
df.to_csv(ruta_csv)  
print(df)
shipwreckPlot.generate_plot(df,ruta_visualitzacio)
print("Process finalitzat")

