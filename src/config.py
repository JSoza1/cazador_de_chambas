import os
import sys
from dotenv import load_dotenv

# Carga de variables del archivo .env
# Búsqueda automática del archivo .env en la raíz del proyecto
load_dotenv()

def get_env_variable(var_name, default=None, required=True):
    """
    Obtiene una variable de entorno con manejo de errores para valores faltantes.
    
    Args:
        var_name (str): El nombre de la variable (ej: 'BUMERAN_EMAIL')
        default: Valor por defecto si no existe la variable.
        required (bool): Si es True y la variable no existe, detiene la ejecución.
        
    Returns:
        str: El valor de la variable.
    """
    value = os.getenv(var_name, default)
    
    if required and not value:
        print(f"❌ Error Crítico: La variable de entorno '{var_name}' no está definida.")
        print("   Verificar el archivo .env")
        sys.exit(1) # Detiene el programa indicando error
        
    return value

# --- Credenciales Bumeran ---
BUMERAN_EMAIL = os.getenv("BUMERAN_EMAIL")
BUMERAN_PASSWORD = os.getenv("BUMERAN_PASSWORD")

# --- Credenciales Computrabajo ---
COMPUTRABAJO_EMAIL = os.getenv("COMPUTRABAJO_EMAIL")
COMPUTRABAJO_PASSWORD = os.getenv("COMPUTRABAJO_PASSWORD")

# Credenciales de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- CONFIGURACIÓN DE BÚSQUEDA ---

# 1. Palabras Clave POSITIVAS
# El sistema buscará estas palabras en los TÍTULOS de las ofertas.
SEARCH_KEYWORDS = [
    "desarrollo web", 
    "frontend", 
    "programador web", 
    "python",
    "programador",
    "react",
    "javascript",  
    "maquetador web",
    "web developer",
    "front-end",
    "desarrollador",
    "desarrollador web",
    "desarrollador frontend",
    "desarrollador backend",
    "developer",
    "pasantía desarrollador",
    "pasantía programador",
    "pasantia programador",
    "pasantia desarrollador",
    "pasante desarrollador",
    "pasante programador"
]

# 2. Palabras Clave NEGATIVAS
# Si el título contiene alguna de estas palabras, la oferta se DESCARTA automáticamente.
# Utilidad para filtrar puestos por seniority no deseado (ej: Senior vs Junior).
NEGATIVE_KEYWORDS = [
    "senior", 
    "sr", 
    "ssr", 
    "lead", 
    "arquitecto", 
    "+3 años", 
    "+4 años", 
    "+5 años",
    "ingles avanzado", 
    "bilingue",
    ".net",
    "net",
    "cobol",
    "angular",
    "vue",
    "analista de datos",
    "power bi",
    "qa",
    "c#",
    "c++",
    "arduino",
    "PLC",
    "soporte it",
    "wordpress",
    "devops",
    "sysadmin",
    "php",
    "laravel",
    "django",
    "fullstack",
    "full stack",
    "full-stack",
    "sap",
    "sap abap",
    "abap",
    "cloud",
    "aws",
    "azure",
    "google cloud",
    "google-cloud",
    "java",
    "data science",
    "data",
    "ux/ui",
    "ux ui",
    "ux",
    "ui",
    "pruebas",
    "pl",
    "sql",
    "engineer",
    "enginner",
    "enginer",
    "ingeniero",
    "native",
    "lider",
    "líder",
    "next.js",
    "next",
    "business",
    "webflow"
]

# --- CONFIGURACIÓN TÉCNICA ---

# Tiempo de espera entre rondas de búsqueda (en minutos)
# 60 minutos = 1 hora / 360 minutos = 6 horas
CHECK_INTERVAL_MINUTES = 360

# Modo Headless (True = Navegador oculto / False = Navegador visible para depuración)
# False recomendado para desarrollo, True para servidores.
HEADLESS_MODE = True
