import os
import sys
from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from func.utils import make_circle_icon, resource_path, get_tray_icon

def test_make_circle_icon(qtbot):
    icon_active = make_circle_icon(active=True)
    assert isinstance(icon_active, QIcon)
    
    icon_inactive = make_circle_icon(active=False)
    assert isinstance(icon_inactive, QIcon)

def test_resource_path_dev(monkeypatch):
    if hasattr(sys, "_MEIPASS"):
        monkeypatch.delattr(sys, "_MEIPASS")
        
    path = resource_path("img/test.png")
    expected = os.path.join(os.path.abspath("."), "img/test.png")
    assert path == expected

def test_resource_path_pyinstaller(monkeypatch):
    monkeypatch.setattr(sys, "_MEIPASS", "/fake/meipass/path", raising=False)
    
    path = resource_path("img/test.png")
    expected = os.path.join("/fake/meipass/path", "img/test.png")
    assert path == expected

def test_get_tray_icon_file_exists(tmp_path, monkeypatch):
    img_dir = tmp_path / "img"
    img_dir.mkdir()
    
    monkeypatch.setattr(sys, "platform", "win32")
    icon_file = img_dir / "icon_active.ico"
    
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.save(str(icon_file), "ICO")
    
    monkeypatch.setattr("func.utils.resource_path", lambda rel: str(tmp_path / rel))
    
    icon = get_tray_icon(active=True)
    assert isinstance(icon, QIcon)
    assert not icon.isNull()

def test_get_tray_icon_file_not_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr("func.utils.resource_path", lambda rel: str(tmp_path / "non_existent.png"))
    
    with patch("logger.log.warning") as mock_log, \
         patch("func.i18n.get", return_value="Icon not found: {path}"):
         
        icon = get_tray_icon(active=False)
        assert isinstance(icon, QIcon)
        mock_log.assert_called_once()