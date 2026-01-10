import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """
    Envía un mensaje de texto a través del bot de Telegram configurado.
    
    Args:
        message (str): El texto del mensaje a enviar.
        
    Returns:
        bool: True si el envío fue exitoso, False si falló.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("   ⚠️ Telegram no configurado (Falta TOKEN o CHAT_ID). Mensaje omitido.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML" # Permite usar negrita, links, etc.
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"   ❌ Error Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Excepción al enviar a Telegram: {e}")
        return False
