import re
import emoji

from func.aes import aes
from func.i18n import get
from settings import config
from datetime import datetime

def _replace_custom_emoji(match):
    emoji_name = match.group(1)
    if config.get("AES_ENCRYPTION_ENABLED", False):
        return f"[{emoji_name}]"
    return f"[[{emoji_name}]]"

def format_notification(create_at_ms, channel, sender, message_text):

    message = ""
    lines = ["🔔 *Mattermost Notifier*"]

    formatted_time = datetime.now().strftime(get('main.date_format'))

    if create_at_ms:
        dt = datetime.fromtimestamp(create_at_ms / 1000.0)
        formatted_time = dt.strftime(get('main.date_format'))

    lines.append(f"📅 *{get('main.date')}:* {formatted_time}")

    if config.get("ANONYMOUS_MODE", False) or (not config.get("INCLUDE_CHANNEL", True) and not config.get("INCLUDE_SENDER", True) and not config.get("INCLUDE_MESSAGE", True)):
        lines.append(get("main.default_msg"))
        message = "\n".join(lines)
    else:
        if config.get("INCLUDE_CHANNEL", True) and channel:
            lines.append(f"📢 *{get('main.channel')}:* {channel}")
        
        if config.get("INCLUDE_SENDER", True) and sender:
            lines.append(f"👤 *{get('main.sender')}:* {sender}")
            
        if config.get("INCLUDE_MESSAGE", True) and message_text:
            parsed_message_text = emoji.emojize(message_text, language='alias')
            parsed_message_text = re.sub(r':([a-zA-Z0-9_+-]+):', _replace_custom_emoji, parsed_message_text)
            lines.append(f"💬 *{get('main.message')}:*\n{parsed_message_text}")
        
    message = "\n".join(lines)

    if config.get("AES_ENCRYPTION_ENABLED", False) and message:
        return aes(message)
    else:
        return message