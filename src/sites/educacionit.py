from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class EducacionITBot(BaseBot):
    """
    Bot específico para el portal de empleos de EducaciónIT.
    Hereda de BaseBot.
    No requiere login, paginación por URL query param (?p=X).
    """
    
    def login(self):
        pass # No requiere autenticación

    def search(self, _=None):
        """
        Escanea el portal de empleos de EducaciónIT.
        URL Base: https://empleos.educacionit.com/trabajos
        Recorre 5 páginas.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando escaneo en EducaciónIT (5 páginas)...")
        self.notify("🤖 Buscando chamba por EducaciónIT!")

        base_url = "https://empleos.educacionit.com/trabajos"
        MAX_PAGES = 5

        for page in range(1, MAX_PAGES + 1):
            url = f"{base_url}?p={page}"
            print(f"\n   📄 Buscando por PÁGINA {page}")
            
            try:
                self.driver.get(url)
                self.random_sleep(2, 4)

                # Esperamos a que haya items o el contenedor principal
                try:
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "itemEmpleo")))
                except:
                    print(f"   ⚠️ No se detectaron ofertas en página {page}.")
                    continue

                # Buscamos todas las tarjetas de empleo
                job_cards = self.driver.find_elements(By.CLASS_NAME, "itemEmpleo")
                
                if not job_cards:
                    print(f"   ⚠️ Lista vacía en página {page}.")
                    continue

                print(f"   -> Analizando {len(job_cards)} ofertas...")

                for card in job_cards:
                    try:
                        # 1. Extraer Título y Link
                        # Estructura: <h3> <a href="..."> Título </a> </h3>
                        # Usamos CSS Selector relativo a la tarjeta
                        title_node = card.find_element(By.CSS_SELECTOR, "h3 a")
                        
                        title_text = title_node.text.strip()
                        url_oferta = normalize_url(title_node.get_attribute("href"))

                        # Limpieza básica
                        if not title_text or len(title_text) < 3:
                            continue

                        # 2. Validación
                        match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                        if match_keyword:
                            # 🛑 VERIFICAR DUPLICADOS (HISTORIAL)
                            if not self.check_and_track(url_oferta):
                                continue

                            print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                            print(f"            🔗 URL: {url_oferta}")
                            
                            # Notificación Telegram
                            msg = (
                                f"✨ <b>¡NUEVA OFERTA EN EDUCACIÓN IT!</b>\n\n"
                                f"📌 <b>Cargo:</b> {title_text}\n"
                                f"🔑 <b>Match:</b> {match_keyword}\n"
                                f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                            )
                            self.notify(msg)

                    except Exception as e:
                        # print(f"      debug: error parsing card: {e}") 
                        continue
            
            except Exception as e:
                print(f"❌ Error crítico en página {page}: {e}")
                continue

        print("   ✅ Escaneo de EducaciónIT finalizado.")
