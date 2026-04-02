import json
import os


KEYWORDS_FILE = "keywords.json"

# Valores por defecto usados al crear el archivo por primera vez.
# También actúan de fallback si el archivo está corrupto o no accesible.
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
    "soporte técnico",
    "soporte técnico it",
    "help desk",
    "helpdesk",
    "wordpress",
    "SEO",
    "elementor",
    "2026",
    "java",
    "sql",
    "administrativo jr",
    "administrativo",
    "analista de sistemas",
    "analista de sistemas jr",
    "analista",
    "pagos",
    "cobranzas",
    "cuentas"
]

DEFAULT_NEGATIVE_KEYWORDS = [
    "senior", "sr", "lead", "arquitecto",
    "+4 años", "+5 años",
    "ingles avanzado", "bilingue",
    ".net", "net", "cobol", "angular", "vue",
    "analista de datos", "power bi",
    "qa", "c#", "c++", "arduino", "PLC",
    "devops", "sysadmin",
    "php", "laravel", "django",
    "sap", "sap abap", "abap",
    "cloud", "aws", "azure", "google cloud", "google-cloud",
    "data science", "data",
    "ux/ui", "ux ui", "ux", "ui",
    "pruebas", "pl", "native",
    "lider", "líder",
    "next.js", "next",
    "business", "webflow",
]

DEFAULT_LANGUAGE_KEYWORDS = [
    # Inglés
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
    "buona conoscenza", "si occuperà", "azienda leader", "offriamo", "chi siamo", "cosa farai",
]


def load_keywords():
    """
    Carga las palabras clave desde el archivo JSON.

    Si el archivo no existe, lo crea con los valores por defecto.
    Si el archivo está corrupto o no es accesible, retorna los valores por defecto.

    Returns:
        dict: Diccionario con las claves 'search_keywords', 'negative_keywords'
              y 'language_negative_keywords'.
    """
    if not os.path.exists(KEYWORDS_FILE):
        default_data = {
            "search_keywords": DEFAULT_SEARCH_KEYWORDS,
            "negative_keywords": DEFAULT_NEGATIVE_KEYWORDS,
            "language_negative_keywords": DEFAULT_LANGUAGE_KEYWORDS,
        }
        save_keywords(default_data)
        return default_data

    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as error:
        print(f"⚠️ Error cargando keywords: {error}. Usando valores por defecto.")
        return {
            "search_keywords": DEFAULT_SEARCH_KEYWORDS,
            "negative_keywords": DEFAULT_NEGATIVE_KEYWORDS,
            "language_negative_keywords": DEFAULT_LANGUAGE_KEYWORDS,
        }


def save_keywords(keywords_data):
    """
    Persiste el diccionario de palabras clave en el archivo JSON.

    Args:
        keywords_data (dict): Diccionario con las listas de palabras clave.
    """
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(keywords_data, f, indent=4, ensure_ascii=False)


def get_positive_keywords():
    """Retorna la unión de las palabras por defecto y las configuradas por el usuario en el JSON."""
    user_keywords = load_keywords().get("search_keywords", [])
    # Unimos ambos, normalizamos a minúsculas y eliminamos duplicados
    combined = list(set([k.lower() for k in DEFAULT_SEARCH_KEYWORDS] + [k.lower() for k in user_keywords]))
    return combined


def get_negative_keywords():
    """Retorna la unión de las negativas por defecto y las configuradas por el usuario."""
    user_keywords = load_keywords().get("negative_keywords", [])
    combined = list(set([k.lower() for k in DEFAULT_NEGATIVE_KEYWORDS] + [k.lower() for k in user_keywords]))
    return combined


def get_language_keywords():
    """Retorna la unión de las frases de idioma por defecto y las configuradas por el usuario."""
    user_keywords = load_keywords().get("language_negative_keywords", [])
    combined = list(set([k.lower() for k in DEFAULT_LANGUAGE_KEYWORDS] + [k.lower() for k in user_keywords]))
    return combined


def add_positive_keyword(new_word):
    """
    Agrega una palabra clave positiva.

    Returns:
        bool: True si se agregó, False si ya existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("search_keywords", [])
    normalized = new_word.lower().strip()

    if normalized not in current_list:
        current_list.append(normalized)
        keywords_data["search_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False


def add_negative_keyword(new_word):
    """
    Agrega una palabra clave negativa.

    Returns:
        bool: True si se agregó, False si ya existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("negative_keywords", [])
    normalized = new_word.lower().strip()

    if normalized not in current_list:
        current_list.append(normalized)
        keywords_data["negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False


def remove_positive_keyword(word_to_remove):
    """
    Elimina una palabra clave positiva.

    Returns:
        bool: True si se eliminó, False si no existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("search_keywords", [])
    normalized = word_to_remove.lower().strip()

    if normalized in current_list:
        current_list.remove(normalized)
        keywords_data["search_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False


def remove_negative_keyword(word_to_remove):
    """
    Elimina una palabra clave negativa.

    Returns:
        bool: True si se eliminó, False si no existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("negative_keywords", [])
    normalized = word_to_remove.lower().strip()

    if normalized in current_list:
        current_list.remove(normalized)
        keywords_data["negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False


def add_language_keyword(new_word):
    """
    Agrega una frase al filtro de idioma.

    Returns:
        bool: True si se agregó, False si ya existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("language_negative_keywords", [])
    normalized = new_word.lower().strip()

    if normalized not in current_list:
        current_list.append(normalized)
        keywords_data["language_negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False


def remove_language_keyword(word_to_remove):
    """
    Elimina una frase del filtro de idioma.

    Returns:
        bool: True si se eliminó, False si no existía.
    """
    keywords_data = load_keywords()
    current_list = keywords_data.get("language_negative_keywords", [])
    normalized = word_to_remove.lower().strip()

    if normalized in current_list:
        current_list.remove(normalized)
        keywords_data["language_negative_keywords"] = current_list
        save_keywords(keywords_data)
        return True
    return False
