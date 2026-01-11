import json
import os
from datetime import datetime, timedelta

HISTORY_FILE = "seen_jobs.json"
DAYS_TO_REMEMBER = 15

class JobHistory:
    """
    Gestiona la persistencia de ofertas vistas para evitar duplicados.
    Guarda las URLs y la fecha de detección.
    Olvida las ofertas después de 15 días.
    """
    
    def __init__(self):
        self.seen_jobs = {}
        self.load()

    def load(self):
        """Carga el historial y limpia registros antiguos."""
        if not os.path.exists(HISTORY_FILE):
            self.seen_jobs = {}
            return

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Limpieza de antidgüedad
            cleaned_data = {}
            limit_date = datetime.now() - timedelta(days=DAYS_TO_REMEMBER)
            
            for url, date_str in data.items():
                try:
                    seen_date = datetime.fromisoformat(date_str)
                    if seen_date > limit_date:
                        cleaned_data[url] = date_str
                except ValueError:
                    continue # Ignorar fechas malformadas
            
            self.seen_jobs = cleaned_data
            self.save() # Guardar la versión limpia

        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error cargando historial: {e}. Se iniciará uno nuevo.")
            self.seen_jobs = {}

    def save(self):
        """Guarda el historial en disco."""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.seen_jobs, f, indent=4)
        except Exception as e:
            print(f"⚠️ No se pudo guardar el historial: {e}")

    def is_seen(self, url):
        """Verifica si una URL ya fue procesada recientemente."""
        return url in self.seen_jobs

    def add_job(self, url):
        """Agrega una URL al historial con la fecha actual."""
        self.seen_jobs[url] = datetime.now().isoformat()
        self.save()

# Instancia global para usar en todo el proyecto
history = JobHistory()
