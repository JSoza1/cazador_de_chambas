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

    # Suprime logs de Chrome, mostrando solo errores fatales.
    chrome_options.add_argument("--log-level=3")

    is_android = "ANDROID_ROOT" in os.environ

    try:
        if is_android:
            print("📱 Detectado entorno Android (Termux)")
            from selenium.webdriver.chrome.service import Service
            chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
            service = Service("/data/data/com.termux/files/usr/bin/chromedriver")
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
