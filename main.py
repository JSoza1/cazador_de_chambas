import time
import sys

from src.config import CHECK_INTERVAL_MINUTES
from src.keywords_manager import get_positive_keywords, get_negative_keywords, get_language_keywords
from src.driver import get_driver
from src.notifications import send_telegram_message
from src.sites.bumeran import BumeranBot
from src.sites.computrabajo import ComputrabajoBot
from src.sites.empleosit import EmpleosITBot


def main():
    """
    Punto de entrada principal del bot.

    Ejecuta un ciclo infinito donde, en cada iteración:
    1. Inicializa el navegador.
    2. Corre cada bot de búsqueda secuencialmente.
    3. Cierra el navegador y espera el intervalo configurado.

    Durante la espera, el bot sigue escuchando respuestas de Telegram
    cada 60 segundos para procesar archivados de ofertas en tiempo real.
    """
    pos_list = get_positive_keywords()
    neg_list = get_negative_keywords()
    lan_list = get_language_keywords()

    print("====================================================")
    print("🤖 CAZADOR DE CHAMBAS - SISTEMA INICIADO")
    print("====================================================")
    print(f"✅ Palabras Positivas ({len(pos_list)}):")
    print(f"   {', '.join(sorted(pos_list))}")
    print(f"\n🚫 Palabras Negativas ({len(neg_list)}):")
    print(f"   {', '.join(sorted(neg_list))}")
    print(f"\n🌐 Filtros de Idioma ({len(lan_list)} frases activas):")
    print(f"   {', '.join(sorted(lan_list))}")
    print(f"\n⏲️  Intervalo de Espera: {CHECK_INTERVAL_MINUTES} minutos")
    print("====================================================")

    try:
        while True:
            from src.listener import check_telegram_replies

            # Procesamos respuestas pendientes de Telegram antes de iniciar
            check_telegram_replies()

            driver = get_driver()

            try:
                # --- BUMERAN ---
                print("\n🚀 PROCESANDO: BUMERAN")
                BumeranBot(driver).search()
                check_telegram_replies()

                # --- COMPUTRABAJO ---
                print("\n🚀 PROCESANDO: COMPUTRABAJO")
                ComputrabajoBot(driver).search()
                check_telegram_replies()

                # --- ANDREANI ---
                print("\n🚀 PROCESANDO: ANDREANI")
                from src.sites.andreani import AndreaniBot
                AndreaniBot(driver).search()
                check_telegram_replies()

                # --- EDUCACIÓN IT ---
                print("\n🚀 PROCESANDO: EDUCACIÓN IT")
                from src.sites.educacionit import EducacionITBot
                EducacionITBot(driver).search()
                check_telegram_replies()

                # --- BBVA ---
                print("\n🚀 PROCESANDO: BBVA")
                from src.sites.bbva import BBVABot
                BBVABot(driver).search()
                check_telegram_replies()

                # --- VICENTE LÓPEZ ---
                print("\n🚀 PROCESANDO: VICENTE LÓPEZ")
                from src.sites.vicentelopez import VicenteLopezBot
                VicenteLopezBot(driver).search()
                check_telegram_replies()

                # --- UTN TALENTIA ---
                print("\n🚀 PROCESANDO: UTN TALENTIA")
                from src.sites.talentia import TalentiaBot
                TalentiaBot(driver).search()
                check_telegram_replies()

                # --- EMPLEOS IT ---
                print("\n🚀 PROCESANDO: EMPLEOS IT")
                EmpleosITBot(driver).search()
                check_telegram_replies()

                # --- LINKEDIN ---
                # Requiere perfil persistente de Chrome con sesión activa.
                # Descomentar para usar en entorno PC (no compatible con Termux).
                # print("\n🚀 PROCESANDO: LINKEDIN")
                # from src.sites.linkedin import LinkedInBot
                # LinkedInBot(driver).search()
                # check_telegram_replies()

                print("\n✅ Ciclo finalizado exitosamente.")

                hours_wait = CHECK_INTERVAL_MINUTES / 60
                send_telegram_message(
                    f"🏁 <b>Ciclo de búsqueda finalizado.</b>\n"
                    f"💤 Durmiendo {int(hours_wait)}hs hasta el próximo turno."
                )

            except Exception as error:
                print(f"\n❌ Error durante la búsqueda: {error}")

            finally:
                # El bloque finally garantiza que el navegador siempre se cierra,
                # incluso si ocurrió un error en algún bot.
                print("🔒 Cerrando navegador para liberar memoria.")
                driver.quit()

            # Período de espera entre ciclos con escucha activa de Telegram.
            # Cada 60 segundos se procesan respuestas pendientes del usuario.
            print(f"💤 Durmiendo {CHECK_INTERVAL_MINUTES} minutos hasta el próximo turno...")

            total_wait_seconds = CHECK_INTERVAL_MINUTES * 60
            check_interval = 60
            elapsed = 0

            while elapsed < total_wait_seconds:
                try:
                    from src.listener import check_telegram_replies
                    check_telegram_replies()
                except Exception as e:
                    print(f"⚠️ Error chequeando Telegram en espera: {e}")

                time.sleep(check_interval)
                elapsed += check_interval

    except KeyboardInterrupt:
        print("\n👋 Bot detenido manualmente. Terminando ejecución.")
        sys.exit(0)


if __name__ == "__main__":
    main()
