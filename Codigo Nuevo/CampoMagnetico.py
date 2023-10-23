from CargadorDeDatos import *
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.colors as colors

cdf_campo = obtener_archivos_cdf_en_directorio('FIELDS_1min')
cdf_EPH = obtener_archivos_cdf_en_directorio('EPHEMERIS')
#cdf_proton = obtener_archivos_cdf_en_directorio('SWEAP_SPC_proton')

EPH_DAT = cargar_datos_cdf(cdf_EPH, ['Epoch', 'RAD_AU'])
MAG_DAT = cargar_datos_cdf(cdf_campo, ["epoch_mag_RTN_1min", "psp_fld_l2_mag_RTN_1min", 'psp_fld_l2_quality_flags' ])
#SWP_DAT = cargar_datos_cdf(cdf_proton, ['Epoch','vp_moment_RTN','np_moment', 'wp_moment'  ])

Epoch_R     = Arreglar(EPH_DAT['Epoch'])
R_original         = Arreglar(EPH_DAT['RAD_AU'])
Epoch_B     = Arreglar(MAG_DAT['epoch_mag_RTN_1min'])
Bv         = Arreglar(MAG_DAT['psp_fld_l2_mag_RTN_1min'])
B_qf    = Arreglar(MAG_DAT['psp_fld_l2_quality_flags'])
#Epoch_P     = Arreglar(SWP_DAT['Epoch'])
#V_p         = Arreglar(SWP_DAT['vp_moment_RTN'])
#n_p         = Arreglar(SWP_DAT['np_moment'] )
#T_p         = Arreglar(SWP_DAT['wp_moment'] )


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

# Define la duración de la vecindad de tiempo alrededor de cada perihelio (3 meses en segundos)
ventana_temporal = 14* 24 * 60 * 60  # 7 dias en segundos
# Crear una lista de rangos de tiempo alrededor de cada perihelio
rangos_de_tiempo = []
for perihelio in fechas_perihelio_todas:
    inicio = perihelio - ventana_temporal / 2
    final = perihelio + ventana_temporal / 2
    rangos_de_tiempo.append((inicio, final))

INICIO = datetime.fromisoformat('2023-01-01').timestamp()
FINAL = datetime.fromisoformat('2024-01-01').timestamp()

B_original=[]
for i, dat in enumerate(Bv):
    B_original.append(np.sqrt(dat[0]**2 + dat[1]**2 + dat[2]**2))
B_original = np.array(B_original)

polinomios = []
Rs_del_pol = []
def yfit(x, poli):
    return np.power(10, poli(np.log10(x)))
    #return poly(np.log10(x))

fig, axs = plt.subplots(3,5,figsize=(13,16), sharex=True,sharey=True)


for i, (inicio,final) in enumerate(rangos_de_tiempo):

    a = i//5
    b = i%5

    print(i, a,b)
    ax = axs[a,b]

    R = seleccionar_datos_en_rango(R_original, Epoch_R, inicio, final)
    B = seleccionar_datos_en_rango(B_original, Epoch_B, inicio, final)

    R, B = igualar_longitud_arrays(R,B)
    R, B = eliminar_nan_correspondientes(R, B)

    R_bins = np.logspace(np.log10(np.min(R)), np.log10(np.max(R)), 100)
    B_bins = np.logspace(np.log10(np.min(B)), np.log10(np.max(B)), 100)

    logx = np.log10(R)
    logy = np.log10(B)
    coeffs = np.polyfit(logx,logy,deg=1)
    poly = np.poly1d(coeffs)
    polinomios.append(poly)
    Rs_del_pol.append(R)

    fecha = datetime.fromtimestamp(fechas_perihelio_todas[i])
    
    ax.plot(R, yfit(R, poly), '--', label=str(poly), c='black'  )
    ax.hist2d(R, B, bins=(R_bins, B_bins), norm= colors.LogNorm(), cmap='plasma', density=True)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(str(fecha.date()))
    #ax.legend()
    
    if i in [0,5,10]:
        ax.set_ylabel('B nT')
    
    if i in [10,11,12,13,14]:
        ax.set_xlabel('R AU')
    
    #ax.set_xlim(0.08, 0.5)

plt.suptitle('Histogramas por acercamiento')
#plt.tight_layout()

plt.show()

plt.figure(figsize=(12,9))
plt.title('Evolución de las pendientes encontradas')
plt.xlabel('N° Acercamiento')
plt.ylabel('Pendiente recta ajustada')
i=1
fechas = [] 
y = []
for p, t in zip(polinomios, fechas_perihelio_todas):
    #print(p[0], p[1], p)
    fechas.append(datetime.fromtimestamp(t))
    y.append(p[1])
    i+=1 
plt.plot(fechas, y, '--') 
#plt.xscale('log')
#plt.yscale('log')
plt.legend()
plt.show()

plt.figure(figsize=(12,9))
plt.title('Evolución de los interceptos encontradas') 
plt.xlabel('Fecha de acercamiento')
plt.ylabel('Intercepto recta ajustada')
i=1
x = []
y = []
for p, r in zip(polinomios, Rs_del_pol):
    #print(p[0], p[1], p)
    x.append(i)
    y.append(p[0])
    i+=1
plt.plot(fechas, y, '--')
#plt.xscale('log')
#plt.yscale('log')
plt.legend()
plt.show()