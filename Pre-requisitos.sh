#!/bin/bash

# Obtener la ubicación actual del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Actualizar paquetes e instalar dependencias
sudo apt -y update
sudo apt install -y wget curl unzip libvulkan1

# Instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Obtener la versión más reciente del Chrome Driver
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip

unzip -o "chromedriver_linux64.zip" -d "$SCRIPT_DIR"
chmod +x "chromedriver_linux64/chromedriver"

echo "listo"