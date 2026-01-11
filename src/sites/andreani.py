from src.sites.base import BaseBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class AndreaniBot(BaseBot):
    """
    Bot específico para el portal de empleos de Andreani (Oracle Cloud).
    Hereda de BaseBot.
    No requiere login, solo monitoreo y notificación.
    """
    
    def login(self):
        pass # Requisito de BaseBot, aunque no se use.

    def search(self, _=None):
        """
        Escanea el portal de empleos de Andreani.
        URL: https://ibmzjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/es/sites/CX_1001/jobs
        """
        # Importación diferida para evitar ciclos si fuera necesario, y usar la config global
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        # Normalización
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 Iniciando escaneo en Andreani (keywords: {SEARCH_KEYWORDS})")
        self.notify("🤖 Buscando chamba por Andreani!")

        target_url = "https://ibmzjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/es/sites/CX_1001/jobs"
        
        self.driver.get(target_url)
        self.random_sleep(3, 5) # Espera inicial para carga de Oracle Cloud

        # Esperar a que aparezcan los items de la lista
        try:
            print("   ⏳ Esperando carga de ofertas...")
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job-list-item")))
            self.random_sleep(2, 3) # Un poco más por seguridad, es una SPA pesada
        except:
            print("   ⚠️ No se detectaron ofertas o tardó mucho en cargar.")
            return

        # Buscamos todas las tarjetas de empleo
        job_cards = self.driver.find_elements(By.CLASS_NAME, "job-list-item")
        
        if not job_cards:
            print("   ⚠️ No se encontraron tarjetas de empleo.")
            return

        print(f"   -> Analizando {len(job_cards)} ofertas visibles...")

        for card in job_cards:
            try:
                # 1. Extraer Título
                # El título está en un span con clase 'job-tile__title'
                title_element = card.find_element(By.CLASS_NAME, "job-tile__title")
                title_text = title_element.text.lower()

                # 2. Extraer Link
                # El link está en un <a> con clase 'job-list-item__link'
                link_element = card.find_element(By.CLASS_NAME, "job-list-item__link")
                url_oferta = link_element.get_attribute("href")

                # Limpieza básica
                if not title_text or len(title_text) < 3:
                    continue

                # 3. Validación (usando lógica del padre BaseBot si existe, o manual)
                match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                if match_keyword:
                    # 🛑 VERIFICAR DUPLICADOS (HISTORIAL)
                    if not self.check_and_track(url_oferta):
                        continue

                    print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                    print(f"            🔗 URL: {url_oferta}")
                    
                    # Notificación Telegram
                    msg = (
                        f"✨ <b>¡NUEVA OFERTA EN ANDREANI!</b>\n\n"
                        f"📌 <b>Cargo:</b> {title_text.title()}\n"
                        f"🔑 <b>Match:</b> {match_keyword}\n"
                        f"🔗 <a href='{url_oferta}'>Ver Oferta</a>"
                    )
                    self.notify(msg)
                    
                    # Opcional: Si quisieras abrirla, pero el usuario pidió solo notificar y pasar link.
                    # No hacemos click().
                
            except Exception as e:
                # A veces el DOM cambia o el elemento no está listo
                # print(f"      debug: error parsing card: {e}") 
                continue

        print("   ✅ Escaneo de Andreani finalizado.")
