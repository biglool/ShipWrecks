
import re
import datetime
import calendar
import pandas as pd

#neteja de cordenades,anotacions i dates
def clean_data(df):
    df=df[['SHIP','FLAG','SUNK DATE','VESSEL TYPE','ZONA1','ZONA2','ZONA3','ZONA4','COORDINATES','NOTES','IMAGE']]
    df2 = df.copy()
    if 'COORDINATES' in df.columns:
        df2["COORDINATES"] = df["COORDINATES"].apply(convert_coordinates)

    if 'NOTES' in df.columns:
        df2["NOTES"] = df["NOTES"].apply(lambda s:re.sub("\[[0-9]+\]", "", str(s)))

    if "SUNK DATE" in df.columns:
        df2["SUNK DATE"] = df["SUNK DATE"].apply(convert_date)

    return df2

#arreglem cordenades
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
        return s.replace(" ", "")
    else:
        return ""

# arreglem dates, he provat parsejadors i tots hem peten. matada manual. format dd/mm/YYYY
def convert_date(s):

    months_full = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
   
    s=re.sub("\([A-Za-z]+\)", "", str(s))

    if re.search("[0-9][0-9][0-9][0-9]",s):
        anys=re.search("[0-9][0-9][0-9][0-9]",s).group(0) 
        s=re.sub("[0-9][0-9][0-9][0-9]","",s)
        mes=1 
        dia=1
        if any((match := re.search(mes,s)) for mes in months_full) or any((match2 := re.search(mes,s)) for mes in months_short) :
            if match:
               mes = months_full.index(match.group(0))+1
            else:           
                mes = months_short.index(match2.group(0))+1
                match=match2
            s=re.sub(match.group(0),"",s)
            if re.search("[0-9][0-9] | [0-9]",s):
                dia=re.search("[0-9][0-9] | [0-9]",s).group(0) 

            anys=1 if int(anys) <1 else anys
            mes=1 if int(mes) >12 else mes
            dia=1 if int(dia) >int(calendar.monthrange(int(anys), int(mes))[1]) or int(dia)<1 else dia
            
        return datetime.datetime(int(anys), int(mes), int(dia)).strftime('%d/%m/%Y')

    return ""