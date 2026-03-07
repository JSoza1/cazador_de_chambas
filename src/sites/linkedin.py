from src.sites.base import BaseBot
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from src.config import JOB_SEARCH_URLS, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS
from src.listener import check_telegram_replies
from src.keywords_manager import get_language_keywords
from src.history import history

class LinkedInBot(BaseBot):
    """
    Bot para búsqueda de empleo en LinkedIn.
    
    HERENCIA:
    Hereda de 'BaseBot' (src/sites/base.py), lo que le da acceso a métodos comunes
    como self.notify() para Telegram, self.driver para el navegador, etc.
    
    ESTRATEGIA:
    LinkedIn tiene medidas anti-bot muy fuertes. Para evitarlas, NO hacemos login
    con usuario/contraseña en cada ejecución. En su lugar, usamos un PERFIL DE CHROME
    PERSISTENTE (una carpeta donde Chrome guarda cookies).
    
    1. La primera vez, el usuario se loguea manualmente.
    2. Las cookies quedan guardadas en la carpeta 'profile'.
    3. En futuras ejecuciones, el bot ya entra 'logueado'.
    """
    
    def login(self):
        # Al usar perfil persistente, asumimos que ya está logueado o que 
        # el usuario lo hará manualmente si es necesario la primera vez.
        print("   ℹ️  Usando sesión de LinkedIn del perfil persistente.")
        pass

    def search(self):
        """
        Itera sobre las URLs configuradas y extrae ofertas.
        """
        # Notificación al iniciar el módulo LinkedIn
        self.notify("🤖 Buscando chamba por LinkedIn!")

        for url_index, base_url in enumerate(JOB_SEARCH_URLS):
            print(f"\n   🌍 [LinkedIn] Iniciando Búsqueda #{url_index + 1}")
            print(f"   🔗 URL: {base_url}")
            
            try:
                # Chequeo de comandos ANTES de empezar nueva ronda
                check_telegram_replies()
                
                print("   🌐 Navegando...")
                self.driver.get(base_url)
                time.sleep(5) # Espera inicial

                page_num = 1
                max_pages = 18 # Límite de seguridad
                
                fix_applied = False
                
                while page_num <= max_pages:
                    # =========================================================================
                    # 🌀 MANIOBRA "SALTO DE PÁGINA" (ANTI-BLOQUEO DE SCROLL)
                    # =========================================================================
                    # Problema: En la primera página, a veces LinkedIn "congela" el scroll
                    # o los elementos no cargan dinámicamente porque el foco del navegador
                    # no está bien establecido en modo automático.
                    #
                    # Solución: Forzamos una interacción real:
                    # 1. Bajamos al pie de página.
                    # 2. Vamos a la página 2.
                    # 3. Scrolleamos un poco en la página 2.
                    # 4. Volvemos a la página 1 con el botón "Anterior".
                    #
                    # Esto "despierta" los scripts de carga dinámica (Lazy Loading) de LinkedIn.
                    # Solo lo hacemos una vez al principio (if not fix_applied).
                    # =========================================================================
                    if page_num == 1 and not fix_applied:
                        try:
                            # Detectar entorno
                            is_android = "ANDROID_ROOT" in os.environ
                            maniobra_msg = "🔄 Maniobra Especial (PC)" if not is_android else "🔄 Maniobra Especial (Android/JS)"
                            print(f"      {maniobra_msg}: Ir a Pág 2 -> Scroll -> Volver...")
                            
                            # 1. Bajar al fondo
                            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                            time.sleep(2)
                            
                            # 2. Click 'Siguiente'
                            next_btn = self.driver.find_element(By.CSS_SELECTOR, "button.jobs-search-pagination__button--next")
                            
                            if is_android:
                                # ANDROID: Click nuclear con JS (ignora superposiciones)
                                self.driver.execute_script("arguments[0].click();", next_btn)
                            else:
                                # PC: Click normal
                                next_btn.click()
                                
                            wait_time = 8 if is_android else 4
                            time.sleep(wait_time)
                            
                            # 3. Scrollear un poco en Pág 2
                            body = self.driver.find_element(By.TAG_NAME, 'body')
                            for _ in range(5):
                                body.send_keys(Keys.PAGE_DOWN)
                                time.sleep(0.5)
                            time.sleep(1)
                            
                            # 4. Click 'Anterior' para volver a Pág 1
                            prev_btn = self.driver.find_element(By.CSS_SELECTOR, "button.jobs-search-pagination__button--previous")
                            
                            if is_android:
                                # ANDROID: Click nuclear con JS
                                self.driver.execute_script("arguments[0].click();", prev_btn)
                            else:
                                # PC: Click normal
                                prev_btn.click()
                                
                            print("      🔙 Volviendo a Pág 1...")
                            wait_time = 8 if is_android else 4
                            time.sleep(wait_time)
                            
                            fix_applied = True # ¡Listo! No lo volvemos a hacer en esta URL.
                        except Exception as e:
                            print(f"      ⚠️ No se pudo realizar la maniobra 1->2->1: {e}")

                            # Si falla, marcamos como hecho para no quedarnos en un bucle infinito
                            fix_applied = True

                    # Chequeo de comandos EN CADA PÁGINA
                    check_telegram_replies()
                    
                    print(f"\n   📄 [LinkedIn #{url_index + 1}] Procesando PÁGINA {page_num}...")
                    
                    # --- SCROLL GLOBAL CON TECLADO (El ganador 🏆) ---
                    # Probado que funciona mejor: enviar PAGE_DOWN al body directamente.
                    try:
                        print("      ⬇️ Scrolleando con teclado (Global)...")
                        
                        # Intento de foco: click en el contenedor de resultados (ayuda en página 1)
                        try:
                            self.driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list").click()
                        except:
                            pass

                        body = self.driver.find_element(By.TAG_NAME, 'body')
                        
                        # 8 pulsaciones de PAGE_DOWN para asegurar carga profunda
                        # Ajustamos velocidad para Android
                        is_android = "ANDROID_ROOT" in os.environ
                        scroll_wait = 1.6 if is_android else 0.8
                        final_wait = 5 if is_android else 2
                        
                        for k in range(8): 
                            body.send_keys(Keys.PAGE_DOWN)
                            time.sleep(scroll_wait) # Espera para carga de contenido (lazy loading)
                            
                        # Pequeña espera final
                        time.sleep(final_wait)
                            
                    except Exception as e:
                        print(f"   ⚠️ Error en scroll de teclado: {e}")
                    
                    # --- EXTRAYENDO TARJETAS ---
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
                    
                    print(f"   🔎 Analizando {len(job_cards)} tarjetas en esta página...")
                    
                    found_on_page = 0
                    
                    for card in job_cards:
                        try:
                            # Buscamos el título dentro de la tarjeta
                            title_element = card.find_element(By.CSS_SELECTOR, "a.job-card-container__link, a.job-card-list__title--link")
                            
                            title_text = title_element.text.strip().lower()
                            title_text = title_text.replace("\n", " ").replace("solicitud sencilla", "")
                            
                            link = title_element.get_attribute("href")
                            
                            if len(title_text) < 3: continue

                            # --- CHECK HISTORIAL ---
                            if not self.check_and_track(link):
                                # Si devuelve False, es que ya fue vista (o descartada por historial)
                                # Nota: check_and_track verifica history.is_seen internally
                                continue
                            
                            # --- FILTRADO ---
                            # Usamos la lógica de BaseBot si es compatible, o la custom si preferimos.
                            # BaseBot.validate_job_title devuelve la keyword si hizo match, o None.
                            # Pero BaseBot.validate_job_title NO maneja "solicitud sencilla" removal etc, 
                            # aunque ya lo hicimos arriba.
                            
                            match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)
                            
                            if match_keyword:
                                found_on_page += 1
                                print(f"      ✨ MATCH: {title_text}")

                                # --- FILTRO DE IDIOMA (panel lateral) ---
                                current_language_filters = get_language_keywords()
                                language_blocked = False
                                blocking_word = None

                                if current_language_filters:
                                    try:
                                        card.click()
                                        time.sleep(3)
                                        try:
                                            desc_element = self.driver.find_element(
                                                By.CSS_SELECTOR,
                                                ".jobs-description__content, .jobs-description, .job-view-layout"
                                            )
                                            description_text = desc_element.text.lower()
                                        except Exception:
                                            description_text = ""

                                        for lang_word in current_language_filters:
                                            if lang_word.lower() in description_text:
                                                language_blocked = True
                                                blocking_word = lang_word
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
                                msg = (
                                    f"✨ <b>MATCH DETECTADO (LinkedIn)</b>\n"
                                    f"📌 <b>{title_text.title()}</b>\n"
                                    f"🔗 <a href='{link}'>Ver Oferta</a>"
                                )
                                self.notify(msg)

                        except Exception:
                            continue

                    print(f"   ✅ Página {page_num} terminada. Matches nuevos: {found_on_page}")

                    # --- PAGINACIÓN ---
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, "button.jobs-search-pagination__button--next")
                        
                        if next_btn.is_enabled():
                            print("   ➡️ Avanzando a siguiente página...")
                            next_btn.click()
                            time.sleep(5) # Esperar carga de nueva página
                            page_num += 1
                        else:
                            print("   ⏹️ Botón 'Siguiente' deshabilitado. Fin de esta búsqueda.")
                            break
                    except Exception:
                        print("   ⏹️ No se encontró botón 'Siguiente'. Fin de esta búsqueda.")
                        break

            except Exception as e:
                print(f"   ❌ Error en búsqueda #{url_index + 1}: {e}")
                continue # Pasar a la siguiente URL si falla una
