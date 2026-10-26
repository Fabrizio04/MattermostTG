import os
import json
from func import i18n

def test_load_file_and_get(tmp_path, monkeypatch):
    lang_data = {
        "_metadata": {"language": "Italiano"},
        "test": {
            "greeting": "Ciao",
            "nested": {
                "value": "Valore profondo"
            }
        }
    }
    lang_file = tmp_path / "it_IT.json"
    lang_file.write_text(json.dumps(lang_data), encoding="utf-8")

    monkeypatch.setattr(i18n, "translations", {})
    monkeypatch.setattr(i18n, "metadata", {})

    i18n._loadFile(str(lang_file))

    assert i18n.get("test.greeting") == "Ciao"
    assert i18n.get("test.nested.value") == "Valore profondo"

    assert i18n.get("chiave.inesistente", default="Fallback") == "Fallback"

def test_copy_default(tmp_path, monkeypatch):
    monkeypatch.setattr(i18n, "I18N_PATH", tmp_path)
    
    internal_dir = tmp_path / "internal_i18n"
    internal_dir.mkdir()
    internal_file = internal_dir / "en_US.json"
    internal_file.write_text('{"hello": "world"}', encoding="utf-8")

    monkeypatch.setattr(i18n, "resource_path", lambda path: str(internal_dir / os.path.basename(path)))

    i18n._copyDefault()

    target_file = tmp_path / "en_US.json"
    assert target_file.exists()
    assert "hello" in target_file.read_text(encoding="utf-8")

def test_load_language_from_config(tmp_path, monkeypatch):
    monkeypatch.setattr(i18n, "I18N_PATH", tmp_path)
    
    custom_lang_file = tmp_path / "es_ES.json"
    custom_lang_file.write_text(json.dumps({"welcome": "Bienvenido"}), encoding="utf-8")

    monkeypatch.setattr(i18n, "config", {"LANGUAGE": "es_ES"})
    monkeypatch.setattr(i18n, "translations", {})

    i18n.load_language()

    assert i18n.get("welcome") == "Bienvenido"