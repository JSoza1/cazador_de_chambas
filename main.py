import time  # Librería estándar para gestión de tiempo
import sys   # Librería estándar para interacción con el sistema

# IMPORTACIONES LOCALES
# ----------------------------------------------------
# Importación de variables de configuración desde src/config.py
from src.config import SEARCH_KEYWORDS, CHECK_INTERVAL_MINUTES

# Función constructora del navegador
from src.driver import get_driver
from src.notifications import send_telegram_message

# Clase del Bot específico de Bumeran
from src.sites.bumeran import BumeranBot
# Clase del Bot específico de Computrabajo
from src.sites.computrabajo import ComputrabajoBot
from src.sites.empleosit import EmpleosITBot

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
            # --- FASE 0: ESCUCHA DE TELEGRAM ---
            # Chequeamos si el usuario respondió "ya lo vi" a alguna oferta anterior
            from src.listener import check_telegram_replies
            check_telegram_replies()

            # --- FASE 1: PREPARACIÓN ---
            # Inicialización del navegador
            driver = get_driver()
            
            # Si falla este try, se ejecuta el except (linea 117)
            try:
                # --- FASE 2: EJECUCIÓN ---
                
                # --- BUMERAN  ---
                # print("\n🚀 PROCESANDO: BUMERAN")
                # bot_bumeran = BumeranBot(driver)
                # bot_bumeran.login()
                # bot_bumeran.search()
                # check_telegram_replies() # 👂 Check Telegram
                
                # # --- COMPUTRABAJO ---
                # print("\n🚀 PROCESANDO: COMPUTRABAJO")
                # bot_computrabajo = ComputrabajoBot(driver)
                # bot_computrabajo.login()
                # bot_computrabajo.search()
                # check_telegram_replies() # 👂 Check Telegram
                
                # # --- ANDREANI ---
                # print("\n🚀 PROCESANDO: ANDREANI")
                # from src.sites.andreani import AndreaniBot
                # bot_andreani = AndreaniBot(driver)
                # bot_andreani.search()
                # check_telegram_replies() # 👂 Check Telegram

                # # --- EDUCACIÓN IT ---
                # print("\n🚀 PROCESANDO: EDUCACIÓN IT")
                # from src.sites.educacionit import EducacionITBot
                # bot_educacionit = EducacionITBot(driver)
                # bot_educacionit.search()
                # check_telegram_replies() # 👂 Check Telegram

                # # --- BBVA ---
                # print("\n🚀 PROCESANDO: BBVA")
                # from src.sites.bbva import BBVABot
                # bot_bbva = BBVABot(driver)
                # bot_bbva.search()
                # check_telegram_replies() # 👂 Check Telegram

                # # --- VICENTE LÓPEZ ---
                # print("\n🚀 PROCESANDO: VICENTE LÓPEZ")
                # from src.sites.vicentelopez import VicenteLopezBot
                # bot_vl = VicenteLopezBot(driver)
                # bot_vl.search()
                # check_telegram_replies() # 👂 Check Telegram

                # # --- UTN TALENTIA ---
                # print("\n🚀 PROCESANDO: UTN TALENTIA")
                # from src.sites.talentia import TalentiaBot
                # bot_talentia = TalentiaBot(driver)
                # bot_talentia.search()
                # check_telegram_replies() # 👂 Check Telegram

                # # --- EMPLEOS IT ---
                # print("\n🚀 PROCESANDO: EMPLEOS IT")
                # bot_eit = EmpleosITBot(driver)
                # bot_eit.search()
                # check_telegram_replies() # 👂 Check Telegram

                # --- LINKEDIN ---
                print("\n🚀 PROCESANDO: LINKEDIN")
                from src.sites.linkedin import LinkedInBot
                bot_linkedin = LinkedInBot(driver)
                # Login omitido: Se usa perfil persistente
                bot_linkedin.search()
                check_telegram_replies() # 👂 Check Telegram

                print("\n✅ Ciclo finalizado exitosamente.")
                
                # Notificación de fin de ciclo
                hours_wait = CHECK_INTERVAL_MINUTES / 60
                msg_end = (
                    f"🏁 <b>Ciclo de búsqueda finalizado.</b>\n"
                    f"💤 Durmiendo {int(hours_wait)}hs hasta el próximo turno."
                )
                send_telegram_message(msg_end)
                
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
            
            # Esperar para la siguiente ronda (con escucha activa)
            print(f"💤 Durmiendo {CHECK_INTERVAL_MINUTES} minutos hasta el próximo turno...")
            
            # Convertimos minutos a segundos
            total_wait_seconds = CHECK_INTERVAL_MINUTES * 60
            check_interval = 60 # Revisar Telegram cada 60 segundos
            
            elapsed = 0
            while elapsed < total_wait_seconds:
                # Chequeo periódico de respuestas "ya lo vi"
                try:
                    from src.listener import check_telegram_replies
                    check_telegram_replies()
                except Exception as e:
                    print(f"⚠️ Error chequeando Telegram en espera: {e}")

                time.sleep(check_interval)
                elapsed += check_interval
                
                # Feedback de progreso opcional
                # remaining = (total_wait_seconds - elapsed) / 60
                # print(f"   💤 Restan {int(remaining)} minutos...")

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
