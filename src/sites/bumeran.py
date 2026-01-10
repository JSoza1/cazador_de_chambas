from src.sites.base import BaseBot
from src.config import BUMERAN_EMAIL, BUMERAN_PASSWORD
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class BumeranBot(BaseBot):
    """
    Bot específico para Bumeran.
    Hereda de BaseBot, acceso a atributos self.driver, self.wait, etc.
    """
    
    def login(self):
        print("🔑 Navegando al login...")
        self.driver.get("https://www.bumeran.com.ar/login")
        self.random_sleep(2, 4)

        # DETECCIÓN DE SESIÓN:
        # Verificación de redirección automática tras acceso a /login.
        if "login" not in self.driver.current_url and "ingresar" not in self.driver.current_url:
            print(f"   ✅ Sesión activa detectada (URL actual: {self.driver.current_url})")
            return

        print("   -> Sesión inactiva. Iniciando autenticación...")

        # 1. Ingresar Email (Selector corregido: id="email")
        if self.type_text(By.ID, "email", BUMERAN_EMAIL):
            print("   -> Email ingresado")
        else:
            print("   ⚠️ No encontré el campo de email (id='email').")
            return 
            
        # 2. Ingresar Password (id="password")
        if self.type_text(By.ID, "password", BUMERAN_PASSWORD):
            print("   -> Password ingresado")
        
        # 3. Clic en Botón Ingresar (id="ingresar")
        # Esperamos un poco para asegurarnos de que el botón se habilite (deje de estar disabled)
        self.random_sleep(1, 2)
        print("   -> Clickeando botón Ingresar...")
        self.safe_click(By.ID, "ingresar")
        
        self.random_sleep(5, 8) # Esperamos a que cargue la página inicial
        print("   ✅ Proceso de login finalizado.")

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
        self.notify(f"🤖 Iniciando búsqueda de Chamba")
        
        target_base_url = "https://www.bumeran.com.ar/empleos-area-tecnologia-sistemas-y-telecomunicaciones-publicacion-menor-a-5-dias.html"
        MAX_PAGES = 5
        
        for page_num in range(1, MAX_PAGES + 1):
            # Construimos URL
            current_url = target_base_url if page_num == 1 else f"{target_base_url}?page={page_num}"
            
            print(f"\n   📄 --- PROCESANDO PÁGINA {page_num} ---")
            
            if current_url not in self.driver.current_url:
                self.driver.get(current_url)
                self.random_sleep(2, 4)

            # --- Detección de Tarjetas ---
            # Espera relajada. Se intenta buscar elementos incluso si falla la espera explícita.
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/empleos/') and contains(@href, '.html')]")))
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
                    url_oferta = link_element.get_attribute("href")
                    
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
                    
                    # ¡MATCH!
                    print(f"         ✨ ¡MATCH! Coincide con '{match_keyword}'")
                    print(f"            🔗 URL: {url_oferta}")
                    self.notify(f"✨ <b>¡NUEVA OFERTA ENCONTRADA!</b>\n\n📌 <b>Cargo:</b> {title_text.title()}\n🔑 <b>Match:</b> {match_keyword}\n🔗 <a href='{url_oferta}'>Ver Oferta</a>")
                    
                    # Abrir y procesar
                    self.driver.execute_script(f"window.open('{url_oferta}', '_blank');")
                    self.random_sleep(2, 3)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    self.apply_to_current_job()
                    
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


