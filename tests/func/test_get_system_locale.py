import sys
from unittest.mock import MagicMock
from func.get_system_locale import get_system_locale

def test_get_system_locale_windows_success(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    
    mock_ctypes = MagicMock()
    mock_buf = MagicMock()
    mock_buf.value = "it-IT"
    mock_ctypes.create_unicode_buffer.return_value = mock_buf
    
    mock_kernel32 = MagicMock()
    mock_ctypes.windll.kernel32 = mock_kernel32
    
    monkeypatch.setitem(sys.modules, "ctypes", mock_ctypes)
    
    result = get_system_locale()
    assert result == "it_IT"

def test_get_system_locale_windows_fallback_to_locale(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    
    mock_ctypes = MagicMock()
    mock_buf = MagicMock()
    mock_buf.value = ""
    mock_ctypes.create_unicode_buffer.return_value = mock_buf
    monkeypatch.setitem(sys.modules, "ctypes", mock_ctypes)
    
    import locale
    monkeypatch.setattr(locale, "getlocale", lambda: ("fr_FR", "UTF-8"))
    
    result = get_system_locale()
    assert result == "fr_FR"

def test_get_system_locale_unix(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    
    import locale
    monkeypatch.setattr(locale, "getlocale", lambda: ("en_US.UTF-8", "UTF-8"))
    
    result = get_system_locale()
    assert result == "en_US"

def test_get_system_locale_total_fallback(monkeypatch):
    monkeypatch.setattr(sys, "platform", "unknown_os")
    
    import locale
    monkeypatch.setattr(locale, "getlocale", lambda: (None, None))
    
    result = get_system_locale()
    assert result == "en_US"