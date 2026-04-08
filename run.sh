#!/bin/bash

# ====================================================
# AUTO-INSTALADOR Y EJECUTOR (TERMUX / LINUX) - V3
# ====================================================

# Detectar si estamos en Termux
if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    echo "📱 Entorno Termux detectado..."
    
    # 1. Asegurar repositorios y actualizar
    echo "🔄 Actualizando repositorios..."
    pkg update -y
    
    # 2. Instalar tur-repo si no está
    if ! pkg list-installed tur-repo &> /dev/null; then
        echo "🔧 Instalando tur-repo..."
        pkg install tur-repo -y
    fi

    # 3. Forzar instalación de Chromium y Chromedriver
    echo "🔧 Verificando Chromium y Chromedriver..."
    pkg install chromium chromedriver -y

    # 4. Debug: Buscar dónde están los binarios si el script falla
    CHROME_BIN=$(command -v chromium || command -v chromium-browser)
    DRIVER_BIN=$(command -v chromedriver)

    if [ -z "$DRIVER_BIN" ]; then
        echo "⚠️ ADVERTENCIA: No se encontró 'chromedriver' en el PATH."
        echo "🔍 Buscando manualmente en el sistema..."
        DRIVER_BIN=$(find /data/data/com.termux/files/usr/bin -name "*chromedriver*" | head -n 1)
    fi

    echo "✅ Chrome: $CHROME_BIN"
    echo "✅ Driver: $DRIVER_BIN"
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
