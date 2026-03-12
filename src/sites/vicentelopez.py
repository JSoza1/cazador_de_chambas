from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class VicenteLopezBot(BaseBot):
    """
    Bot de búsqueda para el portal de empleos del Municipio de Vicente López.

    Recorre hasta 5 páginas paginadas por query param (&page=X), filtrando
    por publicaciones de la última semana. No requiere autenticación.
    """

    def login(self):
        pass  # No requiere autenticación

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print("🔍 Iniciando escaneo en Vicente López...")
        self.notify("🤖 Buscando chamba por Vicente López!")

        base_url  = "https://empleo.vicentelopez.gov.ar/ofertas-de-empleo?date=last_week"
        MAX_PAGES = 5

        for page in range(1, MAX_PAGES + 1):
            url = base_url if page == 1 else f"{base_url}&page={page}"
            print(f"\n   📄 Buscando por PÁGINA {page}")

            try:
                self.driver.get(url)
                self.random_sleep(2, 4)

                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item.row")))
                except Exception:
                    print(f"   ⚠️ No se detectaron ofertas en página {page} (o fin de lista).")
                    break

                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.item.row")

                if not job_cards:
                    print(f"   ⚠️ Lista vacía en página {page}.")
                    break

                print(f"   -> Encontré {len(job_cards)} ofertas...")

                for card in job_cards:
                    try:
                        try:
                            title_node = card.find_element(By.CSS_SELECTOR, "h4 a")
                            title_text = title_node.text.strip()
                            url_oferta = normalize_url(title_node.get_attribute("href"))
                        except Exception:
                            continue

                        if not title_text or len(title_text) < 3:
                            continue

                        match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                        if match_keyword:
                            if not self.check_and_track(url_oferta):
                                continue

                            print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                            print(f"            🔗 URL: {url_oferta}")

                            self.notify(
                                f"✨ <b>¡NUEVA OFERTA EN VICENTE LÓPEZ!</b>\n\n"
                                f"📌 <b>Cargo:</b> {title_text}\n"
                                f"🔑 <b>Match:</b> {match_keyword}\n"
                                f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                            )

                    except Exception:
                        continue

            except Exception as e:
                print(f"❌ Error en página {page} de Vicente López: {e}")
                continue

        print("   ✅ Escaneo de Vicente López finalizado.")
