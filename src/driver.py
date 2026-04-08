import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.config import HEADLESS_MODE


def get_driver():
    """
    Construye y retorna una instancia configurada de Chrome para Selenium.

    Detecta automáticamente el entorno de ejecución (PC o Android/Termux)
    y aplica la configuración correspondiente. El perfil de Chrome es
    persistente entre ejecuciones para conservar sesiones activas.
    """
    print("🚗 Inicializando el navegador...")

    chrome_options = Options()

    # Perfil persistente: conserva cookies y sesiones entre ejecuciones.
    # Ruta configurable via CHROME_PROFILE_PATH en .env; por defecto usa ./profile.
    from src.config import CHROME_PROFILE_PATH
    from pathlib import Path

    profile_dir = Path(CHROME_PROFILE_PATH) if CHROME_PROFILE_PATH else Path.cwd() / "profile"

    if not profile_dir.exists():
        try:
            profile_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Directorio de perfil creado: {profile_dir}")
        except Exception as e:
            print(f"⚠️ No se pudo crear directorio de perfil: {e}")

    print(f"👤 Usando perfil de Chrome: {profile_dir}")
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")

    # User-Agent estándar de escritorio para evitar bloqueos por detección de bots.
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    if HEADLESS_MODE:
        print("   -> Modo Headless activado")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
    else:
        chrome_options.add_argument("--start-maximized")

    # Oculta las variables de automatización que algunos sitios usan para detectar Selenium.
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Opciones de estabilidad requeridas en entornos Linux/Docker/Termux.
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=0")

    # Suprime logs de Chrome, mostrando solo errores fatales.
    chrome_options.add_argument("--log-level=3")

    is_android = "ANDROID_ROOT" in os.environ

    try:
        if is_android:
            print("📱 Detectado entorno Android (Termux)")
            from selenium.webdriver.chrome.service import Service
            import shutil
            
            # Forzar el PATH para que el sistema encuentre todo
            termux_bin = "/data/data/com.termux/files/usr/bin"
            os.environ["PATH"] = f"{termux_bin}:{os.environ.get('PATH', '')}"
            
            # Buscar binarios
            chrome_path = shutil.which("chromium") or shutil.which("chromium-browser") or f"{termux_bin}/chromium"
            driver_path = shutil.which("chromedriver") or f"{termux_bin}/chromedriver"
            
            # Chequeo extra por si está en la carpeta lib
            if not os.path.exists(driver_path):
                alt_driver_path = "/data/data/com.termux/files/usr/lib/chromium/chromedriver"
                if os.path.exists(alt_driver_path):
                    driver_path = alt_driver_path
            
            if not os.path.exists(driver_path):
                print(f"⚠️ Alerta: No se encontró chromedriver en {driver_path}")
            else:
                # Asegurar permisos de ejecución
                os.chmod(driver_path, 0o755)
                if os.path.exists(chrome_path):
                    os.chmod(chrome_path, 0o755)

            print(f"🔍 Usando Chromium en: {chrome_path}")
            print(f"🔍 Usando Chromedriver en: {driver_path}")
            
            chrome_options.binary_location = chrome_path
            
            # Crear servicio y FORZAR la ruta para evitar que Selenium busque
            service = Service(executable_path=driver_path)
            service.path = driver_path 
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("💻 Detectado entorno PC (Windows/Linux/Mac)")
            # Selenium Manager gestiona el driver automáticamente en PC.
            driver = webdriver.Chrome(options=chrome_options)

        return driver

    except Exception as e:
        print("\n❌ Error fatal al iniciar el navegador:")
        print(f"   {e}")
        print("\n💡 Verificar que Google Chrome esté instalado y actualizado.")
        raise e
