import json
import asyncio
import websockets

from logger import log
from settings import config
from datetime import datetime
from message import send_telegram

# --- STATI APPLICAZIONE ---
running = True
service_active = True
current_ws = None
main_loop = None

async def listen_mattermost():
    global running, service_active, current_ws, main_loop
    main_loop = asyncio.get_running_loop()

    while running:
        ws_url = config.get("MATTERMOST_WS_URL")
        token = config.get("MATTERMOST_TOKEN")

        if not ws_url or not token:
            await asyncio.sleep(3)
            continue

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
                
                while running:
                    msg = await ws.recv()
                    log.debug("Autenticazione WebSocket completata.")
                    data = json.loads(msg)
                    
                    if data.get("event") == "posted":
                        post_data = json.loads(data["data"]["post"])
                        message_text = post_data.get("message", "N/D")
                        sender_name = data["data"].get("sender_name", "N/D")
                        channel_display_name = data["data"].get("channel_display_name", "N/D")

                        create_at_ms = post_data.get("create_at")
                        if create_at_ms:
                            dt = datetime.fromtimestamp(create_at_ms / 1000.0)
                            formatted_time = dt.strftime("%d/%m/%Y alle %H:%M")
                        else:
                            formatted_time = datetime.now().strftime("%d/%m/%Y alle %H:%M")
                                                
                        notification_msg = f"*Mattermost Notifier*\n\nData: {formatted_time}\nCanale: {channel_display_name}\nDa: *{sender_name}*\nMessaggio: {message_text}"
                        log.debug(notification_msg)
                        
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
            if running:
                log.debug("Riconnessione tra 5 secondi...")
                await asyncio.sleep(5)

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
    loop.run_until_complete(listen_mattermost())