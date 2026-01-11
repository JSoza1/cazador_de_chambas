from src.sites.base import BaseBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

class EmpleosITBot(BaseBot):
    """
    Bot específico para el portal EmpleosIT (empleosit.com.ar).
    Hereda de BaseBot.
    Usa paginación por parámetro URL (&page=1, &page=2, etc.)
    """
    
    def login(self):
        pass # No requiere autenticación

    def search(self, _=None):
        """
        Escanea el portal de EmpleosIT.
        URL con filtros predefinidos por el usuario (listings_per_page=100 es muy útil).
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando escaneo en EmpleosIT...")
        self.notify("🤖 Buscando chamba por EmpleosIT!")

        # URL BASE - Nota: El searchId puede expirar, pero usaremos uno genérico o limpiaremos parámetros si falla.
        # Mejor estrategia: URL de búsqueda limpia + filtros.
        # Usuario pasó: https://www.empleosit.com.ar/search-results-jobs/?searchId=...&action=search&page=1&listings_per_page=100&view=list
        # Simplificamos para evitar searchId viejo que de error. Usamos la búsqueda general de jobs.
        
        base_url = "https://www.empleosit.com.ar/search-results-jobs/?action=search&listings_per_page=100&view=list"
        
        MAX_PAGES = 1 # Solo página 1 (trae 100 ofertas, suficiente).

        for page in range(1, MAX_PAGES + 1):
            current_url = f"{base_url}&page={page}"
            
            print(f"\n   📄 Buscando por PÁGINA {page}")
            
            try:
                self.driver.get(current_url)
                self.random_sleep(3, 5)

                try:
                    # Esperamos carga de tarjetas. Clase contenedora: "listing-section" o "listing-title"
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-title")))
                except:
                    print(f"   ⚠️ No se detectaron ofertas o fin de resultados en pág {page}.")
                    break

                # Buscamos elementos contenedores de detalles
                # Cada oferta tiene un div.listing-title que contiene el <a> con el título
                job_titles_divs = self.driver.find_elements(By.CLASS_NAME, "listing-title")
                
                if not job_titles_divs:
                    print(f"   ⚠️ Lista vacía en página {page}.")
                    break

                print(f"   -> Encontré {len(job_titles_divs)} ofertas visibles...")

                for title_div in job_titles_divs:
                    try:
                        # 1. Extraer Título y Link
                        # Estructura: <div class="listing-title"> <a href="..."> Título </a> ... </div>
                        # OJO: A veces hay un anchor vacío <a name="..."> antes. Buscamos el que tiene href.
                        links = title_div.find_elements(By.TAG_NAME, "a")
                        target_link = None
                        
                        for link in links:
                            href = link.get_attribute("href")
                            text = link.text.strip()
                            if href and len(text) > 3:
                                target_link = link
                                break
                        
                        if not target_link:
                            continue

                        title_text = target_link.text.strip()
                        url_oferta = target_link.get_attribute("href")

                        # Limpieza y Validación
                        match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                        if match_keyword:
                            print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                            print(f"            🔗 URL: {url_oferta}")
                            
                            msg = (
                                f"✨ <b>¡NUEVA OFERTA EN EMPLEOSIT!</b>\n\n"
                                f"📌 <b>Cargo:</b> {title_text}\n"
                                f"🔑 <b>Match:</b> {match_keyword}\n"
                                f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                            )
                            self.notify(msg)

                    except Exception as e:
                        continue
            
            except Exception as e:
                print(f"❌ Error en página {page} de EmpleosIT: {e}")
                continue

        print("   ✅ Escaneo de EmpleosIT finalizado.")
