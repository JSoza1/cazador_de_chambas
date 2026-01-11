import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# Eliminación de webdriver_manager para evitar conflictos en entorno Windows
# from webdriver_manager.chrome import ChromeDriverManager 
# from selenium.webdriver.chrome.service import Service 

from src.config import HEADLESS_MODE

def get_driver():
    """
    Inicialización y configuración del navegador Chrome controlado por Selenium.
    """
    
    print("🚗 Inicializando el navegador...")
    
    # 1. Configuración de Opciones
    chrome_options = Options()
    
    # Identificación como navegador real (evita bloqueo por "HeadlessChrome")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if HEADLESS_MODE:
        print("   -> Modo Headless activado")
        chrome_options.add_argument("--headless=new")
        # Definición de tamaño de ventana fijo para evitar diseño responsivo/móvil en headless
        chrome_options.add_argument("--window-size=1920,1080")
        
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if not HEADLESS_MODE:
        chrome_options.add_argument("--start-maximized")
    
    # SILENCIAR LOGS DE CHROME Y OCULTAR "AUTOMATION"
    chrome_options.add_argument("--log-level=3") 
    
    # 🕵️ MODO SIGILO MEJORADO (Anti-detección básica)
    # Estas opciones ocultan la barra de "Chrome está siendo controlado por..."
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 2. Detección de Sistema
    is_android = "ANDROID_ROOT" in os.environ
    
    try:
        if is_android:
            print("📱 Detectado entorno Android (Termux)")
            # En Termux se requiere especificación de rutas manuales
            from selenium.webdriver.chrome.service import Service
            # Actualización: En termux moderno el binario suele ser chromium-browser
            chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
            service = Service("/data/data/com.termux/files/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("💻 Detectado entorno PC (Windows/Linux/Mac)")
            # 🌟 CAMBIO IMPORTANTE: Selenium 4.10+ incluye gestor de drivers nativo.
            # Al omitir 'service', Selenium gestiona el driver automáticamente.
            # Prevención de error Win32.
            driver = webdriver.Chrome(options=chrome_options)
            
        return driver
        
    except Exception as e:
        print("\n❌ Error fatal al iniciar el navegador:")
        print(f"   {e}")
        print("\n💡 Consejo: Verificar actualización de Google Chrome.")
        raise e
