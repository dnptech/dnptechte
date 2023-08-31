#!/bin/bash

# Obtener la ubicación actual del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Actualizar paquetes e instalar dependencias
sudo apt -y update
sudo apt install -y wget curl unzip libvulkan1

# Instalar libu2f-udev
wget http://archive.ubuntu.com/ubuntu/pool/main/libu/libu2f-host/libu2f-udev_1.1.4-1_all.deb
sudo dpkg -i libu2f-udev_1.1.4-1_all.deb

# Instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Obtener la versión más reciente del Chrome Driver
CHROME_DRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])")
echo "Latest Chrome Driver version: $CHROME_DRIVER_VERSION"

# Descargar y configurar el Chrome Driver en el mismo directorio del script
wget -N "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_DRIVER_VERSION/linux64/chromedriver_linux64.zip" -P "$SCRIPT_DIR"
unzip -o "$SCRIPT_DIR/chromedriver_linux64.zip" -d "$SCRIPT_DIR"
chmod +x "$SCRIPT_DIR/chromedriver_linux64/chromedriver"

echo "listo"
