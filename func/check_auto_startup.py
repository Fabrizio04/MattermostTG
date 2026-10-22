import sys
from pathlib import Path
from settings import APP_NAME

def check_auto_startup() -> bool:
    
    if sys.platform.startswith("win"):
        import winreg as reg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
            value, _ = reg.QueryValueEx(key, APP_NAME)
            reg.CloseKey(key)
            return bool(value)
        except Exception:
            return False

    elif sys.platform.startswith("linux"):
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_file = autostart_dir / "mattermost_notifier.desktop"
        return desktop_file.exists()

    elif sys.platform.startswith("darwin"):
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_file = launch_agents_dir / "com.mattermost.notifier.plist"
        return plist_file.exists()

    return False