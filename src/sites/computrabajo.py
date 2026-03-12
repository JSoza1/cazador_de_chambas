from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time


class ComputrabajoBot(BaseBot):
    """
    Bot de búsqueda para Computrabajo Argentina.

    Recorre las zonas configuradas (Capital Federal y GBA) paginando
    los resultados por fecha de publicación. Filtra por título, historial
    de vistos e idioma antes de notificar cada oferta.
    """

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 COMPUTRABAJO: Iniciando búsqueda... {SEARCH_KEYWORDS}")
        self.notify("🤖 Buscando chamba por Computrabajo!")

        ZONES_URLS = [
            "https://ar.computrabajo.com/empleos-de-informatica-y-telecom-en-capital-federal?pubdate=7&by=publicationtime",
            "https://ar.computrabajo.com/empleos-de-informatica-y-telecom-en-buenos-aires-gba?pubdate=7&by=publicationtime",
        ]

        MAX_PAGES = 8

        for zone_index, base_url in enumerate(ZONES_URLS):
            print(f"\n🌍 --- ZONA {zone_index + 1}: {base_url} ---")

            for page in range(1, MAX_PAGES + 1):
                current_url = base_url if page == 1 else f"{base_url}&p={page}"
                print(f"   📄 Buscando por PÁGINA {page}")

                self.driver.get(current_url)
                self.random_sleep(3, 5)

                articles = self.driver.find_elements(By.TAG_NAME, "article")

                if not articles:
                    print(f"   ⚠️ Fin de resultados en página {page}. Pasando a siguiente zona.")
                    break

                print(f"   -> Encontré {len(articles)} posibles ofertas.")

                original_window = self.driver.current_window_handle

                for art in articles:
                    try:
                        # Saltear ofertas en las que el usuario ya se postuló
                        try:
                            applied_tag = art.find_elements(By.CSS_SELECTOR, "span.tag.postulated:not(.hide)")
                            if applied_tag:
                                continue
                        except Exception:
                            pass

                        try:
                            title_elem = art.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a")
                            title_text = title_elem.text
                            link_url   = normalize_url(title_elem.get_attribute("href"))
                        except Exception:
                            continue

                        match = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                        if match:
                            if not self.check_and_track(link_url):
                                continue

                            print(f"      ✨ MATCH: {title_text} ({match})")

                            lang_blocked, lang_word = self.check_language_in_description(link_url)
                            if lang_blocked:
                                print(f"      🌐 ──────────────────────────────")
                                print(f"      🌐 IDIOMA FILTRADO (Computrabajo)")
                                print(f"         📌 Título  : {title_text.title()}")
                                print(f"         🔍 Palabra : '{lang_word}'")
                                print(f"         🔗 Link    : {link_url[:80]}...")
                                print(f"      🌐 ──────────────────────────────")
                                continue

                            self.notify(f"✨ <b>COMPUTRABAJO MATCH!</b>\n\n📌 {title_text}\n🔗 {link_url}")

                            self.driver.execute_script(f"window.open('{link_url}', '_blank');")
                            self.random_sleep(2, 4)
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            self.driver.close()
                            self.driver.switch_to.window(original_window)

                    except Exception as e:
                        print(f"      ❌ Error analizando tarjeta: {e}")
                        continue
