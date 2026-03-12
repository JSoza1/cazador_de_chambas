from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class VicenteLopezBot(BaseBot):
    """
    Bot específico para el portal de empleos de Vicente López.
    Hereda de BaseBot.
    No requiere login, paginación por url (?page=X).
    URL FILTRADA: https://empleo.vicentelopez.gov.ar/ofertas-de-empleo?date=last_week
    """
    
    def login(self):
        pass # No requiere autenticación

    def search(self, _=None):
        """
        Escanea el portal de empleos de Vicente López (Municipio).
        Recorre hasta 5 páginas.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando escaneo en Vicente López...")
        self.notify("🤖 Buscando chamba por Vicente López!")

        # URL base con el filtro de fecha aplicado
        base_url = "https://empleo.vicentelopez.gov.ar/ofertas-de-empleo?date=last_week"
        MAX_PAGES = 5

        for page in range(1, MAX_PAGES + 1):
            # Construcción de la URL paginada (si es page 1, es la base, sino agregamos &page=X)
            url = base_url if page == 1 else f"{base_url}&page={page}"
            
            print(f"\n   📄 Buscando por PÁGINA {page}")
            
            try:
                self.driver.get(url)
                self.random_sleep(2, 4)

                # Esperamos carga de items (div con clase .item)
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item.row")))
                except:
                    print(f"   ⚠️ No se detectaron ofertas en página {page} (o fin de lista).")
                    break # Asumimos que si no carga nada, no hay más páginas

                # Buscamos todas las tarjetas
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.item.row")
                
                if not job_cards:
                    print(f"   ⚠️ Lista vacía en página {page}.")
                    break

                print(f"   -> Encontré {len(job_cards)} ofertas...")

                for card in job_cards:
                    try:
                        # 1. Extraer Título y Link
                        # Estructura: <h4> <a href="..."> Título </a> </h4>
                        try:
                            title_node = card.find_element(By.CSS_SELECTOR, "h4 a")
                            title_text = title_node.text.strip()
                            url_oferta = normalize_url(title_node.get_attribute("href"))
                        except:
                            continue # Si falla la extracción básica, pasamos

                        # Limpieza
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
                                f"✨ <b>¡NUEVA OFERTA EN VICENTE LÓPEZ!</b>\n\n"
                                f"📌 <b>Cargo:</b> {title_text}\n"
                                f"🔑 <b>Match:</b> {match_keyword}\n"
                                f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                            )
                            self.notify(msg)

                    except Exception as e:
                        # print(f"      debug: error parsing card vl: {e}") 
                        continue
            
            except Exception as e:
                print(f"❌ Error en página {page} de Vicente López: {e}")
                continue

        print("   ✅ Escaneo de Vicente López finalizado.")
