from func.aes import aes
from settings import config
from datetime import datetime

def format_notification(create_at_ms, channel, sender, message_text):

    message = ""
    lines = ["🔔 *Mattermost Notifier*"]

    formatted_time = datetime.now().strftime("%d/%m/%Y alle %H:%M")

    if create_at_ms:
        dt = datetime.fromtimestamp(create_at_ms / 1000.0)
        formatted_time = dt.strftime("%d/%m/%Y alle %H:%M") 

    lines.append(f"📅 *Data:* {formatted_time}")

    if config.get("ANONYMOUS_MODE", False) or (not config.get("INCLUDE_CHANNEL", True) and not config.get("INCLUDE_SENDER", True) and not config.get("INCLUDE_MESSAGE", True)):
        lines.append("Hai ricevuto un nuovo messaggio!")
        message = "\n".join(lines)
    else:
        if config.get("INCLUDE_CHANNEL", True) and channel:
            lines.append(f"📢 *Canale:* {channel}")
        
        if config.get("INCLUDE_SENDER", True) and sender:
            lines.append(f"👤 *Mittente:* {sender}")
            
        if config.get("INCLUDE_MESSAGE", True) and message_text:
            lines.append(f"💬 *Messaggio:*\n{message_text}")
        
    message = "\n".join(lines)

    if config.get("AES_ENCRYPTION_ENABLED", False) and message:
        return aes(message)
    else:
        return message