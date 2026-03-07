from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from src.notifications import send_telegram_message
from src.history import history  # 📥 Importamos el gestor de historial

class BaseBot(ABC):
    """
    Clase madre para todos los bots de búsqueda de empleo.
    Provee métodos comunes de Selenium y lógica básica.

    CONCEPTOS IMPORTANTES:
    - ABC (Abstract Base Class): Define un 'contrato'. Cualquier clase que herede de esta
      ESTÁ OBLIGADA a implementar los métodos marcados con @abstractmethod.
      
    Esto asegura consistencia en la implementación de diferentes bots (ej: LinkedInBot, BumeranBot).
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) # Espera máxima de 10 segundos para encontrar elementos



    @abstractmethod
    def search(self, keyword):
        """Implementación de la lógica de búsqueda de empleos por palabra clave."""
        pass

    # --- Métodos de Ayuda (Utilidad general para bots) ---
    
    def random_sleep(self, min_seconds=2, max_seconds=5):
        """
        Espera un tiempo aleatorio.
        Simulación de comportamiento humano para evitar detección automatizada.
        """
        time.sleep(random.uniform(min_seconds, max_seconds))

    def safe_click(self, by, value):
        """
        Intento de clic en elemento de forma segura, esperando su aparición.
        
        Args:
            by: Tipo de selector (By.ID, By.CSS_SELECTOR, etc.)
            value: El valor del selector (ej: "#boton-login")
        """
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            element.click()
            return True
        except Exception as e:
            print(f"   ⚠️ No se pudo hacer clic en {value}: {e}")
            return False

    def type_text(self, by, value, text):
        """Escritura de texto en un campo, con limpieza previa."""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            element.clear()
            element.send_keys(text)
            return True
        except Exception:
            print(f"   ⚠️ No se pudo escribir en {value}")
            return False

    def validate_job_title(self, job_title, search_keywords, negative_keywords):
        """
        Analiza si un título de trabajo es relevante según las palabras clave configuradas.
        
        Args:
            job_title (str): El título del aviso de empleo.
            search_keywords (list): Lista de palabras que DEBEN estar (al menos una).
            negative_keywords (list): Lista de palabras que NO deben estar.
            
        Returns:
            str | None: Devuelve la palabra clave encontrada si hay match, o None si se descarta.
        """
        # Importamos 're' (Regular Expressions) para búsquedas avanzadas de texto
        import re
        
        # 1. Normalización: Pasamos todo a minúsculas
        normalized_title = job_title.lower()
        
        # --- FUNCIÓN INTERNA DE VALIDACIÓN ---
        def contains_exact_word(search_term, content):
            """
            Verifica si 'search_term' aparece en 'content' como una palabra exacta.
            Evita falsos positivos como detectar 'sr' dentro de 'ssr'.
            """
            
            # Escapamos el término por si tiene caracteres especiales (C++, .Net)
            escaped_term = re.escape(search_term)

            # --- ESTRATEGIA A: PALABRAS CON SÍMBOLOS (C#, .Net, C++) ---
            # Las expresiones regulares estándar (\b) no manejan bien símbolos como '#' o '+'.
            # Por ejemplo, \bC++\b no funciona porque + no es una letra/número.
            # SOLUCIÓN: Usamos "Lookbehind" y "Lookahead" negativos (?<!\w) y (?!\w).
            # Esto significa: "Busca la palabra DONDE lo que está antes NO sea una letra/número 
            # y lo que está después TAMPOCO sea una letra/número".
            if not search_term.isalnum(): 
                pattern = r'(?<!\w)' + escaped_term + r'(?!\w)'
                return re.search(pattern, content) is not None
            
            # --- ESTRATEGIA B: PALABRAS ALFANUMÉRICAS (Python, Java, Sr) ---
            # Usamos \b (Word Boundary) ques es el estándar para límites de palabra.
            # \b detecta cambios entre caracteres de palabra (a-z, 0-9) y no-palabra (espacio, punto).
            try:
                pattern = r'\b' + escaped_term + r'\b'
                return re.search(pattern, content) is not None
            except:
                # Fallback de seguridad: Si falla el regex, búsqueda simple (menos precisa pero no rompe)
                return search_term in content

        # 2. APLICACIÓN DE FILTRO NEGATIVO
        # Si encontramos CUALQUIER palabra prohibida como palabra exacta, descartamos el aviso.
        for negative_word in negative_keywords:
            if contains_exact_word(negative_word, normalized_title):
                return None 

        # 3. APLICACIÓN DE FILTRO POSITIVO
        # Buscamos si ALGUNA de las palabras deseadas está presente.
        for meaningful_keyword in search_keywords:
            if contains_exact_word(meaningful_keyword, normalized_title):
                return meaningful_keyword # ¡Éxito! Retornamos la palabra que hizo match
                
        return None

    def notify(self, message):
        """
        Envía una notificación al usuario (Telegram).
        """
        # Imprimimos en consola también para debug
        print(f"   📢 Notificación: Mensaje enviado")
        try:
            send_telegram_message(message)
        except Exception as e:
            print(f"   ⚠️ Error enviando Telegram: {e}")

    def check_and_track(self, url):
        """
        Verifica si la URL ya fue vista en los últimos 15 días.
        Si es nueva, la registra.
        
        Returns:
            bool: True si es NUEVA (o expirada), False si ya fue vista reciente.
        """
        if not url: return True
        
        if history.is_seen(url):
            return False # Ya vista (el usuario dijo "ya lo vi"), ignorar.
        else:
            # NO agregamos automáticamente. 
            # El usuario debe confirmar por Telegram para que se guarde.
            return True

    def check_language_in_description(self, url):
        """
        Navega a la URL del detalle de la oferta en una pestaña nueva,
        lee todo el texto visible y chequea si hay frases de otro idioma.

        Returns:
            tuple (bool, str | None):
                - (True, 'frase detectada') si la descripción está en otro idioma.
                - (False, None) si pasa el filtro o si ocurre algún error.
        """
        from src.keywords_manager import get_language_keywords
        import time

        language_filters = get_language_keywords()
        if not language_filters:
            return False, None

        original_window = self.driver.current_window_handle

        try:
            # Abrir la URL en una nueva pestaña para no perder el contexto actual
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(3)

            # Cambiar a la nueva pestaña
            new_handles = [h for h in self.driver.window_handles if h != original_window]
            if not new_handles:
                return False, None

            self.driver.switch_to.window(new_handles[-1])
            time.sleep(2)

            # Leer el texto completo de la página
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            except Exception:
                body_text = ""

            # Cerrar pestaña y volver
            self.driver.close()
            self.driver.switch_to.window(original_window)

            # Chequear contra el filtro de idioma
            for lang_word in language_filters:
                if lang_word.lower() in body_text:
                    return True, lang_word

            return False, None

        except Exception as e:
            print(f"      ⚠️ Error en check_language_in_description: {e}")
            # Intentamos cerrar la pestaña extra si quedó abierta
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except Exception:
                pass
            # No bloqueamos si algo falla — mejor perder un filtro que romper el bot
            return False, None
