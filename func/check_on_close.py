from func.i18n import get
from settings import config
from ui.CustomMessageBox import CustomMessageBox

def check_on_close(parent_window, current_values: dict, save_callback) -> bool:
    """
    Confronta i valori correnti della UI con quelli salvati in config.
    Se ci sono differenze, chiede all'utente se vuole salvare.
    
    Ritorna:
        - True se la finestra può chiudersi (salvato, scartato o nessun cambiamento).
        - False se l'utente ha cliccato su 'Annulla' e vuole tornare alla finestra.
    """
    
    has_changes = False
    
    for key, current_val in current_values.items():
        if config.get(key) != current_val:
            has_changes = True
            break
            
    if has_changes:
        reply = CustomMessageBox.ask_save_changes(
            parent_window,
            get("settings.check_on_close.title"),
            get("settings.check_on_close.message")
        )
        
        if reply == "save":
            save_callback()
            return True
        elif reply == "discard":
            return True
        else:
            return False
            
    return True