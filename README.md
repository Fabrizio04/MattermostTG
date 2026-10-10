# 🔔 Mattermost to Telegram Notifier

Un'applicazione tray cross-platform (Windows, Linux, macOS) leggera, sicura ed elegante creata in Python e PyQt6 per inoltrare le notifiche da **Mattermost** direttamente a un bot **Telegram** personalizzato.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

---

## 🌟 Caratteristiche Principali

* **Cross-Platform System Tray App**: Funziona in background su Windows, Linux (GNOME, Cinnamon, XFCE) e macOS con un'icona di stato dinamica (Attiva / Inattiva).
* **Connessione WebSocket**: Ascolto in tempo reale degli eventi Mattermost senza carico sul server.
* **Sicurezza Avanzata**:
  * I token sensibili (Mattermost e Telegram) sono salvati in modo sicuro nel gestore credenziali di sistema (**Windows Credential Manager**, **Secret Service/KWallet**, **macOS Keychain**) tramite `keyring` con fallback graceful.
  * Le impostazioni generali non sensibili sono salvate in locale su `settings.json`.
* **Compatibilità Linux/GNOME**: Gestione automatica del backend grafico (`xcb`/`wayland`) e isolamento da bug di temi GTK3/GLib per evitare crash di sistema.
* **Riconnessione al volo**: Modificando l'URL o il token nelle impostazioni, il WebSocket viene ricreato automaticamente senza dover riavviare l'applicazione.
* **Notifiche Formattate**: Ricevi la data e l'ora del messaggio, il nome del mittente e il canale direttamente su Telegram.
* **Logging personalizzato**: Tracciamento di eventi ed errori su console e file locale `app.log`.

---

## 🛠️ Architettura del Progetto

```
MattermostTG/
├── img/
    ├── icon_active.ico       # Icona per Windows (Attiva)
    ├── icon_inactive.ico     # Icona per Windows (Inattiva)
    ├── icon_active.png       # Icona per Linux / macOS (Attiva)
    ├── icon_inactive.png     # Icona per Linux / macOS (Inattiva)
    └── mattermost.af         # Progetto affinity
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

2. **Installa le dipendenze di sistema (Solo Linux):**

   **Ubuntu / Debian / Linux Mint**
   ```bash
   sudo apt update
   sudo apt install -y libxcb-cursor0 libxcb-util1 libx11-xcb1 dbus
   ```

4. **Crea ed attiva un ambiente virtuale (opzionale ma consigliato):**
   
   **Windows**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   **Linux / macOS**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Installa le dipendenze Python:**
   ```bash
   pip install PyQt6 websockets requests keyring pyinstaller
   ```

6. **Avvia l'applicazione:**
   ```bash
   python mattermost_notifier.py
   ```

---

## 📦 Generazione dell'Eseguibile Standalone (`.exe`)

### 🪟 Windows (.exe)

```bash
py -m PyInstaller --noconsole --onefile --add-data "img;img" --icon="img/icon_active.ico" --name="MattermostNotifier-Win" mattermost_notifier.py
```

### 🐧 Linux (Binary ELF)

```bash
pyinstaller --noconsole --onefile --add-data "img:img" --name "MattermostNotifier-Linux" mattermost_notifier.py
```

### 🍏 macOS (Binary Executable)

```bash
pyinstaller --noconsole --onefile --add-data "img:img" --name "MattermostNotifier-macOS" mattermost_notifier.py
```

Troverai il file eseguibile compilato all'interno della cartella `dist/`.

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

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza **MIT**. Consulta il file [LICENSE](LICENSE) per maggiori dettagli.