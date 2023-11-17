from CargadorDeDatos import *
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.colors as colors
import pandas as pd

cdf_campo = obtener_archivos_cdf_en_directorio('FIELDS_1min')
cdf_EPH = obtener_archivos_cdf_en_directorio('EPHEMERIS')
EPH_DAT = pd.DataFrame(cargar_datos_cdf(cdf_EPH, ['Epoch', 'RAD_AU']))
MAG_DAT = cargar_datos_cdf(cdf_campo, ["epoch_mag_RTN_1min", "psp_fld_l2_mag_RTN_1min", 'psp_fld_l2_quality_flags' ])
chunks_Epoch_R     = EPH_DAT['Epoch']
chunks_R        = EPH_DAT['RAD_AU']
chunks_Epoch_B     = MAG_DAT['epoch_mag_RTN_1min']
chunks_Bv         = MAG_DAT['psp_fld_l2_mag_RTN_1min']
chunks_B_qf    = MAG_DAT['psp_fld_l2_quality_flags']


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
SMALL_SIZE =13
MEDIUM_SIZE = 18
BIGGER_SIZE = 25
plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

polinomios_acerc = []
Rs_pol_acerc = []
desv_acerc1 = []
desv_acerc2 = []

polinomios_alej = []
Rs_pol_alej = []
desv_alej1 = []
desv_alej2 = []

################################################################################
####################  ACERCAMIENTOS ###########################################
###############################################################################
for n, fecha_referencia in enumerate(fechas_perihelio_todas):

    tiempo_anterior = fecha_referencia - timedelta(days=40).total_seconds()
    tiempo_posterior = fecha_referencia + timedelta(days=1).total_seconds()

    # Filtrar los "chunks" de EPH_DAT
    indices_filtrados_R, data_filtrada_R = filtrar_chunks(chunks_Epoch_R, chunks_R, tiempo_anterior, tiempo_posterior)

    # Filtrar los "chunks" de SWP_DAT
    indices_filtrados_B, data_filtrada_B = filtrar_chunks(chunks_Epoch_B, chunks_Bv, tiempo_anterior, tiempo_posterior)
    indices_filtrados_flags, data_filtrada_flags = filtrar_chunks(chunks_Epoch_B, chunks_B_qf, tiempo_anterior, tiempo_posterior)

    n_datos= 0
    tmp1 = []
    for i, chunk in enumerate(data_filtrada_B):
        for j, dat in enumerate(chunk):
            if data_filtrada_flags[i][j] == 0: ## 0 significa sin flags
                val = np.sqrt(dat[0]**2 + dat[1]**2 + dat[2]**2)
                if val <= np.sqrt(3)*1e6:
                    tmp1.append(val)
    print( 'Plot: ', n,' procesado con ', len(tmp1), ' totales de datos guardados')

    def yfit(x, poli):
        return np.power(10, poli(np.log10(x)))

    R = np.array(data_filtrada_R[0]) ## al R no es necesario tratarlo ya que contiene un solo chunk
    B = np.array(tmp1)

    R, B = igualar_longitud_arrays(R,B)
    R, B = eliminar_nan_correspondientes(R, B)
    if B.size != 0:
        R_bins = np.logspace(np.log10(np.min(R)), np.log10(np.max(R)), 100)
        B_bins = np.logspace(np.log10(np.min(B)), np.log10(np.max(B)), 100)

        logx = np.log10(R)
        logy = np.log10(B)
        coeffs, V = np.polyfit(logx,logy,deg=1, cov= 'unscaled')
        poly = np.poly1d(coeffs)
        
        polinomios_acerc.append(poly)
        Rs_pol_acerc.append(R)

        desv_acerc1.append(np.sqrt(V[0,0])) #intercepto
        desv_acerc2.append(np.sqrt(V[1,1])) #pendiente
        


i=1
x = []
y1 = []
y2=[]
for p, r in zip(polinomios_acerc, Rs_pol_acerc):
    x.append(i)
    y1.append(p[0])
    y2.append(p[1])
    i+=1 

################################################################################
####################  ALEJAMIENTOS ###########################################
################################################################################
for n, fecha_referencia in enumerate(fechas_perihelio_todas):
    #fecha_referencia = datetime.fromisoformat('2021-04-29').timestamp()
    tiempo_anterior = fecha_referencia - timedelta(days=1).total_seconds()
    tiempo_posterior = fecha_referencia + timedelta(days=40).total_seconds()

    # Filtrar los "chunks" de EPH_DAT
    indices_filtrados_R, data_filtrada_R = filtrar_chunks(chunks_Epoch_R, chunks_R, tiempo_anterior, tiempo_posterior)

    # Filtrar los "chunks" de SWP_DAT
    indices_filtrados_B, data_filtrada_B = filtrar_chunks(chunks_Epoch_B, chunks_Bv, tiempo_anterior, tiempo_posterior)
    indices_filtrados_flags, data_filtrada_flags = filtrar_chunks(chunks_Epoch_B, chunks_B_qf, tiempo_anterior, tiempo_posterior)

    n_datos= 0
    tmp1 = []
    for i, chunk in enumerate(data_filtrada_B):
        for j, dat in enumerate(chunk):
            if data_filtrada_flags[i][j] == 0: ## 0 significa sin flags
                val = np.sqrt(dat[0]**2 + dat[1]**2 + dat[2]**2)
                if val <= np.sqrt(3)*1e6:
                    tmp1.append(val)
    print( 'Plot: ', n,' procesado con ', len(tmp1), ' totales de datos guardados')

    def yfit(x, poli):
        return np.power(10, poli(np.log10(x)))

    R = np.array(data_filtrada_R[0]) ## al R no es necesario tratarlo ya que contiene un solo chunk
    B = np.array(tmp1)

    R, B = igualar_longitud_arrays(R,B)
    R, B = eliminar_nan_correspondientes(R, B)
    if B.size != 0:
        R_bins = np.logspace(np.log10(np.min(R)), np.log10(np.max(R)), 100)
        B_bins = np.logspace(np.log10(np.min(B)), np.log10(np.max(B)), 100)

        logx = np.log10(R)
        logy = np.log10(B)
        coeffs, Vmatrix = np.polyfit(logx,logy,deg=1, cov= 'unscaled')
        poly = np.poly1d(coeffs)
        polinomios_alej.append(poly)
        Rs_pol_alej.append(R)

        desv_alej1.append(np.sqrt(V[0,0])) #intercepto
        desv_alej2.append(np.sqrt(V[1,1])) #pendiente
        

fig, axs = plt.subplots(2,1, figsize=(7,7), sharex=True)

#fig.suptitle('Evolución de los coeficientes encontrados') 
fig.supxlabel('Número de órbita')
fig.supylabel('Coeficiente')


plt.tight_layout()
axs[0].grid(True)
axs[1].grid(True)

i=1
x_alej = []
y1_alej = []
y2_alej = []
for p, r in zip(polinomios_alej, Rs_pol_alej):
    x_alej.append(i)
    y1_alej.append(p[0])
    y2_alej.append(p[1])
    i+=1 

print(desv_acerc1)

axs[0].errorbar(x, y1,  desv_acerc1, linestyle='--', lw=.9, c='black')
axs[0].plot(    x, y1,  'd', label='Intercepto Acercamiento', c='blue')

axs[1].errorbar(x, y2,  desv_acerc2, linestyle='--',lw=.9, c='black')
axs[1].plot(    x, y2,  'o', label='Pendiente Acercamiento', c='blue')

axs[0].errorbar(x_alej, y1_alej, desv_alej1, linestyle='--', lw=.9,c='black')
axs[0].plot(    x_alej, y1_alej,    'd',label='Intercepto Alejamiento', c='red')

axs[1].errorbar(x_alej,y2_alej,desv_alej2, linestyle='--',lw=.9, c='black')
axs[1].plot(x_alej,y2_alej,'o',label='Pendiente Alejamiento', c='red')

axs[0].legend()
axs[1].legend()

fig.subplots_adjust(hspace=0)
plt.tight_layout()
plt.show()
