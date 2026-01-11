from src.sites.base import BaseBot
from src.config import COMPUTRABAJO_EMAIL, COMPUTRABAJO_PASSWORD
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time

class ComputrabajoBot(BaseBot):
    """
    Bot específico para Computrabajo (Argentina).
    """

    def login(self):
        print("🔑 COMPUTRABAJO: Iniciando proceso de login...")
        
        # 1. Vamos a la home
        self.driver.get("https://ar.computrabajo.com/")
        self.random_sleep(2, 4)

        # 2. Verificamos si ya estamos logueados (buscando menú de usuario o algo similar)
        if "candidato.ar.computrabajo.com" in self.driver.current_url:
             print(f"   ✅ Sesión activa detectada.")
             return

        # 3. Buscamos el botón "Ingresar"
        print("   -> Buscando botón de ingreso...")
        try:
            # PASO 1: Abrir el menú lateral (span con data-login-button-desktop)
            menu_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-login-button-desktop]")
            menu_btn.click()
            self.random_sleep(1, 2)
            
            # PASO 2: Clic en "Ingresar" del menú desplegado (span con data-access-menu)
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-access-menu]")
            login_btn.click()
            
        except Exception as e:
            print(f"   ⚠️ Falló el click en menú (Error: {e}). Intentando URL directa...")
            self.driver.get("https://candidato.ar.computrabajo.com/login/")
        
        self.random_sleep(3, 5)

        # 4. Llenar formulario (Login en dos pasos)
        print("   -> Llenando credenciales (Paso 1: Email)...")
        
        # --- PASO A: Email ---
        if not self.type_text(By.ID, "Email", COMPUTRABAJO_EMAIL):
            print("   ❌ No pude ingresar el Email.")
            return

        # Clic en "Continuar" para ir al password
        self.random_sleep(1, 2)
        print("   -> Click 'Continuar'...")
        if not self.safe_click(By.ID, "continueWithMailButton"):
             print("   ❌ No encontré botón 'Continuar'.")
             return
             
        self.random_sleep(2, 4) # Esperar transición

        # --- PASO B: Password ---
        print("   -> Llenando credenciales (Paso 2: Password)...")
        # El campo password (id="password") aparece después
        if not self.type_text(By.ID, "password", COMPUTRABAJO_PASSWORD):
             print("   ❌ No pude ingresar el Password.")
             return

        # Botón Iniciar Sesión (id="btnSubmitPass")
        self.random_sleep(1, 2)
        print("   -> Click 'Iniciar Sesión'...")
        self.safe_click(By.ID, "btnSubmitPass")

        self.random_sleep(5, 8)
        print("   ✅ Login finalizado (o intento completado).")


    def search(self, _=None):
        """
        Búsqueda de ofertas en Computrabajo.
        """
        from src.config import SEARCH_KEYWORDS as RAW_SEARCH, NEGATIVE_KEYWORDS as RAW_NEG
        
        SEARCH_KEYWORDS = [k.lower() for k in RAW_SEARCH]
        NEGATIVE_KEYWORDS = [k.lower() for k in RAW_NEG]

        print(f"🔍 COMPUTRABAJO: Iniciando búsqueda... {SEARCH_KEYWORDS}")
        self.notify(f"🤖 Buscando chamba por Computrabajo!")

        # Zonas de búsqueda definidas por el usuario
        ZONES_URLS = [
            "https://ar.computrabajo.com/empleos-de-informatica-y-telecom-en-capital-federal?pubdate=7&by=publicationtime",
            "https://ar.computrabajo.com/empleos-de-informatica-y-telecom-en-buenos-aires-gba?pubdate=7&by=publicationtime"
        ]
        
        MAX_PAGES = 5

        for zone_index, base_url in enumerate(ZONES_URLS):
            print(f"\n🌍 --- ZONA {zone_index + 1}: {base_url} ---")
            
            for page in range(1, MAX_PAGES + 1):
                # Construcción de URL con paginación
                # Si es p=1, la URL base sirve. Si es p>1, agregamos &p=X
                current_url = base_url if page == 1 else f"{base_url}&p={page}"
                
                print(f"   📄 Buscando por PÁGINA {page}")
                
                self.driver.get(current_url)
                self.random_sleep(3, 5)

                # Selectores de tarjetas de empleo
                articles = self.driver.find_elements(By.TAG_NAME, "article")

                if not articles:
                    print(f"   ⚠️ Fin de resultados en página {page}. Pasando a siguiente zona.")
                    break # Salimos del bucle de páginas, vamos a la siguiente zona

                print(f"   -> Encontré {len(articles)} posibles ofertas.")
                
                original_window = self.driver.current_window_handle

                for art in articles:
                    try:
                        # 0. Chequeo de "Ya postulado"
                        # El HTML tiene: <span class="tag postulated hide" applied-offer-tag="">
                        # Si NO tiene la clase "hide", es que está visible y ya nos postulamos.
                        try:
                            # Buscamos si existe el tag de postulado visible
                            applied_tag = art.find_elements(By.CSS_SELECTOR, "span.tag.postulated:not(.hide)")
                            if applied_tag:
                                #print("      (Saltando: Ya postulado anteriormente)")
                                continue
                        except:
                            pass

                        # Extraer Título y Link
                        try:
                            title_elem = art.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a")
                            title_text = title_elem.text
                            link_url = title_elem.get_attribute("href")
                        except:
                           continue

                        # Validar con nuestra lógica centralizada
                        match = self.validate_job_title(title_text, SEARCH_KEYWORDS, NEGATIVE_KEYWORDS)
                        
                        if match:
                            print(f"      ✨ MATCH: {title_text} ({match})")
                            self.notify(f"✨ <b>COMPUTRABAJO MATCH!</b>\n\n📌 {title_text}\n🔗 {link_url}")
                            
                            # Abrir oferta
                            self.driver.execute_script(f"window.open('{link_url}', '_blank');")
                            self.random_sleep(2, 4)
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            
                            # Intentar postular
                            self.apply_to_current_job() 
                            
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            
                    except Exception as e:
                        print(f"      ❌ Error analizando tarjeta: {e}")
                        continue

    def apply_to_current_job(self):
        """
        Intenta postularse a la oferta abierta en la pestaña actual.
        """
        print("      🚀 Iniciando intento de postulación...")
        try:
            # Buscamos el botón "Postularme"
            # Selector basado en investigación: span.b_primary.big que contiene "Postularme"
            # Ojo: A veces es un 'input' o 'button'. Usaremos XPath por texto para ser flexibles.
            
            apply_btn = None
            try:
                apply_btn = self.driver.find_element(By.XPATH, "//span[contains(@class, 'b_primary') and contains(text(), 'Postularme')]")
            except:
                try:
                    # Intento alternativo por selector CSS directo
                    apply_btn = self.driver.find_element(By.CSS_SELECTOR, "span[data-apply-ac]")
                except:
                    pass

            if apply_btn:
                print("      ✅ Botón 'Postularme' encontrado.")
                # apply_btn.click() # DESCOMENTAR PARA EJECUCIÓN REAL
                print("      🚧 (Simulación) Click en Postular no ejecutado.")
                self.notify("      🚧 Simulación: Encontré el botón de postular.")
                self.random_sleep(2, 3)
                
                # OJO: Computrabajo a veces pide preguntas extra después de postular.
                # Eso requeriría una lógica más compleja de "responder preguntas".
            else:
                print("      ⚠️ No encontré el botón 'Postularme' (¿Ya postulado? ¿Login perdido?)")

        except Exception as e:
            print(f"      ❌ Error al intentar postular: {e}")
