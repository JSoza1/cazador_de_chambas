import time  # Librería estándar para gestión de tiempo
import sys   # Librería estándar para interacción con el sistema

# IMPORTACIONES LOCALES
# ----------------------------------------------------
# Importación de variables de configuración desde src/config.py
from src.config import SEARCH_KEYWORDS, CHECK_INTERVAL_MINUTES

# Función constructora del navegador
from src.driver import get_driver

# Clase del Bot específico de Bumeran
from src.sites.bumeran import BumeranBot
# Clase del Bot específico de Computrabajo
from src.sites.computrabajo import ComputrabajoBot

def main():
    """
    Función Principal (Main Loop).
    Orquestación del flujo del programa.
    """
    
    # 1. Mensaje de Inicialización
    print("========================================")
    print("🤖 JOB SEARCH AUTOMATION - INICIADO")
    print(f"📋 Keywords (Búsqueda): {SEARCH_KEYWORDS}")
    print(f"⏲️ Intervalo de Espera: {CHECK_INTERVAL_MINUTES} minutos")
    print("========================================")

    try:
        # Bucle Infinito de ejecución
        while True:
            # --- FASE 1: PREPARACIÓN ---
            # Inicialización del navegador
            driver = get_driver()
            
            # Si falla este try, se ejecuta el except (linea 54)
            try:
                # --- FASE 2: EJECUCIÓN ---
                
                # --- BUMERAN  ---
                print("\n🚀 PROCESANDO: BUMERAN")
                bot_bumeran = BumeranBot(driver)
                bot_bumeran.login()
                bot_bumeran.search()
                
                # --- COMPUTRABAJO ---
                print("\n🚀 PROCESANDO: COMPUTRABAJO")
                bot_computrabajo = ComputrabajoBot(driver)
                bot_computrabajo.login()
                bot_computrabajo.search()
                
                # --- ANDREANI ---
                print("\n🚀 PROCESANDO: ANDREANI")
                from src.sites.andreani import AndreaniBot
                bot_andreani = AndreaniBot(driver)
                bot_andreani.search()

                # --- EDUCACIÓN IT ---
                print("\n🚀 PROCESANDO: EDUCACIÓN IT")
                from src.sites.educacionit import EducacionITBot
                bot_educacionit = EducacionITBot(driver)
                bot_educacionit.search()

                # --- BBVA ---
                print("\n🚀 PROCESANDO: BBVA")
                from src.sites.bbva import BBVABot
                bot_bbva = BBVABot(driver)
                bot_bbva.search()

                # --- VICENTE LÓPEZ ---
                print("\n🚀 PROCESANDO: VICENTE LÓPEZ")
                from src.sites.vicentelopez import VicenteLopezBot
                bot_vl = VicenteLopezBot(driver)
                bot_vl.search()

                # --- UTN TALENTIA ---
                print("\n🚀 PROCESANDO: UTN TALENTIA")
                from src.sites.talentia import TalentiaBot
                bot_talentia = TalentiaBot(driver)
                bot_talentia.search()

                # --- EMPLEOS IT ---
                print("\n🚀 PROCESANDO: EMPLEOS IT")
                from src.sites.empleosit import EmpleosITBot
                bot_eit = EmpleosITBot(driver)
                bot_eit.search()

                print("\n✅ Ciclo finalizado exitosamente.")
                
            # EXPLICACIÓN DEL MANEJO DE ERRORES:
            # except: Atrapa el error del bloque 'try' en lugar de cerrar el programa.
            # Exception: Captura CUALQUIER tipo de error (Clase madre de errores).
            # as error: Guarda el detalle del error en la variable 'error' para poder imprimirlo.
            except Exception as error:
                # Captura de errores no fatales durante el proceso de búsqueda.
                # Se registra el error y se continúa con el siguiente ciclo.
                print(f"\n❌ Ocurrió un error no fatal durante la búsqueda: {error}")
            
            # finally: Este bloque se ejecuta SIEMPRE, sin importar si hubo éxito o error.
            # Su misión es garantizar que no queden procesos "zombies" consumiendo memoria.
            finally:
                # --- FASE 3: LIMPIEZA ---
                print("🔒 Cerrando navegador para liberar memoria.")
                # Cierre del navegador para liberar memoria.
                driver.quit()
            
            # Esperar para la siguiente ronda
            print(f"💤 Durmiendo {CHECK_INTERVAL_MINUTES} minutos hasta el próximo turno...")
            time.sleep(CHECK_INTERVAL_MINUTES * 60) # Convertimos minutos a segundos

    # EXPLICACIÓN DE CIERRE MANUAL:
    # KeyboardInterrupt: Es un TIPO DE ERROR específico que lanza Python cuando
    # el usuario presiona 'Ctrl + C' en la terminal para detener el script.
    # Al atraparlo, podemos cerrar el programa sin mostrar errores en pantalla.
    except KeyboardInterrupt as e:
        # Captura de interrupción manual (Ctrl + C)
        print("\n👋 Bot detenido manualmente. Terminando ejecución.")
        sys.exit(0)

# Solo ejecuta el bot si corres este archivo directamente.
# Evita que el bot arranque automaticamente si alguien importa 'main.py' en otro script.
if __name__ == "__main__":
    main()
