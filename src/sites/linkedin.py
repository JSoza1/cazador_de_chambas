from src.sites.base import BaseBot
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from src.config import JOB_SEARCH_URLS, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS
from src.listener import check_telegram_replies
from src.keywords_manager import get_language_keywords
from src.history import history, normalize_url


class LinkedInBot(BaseBot):
    """
    Bot de búsqueda para LinkedIn.

    LinkedIn implementa medidas anti-automatización avanzadas. Para mantener
    la sesión activa se utiliza un perfil de Chrome persistente (./profile/):
    el usuario inicia sesión manualmente la primera vez y las cookies se
    conservan entre ejecuciones.

    Para cada URL configurada en JOB_SEARCH_URLS, el bot realiza una maniobra
    de "salto 1→2→1" en la primera página para activar el lazy loading de
    LinkedIn y garantizar que todos los resultados se rendericen correctamente.
    Luego extrae tarjetas de empleo paginando hasta max_pages o hasta que el
    botón "Siguiente" esté deshabilitado.

    El filtro de idioma se aplica leyendo el panel lateral de descripción sin
    abrir una nueva pestaña, lo que es más eficiente en LinkedIn.
    """

    def login(self):
        """Sesión gestionada via perfil persistente. No se requiere acción."""
        print("   ℹ️  Usando sesión de LinkedIn del perfil persistente.")

    def search(self):
        """
        Recorre todas las URLs de búsqueda configuradas y procesa las ofertas.
        """
        self.notify("🤖 Buscando chamba por LinkedIn!")

        for url_index, base_url in enumerate(JOB_SEARCH_URLS):
            print(f"\n   🌍 [LinkedIn] Búsqueda #{url_index + 1}")
            print(f"   🔗 URL: {base_url}")

            try:
                check_telegram_replies()

                self.driver.get(base_url)
                time.sleep(5)

                page_num    = 1
                max_pages   = 18
                fix_applied = False

                while page_num <= max_pages:
                    # Maniobra de activación de lazy loading (solo en la primera página).
                    # Navegar a la página 2 y volver a la 1 fuerza a LinkedIn a renderizar
                    # dinámicamente todos los resultados de la primera página.
                    if page_num == 1 and not fix_applied:
                        try:
                            is_android  = "ANDROID_ROOT" in os.environ
                            maniobra_msg = "🔄 Activando carga dinámica (PC)" if not is_android else "🔄 Activando carga dinámica (Android/JS)"
                            print(f"      {maniobra_msg}: Pág 1 → 2 → 1...")

                            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                            time.sleep(2)

                            next_btn = self.driver.find_element(
                                By.CSS_SELECTOR, "button.jobs-search-pagination__button--next"
                            )

                            if is_android:
                                self.driver.execute_script("arguments[0].click();", next_btn)
                            else:
                                next_btn.click()

                            time.sleep(8 if is_android else 4)

                            body = self.driver.find_element(By.TAG_NAME, "body")
                            for _ in range(5):
                                body.send_keys(Keys.PAGE_DOWN)
                                time.sleep(0.5)
                            time.sleep(1)

                            prev_btn = self.driver.find_element(
                                By.CSS_SELECTOR, "button.jobs-search-pagination__button--previous"
                            )

                            if is_android:
                                self.driver.execute_script("arguments[0].click();", prev_btn)
                            else:
                                prev_btn.click()

                            print("      🔙 Volviendo a Pág 1...")
                            time.sleep(8 if is_android else 4)

                        except Exception as e:
                            print(f"      ⚠️ No se pudo completar la maniobra 1→2→1: {e}")
                        finally:
                            fix_applied = True

                    check_telegram_replies()
                    print(f"\n   📄 [LinkedIn #{url_index + 1}] Procesando PÁGINA {page_num}...")

                    # Scroll progresivo para activar la carga de tarjetas restantes.
                    # LinkedIn usa lazy loading: el contenido aparece al scrollear.
                    try:
                        print("      ⬇️ Scrolleando para cargar contenido...")
                        try:
                            self.driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list").click()
                        except Exception:
                            pass

                        is_android  = "ANDROID_ROOT" in os.environ
                        scroll_wait = 1.6 if is_android else 0.8
                        final_wait  = 5 if is_android else 2
                        body        = self.driver.find_element(By.TAG_NAME, "body")

                        for _ in range(8):
                            body.send_keys(Keys.PAGE_DOWN)
                            time.sleep(scroll_wait)

                        time.sleep(final_wait)

                    except Exception as e:
                        print(f"   ⚠️ Error en scroll: {e}")

                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
                    print(f"   🔎 Analizando {len(job_cards)} tarjetas en esta página...")

                    found_on_page = 0

                    for card in job_cards:
                        try:
                            title_element = card.find_element(
                                By.CSS_SELECTOR,
                                "a.job-card-container__link, a.job-card-list__title--link",
                            )

                            title_text = title_element.text.strip().lower()
                            title_text = title_text.replace("\n", " ").replace("solicitud sencilla", "")
                            link       = normalize_url(title_element.get_attribute("href"))

                            if len(title_text) < 3:
                                continue

                            if not self.check_and_track(link):
                                continue

                            match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)

                            if not match_keyword:
                                continue

                            found_on_page += 1
                            print(f"      ✨ MATCH: {title_text}")

                            # Filtro de idioma: se lee el panel lateral de descripción
                            # sin abrir nueva pestaña (LinkedIn lo renderiza en el mismo DOM).
                            current_language_filters = get_language_keywords()
                            language_blocked = False
                            blocking_word    = None

                            if current_language_filters:
                                try:
                                    card.click()
                                    time.sleep(3)
                                    try:
                                        desc_element     = self.driver.find_element(
                                            By.CSS_SELECTOR,
                                            ".jobs-description__content, .jobs-description, .job-view-layout",
                                        )
                                        description_text = desc_element.text.lower()
                                    except Exception:
                                        description_text = ""

                                    for lang_word in current_language_filters:
                                        if lang_word.lower() in description_text:
                                            language_blocked = True
                                            blocking_word    = lang_word
                                            break
                                except Exception as e:
                                    print(f"      ⚠️ Error leyendo descripción: {e}")

                            if language_blocked:
                                print(f"      🌐 ──────────────────────────────")
                                print(f"      🌐 IDIOMA FILTRADO (LinkedIn)")
                                print(f"         📌 Título  : {title_text.title()}")
                                print(f"         🔍 Palabra : '{blocking_word}'")
                                print(f"         🔗 Link    : {link[:80]}...")
                                print(f"      🌐 ──────────────────────────────")
                                history.add_job(link)
                                continue

                            history.add_job(link)
                            self.notify(
                                f"✨ <b>MATCH DETECTADO (LinkedIn)</b>\n"
                                f"📌 <b>{title_text.title()}</b>\n"
                                f"🔗 <a href='{link}'>Ver Oferta</a>"
                            )

                        except Exception:
                            continue

                    print(f"   ✅ Página {page_num} terminada. Matches nuevos: {found_on_page}")

                    # Paginación: avanzar a la siguiente página si el botón está activo
                    try:
                        next_btn = self.driver.find_element(
                            By.CSS_SELECTOR, "button.jobs-search-pagination__button--next"
                        )
                        if next_btn.is_enabled():
                            print("   ➡️ Avanzando a siguiente página...")
                            next_btn.click()
                            time.sleep(5)
                            page_num += 1
                        else:
                            print("   ⏹️ Fin de resultados para esta búsqueda.")
                            break
                    except Exception:
                        print("   ⏹️ No se encontró botón 'Siguiente'. Fin de esta búsqueda.")
                        break

            except Exception as e:
                print(f"   ❌ Error en búsqueda #{url_index + 1}: {e}")
                continue
