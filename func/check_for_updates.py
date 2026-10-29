import json
import urllib.request

from logger import log
from func.i18n import get 
from version import __version__, GITHUB_REPO

def check_for_updates():
    """
    Controlla se esiste una nuova versione su GitHub.
    Restituisce una tupla: (is_update_available, latest_version, html_url)
    """
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            api_url, 
            headers={"User-Agent": "MattermostTG-App"}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
            latest_tag = data.get("tag_name", "").lstrip("v")
            html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
            
            current_version = __version__.lstrip("v")
            
            if latest_tag and latest_tag != current_version:
                return True, latest_tag, html_url
            
            return False, current_version, html_url
    except Exception as e:
        log.error(f"{get('log.update.check_error')} {e}")
        return False, __version__, ""