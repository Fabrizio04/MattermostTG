import os
import json
import shutil

from logger import log
from settings import config, APP_DIR

from func.utils import resource_path
from func.get_system_locale import get_system_locale

translations = {}
metadata = {}

# ~/.mattermost_notifier/i18n/
I18N_PATH = APP_DIR / "i18n"
try:
    I18N_PATH.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
    
def load_language():

    _copyDefault()
    current_lang = config.get("LANGUAGE", get_system_locale())

    lang_file = I18N_PATH / f"{current_lang}.json"

    if not lang_file.exists():
        internal_file = resource_path(os.path.join("i18n", f"{current_lang}.json"))

        if os.path.exists(internal_file):
            shutil.copy(internal_file, lang_file)
        else:
            lang_file = I18N_PATH / "en_US.json"

    _loadFile(lang_file)
        
def _copyDefault():
    internal_file = resource_path(os.path.join("i18n", "en_US.json"))
    lang_file = I18N_PATH / "en_US.json"
    if os.path.exists(internal_file) and not lang_file.exists():
        shutil.copy(internal_file, lang_file)

def _loadFile(lang_file):
    global translations
    global metadata

    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            metadata = data.get("_metadata", {})
            translations = data
    except Exception as e:
        log.error(f"{get('log.i18n.error').format(lang_file=lang_file)} {e}")
        translations = {}
        metadata = {}

def get(key_path, default="None"):
    global translations

    if not bool(translations):
        load_language()

    keys = key_path.split(".")
    val = translations
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return default
    return val