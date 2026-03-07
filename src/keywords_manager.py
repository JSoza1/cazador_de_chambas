
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
    "pasante programador",
    "pasante",
    "soporte",
    "soporte it",
    "soporte técnico"
    "soporte técnico it",
    "help desk",
    "helpdesk",
    "wordpress",
    "SEO",
    "elementor",
    "2026"
]

DEFAULT_NEGATIVE_KEYWORDS = [
    "senior", 
    "sr",  
    "lead", 
    "arquitecto", 
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
    "devops",
    "sysadmin",
    "php",
    "laravel",
    "django",
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
    "native",
    "lider",
    "líder",
    "next.js",
    "next",
    "business",
    "webflow"
]

DEFAULT_LANGUAGE_KEYWORDS = [
    "we are looking for", "we are seeking", "you will be", "you will have",
    "you will work", "you will join", "must have", "nice to have",
    "about the role", "about the job", "about the company", "about us",
    "what you'll do", "what you will do", "what we offer", "what we're looking",
    "who you are", "our team", "our company", "join our",
    "key responsibilities", "responsibilities", "requirements", "qualifications",
    "preferred qualifications", "the ideal candidate", "strong knowledge of",
    "experience with", "experience in", "proficiency in", "familiarity with",
    "ability to", "we offer", "we provide", "as part of", "as a member",
    "you'll work", "you'll be", "this role", "this position", "remote work", "work from home",
    "we believe", "equal opportunity",
    # Portugués
    "estamos à procura", "você irá", "você vai", "você será",
    "você terá", "você deve", "deve ter",
    "desejável", "conhecimento em", "experiência com", "experiência em",
    "nossa empresa", "nossa equipe", "faça parte", "venha fazer",
    "sobre a vaga", "sobre a empresa",
    # Italiano
    "stiamo cercando", "cerchiamo", "si offre", "si richiede", "requisiti",
    "la risorsa", "il candidato", "inserimento",
    "esperienza in", "esperienza con", "conoscenza di", "ottima conoscenza",
    "buona conoscenza", "si occuperà", "azienda leader", "offriamo", "chi siamo", "cosa farai"
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
            "language_negative_keywords": DEFAULT_LANGUAGE_KEYWORDS,
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
            "language_negative_keywords": DEFAULT_LANGUAGE_KEYWORDS,
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

def get_language_keywords():
    """Retorna la lista actual de palabras de FILTRO DE IDIOMA (descripción)."""
    keywords_data = load_keywords()
    return keywords_data.get("language_negative_keywords", DEFAULT_LANGUAGE_KEYWORDS)

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

def add_language_keyword(new_word):
    """
    Agrega una nueva frase al filtro de idioma.
    Retorna True si se agregó, False si ya existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("language_negative_keywords", [])
    normalized_word = new_word.lower().strip()
    if normalized_word not in current_list:
        current_list.append(normalized_word)
        keywords_data["language_negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False

def remove_language_keyword(word_to_remove):
    """Elimina una frase del filtro de idioma."""
    keywords_data = load_keywords()
    current_list = keywords_data.get("language_negative_keywords", [])
    normalized_word = word_to_remove.lower().strip()
    if normalized_word in current_list:
        current_list.remove(normalized_word)
        keywords_data["language_negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False
