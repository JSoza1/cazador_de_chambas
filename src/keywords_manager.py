
import json
import os

# Nombre del archivo donde se guardarán las palabras clave de forma persistente
KEYWORDS_FILE = "keywords.json"

# Listas por defecto (Copiadas del config original de cazador_de_chambas)
DEFAULT_SEARCH_KEYWORDS = [
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

DEFAULT_NEGATIVE_KEYWORDS = [
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

def load_keywords():
    """
    Carga las palabras clave desde el archivo JSON.
    Si el archivo no existe, lo crea con los valores por defecto.
    Retorna un diccionario con las listas de positivas y negativas.
    """
    # Si el archivo no existe, lo creamos con los valores por defecto
    if not os.path.exists(KEYWORDS_FILE):
        default_data = {
            "search_keywords": DEFAULT_SEARCH_KEYWORDS,
            "negative_keywords": DEFAULT_NEGATIVE_KEYWORDS
        }
        save_keywords(default_data)
        return default_data
    
    try:
        # Intentamos leer el archivo existente
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as file_handler:
            return json.load(file_handler)
    except Exception as error:
        print(f"Error cargando keywords: {error}")
        # En caso de error (archivo corrupto), retornamos los defaults por seguridad
        return {
            "search_keywords": DEFAULT_SEARCH_KEYWORDS,
            "negative_keywords": DEFAULT_NEGATIVE_KEYWORDS
        }

def save_keywords(keywords_data):
    """
    Guarda el diccionario de palabras clave en el archivo JSON.
    
    Args:
        keywords_data (dict): Diccionario con claves 'search_keywords' y 'negative_keywords'.
    """
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as file_handler:
        # ensure_ascii=False permite guardar tildes y caracteres especiales correctamente
        json.dump(keywords_data, file_handler, indent=4, ensure_ascii=False)

def get_positive_keywords():
    """Retorna la lista actual de palabras clave POSITIVAS."""
    keywords_data = load_keywords()
    return keywords_data.get("search_keywords", DEFAULT_SEARCH_KEYWORDS)

def get_negative_keywords():
    """Retorna la lista actual de palabras clave NEGATIVAS."""
    keywords_data = load_keywords()
    return keywords_data.get("negative_keywords", DEFAULT_NEGATIVE_KEYWORDS)

def add_positive_keyword(new_word):
    """
    Agrega una nueva palabra clave positiva.
    Retorna True si se agregó, False si ya existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("search_keywords", [])
    
    # Normalizamos a minúsculas y quitamos espacios extra
    normalized_word = new_word.lower().strip()
    
    if normalized_word not in current_list:
        current_list.append(normalized_word)
        keywords_data["search_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False

def add_negative_keyword(new_word):
    """
    Agrega una nueva palabra clave negativa.
    Retorna True si se agregó, False si ya existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("negative_keywords", [])
    
    normalized_word = new_word.lower().strip()
    
    if normalized_word not in current_list:
        current_list.append(normalized_word)
        keywords_data["negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False

def remove_positive_keyword(word_to_remove):
    """Elimina una palabra clave positiva."""
    keywords_data = load_keywords()
    current_list = keywords_data.get("search_keywords", [])
    
    normalized_word = word_to_remove.lower().strip()
    
    if normalized_word in current_list:
        current_list.remove(normalized_word)
        keywords_data["search_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False

def remove_negative_keyword(word_to_remove):
    """Elimina una palabra clave negativa."""
    keywords_data = load_keywords()
    current_list = keywords_data.get("negative_keywords", [])
    
    normalized_word = word_to_remove.lower().strip()
    
    if normalized_word in current_list:
        current_list.remove(normalized_word)
        keywords_data["negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False
