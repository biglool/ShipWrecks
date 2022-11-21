from shipWrecks.spiders.shipwreck import ShipWreckSpider
from scrapy.crawler import CrawlerProcess
from concurrent.futures import process
import pandas as pd

ruta_csv='../../../dataset/shipWrecks.csv'
#fem corre el process
process =CrawlerProcess()
process.crawl(ShipWreckSpider)
process.start()

#un cop acabat el process anexem totes les taules trobades i guardem el dataset amb les columnes desitjades
df=pd.concat(ShipWreckSpider.taules, axis=0)
df=df[['SHIP','FLAG','SUNK DATE','VESSEL TYPE','ZONA1','ZONA2','ZONA3','ZONA4','COORDINATES','NOTES','IMAGE']]
df.to_csv()  
print(df)
