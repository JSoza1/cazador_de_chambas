import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message):
    """
    Envía un mensaje HTML al chat de Telegram configurado.

    Usa parse_mode=HTML para permitir formato enriquecido en los mensajes
    (negritas con <b>, enlaces con <a href>).

    Args:
        message (str): Contenido del mensaje. Puede contener HTML básico.

    Returns:
        bool: True si el mensaje fue enviado correctamente, False en caso contrario.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("   ⚠️ Telegram no configurado (Falta TOKEN o CHAT_ID). Mensaje omitido.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
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
