import sys
import logging
from logger import log

def parse_arguments():
    if "/debug" in sys.argv or "--debug" in sys.argv:
        log.setLevel(logging.DEBUG)
        print("Modalità DEBUG attivata via riga di comando.")