from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


class EmpleosITBot(BaseBot):
    """
    Bot de búsqueda para EmpleosIT (empleosit.com.ar).

    Carga hasta 100 ofertas por página usando el parámetro listings_per_page.
    Las URLs se normalizan para eliminar el parámetro searchId, que varía
    entre sesiones pero no identifica el recurso.
    """

    def login(self):
        pass  # No requiere autenticación

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print("🔍 Iniciando escaneo en EmpleosIT...")
        self.notify("🤖 Buscando chamba por EmpleosIT!")

        base_url  = "https://www.empleosit.com.ar/search-results-jobs/?action=search&listings_per_page=100&view=list"
        MAX_PAGES = 1

        for page in range(1, MAX_PAGES + 1):
            current_url = f"{base_url}&page={page}"
            print(f"\n   📄 Buscando por PÁGINA {page}")

            try:
                self.driver.get(current_url)
                self.random_sleep(3, 5)

                try:
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-title")))
                except Exception:
                    print(f"   ⚠️ No se detectaron ofertas o fin de resultados en pág {page}.")
                    break

                job_titles_divs = self.driver.find_elements(By.CLASS_NAME, "listing-title")

                if not job_titles_divs:
                    print(f"   ⚠️ Lista vacía en página {page}.")
                    break

                print(f"   -> Encontré {len(job_titles_divs)} ofertas visibles...")

                for title_div in job_titles_divs:
                    try:
                        # Cada div puede tener varios anchors; tomamos el que tiene texto visible.
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
                        url_oferta = normalize_url(target_link.get_attribute("href"))

                        match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                        if match_keyword:
                            if not self.check_and_track(url_oferta):
                                continue

                            print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                            print(f"            🔗 URL: {url_oferta}")

                            lang_blocked, lang_word = self.check_language_in_description(url_oferta)
                            if lang_blocked:
                                print(f"         🌐 ──────────────────────────────")
                                print(f"         🌐 IDIOMA FILTRADO (EmpleosIT)")
                                print(f"            📌 Título  : {title_text.title()}")
                                print(f"            🔍 Palabra : '{lang_word}'")
                                print(f"            🔗 Link    : {url_oferta[:80]}...")
                                print(f"         🌐 ──────────────────────────────")
                                continue

                            self.notify(
                                f"✨ <b>¡NUEVA OFERTA EN EMPLEOSIT!</b>\n\n"
                                f"📌 <b>Cargo:</b> {title_text}\n"
                                f"🔑 <b>Match:</b> {match_keyword}\n"
                                f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                            )

                    except Exception:
                        continue

            except Exception as e:
                print(f"❌ Error en página {page} de EmpleosIT: {e}")
                continue

        print("   ✅ Escaneo de EmpleosIT finalizado.")
