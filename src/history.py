import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Definimos constantes para fácil configuración
HISTORY_FILE = "seen_jobs.json" 
DAYS_TO_REMEMBER = 15           

# Parámetros de query string que son de sesión/tracking y deben ignorarse
# al comparar URLs. Agregar aquí si aparecen nuevos sitios con el mismo problema.
TRACKING_PARAMS = {
    "searchId",   # EmpleosIT: cambia en cada sesión de búsqueda
    "page",       # EmpleosIT: número de página de la búsqueda (no del recurso)
    "s",          # Bumeran y otros: hash de sesión
    "lc",         # Computrabajo: posición en la lista (redundante, ya cubierto por #fragment)
    "utm_source", # Parámetros de marketing genéricos
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
}

def normalize_url(url):
    """
    Normaliza una URL para comparación consistente entre búsquedas.
    
    Elimina:
    - El fragmento (#...) → Computrabajo agrega '#lc=ListOffers-Score-N' que
      varía según la posición en la lista pero apunta a la misma oferta.
    - Parámetros de tracking/sesión definidos en TRACKING_PARAMS →
      EmpleosIT agrega 'searchId' y 'page' que cambian en cada búsqueda.
    - Espacios en blanco al inicio/fin.
    
    Args:
        url (str): La URL a normalizar.
        
    Returns:
        str: La URL normalizada (sin fragmento ni params de tracking).
    """
    if not url:
        return url
    try:
        parsed = urlparse(url.strip())
        
        # Filtramos los query params: conservamos solo los que NO son de tracking
        original_params = parse_qs(parsed.query, keep_blank_values=True)
        clean_params = {
            k: v for k, v in original_params.items()
            if k.lower() not in TRACKING_PARAMS
        }
        
        # Reconstruimos la query string limpia (sorted para orden consistente)
        clean_query = urlencode(clean_params, doseq=True)
        
        # Reconstruimos la URL sin el fragmento y con query limpia
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            ""  # Sin fragmento (#...)
        ))
        return normalized
    except Exception:
        return url.strip()

class JobHistory:
    """
    Gestiona la persistencia de ofertas vistas para evitar duplicados.
    
    FUNCIONAMIENTO:
    Mantiene un archivo JSON local ('seen_jobs.json') con parejas URL -> Fecha.
    Cada vez que el usuario confirma una oferta ("ya lo vi"), se guarda aquí.
    
    LIMPIEZA AUTOMÁTICA:
    Al iniciar, borra del archivo todas las ofertas que tengan más de X días.
    Esto evita que el archivo crezca infinitamente y degrade el rendimiento.
    """
    
    def __init__(self):
        self.seen_jobs = {}
        self.load()

    def load(self):
        """
        Carga el historial y purga registros más antiguos que DAYS_TO_REMEMBER.
        """
        if not os.path.exists(HISTORY_FILE):
            self.seen_jobs = {}
            return

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Limpieza de registros expirados
            cleaned_data = {}
            limit_date = datetime.now() - timedelta(days=DAYS_TO_REMEMBER)
            
            for url, date_str in data.items():
                try:
                    seen_date = datetime.fromisoformat(date_str)
                    
                    # Solo mantener si la oferta es reciente
                    if seen_date > limit_date:
                        cleaned_data[url] = date_str
                except ValueError:
                    continue 
            
            self.seen_jobs = cleaned_data
            self.save() 

        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error cargando historial: {e}. Se iniciará uno nuevo.")
            self.seen_jobs = {}

    def save(self):
        """Persiste el historial en disco (JSON)."""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.seen_jobs, f, indent=4)
        except Exception as e:
            print(f"⚠️ No se pudo guardar el historial: {e}")

    def is_seen(self, url):
        """Verifica si una URL (normalizada) ya existe en el registro."""
        return normalize_url(url) in self.seen_jobs

    def add_job(self, url):
        """
        Registra una URL (normalizada) con la fecha actual y guarda cambios.
        """
        clean_url = normalize_url(url)
        self.seen_jobs[clean_url] = datetime.now().isoformat()
        self.save()

# Instancia global para usar en todo el proyecto
history = JobHistory()
