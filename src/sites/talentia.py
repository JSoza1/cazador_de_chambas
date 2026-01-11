from src.sites.base import BaseBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

class TalentiaBot(BaseBot):
    """
    Bot específico para el portal de empleos de UTN Talentia.
    Hereda de BaseBot.
    Maneja una SPA (Single Page Application) donde la paginación no cambia la URL.
    """
    
    def login(self):
        pass # No requiere autenticación

    def search(self, _=None):
        """
        Escanea el portal de empleos de UTN Talentia.
        URL: https://utnba.talentia.com/portal/offers
        Maneja paginación dinámica haciendo click en 'Siguiente'.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando escaneo en UTN Talentia...")
        self.notify("🤖 Buscando chamba por UTN Talentia!")

        url = "https://utnba.talentia.com/portal/offers"
        MAX_PAGES = 5

        self.driver.get(url)
        self.random_sleep(5, 8) # Espera larga inicial para carga de la SPA

        for page in range(1, MAX_PAGES + 1):
            print(f"\n   📄 Buscando por PÁGINA {page}")

            # 1. Esperamos a que carguen las tarjetas
            try:
                # Selector analizado: .clickable-element.bubble-element.Group.cmnsr (Contenedor Tarjeta)
                # Usaremos una espera por presencia de elementos .clickable-element que contengan texto (títulos)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".bubble-element.Group.cmnsr")))
                self.random_sleep(2, 3) 
            except:
                print(f"   ⚠️ No se detectaron tarjetas (o fin de carga).")
                break

            # 2. Buscamos todas las tarjetas en el DOM actual
            # OJO: Talentia es un "bubble.io" app, las clases son raras. 
            # Buscaremos por estructura: Divs que parecen tarjetas.
            # Mejor estrategia: Buscar los títulos directamente y subir al padre si es necesario, 
            # o simplemente iterar los bloques de texto grandes.
            
            # Selector de tarjeta exacto según análisis:
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".clickable-element.bubble-element.Group.cmnsr")
            
            if not cards:
                print(f"   ⚠️ No encontré tarjetas con el selector estándar.")
                # Fallback: buscar por texto
                cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'bubble-element') and contains(@class, 'Group')][.//div[contains(text(), 'híbrido') or contains(text(), 'remoto') or contains(text(), 'presencial')]]")

            print(f"   -> Encontré {len(cards)} posibles ofertas...")

            found_any = False
            for card in cards:
                try:
                    # 3. Extraer Título
                    # El título está en un div interno: .bubble-element.Text.cmnsy
                    # A veces las clases cambian dinámicamente en bubble.io.
                    # Buscamos el elemento de texto que sea negrita o encabezado dentro de la tarjeta.
                    try:
                        # Buscamos el div de texto principal
                        title_node = card.find_element(By.CSS_SELECTOR, ".bubble-element.Text.cmnsy")
                        title_text = title_node.text.strip()
                    except:
                        # Fallback: El primer texto grande
                        title_text = card.text.split("\n")[0].strip()

                    # Talentia no tiene URLs directas visibles fáciles (son JS actions).
                    # La URL es la misma base, pero podemos inventar un link "fake" o dejarlo genérico
                    # O tratar de buscar si hay un <a> wrapper.
                    url_oferta = "https://utnba.talentia.com/portal/offers" 

                    # Limpieza
                    if not title_text or len(title_text) < 3:
                        continue

                    # 4. Validación
                    match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                    if match_keyword:
                        # 🛑 VERIFICAR DUPLICADOS (HISTORIAL)
                        # Nota: Talentia no tiene URL única por oferta, usamos el Título como ID único.
                        # Esto tiene el riesgo de ignorar si repostean el mismo título, pero es lo mejor posible.
                        fake_id_url = f"talentia://{title_text.replace(' ', '_')}"
                        
                        if not self.check_and_track(fake_id_url):
                            continue

                        found_any = True
                        # Evitamos duplicados en el mismo ciclo (aunque la paginación lo soluciona)
                        print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                        print(f"            🔗 Portal: {url_oferta}")
                        
                        msg = (
                            f"✨ <b>¡NUEVA OFERTA EN UTN TALENTIA!</b>\n\n"
                            f"📌 <b>Cargo:</b> {title_text}\n"
                            f"🔑 <b>Match:</b> {match_keyword}\n"
                            f"🔗 <a href='{url_oferta}'>Ir al Portal</a>"
                        )
                        self.notify(msg)

                except Exception as e:
                    continue

            # 5. Paginación (Click en "Siguiente")
            if page < MAX_PAGES:
                print("   -> Buscando botón 'Siguiente'...")
                try:
                    # Botón siguiente detectado como div con texto "Siguiente" dentro de un clickable
                    # Usamos XPath por texto que es lo más seguro en apps tipo Bubble
                    next_btn = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Siguiente')]")
                    
                    # Verificamos si es clickeable (a veces se deshabilita u oculta)
                    if not next_btn.is_displayed():
                        print("   ⚠️ Botón Siguiente no visible. Fin.")
                        break

                    # Scroll para asegurarnos que se vea
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                    self.random_sleep(1, 2)
                    
                    # Click
                    next_btn.click()
                    print("   -> Click realizado. Esperando carga...")
                    self.random_sleep(4, 6) # Espera para que el SPA renderice las nuevas cartas
                    
                except Exception as e:
                    print(f"   ⚠️ No se pudo avanzar de página: {e}")
                    break

        print("   ✅ Escaneo de UTN Talentia finalizado.")
