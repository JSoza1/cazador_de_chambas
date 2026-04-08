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
    
    # 2. Instalar tur-repo y REFRESCAR
    if ! pkg list-installed tur-repo &> /dev/null; then
        echo "🔧 Instalando tur-repo..."
        pkg install tur-repo -y
        pkg update -y # Crucial: actualizar para ver los nuevos paquetes del TUR
    fi

    # 3. Instalar Chromium (Por separado para que no falle el resto)
    echo "🔧 Instalando Chromium..."
    pkg install chromium -y

    # 4. Intentar instalar Chromedriver (Varios nombres posibles)
    echo "🔧 Intentar instalar Chromedriver..."
    pkg install chromedriver -y || pkg install chromium-chromedriver -y

    # 5. Debug Final: Localización real
    CHROME_BIN=$(command -v chromium || command -v chromium-browser)
    DRIVER_BIN=$(command -v chromedriver || find /data/data/com.termux/files/usr/bin -name "*chromedriver*" | head -n 1)

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
