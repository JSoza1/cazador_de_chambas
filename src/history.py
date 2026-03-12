import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Constantes de configuración
HISTORY_FILE = "seen_jobs.json"
DAYS_TO_REMEMBER = 15

# Parámetros de query string que no identifican el recurso y deben ignorarse
# al comparar URLs. Cada portal de empleo suele agregar sus propios parámetros
# de sesión o paginación que varían entre búsquedas pero apuntan a la misma oferta.
TRACKING_PARAMS = {
    "searchid",    # EmpleosIT: identificador de sesión de búsqueda
    "page",        # EmpleosIT: página de los resultados de búsqueda
    "s",           # Bumeran: hash de sesión
    "lc",          # Computrabajo: posición en el listado de resultados
    "utm_source",  # Parámetros de marketing estándar (Google Analytics, etc.)
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
}

def normalize_url(url):
    """
    Normaliza una URL antes de compararla o guardarla.

    Distintos portales de empleo agregan parámetros a la URL de cada oferta
    (sesión, posición en la lista, página de búsqueda, etc.) que cambian entre
    ejecuciones pero apuntan al mismo recurso. Esta función los elimina para
    garantizar que la misma oferta siempre produzca la misma clave canónica.

    Elimina:
    - Fragmento (#...): ancla de página, no afecta al recurso.
    - Parámetros de tracking definidos en TRACKING_PARAMS.
    - Espacios en blanco al inicio/fin.

    Args:
        url (str): URL a normalizar.

    Returns:
        str: URL canónica sin fragmento ni parámetros de sesión/tracking.
    """
    if not url:
        return url
    try:
        parsed = urlparse(url.strip())

        # Conservamos solo los query params que no están en la lista de exclusión
        original_params = parse_qs(parsed.query, keep_blank_values=True)
        clean_params = {
            k: v for k, v in original_params.items()
            if k.lower() not in TRACKING_PARAMS
        }

        clean_query = urlencode(clean_params, doseq=True)

        # Reconstruimos la URL sin fragmento y con query string limpia
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            ""  # Sin fragmento
        ))
        return normalized
    except Exception:
        return url.strip()


class JobHistory:
    """
    Gestiona la persistencia de ofertas vistas para evitar duplicados.

    Mantiene un archivo JSON local ('seen_jobs.json') con pares URL → Fecha.
    Todas las URLs se almacenan normalizadas (ver normalize_url) para garantizar
    comparaciones consistentes independientemente de los parámetros de sesión
    que cada portal pueda agregar.

    Al iniciar, purga automáticamente los registros con más de DAYS_TO_REMEMBER
    días para evitar que el archivo crezca indefinidamente.
    """

    def __init__(self):
        self.seen_jobs = {}
        self.load()

    def load(self):
        """
        Carga el historial desde disco, purga entradas expiradas y normaliza
        todas las claves URL para garantizar comparaciones consistentes.

        Si dos entradas distintas en disco normalizan a la misma URL canónica
        (ej: misma oferta con searchId diferente), se conserva la más reciente.
        Al finalizar, persiste el historial ya limpio y normalizado.
        """
        if not os.path.exists(HISTORY_FILE):
            self.seen_jobs = {}
            return

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            cleaned_data = {}
            limit_date = datetime.now() - timedelta(days=DAYS_TO_REMEMBER)

            for url, date_str in data.items():
                try:
                    seen_date = datetime.fromisoformat(date_str)

                    if seen_date > limit_date:
                        clean_url = normalize_url(url)

                        # Si dos entradas distintas resultan en la misma URL
                        # canónica, conservamos la fecha más reciente de las dos
                        if clean_url in cleaned_data:
                            existing_date = datetime.fromisoformat(cleaned_data[clean_url])
                            if seen_date > existing_date:
                                cleaned_data[clean_url] = date_str
                        else:
                            cleaned_data[clean_url] = date_str
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
        """Verifica si una URL ya existe en el historial (comparación normalizada)."""
        return normalize_url(url) in self.seen_jobs

    def add_job(self, url):
        """Registra una URL en el historial con la fecha actual y persiste el cambio."""
        clean_url = normalize_url(url)
        self.seen_jobs[clean_url] = datetime.now().isoformat()
        self.save()


# Instancia global compartida por todos los módulos del proyecto
history = JobHistory()
