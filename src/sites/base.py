from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from src.notifications import send_telegram_message
from src.history import history


class BaseBot(ABC):
    """
    Clase base para todos los bots de búsqueda de empleo.

    Define la interfaz común que cada bot debe implementar y provee
    métodos de utilidad compartidos: control del navegador, validación
    de títulos, notificaciones, historial y filtro de idioma.

    Herencia: Todas las clases de sitios (BumeranBot, ComputrabajoBot, etc.)
    extienden esta clase y están obligadas a implementar el método `search`.
    """

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    @abstractmethod
    def search(self, keyword=None):
        """Implementa la lógica de búsqueda y notificación para el sitio correspondiente."""
        pass

    def random_sleep(self, min_seconds=2, max_seconds=5):
        """
        Pausa la ejecución por un intervalo aleatorio.
        Simula tiempos de lectura humanos para reducir la detección automatizada.
        """
        time.sleep(random.uniform(min_seconds, max_seconds))

    def safe_click(self, by, value):
        """
        Intenta hacer clic en un elemento esperando que sea interactuable.

        Args:
            by: Tipo de selector (By.ID, By.CSS_SELECTOR, etc.)
            value: Valor del selector.

        Returns:
            bool: True si el clic fue exitoso, False en caso contrario.
        """
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            element.click()
            return True
        except Exception as e:
            print(f"   ⚠️ No se pudo hacer clic en {value}: {e}")
            return False

    def type_text(self, by, value, text):
        """
        Escribe texto en un campo de entrada, limpiándolo previamente.

        Args:
            by: Tipo de selector.
            value: Valor del selector.
            text: Texto a escribir.

        Returns:
            bool: True si la escritura fue exitosa.
        """
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
        Evalúa si un título de empleo es relevante según las palabras clave configuradas.

        Aplica primero el filtro negativo (descarte inmediato si hay match) y luego
        el filtro positivo (retorna la keyword que produjo el match).

        La búsqueda usa word boundaries para evitar falsos positivos:
        - Palabras alfanuméricas: usa \\b (ej: 'sr' no matchea dentro de 'ssr').
        - Palabras con símbolos (C#, .Net): usa lookahead/lookbehind negativos.

        Args:
            job_title (str): Título del aviso de empleo.
            search_keywords (list): Términos que deben estar presentes (al menos uno).
            negative_keywords (list): Términos que descartan la oferta si aparecen.

        Returns:
            str | None: La keyword que produjo el match, o None si la oferta se descarta.
        """
        import re

        normalized_title = job_title.lower()

        def contains_exact_word(term, content):
            escaped = re.escape(term)
            if not term.isalnum():
                # Palabras con símbolos especiales (C#, .Net, C++): lookbehind/lookahead
                pattern = r'(?<!\w)' + escaped + r'(?!\w)'
            else:
                # Palabras alfanuméricas estándar: word boundary
                pattern = r'\b' + escaped + r'\b'
            try:
                return re.search(pattern, content) is not None
            except Exception:
                return term in content

        for negative_word in negative_keywords:
            if contains_exact_word(negative_word, normalized_title):
                return None

        for keyword in search_keywords:
            if contains_exact_word(keyword, normalized_title):
                return keyword

        return None

    def notify(self, message):
        """Envía un mensaje al usuario via Telegram."""
        print("   📢 Notificación: Mensaje enviado")
        try:
            send_telegram_message(message)
        except Exception as e:
            print(f"   ⚠️ Error enviando Telegram: {e}")

    def check_and_track(self, url):
        """
        Verifica si una oferta ya fue procesada en los últimos días.

        No registra la URL automáticamente; el usuario debe confirmar via Telegram
        para que quede guardada en el historial.

        Args:
            url (str): URL de la oferta a verificar.

        Returns:
            bool: True si la oferta es nueva, False si ya fue vista.
        """
        if not url:
            return True
        return not history.is_seen(url)

    def check_language_in_description(self, url):
        """
        Abre la URL de la oferta en una pestaña nueva y verifica si la descripción
        está en un idioma distinto al español, comparando contra las frases configuradas.

        Si ocurre algún error durante la navegación, retorna False para no bloquear
        incorrectamente ofertas válidas.

        Args:
            url (str): URL del detalle de la oferta.

        Returns:
            tuple: (True, 'frase detectada') si la descripción está en otro idioma,
                   (False, None) si pasa el filtro o si ocurre algún error.
        """
        from src.keywords_manager import get_language_keywords

        language_filters = get_language_keywords()
        if not language_filters:
            return False, None

        original_window = self.driver.current_window_handle

        try:
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(3)

            new_handles = [h for h in self.driver.window_handles if h != original_window]
            if not new_handles:
                return False, None

            self.driver.switch_to.window(new_handles[-1])
            time.sleep(2)

            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            except Exception:
                body_text = ""

            self.driver.close()
            self.driver.switch_to.window(original_window)

            for lang_word in language_filters:
                if lang_word.lower() in body_text:
                    return True, lang_word

            return False, None

        except Exception as e:
            print(f"      ⚠️ Error en check_language_in_description: {e}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
            except Exception:
                pass
            return False, None
