import argparse
import os
import sys

from func.get_system_locale import get_system_locale
from func.i18n import get

class WideHelpFormatter(argparse.RawTextHelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=43, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)

def parse_args():
    if "/?" in sys.argv:
        sys.argv[sys.argv.index("/?")] = "--help"

    parser = argparse.ArgumentParser(
        description=get("args.description"),
        formatter_class=WideHelpFormatter,
        epilog=""""""+get("args.env")+"""
  HEADLESS                        """+get("args.headless")+"""
  PORT                            """+get("args.port")+"""
  CONFIG_PATH                     """+get("args.config")+"""
  MATTERMOST_WS_URL               Mattermost WS URL.
  MATTERMOST_TOKEN                Mattermost Token.
  TELEGRAM_BOT_TOKEN              Telegram Bot Token.
  TELEGRAM_CHAT_ID                Telegram Chat ID.
  EXCLUDED_SENDERS                """+get("excludedlist.senders.title_text")+""".
  EXCLUDED_CHANNELS               """+get("excludedlist.channels.title_text")+""".
  ECHO_SUPPRESSION_ENABLED        """+get("settings.ui.chk_echo")+""".
  ANONYMOUS_MODE                  """+get("settings.ui.toggle_anon")+""".
  INCLUDE_SENDER                  """+get("settings.ui.toggle_sender")+""".
  INCLUDE_CHANNEL                 """+get("settings.ui.toggle_channel")+""".
  INCLUDE_MESSAGE                 """+get("settings.ui.toggle_message")+""".
  AES_ENCRYPTION_ENABLED          """+get("settings.ui.toggle_aes")+""".
  AES_ENCRYPTION_KEY              """+get("args.aes_key")+"""
  WS_RECONNECT_TIMEOUT            """+get("timeout.field1").replace(":",".")+"""
  RETRY_LOGIC_TIMEOUT             """+get("timeout.field2").replace(":",".")+"""
  RETRY_LOGIC_MAX_ATTEMPTS        """+get("timeout.field3").replace(":",".")+"""
  TG_HTTP_TIMEOUT                 """+get("timeout.field4").replace(":",".")+"""
  LOG_LEVEL                       """+get("args.log_level")+"""
  LANGUAGE                        """+get("args.lang")+"""
"""
    )

    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            action.help = ""

    parser.add_argument(
        "--open-settings",
        action="store_true",
        default=False,
        help=get("args.help")
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=os.getenv("HEADLESS", "false").lower() == "true",
        help=get("args.headless")
    )

    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8080")),
        help=get("args.port")
    )

    parser.add_argument(
        "--config",
        type=str,
        default=os.getenv("CONFIG_PATH", ""),
        help=get("args.config")
    )

    parser.add_argument(
        "--ws-url",
        type=str,
        default=os.getenv("MATTERMOST_WS_URL", ""),
        help="Mattermost WS URL."
    )

    parser.add_argument(
        "--token",
        type=str,
        default=os.getenv("MATTERMOST_TOKEN", ""),
        help="Mattermost Token."
    )

    parser.add_argument(
        "--bot-token",
        type=str,
        default=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        help="Telegram Bot Token."
    )

    parser.add_argument(
        "--chat-id",
        type=str,
        default=os.getenv("TELEGRAM_CHAT_ID", ""),
        help="Telegram Chat ID."
    )

    parser.add_argument(
        "--excluded-senders",
        type=str,
        default=os.getenv("EXCLUDED_SENDERS", ""),
        help=get("excludedlist.senders.title_text")+"."
    )

    parser.add_argument(
        "--excluded-channels",
        type=str,
        default=os.getenv("EXCLUDED_CHANNELS", ""),
        help=get("excludedlist.channels.title_text")+"."
    )

    parser.add_argument(
        "--echo-suppression",
        action="store_true",
        default=os.getenv("ECHO_SUPPRESSION_ENABLED", "false").lower() == "true",
        help=get("settings.ui.chk_echo")+"."
    )

    parser.add_argument(
        "--anonymous-mode",
        action="store_true",
        default=os.getenv("ANONYMOUS_MODE", "false").lower() == "true",
        help=get("settings.ui.toggle_anon")+"."
    )

    parser.add_argument(
        "--include-sender",
        action="store_true",
        default=os.getenv("INCLUDE_SENDER", "false").lower() == "true",
        help=get("settings.ui.toggle_sender")+"."
    )

    parser.add_argument(
        "--include-channel",
        action="store_true",
        default=os.getenv("INCLUDE_CHANNEL", "false").lower() == "true",
        help=get("settings.ui.toggle_channel")+"."
    )

    parser.add_argument(
        "--include-message",
        action="store_true",
        default=os.getenv("INCLUDE_MESSAGE", "false").lower() == "true",
        help=get("settings.ui.toggle_message")+"."
    )

    parser.add_argument(
        "--aes-enabled",
        action="store_true",
        default=os.getenv("AES_ENCRYPTION_ENABLED", "false").lower() == "true",
        help=get("settings.ui.toggle_aes")+"."
    )

    parser.add_argument(
        "--aes-key",
        type=str,
        default=os.getenv("AES_ENCRYPTION_KEY", ""),
        help=get("args.aes_key")
    )

    parser.add_argument(
        "--ws-val",
        type=int,
        default=int(os.getenv("WS_RECONNECT_TIMEOUT", "5")),
        help=get("timeout.field1").replace(":",".")
    )

    parser.add_argument(
        "--retry-val",
        type=int,
        default=int(os.getenv("RETRY_LOGIC_TIMEOUT", "10")),
        help=get("timeout.field2").replace(":",".")
    )

    parser.add_argument(
        "--attempts-val",
        type=int,
        default=int(os.getenv("RETRY_LOGIC_MAX_ATTEMPTS", "5")),
        help=get("timeout.field3").replace(":",".")
    )

    parser.add_argument(
        "--tg-http-val",
        type=int,
        default=int(os.getenv("TG_HTTP_TIMEOUT", "5")),
        help=get("timeout.field4").replace(":",".")
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "INFO"),
        help=get("args.log_level")
    )

    parser.add_argument(
        "--lang",
        type=str,
        default=os.getenv("LANGUAGE", get_system_locale()),
        help=get("args.lang")
    )

    return parser.parse_args()