import requests
import cdflib
import pandas as pd
import os
import numpy as np
from bs4 import BeautifulSoup


zVars = ['Epoch', 'radialDistance', 'heliographicLatitude', 'heliographicLongitude', 
             'BR', 'BT', 'BN', 'B', 'VR', 'VT', 'VN', 'ProtonSpeed', 'flow_theta', 'flow_lon', 
             'protonDensity', 'protonTemp']
            # Estos son los datos de interes que estan tomados en intervalos de una hora
            # zVars = cdf.cdf_info().zVariables
            # Esta lista contiene las data_keys para sacar los datos de el archivo temporal
            # Asi puedo guardar las variables por separado


## Con esta funcion obtengo todos los archivos .cdf dentro del directorio url entregado
def Get_CDF_Links(url):
    respuesta = requests.get(url)
    CDF_links = []
    if respuesta.status_code == 200:
        sopa = BeautifulSoup(respuesta.content, 'html.parser')
        links = [ link.get('href') for link in sopa.find_all('a') ]
        for link in links:
            if link.endswith('.cdf'):
                CDF_links.append(os.path.join(url, link))
            elif link.endswith('/'):
                CDF_links.extend(Get_CDF_Links(url+link))
    return CDF_links

def LimpiarDivergencias(datos_cdf):
    datos_limpios = []
    for dat in datos_cdf:
        if abs(dat) < 1e30:
            datos_limpios.append(dat)
        else:
            datos_limpios.append(np.nan)
    
    return datos_limpios

## En esta funcion le entregas las llaves 
## data_keys = ["B", "BT", "BN",...]
## y devuelve un array con los datos separados 
## en el mismo orden que las data_keys
def ObtenerDatas(data_keys, desde= 0, hasta = -1):
    cont = 0
    urls = Get_CDF_Links('https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/')
    tmp_data = [np.array([]) for _ in range(len(data_keys))]
    for url in urls[desde:hasta]:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:


            with open('tmp.cdf', 'wb') as tmp_file:
                tmp_file.write(respuesta.content)

            cdf = cdflib.CDF('tmp.cdf')
            index = 0
            for data_key in data_keys:
                tmp_data[index] = np.concatenate( (tmp_data[index], LimpiarDivergencias(cdf[data_key])) )
                index += 1

            cont += 1
            print( "Meses cargados: ", cont)

    return tmp_data

def ObtenerSingleData(data_key, desde = 0, hasta = -1 ):
    cont = 0
    ## son 12 urls por año menos para el 2023
    urls = Get_CDF_Links('https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/')
    tmp_data = np.array([])
    for url in urls[desde:hasta]:
        respuesta = requests.get(url)
        # A CADA URL VOY A SOLICITAR UNA RESPUESTA PARA ASEGURARME DE QUE
        # EL ARCHIVO SE OBTENGA DE MANERA CORRECTA
        if respuesta.status_code == 200:
            #print(url)
            # Abro los archivos y los escribo en otro
            # archivo temporal para trabajarlo
            with open('tmp.cdf', 'wb') as tmp_file:
                tmp_file.write(respuesta.content)

            # Usando la libreria cdflib, puedo obtener facilmente la data
            cdf = cdflib.CDF('tmp.cdf')
            tmp_data = np.concatenate( (tmp_data, LimpiarDivergencias(cdf[data_key])) )
            cont += 1
            print( "Meses cargados: ", cont)

    #tmp_file.close()
    return tmp_data
