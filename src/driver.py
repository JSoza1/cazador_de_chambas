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
    
    # 1. Configuración de Opciones del Navegador
    chrome_options = Options()
    
    # User-Agent: Simula un navegador real para evitar bloqueos básicos.
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Modo Headless (Sin interfaz gráfica)
    if HEADLESS_MODE:
        print("   -> Modo Headless activado")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080") # Resolución fija para evitar problemas de layout
        
    # Anti-Detección: Ocutla varaibles de automatización de Selenium
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    
    # Optimizaciones para entornos Linux/Docker
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 
    
    if not HEADLESS_MODE:
        chrome_options.add_argument("--start-maximized")
    
    # Reducir logs de consola (Solo errores fatales)
    chrome_options.add_argument("--log-level=3") 
    
    # Ocultar barra "Un software automatizado de pruebas..."
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 2. Detección de Entorno (PC vs Android/Termux)
    is_android = "ANDROID_ROOT" in os.environ
    
    try:
        if is_android:
            print("📱 Detectado entorno Android (Termux)")
            from selenium.webdriver.chrome.service import Service
            
            # Rutas específicas para Chromium en Termux
            chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
            service = Service("/data/data/com.termux/files/usr/bin/chromedriver")
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("💻 Detectado entorno PC (Windows/Linux/Mac)")
            # Selenium Manager gestiona el driver automáticamente
            driver = webdriver.Chrome(options=chrome_options)
            
        return driver
        
    except Exception as e:
        print("\n❌ Error fatal al iniciar el navegador:")
        print(f"   {e}")
        print("\n💡 Consejo: Verificar actualización de Google Chrome.")
        raise e
