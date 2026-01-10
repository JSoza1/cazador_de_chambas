from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from src.notifications import send_telegram_message

class BaseBot(ABC):
    """
    Clase Base Abstracta para bots de búsqueda.
    
    CONCEPTOS IMPORTANTES:
    - ABC (Abstract Base Class): Define un 'contrato'. Cualquier clase que herede de esta
      ESTÁ OBLIGADA a implementar los métodos marcados con @abstractmethod.
      
    Esto asegura consistencia en la implementación de diferentes bots (ej: LinkedInBot, BumeranBot).
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) # Espera máxima de 10 segundos para encontrar elementos

    @abstractmethod
    def login(self):
        """Implementación de la lógica de inicio de sesión."""
        pass

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

    def validate_job_title(self, title_text, search_keywords, negative_keywords):
        """
        Valida si un título de empleo cumple con los requisitos de búsqueda.
        Retorna la palabra clave coincidente o None si no sirve.
        """
        title_text = title_text.lower()
        
        # 1. Filtro Negativo
        if any(bad in title_text for bad in negative_keywords):
            return None

        # 2. Filtro Positivo
        for k in search_keywords:
            if k in title_text:
                return k # Retornamos la keyword que hizo match
                
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
