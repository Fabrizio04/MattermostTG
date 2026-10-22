# 🔔 Mattermost to Telegram Notifier

Un'applicazione tray cross-platform (Windows, Linux, macOS) leggera, sicura ed elegante creata in Python e PyQt6 per inoltrare le notifiche da **Mattermost** direttamente a un bot **Telegram** personalizzato.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Build](https://github.com/Fabrizio04/MattermostTG/actions/workflows/build.yml/badge.svg)

---

## 🌟 Caratteristiche Principali

* **Cross-Platform System Tray App**: Funziona in background su Windows, Linux (GNOME, Cinnamon, XFCE) e macOS con un'icona di stato dinamica (Attiva / Inattiva).
* **Connessione WebSocket**: Ascolto in tempo reale degli eventi Mattermost senza carico sul server.
* **Sicurezza Avanzata**:
  * I token sensibili (Mattermost e Telegram) sono salvati in modo sicuro nel gestore credenziali di sistema (**Windows Credential Manager**, **Secret Service/KWallet**, **macOS Keychain**) tramite `keyring` con fallback graceful.
  * È possibile inoltrare i messaggi usando lo standard di crittografia `AES-256`
  * Le impostazioni generali non sensibili sono salvate in locale su `mattermosttg.json`.
* **Compatibilità Linux/GNOME**: Gestione automatica del backend grafico (`xcb`/`wayland`) e isolamento da bug di temi GTK3/GLib per evitare crash di sistema.
* **Riconnessione al volo**: Modificando l'URL o il token nelle impostazioni, il WebSocket viene ricreato automaticamente senza dover riavviare l'applicazione.
* **Notifiche Formattate**: Ricevi la data e l'ora del messaggio, il nome del mittente e il canale direttamente su Telegram.
* **Logging personalizzato**: Tracciamento di eventi ed errori su console e file locale `mattermosttg.log`.

---

## 🛠️ Architettura del Progetto

```
MattermostTG/
├── aes/
    └── decrypter.html             # Webapp per decifrazione AES-256
├── func/
    ├── aes.py                     # Gestione crittografia AES-256
    ├── check_auto_startup.py      # Funzione per verifica auto startup
    ├── check_on_close.py          # Funzione per controllo modifiche
    ├── create_toggle_row.py       # Funzione per creazione toggle row
    ├── fetch_user_id.py           # Funzione per salvataggio id utente
    ├── format_notification.py     # Funzione per formattazione notifica
    ├── get_system_locale.py       # Funzione per localizzazione corrente
    ├── i18n.py                    # Gestione localizzazione applicazione
    ├── message_queue.py           # Gestione retry e coda di invio
    ├── message.py                 # Invio chiamate API verso Telegram
    ├── theme.py                   # Gestione tema e stili applicazione
    ├── utils.py                   # Gestione percorsi risorse e icone
    └── window.py                  # Gestione configurazione finestre
├── i18n/
    ├── en_US.json                 # Language pack English en_US
    └── it_IT.json                 # Language pack Italiano it_IT
├── img/
    ├── icon_active.ico            # Icona per Windows (Attiva)
    ├── icon_inactive.ico          # Icona per Windows (Inattiva)
    ├── icon_active.png            # Icona per Linux / macOS (Attiva)
    ├── icon_inactive.png          # Icona per Linux / macOS (Inattiva)
    ├── mattermosttg.af            # Progetto affinity
    └── mattermosttg.svg           # Immagine vettoriale
├── model/
    └── FailedMessage.py           # Messaggio per coda retry
├── ui/
    ├── AboutDialog.py             # Interfaccia GUI per le informazioni
    ├── CustomMessageBox.py        # Interfaccia GUI per messaggi generali
    ├── CustomTitleBar.py          # Componente GUI per barra del titolo
    ├── DimmerOverlay.py           # Componente GUI per overlay modali
    ├── ExcludedListDialog.py      # Interfaccia GUI per le liste di esclusione
    ├── LangStatusBridge.py        # Componente GUI bridge di comunicazione
    ├── LanguageDialog.py          # Interfaccia GUI per la selezione lingua
    ├── LogViewerDialog.py         # Interfaccia GUI per i log dell'applicazione
    ├── SettingsDialog.py          # Interfaccia GUI per la configurazione
    ├── TimeoutSettingsDialog.py   # Interfaccia GUI per i parametri timeout
    ├── ToggleSwitch.py            # Componente GUI toggle switch
    └── WSStatusBridge.py          # Componente GUI bridge di comunicazione
├── logger.py                      # Sistema di logging centralizzato
├── mattermost_listener.py         # Gestione ciclo eventi WebSocket asyncio
├── mattermost_notifier.py         # Entry point dell'applicazione
├── MattermostApp.py               # Gestione System Tray e menu contestuale
└── settings.py                    # Lettura/scrittura configurazioni e keyring
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
   pip install PyQt6 websockets requests keyring cryptography pyinstaller
   ```

6. **Avvia l'applicazione:**
   ```bash
   python mattermost_notifier.py
   ```

---

## 📦 Generazione dell'Eseguibile Standalone

### 🪟 Windows (.exe)

```bash
py -m PyInstaller --noconsole --onefile --add-data "img;img" --add-data "aes;aes" --add-data "i18n;i18n" --icon="img/icon_active.ico" --name="MattermostNotifier-Win" mattermost_notifier.py
```

### 🐧 Linux (Binary ELF)

```bash
pyinstaller --noconsole --onefile --add-data "img:img" --add-data "aes:aes" --add-data "i18n:i18n" --name "MattermostNotifier-Linux" mattermost_notifier.py
```

Per una guida dettagliata all'installazione permanente e all'integrazione nel menu di sistema su distribuzioni Linux, consulta la [Guida Linux](doc/LINUX_DEPLOY.md).

### 🍏 macOS (Binary Executable)

```bash
pyinstaller --noconsole --onefile --add-data "img:img" --add-data "aes:aes" --add-data "i18n:i18n" --name "MattermostNotifier-macOS" mattermost_notifier.py
```

Troverai il file eseguibile compilato all'interno della cartella `dist/`.

---

## ⚙️ Avvio Automatico (Autostart)

Per una guida dettagliata sulla configurazione dell'avvio automatico, consulta la [Guida Autostart](doc/AUTOSTART.md).

---

## 📋 Configurazione Iniziale

Alla prima esecuzione:
1. Clicca con il tasto destro sull'icona della System Tray e seleziona **Impostazioni**.
2. Inserisci:
   * **URL WebSocket Mattermost** (es. `wss://mattermost.tuodominio.it/api/v4/websocket`)
   * **Token Personal Access Mattermost**
   * **Telegram Bot Token** (ottenuto da [@BotFather](https://telegram.me/BotFather))
   * **Telegram Chat ID** (ottenuto da [@userinfobot](https://telegram.me/userinfobot))
3. Clicca su **Salva**. L'app si connetterà immediatamente!

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza **MIT**. Consulta il file [LICENSE](LICENSE.txt) per maggiori dettagli.