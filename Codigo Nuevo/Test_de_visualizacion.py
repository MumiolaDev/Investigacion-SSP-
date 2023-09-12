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

def LimpiarDivergencias(datos_cdf, tol = 1e30):
    datos_limpios = []
    for dat in datos_cdf:
        
        if np.any(dat) < tol:
            datos_limpios.append(dat)
        else:
            datos_limpios.append(np.nan)

    return datos_limpios

def LimpiarZeros(datos_cdf, tol = 1e-16):
    datos_limpios=[]
    for dat in datos_cdf:
        if np.abs(dat) < tol:
            datos_limpios.append(0)
        else:
            datos_limpios.append(dat)

    return datos_limpios

def GetCDF_info(link):
    respuesta = requests.get(link)
    print('abriendo')
    vars = []
    if respuesta.status_code == 200:
        print('link correcto')
        with open('tmp.cdf', 'wb') as tmp_file:
            print('escribiendo')
            tmp_file.write(respuesta.content)
            cdf = cdflib.CDF('tmp.cdf')
            vars = cdf.zVariables
            cdf.close()

    return vars


## En esta funcion le entregas las llaves 
## data_keys = ["B", "BT", "BN",...]
## y devuelve un array con los datos separados 
## en el mismo orden que las data_keys

def ObtenerDatas(data_keys,
                 desde=0,hasta = -1,
                 link_origen='https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/',
                 carpeta=''):
    
    print('Juntando Links...')
    cont = desde
    urls = Get_CDF_Links(link_origen)
    print(len(urls))
    tmp_data = []
    for url in urls[desde:hasta]:
        filename= carpeta+'\data_'+str(cont)+'.cdf'

        if os.path.isfile(filename):
            cdf = cdflib.CDF(filename)
            index = 0
            if len(tmp_data)==0:
                tmp_data = [np.empty_like(cdf[data_key]) for data_key in data_keys ]
            
            print('Cargando set de datos numero: '+str(cont))
            for data_key in data_keys:
                tmp_data[index] = np.concatenate( (tmp_data[index], cdf[data_key]) )
                index += 1
            cont += 1
        else:
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                with open(filename, 'wb') as tmp_file:
                    print('Descargando set de datos numero: '+str(cont))
                    tmp_file.write(respuesta.content)
                    tmp_file.close()

                cdf = cdflib.CDF(filename)
                #print(cdf.cdf_info().zVariables)
                index = 0
                if len(tmp_data)==0:
                    tmp_data = [np.empty_like(cdf[data_key]) for data_key in data_keys ]
                for data_key in data_keys:
                    tmp_data[index] = np.concatenate( (tmp_data[index], cdf[data_key]) )
                    index += 1
                
                cont += 1
            else:
                print('Link malo')
                return []
        
    return tmp_data
                