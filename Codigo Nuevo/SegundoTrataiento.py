from Test_de_visualizacion import *
import matplotlib.pyplot as plt
import numpy as np

from scipy.interpolate import interp1d

def ajustar_tamano(lista, nuevo_tamano):
    # Crear una función interpolante a partir de los datos de distancia
    interpolante = interp1d(np.arange(len(lista)), lista, kind='linear')
    
    # Calcular las nuevas distancias radiales interpoladas
    nuevos_indices = np.linspace(0, len(lista) - 1, nuevo_tamano)
    nuevas_distancias = interpolante(nuevos_indices)
    
    return nuevas_distancias

def limpiar_valores_invalidos(array, valor_minimo_valido, valor_maximo_valido):
    # Crear una copia del array original para no modificarlo
    array_limpio = array.copy()
    
    # Aplicar una máscara booleana para identificar los valores fuera del rango válido
    mascara_invalidos = (array_limpio < valor_minimo_valido) | (array_limpio > valor_maximo_valido)
    
    # Reemplazar los valores fuera del rango válido por np.nan
    array_limpio[mascara_invalidos] = np.nan
    
    return array_limpio

eph_link = ''
field_mag_link ='https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/mag_rtn/2020/'

fields_data = ObtenerDatas(data_keys=['epoch_mag_RTN', 'psp_fld_l2_mag_RTN', 'psp_fld_l2_mag_RTN_MET',
                                      'psp_fld_l2_mag_RTN_range', 'psp_fld_l2_mag_RTN_mode', 'psp_fld_l2_mag_RTN_rate'
                                      ,'psp_fld_l2_mag_RTN_packet_index'],
                           desde = 0, hasta=100,  link_origen=field_mag_link,
                            carpeta="Codigo Nuevo\FIELDS")

eph_data = ObtenerDatas(data_keys=['Epoch', 'RAD_AU'], desde=0, hasta=1, link_origen='https://spdf.gsfc.nasa.gov/pub/data/psp/ephemeris/helio1day/',
                        carpeta='Codigo Nuevo\EPHEMERIDES')


epoch_eph = eph_data[0]
rad = limpiar_valores_invalidos(eph_data[1], 0.1, 100.0)
rad = rad[ np.where(~np.isnan(rad))  ]

Bv = fields_data[1]
MET = limpiar_valores_invalidos(fields_data[2],0, 1.2623e9)
BR = limpiar_valores_invalidos(Bv[:,0], -65537.0, 65537.0)
BT = limpiar_valores_invalidos(Bv[:,1], -65537.0, 65537.0) 
BN = limpiar_valores_invalidos(Bv[:,2], -65537.0, 65537.0)
B = np.sqrt( BR**2+BT**2+BN**2 )
valid_indices = np.where(~np.isnan(MET) & ~np.isnan(B))
valid_MET = MET[valid_indices]
valid_B = B[valid_indices]

#rad = ajustar_tamano(rad, len(valid_B))

