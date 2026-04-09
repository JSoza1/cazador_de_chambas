"""
Módulo de configuración central del proyecto.

Carga credenciales desde el archivo .env y expone todas las variables
configurables del bot. Modificar este archivo (o el .env) es suficiente
para ajustar el comportamiento sin tocar el código fuente.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(var_name, default=None, required=True):
    """
    Obtiene una variable de entorno con validación integrada.

    Args:
        var_name (str): Nombre de la variable de entorno.
        default: Valor por defecto si la variable no está definida.
        required (bool): Si es True y la variable no existe, detiene la ejecución.

    Returns:
        str: El valor de la variable de entorno.
    """
    value = os.getenv(var_name, default)

    if required and not value:
        print(f"❌ Error Crítico: La variable de entorno '{var_name}' no está definida.")
        print("   Verificar el archivo .env")
        sys.exit(1)

    return value


# --- CREDENCIALES ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# Ruta al perfil de Chrome para persistir sesiones entre ejecuciones.
# Si no se define, se usa la carpeta 'profile/' en la raíz del proyecto.
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")


# Resolución dinámica de palabras clave para que siempre estén al día sin reiniciar.
def __getattr__(name):
    from src.keywords_manager import get_positive_keywords, get_negative_keywords
    if name == "SEARCH_KEYWORDS":
        return get_positive_keywords()
    if name == "NEGATIVE_KEYWORDS":
        return get_negative_keywords()
    raise AttributeError(f"module {__name__} has no attribute {name}")

# --- CONFIGURACIÓN TÉCNICA ---

# Tiempo de espera entre ciclos de búsqueda (en minutos).
CHECK_INTERVAL_MINUTES = 360

# Modo sin interfaz gráfica. True para servidores o uso en segundo plano.
HEADLESS_MODE = True
