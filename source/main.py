from shipWrecks.spiders.shipwreck import ShipWreckSpider
from scrapy.crawler import CrawlerProcess
from concurrent.futures import process
import pandas as pd
import re

ruta_csv='../dataset/shipWrecks.csv'


#fem corre el process
process =CrawlerProcess()
process.crawl(ShipWreckSpider)
process.start()

#neteja de cordenades,anotacions i dates
def clean_data(df):
    if 'COORDINATES' in df.columns:
        df["COORDINATES"] = df["COORDINATES"].apply(convert_coordinates)

    if 'NOTES' in df.columns:
        df["NOTES"] = df["NOTES"].apply(lambda s:re.sub("\[[0-9]+\]", "", str(s)))
    if "SUNK DATE" in df.columns:
        df["SUNK DATE"] = df["SUNK DATE"].apply(lambda s:re.sub("\([A-Za-z]+\)", "", str(s)))
            #fer funcio per persejar data, els parejadors que he provat no tiren be

    return df

def convert_coordinates(s):

    s=str(s)

    s=s if s.rfind("/") ==-1  else s[s.rfind("/")+1:len(s)]
    s=s if s.find("(")==-1 else s[0:s.find("(")]
    s= s.replace("\n"," ")

    lat=""
    long=""
    if len(s.split("°"))==3 and len(s.split(" "))==2:

        s=s.split(" ")
        lat =  re.split('[°\'′″"]', s[0])
        lat= (float(lat[0]) + (float(lat[1])/60 if len(lat)>2 else 0) + (float(lat[2])/(60*60) if len(lat)>3 else 0)) * (-1 if lat[len(lat)-1] in ['W', 'S'] else 1)

        long =  re.split('[°\'′″"]', s[1])  
        long= (float(long[0]) +( float(long[1])/60 if len(long)>2 else 0 )+ (float(long[2])/(60*60) if len(long)>3 else 0)) * (-1 if long[len(long)-1] in ['W', 'S'] else 1)
        s=str(lat)+ "; " + str(long)
    
    if re.search(";",s):
        return s
    else:
        return ""
   


#un cop acabat el process anexem totes les taules trobades i guardem el dataset amb les columnes desitjades
df=pd.concat(ShipWreckSpider.taules, axis=0)
df=df[['SHIP','FLAG','SUNK DATE','VESSEL TYPE','ZONA1','ZONA2','ZONA3','ZONA4','COORDINATES','NOTES','IMAGE']]
df=clean_data(df)
df.to_csv(ruta_csv)  
print(df)

