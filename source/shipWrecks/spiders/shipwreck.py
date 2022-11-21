
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from concurrent.futures import process
from bs4 import BeautifulSoup, SoupStrainer

import numpy as np
import pandas as pd
import re

class ShipWreckSpider(Spider):
    name = 'shipwreck'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Lists_of_shipwrecks']
    base_url='https://en.wikipedia.org'
    taules=[]

    def start_requests(self):
        for u in self.start_urls:
            yield Request(u, callback=self.parse_main)  

    #procesem la pagina principal
    def parse_main(self, response):  

        data=response.xpath("//a[not(ancestor::table) and starts-with(@title, 'List of shipwrecks')]")       
        for link in data:
            next_page_url =self.base_url+link.xpath('@href').extract()[0]
            yield Request(next_page_url,self.extract_page)
            
    #procesem cada subpagina
    def extract_page(self, response): 

        #EXTRAIEM
        main_title=response.xpath("//span[contains(@class, 'mw-page-title-main')]/text()[1]").extract()[0]
        data=response.xpath("//table[contains(@class, 'wikitable')]/preceding-sibling::*[self::h2 or self::h3 or self::h4][1] | //table[contains(@class, 'wikitable')]")
        data_titles=response.xpath("//span[contains(@class, 'mw-headline') and not(contains(@id, 'Further_reading')) and not(contains(@id, 'References'))  and not(contains(@id, 'External_links'))]/ancestor::*[self::h2 or self::h3 or self::h4][1]")
        zones =self.expand_zones(data_titles)   
        df= self.parse_page(data,main_title,zones)

        #obtenim informacio extra dels links Que hem guardat.  Per cada fila fem una nevacio del link relleants..
        self.taules.append(df)
        for index, row in df.iterrows():
            links=BeautifulSoup(str(row["extra_links"]), 'html5lib').find_all('a')
        
            for link in links:                 
                url=self.base_url+link.get('href') 

                #per cadalinks de les notes busquem una posiple localitzacio !! no sera perfecte pero solen coincidir.
                if row["COORDINATES"]=="" and row["SHIP"]!=link.text:
                    yield Request(url,self.search_cordinates, cb_kwargs={'row_index':index, 'taula_index':len(self.taules)-1} )

                # aqui podriem buscar més informació, donat l'scope de la practica simplement ens guardem el link dela imatge
                # poseteriorment es podrien baixar.
                if row["SHIP"]==link.text :
                    yield Request(url,self.search_image, cb_kwargs={'row_index':index, 'taula_index':len(self.taules)-1} )



    #procesem la informacio de cada subpagina obtenint una taula unificada
    def parse_page(self,data,main_title,zones_expandit):

        main_title=main_title.replace("List of shipwrecks","").replace(" of ","").replace(" in the ","") 
        titol=""
        zones=["","","",""]
        dfs=[]
  
        for info in data:

            dades=BeautifulSoup(info.get(), 'html5lib')
            tipus = dades.find('body').find_all(recursive=False)[0].name

            if tipus !='table':
                # buscame la llista de zones correcta a la qual correspon la taula sgüent
                titol=dades.find('span').text
                index=int(tipus.replace("h", ""))-2
                for info_zones in zones_expandit:
                    if info_zones[index]==titol and int(info_zones[3])==index:         
                         zones=info_zones.copy()

            else:
                #obtenim columnes i generem taula
                zones.insert(0, main_title)
                columnes = [cela.text.replace("\n","") for cela in dades.find_all('tr')[0].find_all('th')]
                columnes = ['Zona1','Zona2','Zona3','Zona4'] + columnes
                files_raw=dades.find("tbody").find_all('tr')       

                df=self.create_table(columnes,zones,files_raw)
                dfs.append(df)

        #anexem totes les taules de la subpagina
        df_final=pd.concat(dfs, axis=0)
        df_final.reset_index(drop=True, inplace=True)
        return df_final


    #Extraiem les dades de la taula i anexem les columnes
    def create_table(self,columnes,zones,raw):

        #donat que el format no es estandard per totes les tules errors detectats
        files=[]  
        for info_fila in raw:
            fila= [cela.text.strip() for cela in info_fila.find_all(recursive=False)]
            fila = zones[:4] +fila

            columnes=self.unify_columns(columnes)

            if len(fila)< len(columnes):
                for i in range(len(columnes)-len(fila)):
                    fila.append("")

            if len(fila)> len(columnes):
                fila.pop()

            if len(fila)== len(columnes):
                files.append(fila)  
            else:
                print(columnes)
                print(fila)

        #guardem els links de cada un dels vaixells
        columnes.append("extra_links")      
        fila.append(''.join(str(link) for link in info_fila.find_all('a')))

        #guardem la taula i fem una mica de neteja
        df=pd.DataFrame(files, columns=columnes)
        df.drop(index=df.index[0], axis=0,inplace=True)
        return df

    #corretgim noms de columnes
    def unify_columns(self,columns):

        columns= [str.upper(col) for col in columns]

        columns= ["SUNK DATE" if col=='DATE WRECKED' else col for col in columns]
        columns= ["SUNK DATE" if col=='END OF SERVICE' else col for col in columns]
        columns= ["SUNK DATE" if col=='DATE' else col for col in columns]

        columns= ["SHIP" if col=='NAME' else col for col in columns]

        if 'LOCATION' in columns:
            a, b = columns.index('LOCATION'), columns.index('ZONA3')
            columns[b], columns[a] = columns[a], columns[b]
        
        if 'RIVER' in columns:
            a, b = columns.index('RIVER'), columns.index('ZONA4')
            columns[b], columns[a] = columns[a], columns[b]

        if 'COORDINATES' not in columns:
            columns.append('COORDINATES')

        if 'IMAGE' not in columns:
            columns.append('IMAGE')

        return columns



    def search_cordinates(self, response,row_index,taula_index):

        cord=response.xpath("//span[contains(@class, 'geo-default')]")
        if len(cord) >0:
            self.taules[taula_index].loc[row_index,"COORDINATES"]=BeautifulSoup(cord.get(), 'html5lib').text

 
    def search_image(self, response,row_index,taula_index):

        info=response.xpath("//table[contains(@class, 'infobox')]")
        #resum de info extra
        if len(info) >0 :
            info=BeautifulSoup(info.get(), 'html5lib')
            imatges=info.find_all('img')

            if len(imatges) >0:
                self.taules[taula_index].loc[row_index,"IMAGE"]=imatges[0].get('src')

 


    #obtenim el llistat de zones complet
    def expand_zones(self,titles):
        #aixo simplement es una funcio de ordenacio que guarda les zones de les capçaleres de la pagina
        #basicament estructura informació que com a humans obtenim del contextualment de la pagina
        last_index=-1
        prefix=['','','','']
        llista=[]
        index=0
        for title in titles:
            dades=BeautifulSoup(title.get(), 'html5lib')
            index=dades.find('body').find_all(recursive=False)[0].name.replace("h", "")
            index=int(index)-2
            text=dades.find('span').text
            if  index > last_index:
                prefix[index] = text
            elif index == last_index:
                prefix[3]=last_index
                llista.append(prefix.copy())
                prefix[index] = text
            else:
                prefix[3]=last_index
                llista.append(prefix.copy())
                prefix[index+1] =""
                if index==0:
                    prefix=['','','','']
                else:
                    prefix[2] =""
                prefix[index] = text
            last_index=index
        prefix[3]=index
        llista.append(prefix.copy())
        return llista
           


