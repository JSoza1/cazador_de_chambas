from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class AndreaniBot(BaseBot):
    """
    Bot de búsqueda para el portal de empleos de Andreani (Oracle Cloud HCM).

    Escanea la primera vista del listado de ofertas disponibles y notifica
    las que coincidan con las palabras clave configuradas.
    """

    def login(self):
        pass  # No requiere autenticación

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Escaneando Andreani...")
        self.notify("🤖 Buscando chamba por Andreani!")

        target_url = "https://ibmzjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/es/sites/CX_1001/jobs"

        self.driver.get(target_url)
        self.random_sleep(3, 5)

        try:
            print("   ⏳ Esperando carga de ofertas...")
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job-list-item")))
            self.random_sleep(2, 3)
        except Exception:
            print("   ⚠️ No se detectaron ofertas o tardó mucho en cargar.")
            return

        job_cards = self.driver.find_elements(By.CLASS_NAME, "job-list-item")

        if not job_cards:
            print("   ⚠️ No se encontraron tarjetas de empleo.")
            return

        print(f"   -> Analizando {len(job_cards)} ofertas visibles...")

        for card in job_cards:
            try:
                title_element = card.find_element(By.CLASS_NAME, "job-tile__title")
                title_text    = title_element.text.lower()

                link_element = card.find_element(By.CLASS_NAME, "job-list-item__link")
                url_oferta   = normalize_url(link_element.get_attribute("href"))

                if not title_text or len(title_text) < 3:
                    continue

                match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                if match_keyword:
                    if not self.check_and_track(url_oferta):
                        continue

                    print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                    print(f"            🔗 URL: {url_oferta}")

                    self.notify(
                        f"✨ <b>¡NUEVA OFERTA EN ANDREANI!</b>\n\n"
                        f"📌 <b>Cargo:</b> {title_text.title()}\n"
                        f"🔑 <b>Match:</b> {match_keyword}\n"
                        f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                    )

            except Exception:
                continue

        print("   ✅ Escaneo de Andreani finalizado.")
