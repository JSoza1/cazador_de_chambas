#!/bin/bash

# ====================================================
# AUTO-INSTALADOR Y EJECUTOR (TERMUX / LINUX) - V4
# ====================================================

# Detectar si estamos en Termux
if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    echo "📱 Entorno Termux detectado..."
    
    # 1. Asegurar repositorios
    echo "🔄 Actualizando repositorios base..."
    pkg update -y
    
    # 2. Instalar repositorios necesarios (tur-repo y x11-repo)
    echo "🔧 Agregando repositorio X11 y TUR..."
    pkg install tur-repo x11-repo -y
    pkg update -y

    # 3. Arreglar paquetes rotos (si los hay)
    apt-get --fix-broken install -y
    
    # 4. Instalar Chromium (Chromedriver viene incluido en este paquete!)
    echo "🔧 Instalando Chromium..."
    pkg install chromium -y

    # 5. Debug Final: Localización real
    CHROME_BIN=$(command -v chromium || command -v chromium-browser || find /data/data/com.termux/files/usr/bin -name "*chromium*" | head -n 1)
    DRIVER_BIN=$(command -v chromedriver || find /data/data/com.termux/files/usr -name "*chromedriver*" | head -n 1)

    echo "✅ Chrome encontrado en: $CHROME_BIN"
    echo "✅ Driver encontrado en: $DRIVER_BIN"
    
    if [ -z "$CHROME_BIN" ]; then
        echo "❌ ERROR CRÍTICO: No se pudo instalar Chromium."
    fi
fi

# Gestionar Entorno Virtual
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
fi

echo "🔋 Activando entorno virtual..."
source ./venv/bin/activate

echo "📦 Verificando librerías de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Iniciando Cazador de Chambas..."
python3 main.py
