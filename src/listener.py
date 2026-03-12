import requests
import re
import os
import sys
import json
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.history import history, normalize_url
from src.keywords_manager import (
    add_negative_keyword,
    add_positive_keyword,
    get_negative_keywords,
    get_positive_keywords,
    remove_negative_keyword,
    remove_positive_keyword,
    add_language_keyword,
    remove_language_keyword,
    get_language_keywords,
)

UPDATES_FILE = "last_update.json"


def get_last_update_id():
    """
    Recupera el ID de la última actualización procesada desde disco.
    Usado como offset en el polling de Telegram para no reprocesar mensajes.

    Returns:
        int: El último update_id procesado, o 0 si no existe registro previo.
    """
    if not os.path.exists(UPDATES_FILE):
        return 0
    try:
        with open(UPDATES_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    except Exception:
        return 0


def save_last_update_id(update_id):
    """
    Persiste el update_id más reciente en disco para el próximo ciclo de polling.

    Args:
        update_id (int): ID de la última actualización procesada.
    """
    with open(UPDATES_FILE, "w") as f:
        json.dump({"last_id": update_id}, f)


def send_msg(chat_id, text_message):
    """
    Envía un mensaje de texto simple a un chat de Telegram.

    Args:
        chat_id (str | int): ID del chat destino.
        text_message (str): Contenido del mensaje.
    """
    try:
        url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text_message}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Error enviando mensaje a {chat_id}: {e}")


def check_telegram_replies():
    """
    Procesa las actualizaciones pendientes de Telegram (long polling).

    Maneja dos tipos de interacciones:
    - Comandos (mensajes que empiezan con /): gestión de palabras clave,
      apagado remoto y consulta de listas.
    - Respuestas a notificaciones del bot: archivar ofertas en el historial
      cuando el usuario responde con frases como 'ya lo vi', 'paso', 'listo', etc.

    Solo procesa mensajes del TELEGRAM_CHAT_ID configurado, descartando
    cualquier interacción de otros usuarios.
    """
    if not TELEGRAM_BOT_TOKEN:
        return

    last_id = get_last_update_id()
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_id + 1}"

    try:
        response      = requests.get(url, timeout=5)
        response_data = response.json()

        if not response_data.get("ok"):
            return

        updates_result = response_data.get("result", [])
        current_max_id = last_id

        # Frases que el usuario puede enviar como reply a una oferta para archivarla
        commands_to_ignore_job = [
            "ya lo vi", "ya la vi", "listo", "visto",
            "olvidalo", "este no", "ya esta", "paso",
        ]

        for update in updates_result:
            update_id = update["update_id"]

            if update_id > current_max_id:
                current_max_id = update_id

            message_data = update.get("message", {})
            chat_id      = message_data.get("chat", {}).get("id")

            # Solo procesamos mensajes del propietario del bot
            if str(chat_id) != str(TELEGRAM_CHAT_ID):
                print(f"   ⚠️ Acceso no autorizado detectado desde ID: {chat_id}")
                continue

            message_text       = message_data.get("text", "").strip()
            message_text_lower = message_text.lower()

            # ----------------------------------------------------------------
            # BLOQUE 1: COMANDOS (mensajes que empiezan con /)
            # ----------------------------------------------------------------
            if message_text_lower.startswith("/"):
                parts        = message_text.split(" ", 1)
                command_name = parts[0].lower()
                argument_word = parts[1].strip() if len(parts) > 1 else None

                # Agregar palabra negativa
                if command_name in ["/addneg", "/negativa", "/an", "/menos"]:
                    if argument_word:
                        if add_negative_keyword(argument_word):
                            send_msg(chat_id, f"🚫 Palabra negativa agregada: '{argument_word}'")
                            print(f"   🛑 [CMD] Usuario agregó NEGATIVA: {argument_word}")
                        else:
                            send_msg(chat_id, f"⚠️ La palabra '{argument_word}' ya estaba en la lista negativa.")
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /menos <palabra>")

                # Eliminar palabra negativa
                elif command_name in ["/delneg", "/rmneg", "/sacarmenos", "/dn"]:
                    if argument_word:
                        if remove_negative_keyword(argument_word):
                            send_msg(chat_id, f"🗑️ Palabra negativa eliminada: '{argument_word}'")
                            print(f"   🗑️ [CMD] Usuario eliminó NEGATIVA: {argument_word}")
                        else:
                            send_msg(chat_id, f"⚠️ La palabra '{argument_word}' no estaba en la lista negativa.")
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /sacarmenos <palabra>")

                # Agregar palabra positiva
                elif command_name in ["/addpos", "/positiva", "/ap", "/mas"]:
                    if argument_word:
                        if add_positive_keyword(argument_word):
                            send_msg(chat_id, f"✅ Palabra positiva agregada: '{argument_word}'")
                            print(f"   ✨ [CMD] Usuario agregó POSITIVA: {argument_word}")
                        else:
                            send_msg(chat_id, f"⚠️ La palabra '{argument_word}' ya estaba en la lista positiva.")
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /mas <palabra>")

                # Eliminar palabra positiva
                elif command_name in ["/delpos", "/rmpos", "/sacarmas", "/dp"]:
                    if argument_word:
                        if remove_positive_keyword(argument_word):
                            send_msg(chat_id, f"🗑️ Palabra positiva eliminada: '{argument_word}'")
                            print(f"   🗑️ [CMD] Usuario eliminó POSITIVA: {argument_word}")
                        else:
                            send_msg(chat_id, f"⚠️ La palabra '{argument_word}' no estaba en la lista positiva.")
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /sacarmas <palabra>")

                # Listar palabras negativas
                elif command_name in ["/listneg", "/vernegativas", "/ln", "/vermenos"]:
                    negative_list = sorted(get_negative_keywords())
                    print("   ℹ️ [CMD] Usuario solicitó lista de NEGATIVAS.")
                    response_message = "🚫 **Palabras Negativas:**\n\n" + ", ".join(negative_list)
                    if len(response_message) > 4000:
                        for i in range(0, len(response_message), 4000):
                            send_msg(chat_id, response_message[i:i+4000])
                    else:
                        send_msg(chat_id, response_message)

                # Listar palabras positivas
                elif command_name in ["/listpos", "/verpositivas", "/lp", "/vermas"]:
                    positive_list = sorted(get_positive_keywords())
                    print("   ℹ️ [CMD] Usuario solicitó lista de POSITIVAS.")
                    response_message = "✅ **Palabras Positivas:**\n\n" + ", ".join(positive_list)
                    if len(response_message) > 4000:
                        for i in range(0, len(response_message), 4000):
                            send_msg(chat_id, response_message[i:i+4000])
                    else:
                        send_msg(chat_id, response_message)

                # Agregar filtro de idioma
                elif command_name in ["/addidioma", "/ai"]:
                    if argument_word:
                        if add_language_keyword(argument_word):
                            send_msg(chat_id, f"🌐 Filtro de idioma agregado: '{argument_word}'")
                            print(f"   🌐 [CMD] Usuario agregó IDIOMA: {argument_word}")
                        else:
                            send_msg(chat_id, f"⚠️ La frase '{argument_word}' ya estaba en el filtro de idioma.")
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /addidioma <frase>")

                # Eliminar filtro de idioma
                elif command_name in ["/sacaridioma", "/si"]:
                    if argument_word:
                        if remove_language_keyword(argument_word):
                            send_msg(chat_id, f"🗑️ Filtro de idioma eliminado: '{argument_word}'")
                            print(f"   🗑️ [CMD] Usuario eliminó IDIOMA: {argument_word}")
                        else:
                            send_msg(chat_id, f"⚠️ La frase '{argument_word}' no estaba en el filtro de idioma.")
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /sacaridioma <frase>")

                # Listar filtros de idioma
                elif command_name in ["/veridioma", "/listidioma", "/vi"]:
                    language_list    = sorted(get_language_keywords())
                    response_message = "🌐 **Filtro de Idioma:**\n\n" + ", ".join(language_list)
                    print("   ℹ️ [CMD] Usuario solicitó lista de FILTROS DE IDIOMA.")
                    if len(response_message) > 4000:
                        for i in range(0, len(response_message), 4000):
                            send_msg(chat_id, response_message[i:i+4000])
                    else:
                        send_msg(chat_id, response_message)

                # Ayuda / listado de comandos disponibles
                elif command_name in ["/comandos", "/help", "/ayuda"]:
                    help_text = (
                        "🤖 **Comandos Disponibles:**\n\n"
                        "🚫 **Negativas (Ignorar título):**\n"
                        "• Agregar: `/addneg`, `/menos`, `/an` <palabra>\n"
                        "• Eliminar: `/delneg`, `/sacarmenos` <palabra>\n"
                        "• Listar: `/listneg`, `/vermenos`, `/ln`\n\n"
                        "✅ **Positivas (Buscar en título):**\n"
                        "• Agregar: `/addpos`, `/mas`, `/ap` <palabra>\n"
                        "• Eliminar: `/delpos`, `/sacarmas` <palabra>\n"
                        "• Listar: `/listpos`, `/vermas`, `/lp`\n\n"
                        "🌐 **Filtro de Idioma (descripción del puesto):**\n"
                        "• Agregar: `/addidioma`, `/ai` <frase>\n"
                        "• Eliminar: `/sacaridioma`, `/si` <frase>\n"
                        "• Listar: `/veridioma`, `/vi`\n\n"
                        "ℹ️ **Ayuda:**\n"
                        "• `/comandos`, `/help`, `/ayuda`\n\n"
                        "🗃️ **Archivar ofertas:**\n"
                        "Responder `ya lo vi`, `listo` o `paso` a una notificación del bot."
                    )
                    send_msg(chat_id, help_text)

                # Apagado remoto del bot
                elif command_name in ["/stop", "/shutdown", "/apagar", "/exit", "/salir"]:
                    print("   🛑 [CMD] Usuario ordenó APAGADO REMOTO.")
                    send_msg(chat_id, "👋 Entendido. Apagando sistemas... ¡Nos vemos!")
                    try:
                        import time
                        time.sleep(1)
                    except Exception:
                        pass
                    save_last_update_id(update_id)
                    sys.exit(0)

                continue  # Fin del bloque de comandos; pasamos al siguiente update

            # ----------------------------------------------------------------
            # BLOQUE 2: ARCHIVAR OFERTAS (reply a una notificación del bot)
            # ----------------------------------------------------------------
            if any(cmd in message_text_lower for cmd in commands_to_ignore_job):
                reply_to_message = message_data.get("reply_to_message", {})

                # El usuario debe responder (reply) al mensaje original del bot
                if not reply_to_message:
                    continue

                found_url    = None
                entities     = reply_to_message.get("entities", [])
                original_text = reply_to_message.get("text", "")

                # Método A: Link embebido como text_link en las entidades del mensaje
                for entity in entities:
                    if entity["type"] == "text_link":
                        found_url = entity["url"]
                        break

                # Método B: URL plana en el texto, extraída con regex.
                # Más robusto para mensajes con emojis, donde los offsets de Telegram
                # (UTF-16) pueden desalinearse con los índices de Python (Unicode).
                if not found_url:
                    urls_found = re.findall(r'https?://[^\s<>"]+', original_text)
                    if urls_found:
                        found_url = urls_found[0]

                if found_url:
                    found_url = normalize_url(found_url)
                    print(f"   📩 Usuario marcó oferta como vista: {found_url[:60]}...")

                    if history.is_seen(found_url):
                        send_msg(chat_id, "ℹ️ La URL ya se encuentra en el historial.")
                    else:
                        history.add_job(found_url)
                        send_msg(chat_id, "✅ Oferta archivada correctamente.")
                else:
                    print("   ⚠️ Comando recibido, pero no detecté ninguna URL en el mensaje original.")

        if current_max_id > last_id:
            save_last_update_id(current_max_id)

    except Exception as error:
        print(f"   ⚠️ Error chequeando Telegram: {error}")
