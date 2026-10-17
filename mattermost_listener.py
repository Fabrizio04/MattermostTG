import json
import asyncio
import websockets

from logger import log
from settings import config
from func.message import send_telegram
from ui.WSStatusBridge import ws_bridge
from func.fetch_user_id import fetch_user_id
from func.format_notification import format_notification

# --- STATI APPLICAZIONE ---
running = True
service_active = True
current_ws = None
main_loop = None
user_id = None

async def mattermost_listener():
    global running, service_active, current_ws, main_loop, user_id
    main_loop = asyncio.get_running_loop()

    while running:
        ws_url = config.get("MATTERMOST_WS_URL")
        token = config.get("MATTERMOST_TOKEN")

        if not ws_url or not token:
            await asyncio.sleep(int(config.get("WS_RECONNECT_TIMEOUT", 5)))
            continue

        user_id = fetch_user_id(ws_url, token)

        try:
            log.debug("Connessione al WebSocket Mattermost in corso...")
            async with websockets.connect(ws_url) as ws:
                current_ws = ws

                auth_payload = {
                    "seq": 1,
                    "action": "authentication_challenge",
                    "data": {"token": token}
                }
                await ws.send(json.dumps(auth_payload))

                log.debug("Autenticazione WebSocket completata.")
                ws_bridge.status_changed.emit(True)
                
                while running:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    
                    if data.get("event") == "posted":
                        post_data = json.loads(data["data"]["post"])

                        # dati del messaggio
                        message_text = post_data.get("message", "N/D")
                        sender_name = data["data"].get("sender_name", "N/D")
                        channel_display_name = data["data"].get("channel_display_name", "N/D")
                        post_user_id = post_data.get("user_id")

                        # controllo automatico Echo Suppression tramite user_id
                        if config.get("ECHO_SUPPRESSION_ENABLED", True):
                            if user_id and post_user_id == user_id:
                                log.debug("Messaggio scartato (Echo Suppression).")
                                continue

                        # verifica liste di esclusione
                        excluded_senders_raw = config.get("EXCLUDED_SENDERS", "")
                        excluded_channels_raw = config.get("EXCLUDED_CHANNELS", "")

                        excluded_senders = {s.strip().lower() for s in excluded_senders_raw.replace(",", "\n").split("\n") if s.strip()}
                        excluded_channels = {c.strip().lower() for c in excluded_channels_raw.replace(",", "\n").split("\n") if c.strip()}

                        if sender_name.lower() in excluded_senders:
                            log.debug(f"Messaggio scartato: mittente '{sender_name}' in lista di esclusione.")
                            continue

                        if channel_display_name.lower() in excluded_channels:
                            log.debug(f"Messaggio scartato: canale '{channel_display_name}' in lista di esclusione.")
                            continue

                        # invio messaggio
                        create_at_ms = post_data.get("create_at")
                                                
                        notification_msg = format_notification(create_at_ms, channel_display_name, sender_name, message_text)
                        log.debug(f"Messaggio formattato: {notification_msg}")

                        if not notification_msg:
                            log.warning("Messaggio formattato non valido")
                        else:
                            if service_active:
                                send_telegram(notification_msg)
                            else:
                                log.warning("Servizio in pausa: notifica ignorata")

        #except websockets.exceptions.ConnectionClosed:
            #log.debug("Connessione WebSocket chiusa.")
        except Exception as e:
            log.error(f"Errore di connessione verso Mattermost WS: {e}")
        finally:
            current_ws = None
            ws_bridge.status_changed.emit(False)
            if running:
                log.debug(f"Riconnessione tra {config.get("WS_RECONNECT_TIMEOUT", 5)} secondi...")
                await asyncio.sleep(int(config.get("WS_RECONNECT_TIMEOUT", 5)))

def reconnect_websocket():
    """
    Forza la chiusura del socket corrente.
    Il ciclo 'while running' lo riconnetterà immediatamente usando le nuove configurazioni.
    """
    global current_ws, main_loop
    if current_ws and main_loop and main_loop.is_running():
        log.debug("Riconnessione WebSocket richiesta a seguito di modifiche...")
        # Pianifica la chiusura del socket all'interno del loop thread-safe di asyncio
        main_loop.call_soon_threadsafe(lambda: asyncio.create_task(current_ws.close()))

def run_websocket_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(mattermost_listener())


def is_websocket_connected() -> bool:
    global current_ws
    return current_ws is not None