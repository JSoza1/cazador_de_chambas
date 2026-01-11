from src.sites.base import BaseBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class BBVABot(BaseBot):
    """
    Bot específico para el portal de empleos de BBVA (Workday).
    Hereda de BaseBot.
    Scraping de Workday (SPA dinámica).
    """

    def login(self):
        pass # No requiere autenticación

    def search(self, _=None):
        """
        Escanea el portal de empleos de BBVA Workday.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando escaneo en BBVA (Workday)...")
        self.notify("🤖 Buscando chamba por BBVA!")

        # URL PROPORCIONADA CON FILTROS
        target_url = "https://bbva.wd3.myworkdayjobs.com/es/BBVA?AreaBBVA=4e7e381f49d210181652f3c780380002&locationCountry=e42ad5eac46d4cc9b367ceaef42577c5"
        
        self.driver.get(target_url)
        self.random_sleep(4, 6) # Esperar carga inicial de Workday (es pesada)

        # Workday suele ser una Single Page Application.
        # Vamos a intentar leer las tarjetas que cargaron.
        # NOTA: Workday es complejo con la paginación dinámica, pero escanearemos la primera vista
        # que suele traer los 20-30 resultados más relevantes con esos filtros.

        try:
            print("   ⏳ Esperando carga de lista de ofertas...")
            # Buscamos el contenedor de la lista (según tu HTML, es un 'li' con clase rara css-1q2dra3)
            # Usaremos un selector más genérico robusto: li[class*='css-'] h3 a
            # O mejor, buscamos el elemento con data-automation-id="jobTitle" que es estándar en Workday.
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='jobTitle']")))
            self.random_sleep(2, 4)
        except:
            print("   ⚠️ No se detectaron ofertas en BBVA (o tardó mucho).")
            return

        # Buscamos todos los elementos de título
        job_titles_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-automation-id='jobTitle']")
        
        if not job_titles_elements:
            print("   ⚠️ Lista vacía en BBVA.")
            return

        print(f"   -> Analizando {len(job_titles_elements)} ofertas visibles en PÁGINA 1...")

        for title_node in job_titles_elements:
            try:
                # Extraer datos
                title_text = title_node.text.strip()
                url_oferta = title_node.get_attribute("href")

                # Limpieza
                if not title_text or len(title_text) < 3:
                    continue

                # Validación
                match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                if match_keyword:
                    # 🛑 VERIFICAR DUPLICADOS (HISTORIAL)
                    if not self.check_and_track(url_oferta):
                        continue

                    print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                    print(f"            🔗 URL: {url_oferta}")
                    
                    # Notificación Telegram
                    msg = (
                        f"✨ <b>¡NUEVA OFERTA EN BBVA!</b>\n\n"
                        f"📌 <b>Cargo:</b> {title_text}\n"
                        f"🔑 <b>Match:</b> {match_keyword}\n"
                        f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                    )
                    self.notify(msg)

            except Exception as e:
                 # print(f"      debug: error parsing card: {e}") 
                 continue

        print("   ✅ Escaneo de BBVA finalizado.")
