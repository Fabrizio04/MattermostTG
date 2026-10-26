import sys
from pathlib import Path
from unittest.mock import MagicMock

from func.check_auto_startup import check_auto_startup

def test_check_auto_startup_windows_true(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    
    mock_reg = MagicMock()
    mock_key = MagicMock()
    mock_reg.OpenKey.return_value = mock_key
    mock_reg.QueryValueEx.return_value = ("percorso_applicazione", 1)
    
    monkeypatch.setitem(sys.modules, "winreg", mock_reg)
    
    assert check_auto_startup() is True

def test_check_auto_startup_windows_false(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    
    mock_reg = MagicMock()
    mock_reg.OpenKey.side_effect = Exception("Key not found")
    
    monkeypatch.setitem(sys.modules, "winreg", mock_reg)
    
    assert check_auto_startup() is False

def test_check_auto_startup_linux_true(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    autostart_dir = tmp_path / ".config" / "autostart"
    autostart_dir.mkdir(parents=True)
    desktop_file = autostart_dir / "mattermost_notifier.desktop"
    desktop_file.write_text("[Desktop Entry]\nName=Test", encoding="utf-8")
    
    assert check_auto_startup() is True

def test_check_auto_startup_linux_false(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    assert check_auto_startup() is False

def test_check_auto_startup_darwin_true(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    launch_agents_dir = tmp_path / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True)
    plist_file = launch_agents_dir / "com.mattermost.notifier.plist"
    plist_file.write_text("<plist></plist>", encoding="utf-8")
    
    assert check_auto_startup() is True

def test_check_auto_startup_darwin_false(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    assert check_auto_startup() is False

def test_check_auto_startup_unknown_platform(monkeypatch):
    monkeypatch.setattr(sys, "platform", "unknown_os")
    assert check_auto_startup() is False