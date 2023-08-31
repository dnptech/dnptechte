# Actualizar el sistema e instalar dependencias
sudo apt -y update
sudo apt install -y wget curl unzip
sudo apt-get install libpq-dev
sudo pip install psycopg2-binary pandas psycopg2 selenium

# Descargar e instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# Descargar, instalar y configurar ChromeDriver
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P /tmp/
unzip -o /tmp/chromedriver_linux64.zip -d /tmp/
sudo chmod +x /tmp/chromedriver
sudo mv /tmp/chromedriver /usr/local/bin/chromedriver

echo "Configuración completa."