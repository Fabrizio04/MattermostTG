import os

from func.i18n import get
from func.utils import resource_path
from func.aes import get_or_create_aes_key

from logger import log

def get_decrypter(includeKey):
    template_path = resource_path(os.path.join("web", "decrypter.html"))

    if not os.path.exists(template_path):
        return "NF"

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        html_content = html_content.replace("===KEY===", get("decrypter.key"))
        html_content = html_content.replace("===MY_PRIVATE_KEY===", get_or_create_aes_key() if includeKey == True else "")
        html_content = html_content.replace("===UPLOAD===", get("decrypter.upload"))
        html_content = html_content.replace("===PAYLOAD===", get("decrypter.payload"))
        html_content = html_content.replace("===PLACEHOLDER===", get("decrypter.placeholder"))
        html_content = html_content.replace("===BTN_DECRYPT===", get("decrypter.btn_decrypt"))
        html_content = html_content.replace("===MESSAGE===", get("decrypter.message"))
        html_content = html_content.replace("===BTN_COPY===", get("decrypter.btn_copy"))
        html_content = html_content.replace("===ERROR===", get("decrypter.error"))
        html_content = html_content.replace("===COPIED===", get("decrypter.copied"))
        html_content = html_content.replace("===ERROR_COPY===", get("decrypter.error_copy"))

        return html_content
    except Exception as e:
        log.error(f"{get('log.aes.error_decrypter')} {e}")
        return ""