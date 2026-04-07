import sys
import os
import subprocess

# ============================================================================
# GESTIÓN DE DEPENDENCIAS (auto-sanante)
# ============================================================================

def instalar_dependencias(python_exe=None):
    """
    Instala las dependencias necesarias usando el intérprete indicado.
    Prueba varias estrategias hasta que una funcione.
    """
    if python_exe is None:
        python_exe = sys.executable

    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    req = os.path.join(workspace_dir, "requirements.txt")

    if not os.path.exists(req):
        print(f"[ERROR] No se encontró requirements.txt en {workspace_dir}")
        return False

    print(f"\n[INSTALANDO] Dependencias en {python_exe}...")
    
    # Estrategias de instalación
    estrategias = [
        f'"{python_exe}" -m pip install -r "{req}" -q',
        f'"{python_exe}" -m pip install -r "{req}" --break-system-packages -q',
        f'"{python_exe}" -m pip install -r "{req}" --user -q',
    ]

    for cmd in estrategias:
        try:
            if os.system(cmd) == 0:
                print("[OK] Dependencias instaladas correctamente.\n")
                return True
        except Exception:
            continue

    return False


def dependencias_ok(python_exe=None):
    """
    Verifica que las dependencias críticas estén disponibles.
    """
    check_cmd = 'import selenium, dotenv, requests'
    if python_exe is None:
        try:
            import selenium, dotenv, requests # noqa: F401
            return True
        except ImportError:
            return False
    else:
        ret = os.system(f'"{python_exe}" -c "{check_cmd}" 2>/dev/null')
        return ret == 0


def gestionar_venv():
    """
    Crea el entorno virtual si no existe, instala dependencias y relanza el script.
    """
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(workspace_dir, "venv")

    # Rutas según el sistema operativo
    if sys.platform == "win32":
        python_venv = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_venv    = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_venv = os.path.join(venv_dir, "bin", "python")
        pip_venv    = os.path.join(venv_dir, "bin", "pip")

    # 1. Si ya estamos en el venv
    if os.path.abspath(sys.executable) == os.path.abspath(python_venv):
        if not dependencias_ok():
            instalar_dependencias(python_venv)
        return

    # 2. Crear venv si no existe
    if not os.path.exists(venv_dir):
        print("\n[CREANDO] Entorno virtual para el Cazador...")
        # Intentar crear venv
        ret = os.system(f'"{sys.executable}" -m venv "{venv_dir}"')
        if ret != 0:
            print("[ADVERTENCIA] No se pudo crear el venv. ¿Falta python3-venv?")
            print("  Prueba: apt-get update && apt-get install python3-venv")
            # Fallback: intentar instalar globalmente
            if not dependencias_ok():
                instalar_dependencias()
            return

    # 3. Reparar pip si es necesario (común en Proot Ubuntu)
    if os.path.exists(venv_dir) and not os.path.exists(pip_venv):
        os.system(f'"{python_venv}" -m ensurepip --upgrade 2>/dev/null || true')

    # 4. Instalar y Relanzar
    if os.path.exists(python_venv):
        if not dependencias_ok(python_venv):
            instalar_dependencias(python_venv)
        
        print("[RELANZANDO] Cazador desde el entorno virtual...\n")
        exit_code = subprocess.call([python_venv, os.path.abspath(__file__)])
        sys.exit(exit_code)


# ============================================================================
# ENTRADA AL PROGRAMA
# ============================================================================

if __name__ == "__main__":
    # Gestionar entorno antes de importar el resto del proyecto
    gestionar_venv()

    # Ahora que el entorno es seguro, importamos todo
    import time
    from src.config import CHECK_INTERVAL_MINUTES
    from src.keywords_manager import get_positive_keywords, get_negative_keywords, get_language_keywords
    from src.driver import get_driver
    from src.notifications import send_telegram_message
    from src.sites.bumeran import BumeranBot
    from src.sites.computrabajo import ComputrabajoBot
    from src.sites.empleosit import EmpleosITBot

    def run_bot():
        """Punto de entrada principal del bot."""
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

                    print("\n✅ Ciclo finalizado exitosamente.")

                    hours_wait = CHECK_INTERVAL_MINUTES / 60
                    send_telegram_message(
                        f"🏁 <b>Ciclo de búsqueda finalizado.</b>\n"
                        f"💤 Durmiendo {int(hours_wait)}hs hasta el próximo turno."
                    )

                except Exception as error:
                    print(f"\n❌ Error durante la búsqueda: {error}")

                finally:
                    print("🔒 Cerrando navegador para liberar memoria.")
                    driver.quit()

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

    # Iniciar ciclo
    run_bot()
