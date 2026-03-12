from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


class TalentiaBot(BaseBot):
    """
    Bot de búsqueda para UTN Talentia (utnba.talentia.com).

    Talentia es una SPA construida con bubble.io, por lo que la paginación
    se maneja via clicks en el botón "Siguiente" en lugar de cambios de URL.

    Para cada oferta relevante, el bot navega al detalle abriendo una nueva
    pestaña para extraer la URL canónica, que luego se usa para historial
    y notificación.
    """

    def login(self):
        pass  # No requiere autenticación

    def search(self, _=None):
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG

        SEARCH_KEYWORDS   = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print("🔍 Iniciando escaneo en UTN Talentia...")
        self.notify("🤖 Buscando chamba por UTN Talentia!")

        url       = "https://utnba.talentia.com/portal/offers"
        MAX_PAGES = 5

        self.driver.get(url)
        self.random_sleep(5, 8)  # Espera extendida para que la SPA termine de renderizar

        for page in range(1, MAX_PAGES + 1):
            print(f"\n   📄 Buscando por PÁGINA {page}")

            try:
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".bubble-element.Group.cmnsr")
                ))
                self.random_sleep(2, 3)
            except Exception:
                print("   ⚠️ No se detectaron tarjetas (o fin de carga).")
                break

            cards = self.driver.find_elements(
                By.CSS_SELECTOR, ".clickable-element.bubble-element.Group.cmnsr"
            )

            if not cards:
                # Selector alternativo para variaciones de la SPA
                cards = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'bubble-element') and contains(@class, 'Group')]"
                    "[.//div[contains(text(), 'híbrido') or contains(text(), 'remoto') "
                    "or contains(text(), 'presencial')]]"
                )

            print(f"   -> Encontré {len(cards)} posibles ofertas...")

            for card in cards:
                try:
                    try:
                        title_node = card.find_element(By.CSS_SELECTOR, ".bubble-element.Text.cmnsy")
                        title_text = title_node.text.strip()
                    except Exception:
                        title_text = card.text.split("\n")[0].strip()

                    if not title_text or len(title_text) < 3:
                        continue

                    match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                    if match_keyword:
                        # Abrimos el detalle en una nueva pestaña para obtener la URL canónica.
                        url_oferta = "https://utnba.talentia.com/portal/offers"

                        try:
                            print(f"         🔍 Extrayendo URL específica para '{title_text}'...")
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", card
                            )
                            self.random_sleep(1, 2)
                            card.click()
                            self.random_sleep(2, 3)

                            btn_full = self.wait.until(EC.element_to_be_clickable(
                                (By.XPATH, "//div[contains(text(), 'Ver pantalla completa')]")
                            ))

                            curr_handles = self.driver.window_handles
                            btn_full.click()
                            self.random_sleep(2, 3)

                            new_handles = self.driver.window_handles

                            if len(new_handles) > len(curr_handles):
                                new_tab = [h for h in new_handles if h not in curr_handles][0]
                                self.driver.switch_to.window(new_tab)
                                self.random_sleep(1, 2)
                                url_oferta = normalize_url(self.driver.current_url)
                                self.driver.close()
                                self.driver.switch_to.window(curr_handles[0])
                                print(f"         🔗 URL encontrada: {url_oferta}")
                            else:
                                print("         ⚠️ No se abrió nueva pestaña.")

                        except Exception as e:
                            print(f"         ⚠️ No se pudo extraer URL real: {e}")
                            try:
                                self.driver.switch_to.window(self.driver.window_handles[0])
                            except Exception:
                                pass

                        # Usamos la URL real si es de una oferta específica; sino,
                        # construimos un ID único basado en el título.
                        track_id = url_oferta if "detalle_oferta" in url_oferta \
                            else f"talentia://{title_text.replace(' ', '_')}"

                        if not self.check_and_track(track_id):
                            continue

                        print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                        print(f"            🔗 Portal: {url_oferta}")

                        lang_blocked, lang_word = self.check_language_in_description(url_oferta)
                        if lang_blocked:
                            print(f"         🌐 ──────────────────────────────")
                            print(f"         🌐 IDIOMA FILTRADO (Talentia)")
                            print(f"            📌 Título  : {title_text.title()}")
                            print(f"            🔍 Palabra : '{lang_word}'")
                            print(f"         🌐 ──────────────────────────────")
                            continue

                        self.notify(
                            f"✨ <b>¡NUEVA OFERTA EN UTN TALENTIA!</b>\n\n"
                            f"📌 <b>Cargo:</b> {title_text}\n"
                            f"🔑 <b>Match:</b> {match_keyword}\n"
                            f"🔗 <a href='{url_oferta}'>Ir al Portal</a>"
                        )

                except Exception:
                    continue

            # Paginación: click en "Siguiente" para cargar el próximo lote de tarjetas
            if page < MAX_PAGES:
                print("   -> Buscando botón 'Siguiente'...")
                try:
                    next_btn = self.driver.find_element(
                        By.XPATH, "//div[contains(text(), 'Siguiente')]"
                    )

                    if not next_btn.is_displayed():
                        print("   ⚠️ Botón Siguiente no visible. Fin.")
                        break

                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                    self.random_sleep(1, 2)
                    next_btn.click()
                    print("   -> Click realizado. Esperando carga...")
                    self.random_sleep(4, 6)

                except Exception as e:
                    print(f"   ⚠️ No se pudo avanzar de página: {e}")
                    break

        print("   ✅ Escaneo de UTN Talentia finalizado.")
