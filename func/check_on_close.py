from settings import config
from PyQt6.QtWidgets import QMessageBox

from ui.CustomMessageBox import CustomMessageBox

def check_on_close(parent_window, current_values: dict, save_callback) -> bool:
    """
    Confronta i valori correnti della UI con quelli salvati in config.
    Se ci sono differenze, chiede all'utente se vuole salvare.
    
    Ritorna:
        - True se la finestra può chiudersi (salvato, scartato o nessun cambiamento).
        - False se l'utente ha cliccato su 'Annulla' e vuole tornare alla finestra.
    """
    # Mappatura o controllo diretto delle differenze
    has_changes = False
    for key, current_val in current_values.items():
        if config.get(key) != current_val:
            has_changes = True
            break
            
    if has_changes:
        # reply = QMessageBox.question(
        #     parent_window,
        #     "Modifiche non salvate",
        #     "Hai modificato alcune impostazioni senza salvarle.\nVuoi salvare le modifiche prima di chiudere?",
        #     QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        #     QMessageBox.StandardButton.Save
        # )

        reply = CustomMessageBox.ask_save_changes(
            parent_window,
            "Modifiche non salvate",
            "Hai modificato alcune impostazioni senza salvarle.\nVuoi salvare le modifiche prima di chiudere?"
        )
        
        if reply == "save":
            save_callback()  # Esegue la funzione di salvataggio della specifica finestra
            return True
        elif reply == "discard":
            return True      # Chiude senza salvare
        else:
            return False     # Annulla la chiusura e resta nella finestra
            
    return True