
sudo wget "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Obtener la versión más reciente del Chrome Driver
sudo wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip"

sudo unzip -o "chromedriver_linux64.zip" 
sudo chmod +x "chromedriver_linux64/chromedriver"

echo "listo"
