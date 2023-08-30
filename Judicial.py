from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

script_folder = os.path.dirname(os.path.abspath(__file__))

def upload_to_google_drive(file_path, folder_id):
    SERVICE_ACCOUNT_FILE = 'token.json'
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])
    drive_service = build('drive', 'v3', credentials=creds)

    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path)

    uploaded_file = drive_service.files().create(
        body=file_metadata, media_body=media, fields='id,webViewLink').execute()

    file_url = uploaded_file['webViewLink']

    drive_service.permissions().create(
        fileId=uploaded_file['id'], body={'role': 'reader', 'type': 'anyone'}).execute()

    return file_url

# Función para procesar una clave
def procesar_clave(driver, clave, datos_tabla, pdf_urls):
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
                    
                    # Subir el archivo PDF a Google Drive y obtener la URL
                    pdf_file_list = [f for f in os.listdir(script_folder) if f.endswith('.pdf')]
                    if pdf_file_list:
                        latest_pdf_name = max(pdf_file_list, key=os.path.getctime)
                        pdf_file_path = os.path.join(script_folder, latest_pdf_name)
                        pdf_url = upload_to_google_drive(pdf_file_path, folder_id)
                        pdf_urls.append(pdf_url)  # Agregar la URL a la lista
                        print(f"Se ha subido el PDF '{latest_pdf_name}' a Google Drive.")
                        print(f"URL del PDF en Google Drive: {pdf_url}")
                        os.remove(pdf_file_path)  # Eliminar el archivo PDF después de subirlo
                        time.sleep(2)  # Pausa adicional después de subir y obtener la URL
                        
                except Exception as e:
                    print(f"Error en el enlace PDF {enlace_index + 1}: {str(e)}")
                    enlaces_pdf_descargados.append("No se pudo obtener la URL")
                
                # Agregar un retraso entre interacciones
                time.sleep(0.5)

            while len(enlaces_pdf_descargados) < len(enlace_pdf_elements):
                enlaces_pdf_descargados.append("No se pudo obtener la URL")

            datos_fila.extend(enlaces_pdf_descargados)
            datos_tabla.append(datos_fila)
            
        # Fin del bucle existente

        try:
            if len(driver.window_handles) == 1:  # Verificar si solo hay una ventana abierta
                # Intentar hacer clic en el botón "Siguiente" en la paginación
                boton_siguiente = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-tab-content-0-1"]/div/iol-expediente-actuaciones/div/div[2]/mat-paginator/div/div[2]/button[2]')))
                boton_siguiente.click()
                wait.until(EC.staleness_of(tabla_filas[0]))  # Esperar a que la primera fila de la tabla anterior desaparezca
                
                # Agregar una pausa adicional antes de continuar
                time.sleep(2)  # Pausa de 2 segundos
                
                pagina += 1  # Incrementar el contador de página

        except Exception as e:
            # Si no se encuentra el botón "Siguiente" o no es cliclable, salimos del bucle
            break

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_experimental_option('prefs', {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory": script_folder,
    "download.directory_upgrade": True,
    "download.prompt_for_download": False
})
driver = webdriver.Chrome(options=options)

# Carpeta del script
script_folder = os.path.dirname(os.path.abspath(__file__))

# ID de la carpeta de Google Drive
folder_id = '15rTTOntWlgzxzlnQOGTQV9YbD5pv0FyY'

# Lista de claves desde el archivo
with open('claves/claves.txt', 'r') as f:
    claves = f.read().splitlines()

# Lista para almacenar los datos de la tabla y las URLs de PDFs
datos_tabla = []
pdf_urls = []


# Ciclo para procesar cada clave
pdf_urls_indices = []  # List to store the indices of rows with PDF URLs
for clave in claves:
    row_index = procesar_clave(driver, clave, datos_tabla, pdf_urls)
    if row_index is not None:
        pdf_urls_indices.append(row_index)

# Crear un DataFrame de pandas con los datos de la tabla
df = pd.DataFrame(datos_tabla)

# Crear una lista de la misma longitud que el DataFrame
pdf_urls_filled = ['-'] * len(df)

# Asignar los valores de pdf_urls a pdf_urls_filled si hay elementos en pdf_urls
if pdf_urls:
    pdf_urls_filled[:len(pdf_urls)] = pdf_urls

# Asignar pdf_urls_filled a la columna 'Archivo PDF descargado'
df['Archivo PDF descargado'] = pdf_urls_filled

# Agregar las URLs de PDF a las filas correspondientes en el DataFrame
for pdf_url, row_index in zip(pdf_urls, pdf_urls_indices):
    if row_index is not None:
        df.at[row_index, 'Archivo PDF descargado'] = pdf_url

# Guardar el DataFrame en un archivo CSV en la carpeta actual
csv_filename = f"resultados_{time.strftime('%Y%m%d_%H%M%S')}.csv"
csv_path = os.path.join(script_folder, csv_filename)
df.to_csv(csv_path, index=False)

# Cerrar el navegador
print(f'Se procesaron un total de {len(claves)} claves.')
time.sleep(15)
driver.quit()