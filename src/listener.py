import requests
import re
import os
import json
from src.config import TELEGRAM_BOT_TOKEN
from src.history import history

# Archivo de control para evitar procesar mensajes antiguos
UPDATES_FILE = "last_update.json"

def get_last_update_id():
    """Recupera el ID de la última actualización de Telegram procesada."""
    if not os.path.exists(UPDATES_FILE):
        return 0
    try:
        with open(UPDATES_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    except:
        # Retorna 0 si el archivo está corrupto o no se puede leer
        return 0

def save_last_update_id(update_id):
    """Persiste ID de la última actualización en disco para mantener estado entre ejecuciones."""
    with open(UPDATES_FILE, "w") as f:
        json.dump({"last_id": update_id}, f)

def check_telegram_replies():
    """
    Verifica mensajes nuevos en Telegram mediante Long Polling.
    Si el usuario responde 'ya lo vi' (o similar) a un mensaje del bot,
    extrae la URL original y la marca como 'vista' en el historial.
    """
    
    # Validación: Si no hay token configurado, salir silenciosamente
    if not TELEGRAM_BOT_TOKEN:
        return

    last_id = get_last_update_id()
    
    # Construcción de la request a la API de Telegram.
    # Offset = last_id + 1 asegura que solo traemos mensajes nuevos no procesados.
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_id + 1}"
    
    try:
        # Timeout de 10s para no bloquear el flujo principal si Telegram tarda
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Validación de respuesta exitosa de la API
        if not data.get("ok"):
            return

        result = data.get("result", []) 
        max_id = last_id
        
        # Comandos que activan el filtrado (case-insensitive)
        commands_to_ignore = ["ya lo vi", "ya la vi", "listo", "visto", "olvidalo", "este no", "ya esta", "paso"]

        for update in result:
            update_id = update["update_id"]
            # Actualizamos el puntero del último mensaje visto
            if update_id > max_id:
                max_id = update_id

            message = update.get("message", {})
            text = message.get("text", "").lower().strip()
            
            # 1. Verificar si el texto del usuario coincide con algún comando
            if any(cmd in text for cmd in commands_to_ignore):
                
                # 2. Verificar context: ¿Es una respuesta (Reply) a otro mensaje?
                # Sin esto, un mensaje suelto no tiene contexto de qué oferta filtrar.
                reply_to = message.get("reply_to_message", {})
                if not reply_to:
                    continue

                # 3. Extracción de URL del mensaje original
                found_url = None
                
                # Método A: Buscar en 'entities' (Links formateados por Telegram)
                # Es más preciso porque Telegram ya parseó el mensaje.
                entities = reply_to.get("entities", [])
                text_reply = reply_to.get("text", "") 
                
                for ent in entities:
                    if ent["type"] == "text_link":
                        # Caso: <a href="http...">Texto</a>
                        found_url = ent["url"]
                        break
                    elif ent["type"] == "url":
                        # Caso: URL expuesta en el texto
                        offset = ent["offset"]
                        length = ent["length"]
                        found_url = text_reply[offset:offset+length]
                        break
                
                # Método B: Fallback vía Regex (Expresiones Regulares)
                # Si Telegram no detectó la entidad, buscamos patrones 'http/https' manualmente.
                if not found_url:
                    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', text_reply)
                    if urls:
                        found_url = urls[0] 

                # 4. Acción: Actualizar historial y notificar usuario
                if found_url:
                    print(f"   📩 Usuario marcó oferta como vista: {found_url[:30]}...")
                    
                    if history.is_seen(found_url):
                         # Feedback para evitar confusión si ya estaba filtrada
                         requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={message['chat']['id']}&text=Ya estaba marcada, tranqui. 👍")
                    else:
                        # Operación principal: Agregar a persistencia
                        history.add_job(found_url)
                        # Confirmación visual (Check verde)
                        requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={message['chat']['id']}&text=✅ Listo, oferta silenciada por 15 días.")
                else:
                    print("   ⚠️ Usuario respondió comando válido pero no se detectó URL en el mensaje original.")

        # Guardar checkpoint de lectura solo si procesamos mensajes nuevos
        if max_id > last_id:
            save_last_update_id(max_id)

    except Exception as e:
        print(f"   ⚠️ Error chequeando Telegram: {e}")
