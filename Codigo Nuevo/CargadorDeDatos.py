import requests
from bs4 import BeautifulSoup
import os
import cdflib
from tqdm import tqdm
from requests.exceptions import ChunkedEncodingError


def eliminar_archivo(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# Función recursiva para descargar archivos de una página web con subdirectorios
def descargar_archivos_desde_url(url, download_directory):
    try:
        # Obtener el contenido de la página
        response = requests.get(url)

        # Verifica si la solicitud fue exitosa (código de estado 200)
        if response.status_code == 200:
            # Encuentra todos los enlaces en la página
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            # Obtiene la lista de archivos existentes en el directorio de descargas
            archivos_existentes = os.listdir(download_directory)

            # Itera a través de los enlaces
            print('Comenzando descarga de datos...')
            for link in links:
                # Obtiene el enlace del atributo href
                link_url = link.get('href')

                # Verifica si el enlace es un directorio
                if link_url.endswith('/'):
                    # Construye la URL completa del subdirectorio
                    subdirectory_url = url + link_url
                    # Crea un directorio local para el subdirectorio si no existe
                    subdirectory_name = os.path.basename(subdirectory_url[:-1])
                    subdirectory_path = os.path.join(download_directory, subdirectory_name)
                    os.makedirs(subdirectory_path, exist_ok=True)
                    # Llama recursivamente a la función para explorar el subdirectorio
                    descargar_archivos_desde_url(subdirectory_url, subdirectory_path)

                # Verifica si el enlace es un archivo y no un directorio o enlace a otra página
                elif link_url.endswith(('.cdf')):  # Agrega extensiones de archivos deseadas
                    # Construye la URL completa del archivo
                    file_url = url + link_url
                    # Obtiene el nombre del archivo a partir de la URL
                    file_name = os.path.basename(file_url)
                    
                    # Verifica si el archivo ya existe en el directorio de descargas
                    if file_name not in archivos_existentes:
                        # Descarga el archivo y guárdalo en el directorio del subdirectorio actual
                        file_path = os.path.join(download_directory, file_name)

                        with open(file_path, 'wb') as file:
                            # Realiza la descarga mostrando el progreso y velocidad
                            response = requests.get(file_url, stream=True)
                            total_size = int(response.headers.get('content-length', 0))
                            block_size = 1024  # Puedes ajustar el tamaño del bloque según tus preferencias

                            with open(file_path, 'wb') as file:
                                progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name)
                                for data in response.iter_content(block_size):
                                    file.write(data)
                                    progress_bar.update(len(data))
                                progress_bar.close()

    except ChunkedEncodingError as e:
        # En caso de una interrupción en la conexión, capturamos la excepción y eliminamos el archivo descargado
        print(f"Error de conexión: {e}")
        print(f"Eliminando archivo incompleto: {file_name}")
        eliminar_archivo(file_path)
        # Vuelve a ejecutar el programa desde cero
        descargar_archivos_desde_url(url, download_directory)


def obtener_archivos_cdf_en_directorio(base_directory):
    """
    Genera una lista de todos los archivos CDF en un directorio y sus subdirectorios.

    Args:
        base_directory (str): La ruta al directorio base.

    Returns:
        list: Lista de rutas a los archivos CDF encontrados.
    """
    archivos_cdf = []
    
    for ruta_directorio, _, archivos in os.walk(base_directory):
        for archivo in archivos:
            if archivo.endswith(".cdf"):
                archivo_completo = os.path.join(ruta_directorio, archivo)
                archivos_cdf.append(archivo_completo)
    
    return archivos_cdf



def cargar_datos_cdf(archivos, variables_interes):
    """
    Carga datos de archivos CDF y filtra por variables de interés y rango de tiempo.

    Args:
        archivos (list): Lista de rutas a los archivos CDF.
        variables_interes (list): Lista de nombres de variables de interés.
        inicio_tiempo (float): Tiempo de inicio del rango de interés (segundos).
        fin_tiempo (float): Tiempo de finalización del rango de interés (segundos).

    Returns:
        dict: Un diccionario que contiene los datos de las variables de interés.
    """
    # Diccionario para almacenar los datos de las variables
    datos_variables = {var: [] for var in variables_interes}

    # Iterar a través de los archivos CDF con una barra de progreso
    ndatos = 0
    for ruta_archivo in tqdm(archivos, desc="Cargando archivos"):
        try:
            archivo_cdf = cdflib.CDF(ruta_archivo)

            # Obtener las variables disponibles en el archivo
            variables_disponibles = archivo_cdf.cdf_info().zVariables

            # Verificar si las variables de interés están presentes en el archivo
            for var in variables_interes:
                if var in variables_disponibles:
                    
                    if var in ['epoch_mag_RTN_1min', 'Epoch', 'epoch_mag_RTN']:
                        variable = cdflib.cdfepoch.unixtime(archivo_cdf.varget(var))
                        datos_variables[var].append(variable)
                    else:

                        variable = archivo_cdf.varget(var)
                        datos_variables[var].append(variable)


        except Exception as e:
            print(f"Error al cargar el archivo {ruta_archivo}: {e}")
            continue  # Continúa con la siguiente iteración en caso de error

    print('Datos totales:', ndatos)

    return datos_variables


