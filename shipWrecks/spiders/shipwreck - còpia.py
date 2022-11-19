from concurrent.futures import process
from sys import prefix
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup, SoupStrainer
import numpy as np
import re

class ShipWreckSpider(Spider):
    name = 'shipwreck'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Lists_of_shipwrecks']
    base='https://en.wikipedia.org'

    def start_requests(self):
        for u in self.start_urls:
            yield Request(u, callback=self.parse_main)  


    def parse_main(self, response):   
        print("----------") 
        data=response.xpath("//a[not(ancestor::table) and starts-with(@title, 'List of shipwrecks')]") 
        
        for link in data:
            next_page_url ='https://en.wikipedia.org'+link.xpath('@href').extract()[0]
            print(next_page_url)
            yield Request(next_page_url,self.parse_sub)

    def parse_sub(self, response): 
        
         data=response.xpath("//table[contains(@class, 'wikitable')] | //div[contains(string(), 'Main article') and contains(@class,'hatnote navigation-not-searchable')]").extract()
         titles=response.xpath("//span[contains(@class, 'mw-headline') and not(contains(@id, 'Further_reading')) and not(contains(@id, 'References'))  and not(contains(@id, 'External_links'))]/ancestor::*[self::h2 or self::h3 or self::h4][1]")
         titols =self.contract_titles(titles)
         print(len(titols))
         print(len(data))
         print(titols)
         #for taula in data:
           # print(taula)

    def contract_titles(self,titles):
        last_index=-1
        prefix=['','','']
        llista=[]
        for title in titles:
            index=BeautifulSoup(title.get()).find('body').findChildren()[0].name.replace("h", "")
            index=int(index)-2
            text=BeautifulSoup(title.get()).find('span').text
            if  index > last_index:
                prefix[index] = text
            elif index == last_index:
                llista.append(prefix.copy())
                prefix[index] = text
            else:
                llista.append(prefix.copy())
                prefix[index+1] =""
                if index==0:
                    prefix=['','','']
                else:
                    prefix[2] =""
                prefix[index] = text
            last_index=index
        llista.append(prefix.copy())
        return llista

        
                
               

           
process =CrawlerProcess()
process.crawl(ShipWreckSpider)
process.start()
        
