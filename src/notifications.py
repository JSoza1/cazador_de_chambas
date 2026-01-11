import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """
    Envía un mensaje a Telegram mediante solicitud HTTP POST.
    Retorna True si el envío fue exitoso (Status 200).
    """
    
    # Validación de configuración previa
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("   ⚠️ Telegram no configurado (Falta TOKEN o CHAT_ID). Mensaje omitido.")
        return False

    # Endpoint oficial de la API de Telegram para enviar mensajes
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Construcción del payload (cuerpo) de la solicitud
    # - chat_id: Identificador único del usuario destino
    # - text: El contenido del mensaje
    # - parse_mode: HTML permite usar negrita (<b>) y enlaces (<a href>)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,             
        "parse_mode": "HTML"
    }

    try:
        # Ejecutamos la solicitud POST con un timeout de 10 segundos
        response = requests.post(url, json=payload, timeout=10)
        
        # Verificamos el código de estado HTTP
        # 200 OK: La solicitud fue recibida y procesada correctamente
        if response.status_code == 200:
            return True
        else:
            # Si falla (400, 401, 500, etc), mostramos el error devuelto por la API
            print(f"   ❌ Error Telegram: {response.text}")
            return False
            
    except Exception as e:
        # Captura errores de red (DNS, Timeout, Sin conexión)
        print(f"   ❌ Excepción al enviar a Telegram: {e}")
        return False
