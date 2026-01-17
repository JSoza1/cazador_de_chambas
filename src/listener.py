
import requests
import re
import os
import sys
import json
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.history import history
from src.keywords_manager import (
    add_negative_keyword, 
    add_positive_keyword, 
    get_negative_keywords, 
    get_positive_keywords,
    remove_negative_keyword,
    remove_positive_keyword
)

# Archivo de control para evitar procesar mensajes antiguos (evita bucles infinitos)
UPDATES_FILE = "last_update.json"

def get_last_update_id():
    """
    Recupera el ID (identificador único) de la última actualización de Telegram que procesamos.
    Esto permite que si el bot se reinicia, no vuelva a leer mensajes viejos.
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
    Guarda el ID de la última actualización en el disco duro.
    Es como un 'punto de guardado' del juego.
    """
    with open(UPDATES_FILE, "w") as file_handler:
        json.dump({"last_id": update_id}, file_handler)

def send_msg(chat_id, text_message):
    """
    Función auxiliar para enviar mensajes simples a Telegram.
    Se usa para responderle al usuario (ej: '✅ Palabra agregada').
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
    Esta es la función principal que 'escucha' a Telegram.
    Usa una técnica llamada 'Polling' para preguntar si hay mensajes nuevos.
    
    Funcionalidades:
    1. Detecta comandos de gestión (/addneg, /listpos, etc).
    2. Detecta comandos de acción ('ya lo vi', 'listo').
    3. Actualiza el historial de ofertas vistas si corresponde.
    """
    
    if not TELEGRAM_BOT_TOKEN:
        return

    last_id = get_last_update_id()
    
    # Construimos la URL para pedir actualizaciones a Telegram.
    # offset = last_id + 1 le dice a Telegram: "Dame solo los mensajes NUEVOS que llegaron después de este ID".
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

                # === BLOQUE: AYUDA / COMANDOS ===
                elif command_name in ["/comandos", "/help", "/ayuda"]:
                    help_text = (
                        "🤖 **Comandos Disponibles:**\n\n"
                        "🚫 **Negativas (Ignorar):**\n"
                        "• Agregar: `/addneg`, `/menos`, `/an` <palabra>\n"
                        "• Eliminar: `/delneg`, `/sacarmenos` <palabra>\n"
                        "• Listar: `/listneg`, `/vermenos`, `/ln`\n\n"
                        "✅ **Positivas (Buscar):**\n"
                        "• Agregar: `/addpos`, `/mas`, `/ap` <palabra>\n"
                        "• Eliminar: `/delpos`, `/sacarmas` <palabra>\n"
                        "• Listar: `/listpos`, `/vermas`, `/lp`\n\n"
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
                    # Caso 2: URL explícita (ej: https://...)
                    elif entity["type"] == "url":
                        offset = entity["offset"]
                        length = entity["length"]
                        # Cortamos el texto exacto donde está la URL
                        found_url = original_text[offset:offset+length]
                        break
                
                # Método B: Búsqueda manual con Expresiones Regulares (Regex) si lo anterior falla
                if not found_url:
                    # Busca patrones http:// o https://
                    urls_found = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', original_text)
                    if urls_found:
                        found_url = urls_found[0] 
                
                # --- Guardado en Historial ---
                if found_url:
                    print(f"   📩 Usuario marcó oferta como vista: {found_url[:30]}...")
                    
                    # Verificamos si ya estaba en el historial para dar feedback adecuado
                    if history.is_seen(found_url):
                         send_msg(chat_id, "Ya estaba marcada, tranqui. 👍")
                    else:
                        # La magia ocurre aquí: se agrega a seen_jobs.json
                        history.add_job(found_url)
                        send_msg(chat_id, "✅ Listo, oferta archivada.")
                else:
                    print("   ⚠️ Comando recibido, pero no detecté ninguna URL en el mensaje original.")

        # Guardamos el ID del último mensaje procesado para la próxima vez
        if current_max_id > last_id:
            save_last_update_id(current_max_id)

    except Exception as error:
        print(f"   ⚠️ Error chequeando Telegram: {error}")
