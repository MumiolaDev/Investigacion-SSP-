from CargadorDeDatos import *
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.colors as colors
import pandas as pd

cdf_EPH = obtener_archivos_cdf_en_directorio('EPHEMERIS')
cdf_proton = obtener_archivos_cdf_en_directorio('SWEAP_SPC_proton')

EPH_DAT = pd.DataFrame(cargar_datos_cdf(cdf_EPH, ['Epoch', 'RAD_AU']))
SWP_DAT = pd.DataFrame(cargar_datos_cdf(cdf_proton, ['Epoch','vp_moment_RTN','np_moment', 'wp_moment', 'general_flag'  ]))

Chunks_epoch_R = EPH_DAT['Epoch']
Chunks_R = EPH_DAT['RAD_AU']

Chunks_epoch_P = SWP_DAT['Epoch']
Chunks_Vp = SWP_DAT['vp_moment_RTN']
Chunks_flags_swp = SWP_DAT['general_flag']

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
    datetime.fromisoformat('2022-12-11').timestamp(),# 14 -15
    datetime.fromisoformat('2023-03-17').timestamp(),# 15
]

polinomios = []
Rs_del_pol = []
for fecha_referencia in fechas_perihelio_todas:
    #fecha_referencia = datetime.fromisoformat('2021-04-29').timestamp()
    tiempo_anterior = fecha_referencia - timedelta(days=7).total_seconds()
    tiempo_posterior = fecha_referencia + timedelta(days=7).total_seconds()

    # Filtrar los "chunks" de EPH_DAT
    indices_filtrados_R, data_filtrada_R = filtrar_chunks(Chunks_epoch_R, Chunks_R, tiempo_anterior, tiempo_posterior)

    # Filtrar los "chunks" de SWP_DAT
    indices_filtrados_P, data_filtrada_Vp = filtrar_chunks(Chunks_epoch_P, Chunks_Vp, tiempo_anterior, tiempo_posterior)
    indices_filtrados_flags_swp, data_filtrada_flags_swp = filtrar_chunks(Chunks_epoch_P, Chunks_flags_swp, tiempo_anterior, tiempo_posterior)

    n_datos= 0
    tmp1 = []
    for i, chunk in enumerate(data_filtrada_Vp):
        for j, dat in enumerate(chunk):
            if data_filtrada_flags_swp[i][j] == 0:
                val = np.sqrt(dat[0]**2 + dat[1]**2 + dat[2]**2)
                if val <= np.sqrt(3)*1e3:
                    tmp1.append(val)
        print( 'chunk: ', i,' procesado con ', len(tmp1), ' totales de datos guardados')


    def yfit(x, poli):
        return np.power(10, poli(np.log10(x)))


    R = np.array(data_filtrada_R[0])
    Vp = np.array(tmp1)

    R, Vp = igualar_longitud_arrays(R,Vp)
    R, Vp = eliminar_nan_correspondientes(R, Vp)

    if Vp.size != 0:
        R_bins = np.logspace(np.log10(np.min(R)), np.log10(np.max(R)), 100)
        Vp_bins = np.logspace(np.log10(np.min(Vp)), np.log10(np.max(Vp)), 100)

        logx = np.log10(R)
        logy = np.log10(Vp)
        coeffs = np.polyfit(logx,logy,deg=1)
        poly = np.poly1d(coeffs)
        polinomios.append(poly)
        Rs_del_pol.append(R)

        plt.figure(figsize=(7,10))
        plt.plot(R, yfit(R, poly), '--', label=str(poly), c='black'  )
        plt.hist2d(R, Vp, bins=(R_bins, Vp_bins), norm= colors.LogNorm(), cmap='plasma', density=True)
        plt.title(f"Fecha de Perihelio: {datetime.fromtimestamp(fecha_referencia).date()}")
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('R  AU')
        plt.ylabel('Velocidad Protones  km/s')
        date = datetime.fromtimestamp(fecha_referencia).date()
        plt.savefig(f'VelocidadProtones_vs_R_Acercamiento_{date}.png')


plt.figure(figsize=(12,9))
plt.title('Evolución de las pendientes encontradas')
plt.xlabel('N° Acercamiento')
plt.ylabel('Pendiente recta ajustada')
i=1
fechas = [] 
y = []
for p, t in zip(polinomios, fechas_perihelio_todas):
    fechas.append(datetime.fromtimestamp(t))
    y.append(p[1])
    i+=1 
plt.plot(fechas, y, '--') 
plt.show()

plt.figure(figsize=(12,9))
plt.title('Evolución de los interceptos encontradas') 
plt.xlabel('Fecha de acercamiento')
plt.ylabel('Intercepto recta ajustada')
i=1
x = []
y = []
for p, r in zip(polinomios, Rs_del_pol):
    x.append(i)
    y.append(p[0])
    i+=1
plt.plot(fechas, y, '--')
plt.show()