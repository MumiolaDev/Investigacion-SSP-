from CargadorDeDatos import *
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.colors as colors
from scipy.interpolate import interp1d

archivos_cdf_campo = obtener_archivos_cdf_en_directorio('FIELDS_1min')
archivos_cdf_pos = obtener_archivos_cdf_en_directorio('EPHEMERIS')

variables_interes_campo = ["epoch_mag_RTN_1min", "psp_fld_l2_mag_RTN_1min", 'psp_fld_l2_quality_flags']
variables_interes_pos = ['Epoch', 'RAD_AU' ]

datos_cargados_campo = cargar_datos_cdf(archivos_cdf_campo, variables_interes_campo)
datos_cargados_pos = cargar_datos_cdf( archivos_cdf_pos, variables_interes_pos)

epoch_campo = datos_cargados_campo['epoch_mag_RTN_1min'].copy()
datos_campo = datos_cargados_campo['psp_fld_l2_mag_RTN_1min'].copy()

epoch_pos = datos_cargados_pos['Epoch'].copy()
datos_pos = datos_cargados_pos['RAD_AU'].copy()


## Dado un inicio y un final el siguiente codigo
## crea un histograma de campo magnético en funcion de la distancia rdial

epoch_R = epoch_pos[0]
epoch_B = []
R = datos_pos[0]
B = []

for lista1 in epoch_campo:
    if type(lista1) != float:
        
        for t in lista1:
            epoch_B.append(t)
            #print(datetime.fromtimestamp(t))

for lista2 in datos_campo:
    for b in lista2:
        tmp = np.sqrt( b[0]**2 + b[1]**2 + b[2]**2 )

        B.append(tmp)

epoch_B = np.array(epoch_B)
B = np.array(B)

fechas_perihelio = [datetime.fromisoformat('2022-09-06').timestamp(),
                   datetime.fromisoformat('2022-12-11').timestamp(),
                   datetime.fromisoformat('2023-03-17').timestamp(),
                   ]
fechas_perihelio_str = [datetime.fromisoformat('2022-09-06'),
                   datetime.fromisoformat('2022-12-11'),
                   datetime.fromisoformat('2023-03-17'),
                   
                   ]

fechas_perihelio_todas = [
    datetime.fromisoformat('2018-11-05').timestamp(),#1-2
    datetime.fromisoformat('2019-04-04').timestamp(), #2-3
    datetime.fromisoformat('2019-09-01').timestamp(), #3-4
    datetime.fromisoformat('2020-01-29').timestamp(),# 4-5
    datetime.fromisoformat('2020-06-07').timestamp(), #5-6
    datetime.fromisoformat('2020-09-27').timestamp(), # 6-7
    datetime.fromisoformat('2021-01-17').timestamp(),  # 7-8
    datetime.fromisoformat('2021-04-29').timestamp(),  #8-9
    datetime.fromisoformat('2021-08-09').timestamp(), # 9 -10
    datetime.fromisoformat('2021-11-21').timestamp(),# 10 -11
    datetime.fromisoformat('2022-02-25').timestamp(), # 11 -12
    datetime.fromisoformat('2022-06-01').timestamp(),  # 12 - 13
    datetime.fromisoformat('2022-09-06').timestamp(), # 13 -14
    datetime.fromisoformat('2022-12-11').timestamp()# 14 -15
    #datetime.fromisoformat('2023-03-17').timestamp(),# 14 -15
]
# Define la duración de la vecindad de tiempo alrededor de cada perihelio (3 meses en segundos)
ventana_temporal = 7* 24 * 60 * 60  # 3 meses en segundos
# Crear una lista de rangos de tiempo alrededor de cada perihelio
rangos_de_tiempo = []

#for perihelio in fechas_perihelio_todas:
#    inicio = perihelio - ventana_temporal / 2
#    final = perihelio + ventana_temporal / 2
#    rangos_de_tiempo.append((inicio, final))



rangos_de_tiempo = [
    (datetime.fromisoformat('2022-01-01').timestamp(),datetime.fromisoformat('2023-01-01').timestamp()),#1-2
    (datetime.fromisoformat('2023-01-01').timestamp(),datetime.fromisoformat('2023-04-30').timestamp())
 ] #2-3

polinomios = []

def yfit(x):
    #return np.power(10, poly(np.log10(x)))
    return poly(np.log10(x))

fig, axs = plt.subplots(1, 2, figsize=(13,6) )

for i, (inicio, final) in enumerate(rangos_de_tiempo):
    # Filtrar datos según el rango de tiempo
    indice_inicio_R = np.argmax(epoch_R >= inicio)
    indice_final_R = np.argmax(epoch_R >= final)
    indice_inicio_B = np.argmax(epoch_B >= inicio)
    indice_final_B = np.argmax(epoch_B >= final)

    R_filtrados = R[indice_inicio_R:indice_final_R]
    epoch_R_filtrados = epoch_R[indice_inicio_R:indice_final_R]
    B_filtrados = B[indice_inicio_B:indice_final_B]
    epoch_B_filtrados = epoch_B[indice_inicio_B:indice_final_B]
    
    interp_func = interp1d(np.arange(len(R_filtrados)), R_filtrados, kind='linear')
    R_interpolados = interp_func(np.linspace(0, len(R_filtrados) - 1, len(B_filtrados)))

    valid_indices = np.where(~np.isnan(R_interpolados) & ~np.isnan(B_filtrados))
    #print(len(R_interpolados), len(B_filtrados))
    valid_R = R_interpolados[valid_indices]
    valid_B = B_filtrados[valid_indices]

    R_min, R_max = np.min(valid_R), np.max(valid_R)
    B_min, B_max = np.min(valid_B), np.max(valid_B)
    R_bins = np.logspace(np.log10(R_min), np.log10(R_max), 100)
    B_bins = np.logspace(np.log10(B_min), np.log10(B_max), 100)
    
    logx = np.log10(valid_R)
    logy = np.log10(valid_B)
    coeffs = np.polyfit(logx,logy,deg=1)
    poly = np.poly1d(coeffs)


    #polinomios.append(( datetime.fromtimestamp(fechas_perihelio_todas[i]),  poly.coefficients))

    # Selecciona el subplot actual
    ax = axs[i%2]
    #Crea el gráfico en el subplot actual
    h, xedges, yedges, im = ax.hist2d(valid_R, valid_B, bins=(R_bins, B_bins), norm=colors.LogNorm(), cmap='plasma', density=True)
    #ax.plot(valid_R, yfit(valid_R), '--', label=str(poly), c='black')
    ax.set_ylabel('B  nT')
    ax.set_xlabel('R  AU')
    ax.set_title( 'Año '+str(2022+i))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.tick_params(axis='x', direction = 'in', which='both', labelrotation=25, labelsize = 8)
    #ax.legend()
    plt.colorbar(im, ax=ax)
# Ajusta la disposición de los subplots y muestra la figura
plt.tight_layout()

plt.show()

for (fecha, [m , b]) in polinomios:
    print(fecha.date(), m, b) 
