from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class BBVABot(BaseBot):
    """
    Bot de búsqueda para el portal de empleos de BBVA (Workday).

    Workday es una SPA. El bot escanea la primera vista del listado,
    que con los filtros configurados trae los resultados más relevantes.
    """

    def login(self):
        pass  # No requiere autenticación

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print("🔍 Iniciando escaneo en BBVA (Workday)...")
        self.notify("🤖 Buscando chamba por BBVA!")

        target_url = (
            "https://bbva.wd3.myworkdayjobs.com/es/BBVA"
            "?AreaBBVA=4e7e381f49d210181652f3c780380002"
            "&locationCountry=e42ad5eac46d4cc9b367ceaef42577c5"
        )

        self.driver.get(target_url)
        self.random_sleep(4, 6)

        try:
            print("   ⏳ Esperando carga de lista de ofertas...")
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-automation-id='jobTitle']")
            ))
            self.random_sleep(2, 4)
        except Exception:
            print("   ⚠️ No se detectaron ofertas en BBVA (o tardó mucho).")
            return

        job_titles_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-automation-id='jobTitle']"
        )

        if not job_titles_elements:
            print("   ⚠️ Lista vacía en BBVA.")
            return

        print(f"   -> Analizando {len(job_titles_elements)} ofertas visibles en PÁGINA 1...")

        for title_node in job_titles_elements:
            try:
                title_text = title_node.text.strip()
                url_oferta = normalize_url(title_node.get_attribute("href"))

                if not title_text or len(title_text) < 3:
                    continue

                match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                if match_keyword:
                    if not self.check_and_track(url_oferta):
                        continue

                    print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                    print(f"            🔗 URL: {url_oferta}")

                    self.notify(
                        f"✨ <b>¡NUEVA OFERTA EN BBVA!</b>\n\n"
                        f"📌 <b>Cargo:</b> {title_text}\n"
                        f"🔑 <b>Match:</b> {match_keyword}\n"
                        f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                    )

            except Exception:
                continue

        print("   ✅ Escaneo de BBVA finalizado.")
