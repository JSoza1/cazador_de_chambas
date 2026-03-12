from src.sites.base import BaseBot
from src.history import normalize_url
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time

class BumeranBot(BaseBot):
    """
    Bot específico para Bumeran.
    Hereda de BaseBot, acceso a atributos self.driver, self.wait, etc.
    """

    def search(self, _=None):
        """
        Búsqueda de ofertas recorriendo páginas y comparando contra
        todas las palabras clave definidas en config.py.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        # Normalización a minúsculas para evitar inconsistencias
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]
        

        print(f"🔍 Iniciando escaneo inteligente (keywords: {SEARCH_KEYWORDS})")
        self.notify(f"🤖 Buscando chamba por Bumeran!")
        
        target_base_url = "https://www.bumeran.com.ar/empleos-area-tecnologia-sistemas-y-telecomunicaciones-publicacion-menor-a-5-dias.html"
        MAX_PAGES = 10
        
        for page_num in range(1, MAX_PAGES + 1):
            # Construimos URL
            current_url = target_base_url if page_num == 1 else f"{target_base_url}?page={page_num}"
            
            print(f"\n   📄 Buscando por PÁGINA {page_num}")
            
            if current_url not in self.driver.current_url:
                self.driver.get(current_url)
                self.random_sleep(2, 4)

            # --- Detección de Tarjetas ---
            # Espera relajada. Se intenta buscar elementos incluso si falla la espera explícita.
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/empleos/') and contains(@href, '.html')]")))
            except:
                pass 
            
            # Buscamos enlaces de empleo
            job_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/empleos/') and contains(@href, '.html')]")
            
            if not job_links:
                print(f"   ⚠️ No encontré ofertas en pág {page_num}. Terminando.")
                break 
            
            print(f"   -> Analizando {len(job_links)} ofertas...")
            
            original_window = self.driver.current_window_handle
            
            # --- Análisis de cada oferta ---
            for index, link_element in enumerate(job_links):
                try:
                    # Recuperamos el link (por si se pierde la referencia, aunque raro)
                    url_oferta = normalize_url(link_element.get_attribute("href"))
                    
                    # Intentamos sacar el título
                    title_text = ""
                    try:
                        title_text = link_element.find_element(By.TAG_NAME, "h2").text.lower()
                    except:
                        title_text = link_element.text.split("\n")[0].lower() # Primer renglón como fallback

                    # Limpieza
                    if len(title_text) < 3: continue
                    
                    
                    # Validación centralizada desde BaseBot
                    match_keyword = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)
                    
                    if not match_keyword:
                        continue 
                    
                    # 🛑 VERIFICAR DUPLICADOS (HISTORIAL)
                    if not self.check_and_track(url_oferta):
                        continue

                    # ¡MATCH!
                    print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                    print(f"            🔗 URL: {url_oferta}")

                    # --- FILTRO DE IDIOMA ---
                    lang_blocked, lang_word = self.check_language_in_description(url_oferta)
                    if lang_blocked:
                        print(f"         🌐 ──────────────────────────────")
                        print(f"         🌐 IDIOMA FILTRADO (Bumeran)")
                        print(f"            📌 Título  : {title_text.title()}")
                        print(f"            🔍 Palabra : '{lang_word}'")
                        print(f"            🔗 Link    : {url_oferta[:80]}...")
                        print(f"         🌐 ──────────────────────────────")
                        continue

                    self.notify(f"✨ <b>¡NUEVA OFERTA ENCONTRADA!</b>\n\n📌 <b>Cargo:</b> {title_text.title()}\n🔑 <b>Match:</b> {match_keyword}\n🔗 <a href='{url_oferta}'>Ver Oferta</a>")
                    
                    # Abrir y procesar
                    self.driver.execute_script(f"window.open('{url_oferta}', '_blank');")
                    self.random_sleep(2, 3)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    # self.apply_to_current_job()
                    
                    # Cerrar y volver
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    
                except Exception as e:
                    print(f"      ❌ Error al procesar link: {e}")
                    # Recuperación de ventana
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
                    continue

    def apply_to_current_job(self):
        """
        Intenta postularse a la oferta que está abierta actualmente en pantalla.
        """
        try:
             # Buscamos el botón "Postularme" con las clases que identificamos
             # Botón: <button ... class="sc-bryTEL ...">Postulación rápida...
            
            # Opción A: Por Texto (Más seguro)
            # Inicializamos variable como None para evitar errores
            apply_btn = None
            try:
                # Se intenta llenar el valor de la variable con el botón encontrado
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Postulación rápida')]")
            except:
                pass
            
            # Opción B: Por Clase (Si el texto falla)
            if not apply_btn:
                try:
                    # Se intenta llenar el valor de la variable con el botón encontrado
                    apply_btn = self.driver.find_element(By.CSS_SELECTOR, "button.sc-bryTEL")
                except:
                    pass

            # Si se encontró el botón, se usa el metodo .click() de selenium
            if apply_btn:
                print("      🚀 Botón 'Postulación rápida' encontrado.")
                # apply_btn.click() # DESCOMENTAR PARA EJECUCIÓN REAL
                print("      ✅ (Simulación) Click realizado exitosamente.")
                self.random_sleep(2, 4)
            else:
                print("      😓 No encontré botón de postulación (¿Ya postulado o botón distinto?).")
                
        except Exception as e:
            print(f"      ❌ Error al intentar postular en detalle: {e}")


