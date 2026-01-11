import requests
import re
import os
import json
from src.config import TELEGRAM_BOT_TOKEN
from src.history import history

UPDATES_FILE = "last_update.json"

def get_last_update_id():
    """Recupera el ID de la última actualización de Telegram procesada."""
    if not os.path.exists(UPDATES_FILE):
        return 0
    try:
        with open(UPDATES_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    except:
        return 0

def save_last_update_id(update_id):
    """Guarda el ID de la última actualización."""
    with open(UPDATES_FILE, "w") as f:
        json.dump({"last_id": update_id}, f)

def check_telegram_replies():
    """
    Consulta a Telegram si hay nuevos mensajes del usuario.
    Si el usuario respondió 'ya lo vi' a una oferta, guarda la URL en el historial.
    """
    if not TELEGRAM_BOT_TOKEN:
        return

    last_id = get_last_update_id()
    
    # Solicitamos actualizaciones (mensajes nuevos)
    # offset = last_id + 1 para no recibir repetidos
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_id + 1}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get("ok"):
            return

        result = data.get("result", [])
        max_id = last_id

        commands_to_ignore = ["ya lo vi", "ya la vi", "listo", "visto", "olvidalo", "este no", "ya esta", "paso"]

        for update in result:
            update_id = update["update_id"]
            if update_id > max_id:
                max_id = update_id

            message = update.get("message", {})
            text = message.get("text", "").lower().strip()
            
            # 1. ¿Es una respuesta válida?
            if any(cmd in text for cmd in commands_to_ignore):
                
                # 2. ¿Está respondiendo a un mensaje del bot?
                reply_to = message.get("reply_to_message", {})
                if not reply_to:
                    continue

                # 3. EXTRAER URL de la oferta original
                # Estrategia A: Buscar en 'entities' (Links formateados)
                found_url = None
                
                entities = reply_to.get("entities", [])
                text_reply = reply_to.get("text", "") # Texto plano del mensaje original
                
                # Buscamos en entidades (enlaces ocultos en <a href...>)
                for ent in entities:
                    if ent["type"] == "text_link":
                        found_url = ent["url"]
                        break
                    elif ent["type"] == "url":
                        # El link está escrito tal cual en el texto
                        offset = ent["offset"]
                        length = ent["length"]
                        found_url = text_reply[offset:offset+length]
                        break
                
                # Estrategia B: Regex sobre el texto plano (fallback)
                if not found_url:
                    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', text_reply)
                    if urls:
                        found_url = urls[0]

                # 4. ACCIÓN: Guardar en Historial
                if found_url:
                    print(f"   📩 Usuario marcó oferta como vista: {found_url[:30]}...")
                    if history.is_seen(found_url):
                         requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={message['chat']['id']}&text=Ya estaba marcada, tranqui. 👍")
                    else:
                        history.add_job(found_url)
                        # Confirmación visual al usuario
                        requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={message['chat']['id']}&text=✅ Listo, oferta silenciada por 15 días.")
                else:
                    print("   ⚠️ Usuario respondió 'ya lo vi' pero no encontré URL en el mensaje original.")

        # Guardar el nuevo punto de control
        if max_id > last_id:
            save_last_update_id(max_id)

    except Exception as e:
        print(f"   ⚠️ Error chequeando Telegram: {e}")
