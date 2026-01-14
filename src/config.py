"""
MÓDULO DE CONFIGURACIÓN
-----------------------
Este archivo centraliza todas las variables configurables del proyecto.
Permite ajustar el comportamiento del bot sin modificar el código fuente principal.

- Carga credenciales desde .env
- Define palabras clave de búsqueda
- Controla tiempos de espera
"""
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

# Ruta de Perfil Personalizada (Opcional)
# Permite especificar una ruta a un perfil de Chrome existente.
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")

# --- URLs DE BÚSQUEDA LINKEDIN ---
# El bot recorrerá cada una de estas URLs secuencialmente.
JOB_SEARCH_URLS = [
    # === Filtros de ultima semana ===
    # Desarrollador ARG
    "https://www.linkedin.com/jobs/search/?currentJobId=4353192033&f_AL=true&f_TPR=r604800&geoId=100446943&keywords=Desarrollador&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD",

    # Desarrollador España (Remoto)
    "https://www.linkedin.com/jobs/search/?currentJobId=4352619718&f_AL=true&f_TPR=r604800&f_WT=2&geoId=105646813&keywords=Desarrollador&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD",

    # Desarrollador Todo el mundo (Remoto)
    "https://www.linkedin.com/jobs/search/?currentJobId=4361667042&f_AL=true&f_TPR=r604800&f_WT=2&geoId=92000000&keywords=Desarrollador&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true&sortBy=DD",

    # Programador ARG
    "https://www.linkedin.com/jobs/search/?currentJobId=4353004987&f_AL=true&f_TPR=r604800&geoId=100446943&keywords=Programador&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD",

    # Programador España (Remoto)
    "https://www.linkedin.com/jobs/search/?currentJobId=4353084758&f_AL=true&f_TPR=r604800&f_WT=2&geoId=105646813&keywords=Programador&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD",

    # Programador Todo el mundo (Remoto)
    "https://www.linkedin.com/jobs/search/?currentJobId=4359080675&f_AL=true&f_TPR=r604800&f_WT=2&geoId=92000000&keywords=Programador&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&refresh=true&sortBy=DD"
]

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
