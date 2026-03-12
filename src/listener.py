
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
    get_language_keywords
)

# Archivo de control para persistencia del offset de actualizaciones (evita reprocesamiento)
UPDATES_FILE = "last_update.json"

def get_last_update_id():
    """
    Recupera el último 'update_id' procesado desde el almacenamiento local.
    
    Returns:
        int: El último ID de actualización procesado, o 0 si no existe el archivo.
    """
    if not os.path.exists(UPDATES_FILE):
        return 0
    try:
        # 'file_handler' reemplaza a 'f' para ser más claro
        with open(UPDATES_FILE, "r") as file_handler:
            return json.load(file_handler).get("last_id", 0)
    except:
        return 0

def save_last_update_id(update_id):
    """
    Persiste el 'update_id' más reciente en un archivo JSON.
    Esto actualiza el offset para las futuras peticiones de polling.
    
    Args:
        update_id (int): El ID de la última actualización procesada exitosamente.
    """
    with open(UPDATES_FILE, "w") as file_handler:
        json.dump({"last_id": update_id}, file_handler)

def send_msg(chat_id, text_message):
    """
    Envía un mensaje de texto a un chat específico utilizando la API de Telegram.
    
    Args:
        chat_id (str|int): Identificador del chat de destino.
        text_message (str): Contenido del mensaje a enviar.
    """
    try:
        # Usamos POST para evitar problemas con la longitud de la URL y caracteres especiales
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text_message
        }
        requests.post(url, data=data)
    except Exception as e:
        # Si falla el envío (ej. sin internet), no rompemos el programa.
        print(f"Error enviando mensaje a {chat_id}: {e}")

def check_telegram_replies():
    """
    Función principal de 'Polling' para la API de Telegram.
    
    Recupera actualizaciones pendientes, procesa comandos de gestión de keywords,
    y maneja interacciones de archivado de ofertas ('reply' a mensajes).
    
    Flujo:
    1. Obtiene el último offset procesado.
    2. Realiza un request GET a /getUpdates con el offset incrementado.
    3. Itera sobre los mensajes recibidos y despacha la lógica según el contenido.
    """
    
    if not TELEGRAM_BOT_TOKEN:
        return

    last_id = get_last_update_id()
    
    # Construcción de la URL para Long Polling.
    # offset = last_id + 1 confirma las actualizaciones previas y solicita solo las nuevas.
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_id + 1}"
    
    try:
        # Hacemos la petición a Telegram (Request GET)
        # Timeout de 5 segundos para no trabar el bot si internet está lento
        response = requests.get(url, timeout=5)
        response_data = response.json()
        
        # Validamos que la respuesta sea correcta (ok=True)
        if not response_data.get("ok"):
            return

        # Obtenemos la lista de resultados (mensajes)
        updates_result = response_data.get("result", []) 
        current_max_id = last_id
        
        # Lista de frases que el bot entiende para archivar ofertas
        commands_to_ignore_job = ["ya lo vi", "ya la vi", "listo", "visto", "olvidalo", "este no", "ya esta", "paso"]

        for update in updates_result:
            update_id = update["update_id"]
            
            # Mantenemos registro del ID más alto encontrado en este lote
            if update_id > current_max_id:
                current_max_id = update_id

            # Extraemos el mensaje y el chat_id
            message_data = update.get("message", {})
            chat_id = message_data.get("chat", {}).get("id")
            
            # --- SEGURIDAD: VERIFICAR AUTORIZACIÓN ---
            # Si el mensaje no viene del dueño, lo ignoramos.
            if str(chat_id) != str(TELEGRAM_CHAT_ID):
                print(f"   ⚠️ Acceso no autorizado detectado desde ID: {chat_id}")
                continue
            
            # Obtenemos el texto del mensaje limpio de espacios
            message_text = message_data.get("text", "").strip() 
            message_text_lower = message_text.lower()
            
            # ------------------------------------------------------------------
            # 0. GESTIÓN DE PALABRAS CLAVE (Comandos que empiezan con /)
            # ------------------------------------------------------------------
            if message_text_lower.startswith("/"):
                # Separamos el comando del argumento (ej: "/addneg java")
                # parts[0] = "/addneg", parts[1] = "java"
                parts = message_text.split(" ", 1)
                command_name = parts[0].lower()
                
                # Obtenemos el argumento si existe (la palabra a agregar)
                argument_word = parts[1].strip() if len(parts) > 1 else None

                # === BLOQUE: AGREGAR NEGATIVAS ===
                if command_name in ["/addneg", "/negativa", "/an", "/menos"]:
                    if argument_word:
                        if add_negative_keyword(argument_word):
                            msg = f"🚫 Palabra negativa agregada: '{argument_word}'"
                            print(f"   🛑 [CMD] Usuario agregó NEGATIVA: {argument_word}")
                            send_msg(chat_id, msg)
                        else:
                            msg = f"⚠️ La palabra '{argument_word}' ya estaba en la lista negativa."
                            print(f"   ⚠️ [CMD] Intento duplicado NEGATIVA: {argument_word}")
                            send_msg(chat_id, msg)
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /menos <palabra>")

                # === BLOQUE: ELIMINAR NEGATIVAS ===
                elif command_name in ["/delneg", "/rmneg", "/sacarmenos", "/dn"]:
                    if argument_word:
                        if remove_negative_keyword(argument_word):
                            msg = f"🗑️ Palabra negativa eliminada: '{argument_word}'"
                            print(f"   🗑️ [CMD] Usuario eliminó NEGATIVA: {argument_word}")
                            send_msg(chat_id, msg)
                        else:
                            msg = f"⚠️ La palabra '{argument_word}' no estaba en la lista negativa."
                            send_msg(chat_id, msg)
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /sacarmenos <palabra>")
                
                # === BLOQUE: AGREGAR POSITIVAS ===
                elif command_name in ["/addpos", "/positiva", "/ap", "/mas"]:
                    if argument_word:
                        if add_positive_keyword(argument_word):
                            msg = f"✅ Palabra positiva agregada: '{argument_word}'"
                            print(f"   ✨ [CMD] Usuario agregó POSITIVA: {argument_word}")
                            send_msg(chat_id, msg)
                        else:
                            msg = f"⚠️ La palabra '{argument_word}' ya estaba en la lista positiva."
                            print(f"   ⚠️ [CMD] Intento duplicado POSITIVA: {argument_word}")
                            send_msg(chat_id, msg)
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /mas <palabra>")

                # === BLOQUE: ELIMINAR POSITIVAS ===
                elif command_name in ["/delpos", "/rmpos", "/sacarmas", "/dp"]:
                    if argument_word:
                        if remove_positive_keyword(argument_word):
                            msg = f"🗑️ Palabra positiva eliminada: '{argument_word}'"
                            print(f"   🗑️ [CMD] Usuario eliminó POSITIVA: {argument_word}")
                            send_msg(chat_id, msg)
                        else:
                            msg = f"⚠️ La palabra '{argument_word}' no estaba en la lista positiva."
                            send_msg(chat_id, msg)
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /sacarmas <palabra>")

                # === BLOQUE: LISTAR NEGATIVAS ===
                elif command_name in ["/listneg", "/vernegativas", "/ln", "/vermenos"]:
                    # Obtenemos la lista actual y la ordenamos alfabéticamente
                    negative_list = get_negative_keywords()
                    negative_list.sort()
                    print(f"   ℹ️ [CMD] Usuario solicitó lista de NEGATIVAS.")
                    
                    response_message = "🚫 **Palabras Negativas:**\n\n" + ", ".join(negative_list)
                    
                    # Mensaje largo: dividir en partes (chunking)
                    if len(response_message) > 4000:
                        for i in range(0, len(response_message), 4000):
                            send_msg(chat_id, response_message[i:i+4000])
                    else:
                        send_msg(chat_id, response_message)

                # === BLOQUE: LISTAR POSITIVAS ===
                elif command_name in ["/listpos", "/verpositivas", "/lp", "/vermas"]:
                    positive_list = get_positive_keywords()
                    positive_list.sort()
                    print(f"   ℹ️ [CMD] Usuario solicitó lista de POSITIVAS.")
                    
                    response_message = "✅ **Palabras Positivas:**\n\n" + ", ".join(positive_list)
                    
                    # Mensaje largo: dividir en partes (chunking)
                    if len(response_message) > 4000:
                        for i in range(0, len(response_message), 4000):
                            send_msg(chat_id, response_message[i:i+4000])
                    else:
                        send_msg(chat_id, response_message)

                # === BLOQUE: AGREGAR FILTRO DE IDIOMA ===
                elif command_name in ["/addidioma", "/ai"]:
                    if argument_word:
                        if add_language_keyword(argument_word):
                            msg = f"🌐 Filtro de idioma agregado: '{argument_word}'"
                            print(f"   🌐 [CMD] Usuario agregó IDIOMA: {argument_word}")
                            send_msg(chat_id, msg)
                        else:
                            msg = f"⚠️ La frase '{argument_word}' ya estaba en el filtro de idioma."
                            send_msg(chat_id, msg)
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /addidioma <frase>")

                # === BLOQUE: ELIMINAR FILTRO DE IDIOMA ===
                elif command_name in ["/sacaridioma", "/si"]:
                    if argument_word:
                        if remove_language_keyword(argument_word):
                            msg = f"🗑️ Filtro de idioma eliminado: '{argument_word}'"
                            print(f"   🗑️ [CMD] Usuario eliminó IDIOMA: {argument_word}")
                            send_msg(chat_id, msg)
                        else:
                            msg = f"⚠️ La frase '{argument_word}' no estaba en el filtro de idioma."
                            send_msg(chat_id, msg)
                    else:
                        send_msg(chat_id, "⚠️ Uso correcto: /sacaridioma <frase>")

                # === BLOQUE: LISTAR FILTRO DE IDIOMA ===
                elif command_name in ["/veridioma", "/listidioma", "/vi"]:
                    language_list = get_language_keywords()
                    language_list.sort()
                    print(f"   ℹ️ [CMD] Usuario solicitó lista de FILTROS DE IDIOMA.")
                    response_message = "🌐 **Filtro de Idioma:**\n\n" + ", ".join(language_list)
                    if len(response_message) > 4000:
                        for i in range(0, len(response_message), 4000):
                            send_msg(chat_id, response_message[i:i+4000])
                    else:
                        send_msg(chat_id, response_message)

                # === BLOQUE: AYUDA / COMANDOS ===
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
                        "🗃️ **Acciones:**\n"
                        "Responder `ya lo vi`, `listo` o `paso` a una oferta para archivarla."
                    )
                    send_msg(chat_id, help_text)

                # === BLOQUE: APAGADO REMOTO ===
                elif command_name in ["/stop", "/shutdown", "/apagar", "/exit", "/salir"]:
                    print(f"   🛑 [CMD] Usuario ordenó APAGADO REMOTO.")
                    send_msg(chat_id, "👋 Entendido. Apagando sistemas... ¡Nos vemos!")
                    
                    # Esperamos un segundo para que el mensaje salga
                    try:
                        import time
                        time.sleep(1)
                    except: 
                        pass
                    
                    # CRÍTICO: Persistencia del estado antes de finalizar el proceso.
                    # Se guarda el current_update_id para evitar procesar el comando 'stop' nuevamente al reiniciar.
                    save_last_update_id(update_id)
                    
                    sys.exit(0)
                
                # Si procesamos un comando "/", pasamos al siguiente mensaje (continue)
                continue

            # ------------------------------------------------------------------
            # 1. COMANDOS DE ACCIÓN (Marcar oferta como vista)
            # ------------------------------------------------------------------
            # Verificamos si el texto del usuario coincide con alguna frase de "commands_to_ignore_job"
            if any(cmd in message_text_lower for cmd in commands_to_ignore_job):
                
                # Para saber QUÉ oferta archivar, necesitamos que el usuario haya RESPONDIDO (Reply) 
                # al mensaje original del bot que contenía el link.
                reply_to_message = message_data.get("reply_to_message", {})
                
                # Si no es una respuesta a otro mensaje, no hacemos nada
                if not reply_to_message:
                    continue

                # --- Lógica de Extracción de URL (Link) ---
                found_url = None
                
                # Método A: Buscar en 'entities' (Links formateados por Telegram)
                # 'entities' contiene metadatos sobre links, negritas, etc.
                entities = reply_to_message.get("entities", [])
                original_text = reply_to_message.get("text", "") 
                
                for entity in entities:
                    # Caso 1: Enlace de texto (ej: <a href="url">Texto</a>)
                    if entity["type"] == "text_link":
                        found_url = entity["url"]
                        break
                
                # Método B: Búsqueda con Regex (más robusta para URLs en texto plano).
                # Se usa como método principal para URLs de tipo 'url' en entities,
                # porque Telegram calcula offsets en UTF-16 pero Python usa Unicode,
                # lo que puede descasar el índice cuando hay emojis (ej: '🔗' cuenta
                # como 2 unidades en UTF-16 pero 1 en Python, corrompiendo la URL).
                if not found_url:
                    urls_found = re.findall(r'https?://[^\s<>"]+', original_text)
                    if urls_found:
                        found_url = urls_found[0]
                
                # --- Guardado en Historial ---
                if found_url:
                    # Normalizamos la URL antes de guardar (elimina #fragmentos, espacios)
                    found_url = normalize_url(found_url)
                    print(f"   📩 Usuario marcó oferta como vista: {found_url[:60]}...")
                    
                    # Verificamos si ya estaba en el historial para dar feedback adecuado
                    if history.is_seen(found_url):
                         send_msg(chat_id, "ℹ️ La URL ya se encuentra en el historial.")
                    else:
                        # Persistencia: se agrega la URL al archivo seen_jobs.json
                        history.add_job(found_url)
                        send_msg(chat_id, "✅ Oferta archivada correctamente.")
                else:
                    print("   ⚠️ Comando recibido, pero no detecté ninguna URL en el mensaje original.")

        # Guardamos el ID del último mensaje procesado para la próxima vez
        if current_max_id > last_id:
            save_last_update_id(current_max_id)

    except Exception as error:
        print(f"   ⚠️ Error chequeando Telegram: {error}")
