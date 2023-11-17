from CargadorDeDatos import *
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.colors as colors
import pandas as pd

cdf_campo = obtener_archivos_cdf_en_directorio('FIELDS_1min')
cdf_EPH = obtener_archivos_cdf_en_directorio('EPHEMERIS')

EPH_DAT = pd.DataFrame(cargar_datos_cdf(cdf_EPH, ['Epoch', 'RAD_AU','HGI_LAT', 'HGI_LON']))
MAG_DAT = cargar_datos_cdf(cdf_campo, ["epoch_mag_RTN_1min", "psp_fld_l2_mag_RTN_1min", 'psp_fld_l2_quality_flags' ])

chunks_Epoch_R     = EPH_DAT['Epoch']
chunks_R        = EPH_DAT['RAD_AU']
chunks_latitud = EPH_DAT['HGI_LAT']
chunks_longitud = EPH_DAT['HGI_LON']

chunks_Epoch_B     = MAG_DAT['epoch_mag_RTN_1min']
chunks_Bv         = MAG_DAT['psp_fld_l2_mag_RTN_1min']
chunks_B_qf    = MAG_DAT['psp_fld_l2_quality_flags']

ref = datetime.fromisoformat('2022-02-25').timestamp()
tiempo_anterior = ref-timedelta(days=45).total_seconds()
tiempo_posterior = ref+timedelta(days=45).total_seconds()

# Filtrar los "chunks" de EPH_DAT
indices_filtrados_R, data_filtrada_Epoch = filtrar_chunks(chunks_Epoch_R, chunks_Epoch_R, tiempo_anterior, tiempo_posterior)
indices_filtrados_R, data_filtrada_R = filtrar_chunks(chunks_Epoch_R, chunks_R, tiempo_anterior, tiempo_posterior)
indices_filtrados_latit, datafiltrados_latit = filtrar_chunks(chunks_Epoch_R,chunks_latitud, tiempo_anterior, tiempo_posterior)
indices_filtrados_longitud, datafiltrados_longitud = filtrar_chunks(chunks_Epoch_R,chunks_longitud, tiempo_anterior, tiempo_posterior)

# Filtrar los "chunks" de FIELDS
indices_filtrados_B, data_filtrada_Epoch_B = filtrar_chunks(chunks_Epoch_B, chunks_Epoch_B, tiempo_anterior, tiempo_posterior)
indices_filtrados_B, data_filtrada_B = filtrar_chunks(chunks_Epoch_B, chunks_Bv, tiempo_anterior, tiempo_posterior)
indices_filtrados_flags, data_filtrada_flags = filtrar_chunks(chunks_Epoch_B, chunks_B_qf, tiempo_anterior, tiempo_posterior)

SMALL_SIZE =9
MEDIUM_SIZE = 11
BIGGER_SIZE = 14
plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


##  Pasar todo a una lista larga e igualar los tamaños
B=[]
Bmag = []
tiempo_B = []
for i, chunk in enumerate(data_filtrada_B):
    for j, dat in enumerate(chunk):
        try:
            if data_filtrada_flags[i][j] == 0:
                tmp = []
                tmp.append(dat[0])
                tmp.append(dat[1])
                tmp.append(dat[2])

                Bmag.append( np.sqrt(tmp[0]**2 + tmp[1]**2 + tmp[2]**2) )
                B.append(tmp)

                tiempo_B.append(data_filtrada_Epoch_B[i][j])
        except:
            continue

R = data_filtrada_R[0]
LAT = datafiltrados_latit[0]
LON = datafiltrados_longitud[0]

#R  , B=igualar_longitud_arrays(data_filtrada_R[0],B)
#LAT, B = igualar_longitud_arrays(datafiltrados_latit[0],B)
#LON, B = igualar_longitud_arrays(datafiltrados_longitud[0],B)

t_pos = np.array(data_filtrada_Epoch[0])
R = np.array(R)
LAT = np.array(LAT)
LON = np.array(LON)

tiempo_B = np.array(tiempo_B)
B = np.array(B)
Bmag = np.array(Bmag)

fig, axs = plt.subplots(4,1,figsize=(6,6),sharex=True)

axs[0].plot(t_pos,R,'.', label='Distancia Radial', c='black',ms=3)
axs[0].set_ylabel('R  AU')
axs[0].legend()

axs[1].plot(t_pos,LAT,'.', label='Latitud heliografica', c='black',ms=3)
axs[1].set_ylabel('Lat °')
axs[1].legend()

axs[2].plot(t_pos,LON,'.', label='Longitud heliografica', c='black',ms=3)
axs[2].set_ylabel('Lon °')
axs[2].legend()

axs[3].plot(tiempo_B, Bmag,',', label='Magnitud Campo Magnético', c='black')
axs[3].set_ylabel('B nT')
axs[3].legend()


my_ticks = np.linspace(np.min(t_pos), np.max(t_pos), 5)
my_labels = [datetime.fromtimestamp(elem).date() for elem in my_ticks]
axs[3].set(xticks = my_ticks, xticklabels=my_labels)
axs[3].tick_params(axis='x', labelrotation=25)

print(tiempo_B.shape, Bmag.shape)

plt.show()
