# 🔔 Mattermost to Telegram Notifier

Un'applicazione tray per Windows leggera, sicura ed elegante creata in Python e PyQt6 per inoltrare le notifiche da **Mattermost** direttamente a un bot **Telegram** personalizzato.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

---

## 🌟 Caratteristiche Principali

* **System Tray App**: Funziona in background con un'icona di stato dinamica (Attiva / Inattiva).
* **Connessione WebSocket**: Ascolto in tempo reale degli eventi Mattermost senza carico sul server.
* **Sicurezza Avanzata**:
  * I token sensibili (Mattermost e Telegram) sono salvati in modo sicuro in **Windows Credential Manager** tramite `keyring`.
  * Le impostazioni generali non sensibili sono salvate in locale su `settings.json`.
* **Riconnessione al volo**: Modificando l'URL o il token nelle impostazioni, il WebSocket viene ricreato automaticamente senza dover riavviare l'applicazione.
* **Notifiche Formattate**: Ricevi la data e l'ora del messaggio, il nome del mittente e il canale direttamente su Telegram.
* **Logging personalizzato**: Tracciamento di eventi ed errori su console e file locale `app.log`.

---

## 🛠️ Architettura del Progetto

```
MattermostTG/
├── img/
│   ├── icon_active.ico       # Icona per stato attivo
│   ├── icon_inactive.ico     # Icona per stato inattivo
|   └── mattermost.af         # Progetto affinity
├── mattermost_notifier.py    # Entry point dell'applicazione
├── MattermostApp.py          # Gestione System Tray e menu contestuale
├── SettingsDialog.py         # Interfaccia GUI per la configurazione
├── listen_mattermost.py      # Gestione ciclo eventi WebSocket asyncio
├── message.py                # Invio chiamate API verso Telegram
├── settings.py               # Lettura/scrittura configurazioni e keyring
├── logger.py                 # Sistema di logging centralizzato
└── utils.py                  # Gestione percorsi risorse e icone
```

---

## 🚀 Installazione e Avvio (Sviluppo)

1. **Clona il repository:**
   ```bash
   git clone https://github.com/Fabrizio04/MattermostTG.git
   cd MattermostTG
   ```

2. **Crea ed attiva un ambiente virtuale (opzionale ma consigliato):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installa le dipendenze:**
   ```bash
   pip install PyQt6 websockets requests keyring pyinstaller
   ```

4. **Avvia l'applicazione:**
   ```bash
   python mattermost_notifier.py
   ```

---

## 📦 Generazione dell'Eseguibile Standalone (`.exe`)

Per impacchettare l'intera applicazione in un singolo file eseguibile per Windows:

```bash
py -m PyInstaller --noconsole --onefile --add-data "img;img" --icon="img/icon_active.ico" --name="MattermostNotifier" mattermost_notifier.py
```

Troverai il file `MattermostNotifier.exe` pronto all'uso all'interno della cartella `dist/`.

---

## 📋 Configurazione Iniziale

Alla prima esecuzione:
1. Clicca con il tasto destro sull'icona della System Tray e seleziona **Impostazioni**.
2. Inserisci:
   * **URL WebSocket Mattermost** (es. `wss://mattermost.tuodominio.it/api/v4/websocket`)
   * **Token Personal Access Mattermost**
   * **Telegram Bot Token** (ottenuto da `@BotFather`)
   * **Telegram Chat ID** (ottenuto da `@userinfobot`)
3. Clicca su **Salva**. L'app si connetterà immediatamente!