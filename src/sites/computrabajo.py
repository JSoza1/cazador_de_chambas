from src.sites.base import BaseBot
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time

class ComputrabajoBot(BaseBot):
    """
    Bot específico para Computrabajo (Argentina).
    """

    def search(self, _=None):
        """
        Búsqueda de ofertas en Computrabajo.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 COMPUTRABAJO: Iniciando búsqueda... {SEARCH_KEYWORDS}")
        self.notify(f"🤖 Buscando chamba por Computrabajo!")

        # Zonas de búsqueda definidas por el usuario
        ZONES_URLS = [
            "https://ar.computrabajo.com/empleos-de-informatica-y-telecom-en-capital-federal?pubdate=7&by=publicationtime",
            "https://ar.computrabajo.com/empleos-de-informatica-y-telecom-en-buenos-aires-gba?pubdate=7&by=publicationtime"
        ]
        
        MAX_PAGES = 8

        for zone_index, base_url in enumerate(ZONES_URLS):
            print(f"\n🌍 --- ZONA {zone_index + 1}: {base_url} ---")
            
            for page in range(1, MAX_PAGES + 1):
                # Construcción de URL con paginación
                # Si es p=1, la URL base sirve. Si es p>1, agregamos &p=X
                current_url = base_url if page == 1 else f"{base_url}&p={page}"
                
                print(f"   📄 Buscando por PÁGINA {page}")
                
                self.driver.get(current_url)
                self.random_sleep(3, 5)

                # Selectores de tarjetas de empleo
                articles = self.driver.find_elements(By.TAG_NAME, "article")

                if not articles:
                    print(f"   ⚠️ Fin de resultados en página {page}. Pasando a siguiente zona.")
                    break # Salimos del bucle de páginas, vamos a la siguiente zona

                print(f"   -> Encontré {len(articles)} posibles ofertas.")
                
                original_window = self.driver.current_window_handle

                for art in articles:
                    try:
                        # 0. Chequeo de "Ya postulado"
                        # El HTML tiene: <span class="tag postulated hide" applied-offer-tag="">
                        # Si NO tiene la clase "hide", es que está visible y ya nos postulamos.
                        try:
                            # Buscamos si existe el tag de postulado visible
                            applied_tag = art.find_elements(By.CSS_SELECTOR, "span.tag.postulated:not(.hide)")
                            if applied_tag:
                                #print("      (Saltando: Ya postulado anteriormente)")
                                continue
                        except:
                            pass

                        # Extraer Título y Link
                        try:
                            title_elem = art.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a")
                            title_text = title_elem.text
                            link_url = title_elem.get_attribute("href")
                        except:
                           continue

                        # Validar con nuestra lógica centralizada
                        match = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)
                        
                        if match:
                            # 🛑 VERIFICAR DUPLICADOS (HISTORIAL)
                            if not self.check_and_track(link_url):
                                continue

                            print(f"      ✨ MATCH: {title_text} ({match})")
                            self.notify(f"✨ <b>COMPUTRABAJO MATCH!</b>\n\n📌 {title_text}\n🔗 {link_url}")
                            
                            # Abrir oferta
                            self.driver.execute_script(f"window.open('{link_url}', '_blank');")
                            self.random_sleep(2, 4)
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            
                            # Intentar postular
                            # self.apply_to_current_job() # Deshabilitado en modo exploración 
                            
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            
                    except Exception as e:
                        print(f"      ❌ Error analizando tarjeta: {e}")
                        continue

    def apply_to_current_job(self):
        """
        Intenta postularse a la oferta abierta en la pestaña actual.
        """
        print("      🚀 Iniciando intento de postulación...")
        try:
            # Buscamos el botón "Postularme"
            # Selector basado en investigación: span.b_primary.big que contiene "Postularme"
            # Ojo: A veces es un 'input' o 'button'. Usaremos XPath por texto para ser flexibles.
            
            apply_btn = None
            try:
                apply_btn = self.driver.find_element(By.XPATH, "//span[contains(@class, 'b_primary') and contains(text(), 'Postularme')]")
            except:
                try:
                    # Intento alternativo por selector CSS directo
                    apply_btn = self.driver.find_element(By.CSS_SELECTOR, "span[data-apply-ac]")
                except:
                    pass

            if apply_btn:
                print("      ✅ Botón 'Postularme' encontrado.")
                # apply_btn.click() # DESCOMENTAR PARA EJECUCIÓN REAL
                print("      🚧 (Simulación) Click en Postular no ejecutado.")
                self.notify("      🚧 Simulación: Encontré el botón de postular.")
                self.random_sleep(2, 3)
                
                # OJO: Computrabajo a veces pide preguntas extra después de postular.
                # Eso requeriría una lógica más compleja de "responder preguntas".
            else:
                print("      ⚠️ No encontré el botón 'Postularme' (¿Ya postulado? ¿Login perdido?)")

        except Exception as e:
            print(f"      ❌ Error al intentar postular: {e}")
