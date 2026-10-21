import sys
import locale

def get_system_locale():
    # Windows
    if sys.platform.startswith("win"):
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(85)
            ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85)
            if buf.value:
                return buf.value.replace("-", "_")
        except Exception:
            pass

    # Linux, macOS o come fallback per Windows
    try:
        locale.setlocale(locale.LC_ALL, '')
        lang_code, encoding = locale.getlocale()
        if lang_code:
            return lang_code.split('.')[0].replace('-', '_')
    except Exception:
        pass
    
    # Fallback
    return "en_US"