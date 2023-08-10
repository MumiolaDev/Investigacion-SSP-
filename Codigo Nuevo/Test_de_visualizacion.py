
import requests
import cdflib
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

#Lista de urls con los datos directo desde la fuente
urls = [
    'https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2023/psp_coho1hr_merged_mag_plasma_20230101_v01.cdf'
]


# Listas de datos con los que quiero trabajar
epoch = np.array([])
radial_distance = np.array([])
heligraphicLatitude = np.array([])
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

for url in urls:
    respuesta = requests.get(url)
    # A CADA URL VOY A SOLICITAR UNA RESPUESTA PARA ASEGURARME DE QUE
    # EL ARCHIVO SE OBTENGA DE MANERA CORRECTA
    if respuesta.status_code == 200:
        
        # Abro los archivos y los escribo en otro
        # archivo temporal para trabajarlo
        with open('tmp.cdf', 'wb') as tmp_file:
            tmp_file.write(respuesta.content)

        # Usando la libreria cdflib, puedo obtener facilmente la data
        cdf = cdflib.CDF('tmp.cdf')

        # ESTOS SON LOS DATOS DE MAYOR INTERES
        zVars = cdf.cdf_info().zVariables
        #print(data)
        #zVars = ['Epoch', 'radialDistance', 'heliographicLatitude', 'heliographicLongitude', 
        # 'BR', 'BT', 'BN', 'B', 'VR', 'VT', 'VN', 'ProtonSpeed', 'flow_theta', 'flow_lon', 
        # 'protonDensity', 'protonTemp']

        # Esta lista contiene las keys para sacar los datos de el archivo temporal
        # Asi puedo guardar las variables por separado

        # Por ahora solo trabajo con 1 set de datos

        epoch =  np.concatenate( (epoch, cdf['Epoch']) ) 
        
        B  = np.concatenate( (B , cdf['B' ] ) )
        BT = np.concatenate( (BT, cdf['BT'] ) )
        BN = np.concatenate( (BN, cdf['BN'] ) )


        print(cdf.cdf_info())

    else:
        print(" URL INVALIDO:  "+url)
        print(respuesta)

print( B.size)
print( BT.size)
print( BN.size)

n_samples = np.arange(B.size)

#B_norm = B / np.sqrt(np.sum(B**2))
#print( B.max())

#plt.plot(n_samples[:100], B[:100], '.')
#plt.ylim([B.min(), B.max()])
#plt.show()