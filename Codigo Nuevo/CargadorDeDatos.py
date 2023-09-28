import requests
from bs4 import BeautifulSoup
import os
import cdflib
from tqdm import tqdm
from requests.exceptions import ChunkedEncodingError
import numpy as np
from scipy.interpolate import interp1d

def Arreglar(entrada):
    salida = []
    for lista in entrada:
        for dat in lista:
            salida.append(dat)
    return np.array(salida)

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


def seleccionar_datos_en_rango(datos, epoch_datos, tiempo_inicial, tiempo_final):
    """
    Selecciona los datos dentro de un rango de tiempo dado.
    :param datos: Array de datos.
    :param epoch_datos: Array de epoch correspondiente a los datos.
    :param tiempo_inicial: Tiempo inicial del rango deseado.
    :param tiempo_final: Tiempo final del rango deseado.
    :return: Array de datos dentro del rango de tiempo especificado.
    """
    # Encontrar los índices donde los epoch están dentro del rango deseado
    indices_en_rango = np.where((epoch_datos >= tiempo_inicial) & (epoch_datos <= tiempo_final))
    # Seleccionar los datos correspondientes a los índices en rango
    datos_en_rango = datos[indices_en_rango]

    return datos_en_rango


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
    variables_disponibles = []
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
                    
                    if var in ['epoch_mag_RTN_1min', 'Epoch', 'epoch_mag_RTN', 'epoch']:
                        variable = cdflib.cdfepoch.unixtime(archivo_cdf.varget(var))
                        datos_variables[var].append(variable)
                        #datos_variables[var]= np.concatenate(datos_variables[var], variable)
                        ndatos += variable.size
                    else:

                        variable = archivo_cdf.varget(var)
                        datos_variables[var].append(variable)
                        #datos_variables[var]= np.concatenate(datos_variables[var], variable)
                        ndatos += variable.size

        except Exception as e:
            print(f"Error al cargar el archivo {ruta_archivo}: {e}")
            continue  # Continúa con la siguiente iteración en caso de error
        


    return datos_variables

def igualar_longitud_arrays(array1, array2):
    """
    Interpola el primer array para igualar su longitud con el segundo array.
    :param array1: Primer array de datos a interpolar.
    :param array2: Segundo array de datos.
    :return: El primer array interpolado y el segundo array sin cambios.
    """
    len1 = len(array1)
    len2 = len(array2)
    # Crea una funcion de interpolacion 1D para modelar el array 1
    # y = f(x)
    interp_func = interp1d(np.arange(len1), array1, kind='linear')
    array1_interpolado = interp_func(np.linspace(0, len1 - 1, len2))
    
    return array1_interpolado, array2

def eliminar_nan_correspondientes(array1, array2):
    """
    Elimina los valores NaN de dos arrays correspondientes uno a uno.
    :param array1: Primer array de datos.
    :param array2: Segundo array de datos correspondiente al primer array.
    :return: Dos arrays sin los valores NaN correspondientes.
    """
    # Encuentra las posiciones de los valores NaN en ambos arrays
    nan_indices_array1 = np.isnan(array1)
    nan_indices_array2 = np.isnan(array2)
    # Encuentra las posiciones donde al menos uno de los arrays tiene NaN
    nan_indices_combinados = np.logical_or(nan_indices_array1, nan_indices_array2)
    # Elimina los valores NaN de ambos arrays
    array1_sin_nan = array1[~nan_indices_combinados]
    array2_sin_nan = array2[~nan_indices_combinados]

    return array1_sin_nan, array2_sin_nan

def filtrar_datos_por_quality_flag(datos, epoch, quality_flags, quality_flag_aceptado=0):
    """
    Filtra los datos y sus valores de época (epoch) según un quality flag específico.
    Por defecto, se acepta el quality flag con valor 0.

    :param datos: Array de datos.
    :param epoch: Array de valores de época correspondiente a los datos.
    :param quality_flags: Array de quality flags correspondiente a los datos.
    :param quality_flag_aceptado: Valor del quality flag que se desea aceptar (por defecto, 0).
    :return: Dos arrays filtrados, uno con los datos y otro con los valores de época.
    """
    # Encuentra los índices donde el quality flag sea igual al valor aceptado
    indices_aceptados = np.where(quality_flags == quality_flag_aceptado)

    # Filtra los datos y los valores de época según los índices aceptados
    #print(indices_aceptados)
    datos_filtrados = datos[indices_aceptados]
    epoch_filtrados = epoch[indices_aceptados]

    return datos_filtrados, epoch_filtrados