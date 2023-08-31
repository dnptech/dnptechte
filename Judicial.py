import os
import time
import pandas as pd
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Parámetros de configuración
expedientes_a_procesar = 10  # Cantidad de expedientes a procesar
input_file_path = "db.csv"  # Ruta al archivo CSV con los números de expediente y fechas
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_files")
db_params = {
    "dbname": "public.novedades",
    "user": "noob",
    "password": "noob",
    "host": "localhost",
    "port": "5432"
}

# Función para procesar una clave
def procesar_clave(driver, clave, datos_tabla):
    print(f"Procesando clave: {clave}")  # Mostrar la clave que se está procesando

    url = f'https://eje.juscaba.gob.ar/iol-ui/p/expedientes?identificador={clave}&open=false&tituloBusqueda=Causas&tipoBusqueda=CAU'

    # Abrir la página
    driver.get(url)

    # Esperar a que se cargue el elemento específico
    wait = WebDriverWait(driver, 10)
    elemento_especifico = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="alto-app"]/div[2]/mat-sidenav-container/mat-sidenav-content/div/iol-expediente-lista/div/div/div[2]/iol-expediente-tarjeta/div/iol-expediente-tarjeta-encabezado/div/div[2]/div/a/strong')))
    elemento_especifico.click()

    # Hacer clic en la pestaña de Actuaciones
    pestaña_actuaciones = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mat-tab-label-0-1"]/div')))
    pestaña_actuaciones.click()

    # Restablecer el contador de página para cada clave
    pagina = 1
    while True:
        tabla_filas = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="mat-tab-content-0-1"]/div/iol-expediente-actuaciones/div/div[2]/mat-table/mat-row')))
        
        for fila_index, fila in enumerate(tabla_filas):
            print(f"Página {pagina}, Fila {fila_index + 1}...")  # Mostrar página y fila

            datos_fila = fila.find_elements(By.TAG_NAME, 'mat-cell')
            datos_fila = [dato.text for dato in datos_fila]

            enlace_pdf_elements = fila.find_elements(By.XPATH, './mat-cell[6]/a/i | ./mat-cell[7]/a/i')
            enlaces_pdf_descargados = []

            for enlace_index, enlace_pdf_element in enumerate(enlace_pdf_elements):
                try:
                    # Verificar si el enlace contiene el texto "attach_file"
                    if "attach_file" in enlace_pdf_element.get_attribute("outerHTML"):
                        print("Enlace con adjunto detectado, se ignorará")
                        enlaces_pdf_descargados.append("No se descargará el adjunto")
                        continue
                    
                    print(f"Haciendo clic en el enlace PDF {enlace_index + 1}...")
                    driver.execute_script("arguments[0].click();", enlace_pdf_element)
                    
                    # Esperar un momento antes de cambiar de ventana
                    time.sleep(0.5)
                    
                    # Cambiar a la nueva ventana
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # Esperar a que se abra el cuadro de diálogo de impresión
                    time.sleep(2)
                    
                    # Lógica para descargar el PDF aquí (según tu implementación)

                    # Cerrar la ventana del PDF
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                    print(f"Enlace PDF {enlace_index + 1} descargado")
                    enlaces_pdf_descargados.append("Archivo PDF descargado")
   
                        
                except Exception as e:
                    print(f"Error en el enlace PDF {enlace_index + 1}: {str(e)}")
                    enlaces_pdf_descargados.append("No se pudo obtener la URL")



            datos_fila.extend(enlaces_pdf_descargados)
            datos_tabla.append(datos_fila)
            
        # Fin del bucle existente

        try:
            if len(driver.window_handles) == 1:
                # Esperar a que el botón "Siguiente" sea cliclable
                boton_siguiente = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-tab-content-0-1"]/div/iol-expediente-actuaciones/div/div[2]/mat-paginator/div/div[2]/button[2]')))
                
                # Cambiar el enfoque al elemento
                driver.execute_script("arguments[0].scrollIntoView();", boton_siguiente)
                
                # Hacer clic en el botón "Siguiente"
                boton_siguiente.click()
                
                # Esperar a que la primera fila de la tabla anterior desaparezca
                wait = WebDriverWait(driver, 10)
                wait.until(EC.staleness_of(tabla_filas[0]))
                
                # Agregar una pausa adicional antes de continuar
                time.sleep(2)  # Pausa de 2 segundos
                
                pagina += 1  # Incrementar el contador de página

        except Exception as e:
            # Si no se encuentra el botón "Siguiente" o no es cliclable, salimos del bucle
            break
# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--headless')

options.add_experimental_option('prefs', {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory": output_dir,
    "download.directory_upgrade": True,
    "download.prompt_for_download": False
})
driver = webdriver.Chrome(options=options)

# Leer las claves desde el archivo
claves_file_path = "claves\claves.txt"
with open(claves_file_path, 'r', encoding='utf-8') as f:
    claves = f.read().splitlines()

# Lista para almacenar los datos de la tabla
datos_tabla = []

# Ciclo para procesar cada clave
for clave in claves[:expedientes_a_procesar]:
    procesar_clave(driver, clave, datos_tabla)

# Cerrar el navegador
driver.quit()

# Crear un DataFrame de pandas con los datos de la tabla
df = pd.DataFrame(datos_tabla)

# Conexión a la base de datos PostgreSQL
try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    # Crear la tabla "public.novedades" si no existe
    create_novedades_table_query = """
    CREATE TABLE IF NOT EXISTS public.novedades (
        id SERIAL PRIMARY KEY,
        cuij VARCHAR,
        titulo VARCHAR,
        numero VARCHAR,
        fecha_firma DATE,
        firmantes VARCHAR,
        actuaciones VARCHAR, -- Columna para almacenar el nombre del archivo de actuaciones
        fecha_diligenciamento DATE
    );
    """
    cursor.execute(create_novedades_table_query)
    connection.commit()

    # Ciclo para insertar datos en la tabla "public.novedades"
    for index, row in df.iterrows():
        # Insertar datos en la tabla "public.novedades"
        insert_novedades_query = """
        INSERT INTO public.novedades (cuij, titulo, numero, fecha_firma, firmantes, actuaciones, fecha_diligenciamento)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        values_novedades = (
            row['Clave'],
            row['Título'],
            row['Número'],
            row['Fecha de Firma'],
            row['Firmantes'],
            row['Actuaciones'],  # Nombre del archivo de actuaciones
            row['Fecha de Diligenciamiento']
        )
        cursor.execute(insert_novedades_query, values_novedades)
        inserted_id = cursor.fetchone()[0]

        # Resto del código para renombrar y manejar archivos...

        # Realizar commit después de cada inserción
        connection.commit()

    print("Datos insertados en la tabla 'public.novedades', y archivos PDF renombrados.")

except (Exception, psycopg2.Error) as error:
    print("Error al trabajar con la base de datos:", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("Conexión a la base de datos cerrada.")

print("Proceso completado.")