#!/bin/bash

# ====================================================
# AUTO-INSTALADOR Y EJECUTOR (TERMUX / LINUX)
# ====================================================

# Detectar si estamos en Termux
if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    echo "📱 Entorno Termux detectado..."
    
    # Verificar si Chromium y Chromedriver están instalados
    if ! command -v chromium &> /dev/null || ! command -v chromedriver &> /dev/null; then
        echo "🔧 Faltan dependencias del sistema. Instalando Chromium y Chromedriver..."
        pkg update && pkg upgrade -y
        pkg install tur-repo -y
        pkg install chromium chromedriver -y
    else
        echo "✅ Drivers del sistema ya instalados."
    fi
fi

# Gestionar Entorno Virtual de Python
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
fi

echo "🔋 Activando entorno virtual..."
source ./venv/bin/activate

# Instalación de dependencias de Python
echo "📦 Verificando librerías de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Iniciando Cazador de Chambas..."
python3 main.py
