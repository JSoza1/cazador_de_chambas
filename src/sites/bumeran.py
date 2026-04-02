from src.sites.base import BaseBot
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time


class BumeranBot(BaseBot):
    """
    Bot de búsqueda para Bumeran Argentina.

    Recorre el listado de empleos del área de Tecnología filtrado por publicaciones
    recientes, paginando hasta MAX_PAGES. Filtra por título, historial e idioma
    antes de notificar cada oferta.
    """

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando búsqueda con {len(SEARCH_KEYWORDS)} palabras activas.")
        self.notify("🤖 Buscando chamba por Bumeran!")

        target_urls = [
            "https://www.bumeran.com.ar/empleos-area-tecnologia-sistemas-y-telecomunicaciones-publicacion-menor-a-5-dias.html",
            "https://www.bumeran.com.ar/empleos-area-administracion-contabilidad-y-finanzas-publicacion-menor-a-5-dias.html"
        ]
        MAX_PAGES = 10

        for base_url in target_urls:
            print(f"\n🚀 --- ESCANEANDO ÁREA: {base_url.split('/')[-1].replace('.html', '').replace('-', ' ').title()} ---")
            
            for page_num in range(1, MAX_PAGES + 1):
                current_url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
                print(f"\n   📄 Buscando por PÁGINA {page_num}")

                if current_url not in self.driver.current_url:
                    self.driver.get(current_url)
                    self.random_sleep(2, 4)

                try:
                    self.wait.until(EC.presence_of_all_elements_located(
                        (By.XPATH, "//a[contains(@href, '/empleos/') and contains(@href, '.html')]")
                    ))
                except Exception:
                    pass

                job_links = self.driver.find_elements(
                    By.XPATH, "//a[contains(@href, '/empleos/') and contains(@href, '.html')]"
                )

                if not job_links:
                    print(f"   ⚠️ No encontré ofertas en pág {page_num}. Terminando área.")
                    break

                print(f"   -> Analizando {len(job_links)} ofertas...")

                original_window = self.driver.current_window_handle

                for link_element in job_links:
                    try:
                        url_oferta = link_element.get_attribute("href")

                        title_text = ""
                        try:
                            title_text = link_element.find_element(By.TAG_NAME, "h2").text.lower()
                        except Exception:
                            title_text = link_element.text.split("\n")[0].lower()

                        if len(title_text) < 3:
                            continue

                        match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                        if not match_keyword:
                            continue

                        if not self.check_and_track(url_oferta):
                            continue

                        print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                        print(f"            🔗 URL: {url_oferta}")

                        lang_blocked, lang_word = self.check_language_in_description(url_oferta)
                        if lang_blocked:
                            print(f"         🌐 ──────────────────────────────")
                            print(f"         🌐 IDIOMA FILTRADO (Bumeran)")
                            print(f"            📌 Título  : {title_text.title()}")
                            print(f"            🔍 Palabra : '{lang_word}'")
                            print(f"            🔗 Link    : {url_oferta[:80]}...")
                            print(f"         🌐 ──────────────────────────────")
                            continue

                        self.notify(
                            f"✨ <b>¡NUEVA OFERTA ENCONTRADA!</b>\n\n"
                            f"📌 <b>Cargo:</b> {title_text.title()}\n"
                            f"🔑 <b>Match:</b> {match_keyword}\n"
                            f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                        )

                        self.driver.execute_script(f"window.open('{url_oferta}', '_blank');")
                        self.random_sleep(2, 3)
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        self.driver.close()
                        self.driver.switch_to.window(original_window)

                    except Exception as e:
                        print(f"      ❌ Error al procesar link: {e}")
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                        continue
