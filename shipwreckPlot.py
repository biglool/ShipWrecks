#!/usr/bin/env python
# coding: utf-8

# In[72]:


import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd

# Carreguem el dataset en un dataframe de pandas.
df = pd.read_csv('dataset\shipWrecks.csv')

# Creem un nou dataframe amb les columnes que ens interessen per a la visualització.
df2 = df[["SUNK DATE", "COORDINATES"]]

# Eliminem les files amb valors nuls.
df2 = df2.dropna()

# Eliminem els caràcters inapropiats de la columna "COORDINATES".
df2["COORDINATES"] = df2["COORDINATES"].str.replace(" ", '')
df2["COORDINATES"] = df2["COORDINATES"].str.replace("\ufeff", '')

# Separem les coordenades en latitud i longitud, i eliminem la columna "COORDINATES" del dataframe.
df2[["LATITUDE", "LONGITUDE"]] = df2["COORDINATES"].str.split(";", 1, expand=True)
df2 = df2.drop(["COORDINATES"], axis=1)

# Assegurem que totes les dades contingudes a les columnes "LATITUDE" i "LONGITUDE" tenen el format correcte (sense lletres).
df2 = df2[df2["LATITUDE"].str.contains('[a-z]')==False]
df2 = df2[df2["LONGITUDE"].str.contains('[a-z]')==False]

# Eliminem les files que no tenen el format correcte d'any (4 xifres seguides) a la columna "SUNK DATE".
df2 = df2[df2['SUNK DATE'].str.contains('.*\d{4}')]

# Creem una columna "SUNK YEAR" amb només l'any del naufragi, i eliminem la data sencera.
df2['SUNK YEAR'] = df2['SUNK DATE'].str[-4:]
df2 = df2.drop(["SUNK DATE"], axis=1)
df2 = df2[df2["SUNK YEAR"].str.contains('.*\d{4}')==True]

# Passem les columnes de coordinades i d'any a un format numèric per poder-hi treballar.
df2["LATITUDE"] = df2["LATITUDE"].astype(float)
df2["LONGITUDE"] = df2["LONGITUDE"].astype(float)
df2["SUNK YEAR"] = df2["SUNK YEAR"].astype(int)

# Discretitzem l'atribut "SUNK YEAR" per diferenciar els naufragis per segles.
century = ["<XVI", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
df2["SUNK CENTURY"] = pd.cut(df2["SUNK YEAR"],
       bins=[0, 1500, 1600, 1700, 1800, 1900, 2000, 2022], 
       labels= century)

# Carreguem el mapa del món de la llibreria GeoPandas.
countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# Creem un gràfic amb el mapamundi de fons, cada naufragi en les seves coordenades i diferenciat per colors segons el segle.
fig, ax = plt.subplots(figsize=(22,10))
countries.plot(color="lightgrey", ax=ax)
df2.plot(x='LONGITUDE', y='LATITUDE', kind='scatter', c='SUNK CENTURY', s=2, colormap='viridis', ax=ax)

plt.show()

