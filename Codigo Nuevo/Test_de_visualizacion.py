import requests
import cdflib
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from bs4 import BeautifulSoup

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

# List con todos los links que me interesan
urls = Get_CDF_Links('https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/')

# Listas de datos con los que quiero trabajar
epoch = np.array([])
radial_distance = np.array([])
heliographicLatitude = np.array([])
heliographicLongitude = np.array([])

BR = np.array([])
BT = np.array([])
BN = np.array([])
B = np.array([])
VR = np.array([])
VT = np.array([])
VN = np.array([])

ProtonSpeed = np.array([])
flow_theta = np.array([])
flow_ion = np.array([])
protonDensity = np.array([])
protonTemp = np.array([])

def LimpiarDivergencias(datos_cdf):
    datos_limpios = []
    for dat in datos_cdf:
        if abs(dat) < 9999:
            datos_limpios.append(dat)
        else:
            datos_limpios.append(np.nan)
    
    return datos_limpios

cont = 0
## son 12 urls por año menos para el 2023
for url in urls[26:30]:
    respuesta = requests.get(url)
    # A CADA URL VOY A SOLICITAR UNA RESPUESTA PARA ASEGURARME DE QUE
    # EL ARCHIVO SE OBTENGA DE MANERA CORRECTA
    if respuesta.status_code == 200:
        print(url)
        # Abro los archivos y los escribo en otro
        # archivo temporal para trabajarlo
        with open('tmp.cdf', 'wb') as tmp_file:
            tmp_file.write(respuesta.content)

        # Usando la libreria cdflib, puedo obtener facilmente la data
        cdf = cdflib.CDF('tmp.cdf')

        # Estos son los datos de interes que estan tomados en intervalos de una hora
        # zVars = cdf.cdf_info().zVariables
    
        # zVars = ['Epoch', 'radialDistance', 'heliographicLatitude', 'heliographicLongitude', 
        # 'BR', 'BT', 'BN', 'B', 'VR', 'VT', 'VN', 'ProtonSpeed', 'flow_theta', 'flow_lon', 
        # 'protonDensity', 'protonTemp']

        # Esta lista contiene las keys para sacar los datos de el archivo temporal
        # Asi puedo guardar las variables por separado

        # Por ahora solo trabajo con 1 set de datos
        
        #epoch = np.concatenate( (epoch, LimpiarDivergencias( cdf['Epoch'])) )
        #B  = np.concatenate( (B , LimpiarDivergencias(  cdf['B' ] ) ) )
        #BT = np.concatenate( (BT, cdf['BT'] ) )
        #BN = np.concatenate( (BN, cdf['BN'] ) )
        radial_distance = np.concatenate( (radial_distance,   LimpiarDivergencias(cdf['radialDistance'])) )
        heliographicLongitude = np.concatenate( (heliographicLongitude,   LimpiarDivergencias(cdf['heliographicLongitude'])) )
        heliographicLatitude = np.concatenate( (heliographicLatitude,   LimpiarDivergencias(cdf['heliographicLatitude'])) )

        cont += 1
        print( "Meses cargados: ", cont)

    else:
        print(" URL INVALIDO:  "+url)
        print(respuesta)

heliographicLatitude = np.radians(heliographicLatitude)
heliographicLongitude = np.radians(heliographicLongitude)

#plt.polar(heliographicLongitude, radial_distance, '--')
#print(heliographicLongitude.max(),heliographicLongitude.min())
plt.plot(np.arange(heliographicLongitude.size), heliographicLongitude)
#x_val = radial_distance*np.sin(heliographicLatitude)*np.cos(heliographicLongitude)
#y_val = radial_distance*np.sin(heliographicLatitude)*np.sin(heliographicLongitude)
#z_val = radial_distance*np.cos(heliographicLatitude)

#fig = plt.figure()

#ax = fig.add_subplot(111, projection='3d')
#ax.plot(x_val,y_val,z_val)
#ax.set_xlabel('X')
#ax.set_ylabel('Y')
#ax.set_zlabel('Z')
#ax.scatter(0, 0,  color='yellow', s=100, label='Sol')
plt.show()
