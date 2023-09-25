from CargadorDeDatos import *

# URL principal que contiene los subdirectorios
#url_principal = 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/mag_rtn/'
#url_principal = 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l3/sqtn_rfs_v1v2/'
#url_ephemeris = 'https://spdf.gsfc.nasa.gov/pub/data/psp/ephemeris/helio1day/'
url_principal = 'https://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spi/l3/spi_sf00_mom_inst/'

# Directorio donde deseas guardar los archivos descargados
directorio_descargas = 'SWEAP_SPI_proton/'

# Crea el directorio de descargas principal si no existe
os.makedirs(directorio_descargas, exist_ok=True)

# Llama a la función para descargar archivos desde la URL principal (y subdirectorios)
descargar_archivos_desde_url(url_principal, directorio_descargas)

print("Descarga de archivos completada.")
