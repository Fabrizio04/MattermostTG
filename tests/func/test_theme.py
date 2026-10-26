import sys
from func.theme import get_platform_font_css, get_stylesheet

def test_get_platform_font_css_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    css = get_platform_font_css(size_px=14)
    
    assert "Segoe UI" in css
    assert "14px" in css

def test_get_platform_font_css_macos(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    css = get_platform_font_css(size_px=12)
    
    assert "SF Pro Text" in css
    assert "12px" in css

def test_get_platform_font_css_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    css = get_platform_font_css(size_px=13)
    
    assert "Ubuntu" in css
    assert "13px" in css

def test_get_stylesheet_light():
    stylesheet = get_stylesheet("light")
    
    assert isinstance(stylesheet, str)
    assert "#f0f0f0" in stylesheet 
    assert "#cccccc" in stylesheet
    assert "font-family" in stylesheet

def test_get_stylesheet_dark():
    stylesheet = get_stylesheet("dark")
    
    assert isinstance(stylesheet, str)
    assert "#2b2b2b" in stylesheet
    assert "#555555" in stylesheet
    assert "font-family" in stylesheet