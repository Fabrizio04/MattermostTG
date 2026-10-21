import requests

from logger import log
from func.i18n import get

def fetch_user_id(ws_url, token):
    """
    Interroga l'API di Mattermost per ottenere il proprio user_id univoco.
    Converte un WS URL (es wss://chat.dominio.it/api/v4/websocket) in HTTP URL (https://chat.dominio.it/api/v4/users/me).
    """
    
    try:
        base_url = ws_url.replace("wss://", "https://").replace("ws://", "http://")
        if base_url.endswith("/websocket"):
            base_url = base_url[:-len("/websocket")]
        
        api_url = f"{base_url}/users/me"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            uid = user_data.get("id")
            log.debug(f"{get("log.fetch_user_id.user_id")} {uid}")
            return uid
        else:
            log.error(get("log.fetch_user_id.http_error").format(status_code=response.status_code))
    except Exception as e:
        log.error(get("log.fetch_user_id.error"))
        log.error(e)
    return None