# 🐧 Guida all'Installazione e Integrazione su Linux

Questa guida descrive come installare l'eseguibile binario di **MattermostTG** su sistemi Linux (testato su Ubuntu, Linux Mint e MX Linux) e come integrarlo nel menu delle applicazioni con un'icona personalizzata.

---

## 1. Posizionamento del Binario
Crea una cartella dedicata per l'applicazione (ad esempio in `/usr/local/bin/MattermostTG/`) e posiziona lì l'eseguibile compilato con PyInstaller:

```bash
sudo mkdir -p /usr/local/bin/MattermostTG
sudo cp MattermostNotifier-Linux /usr/local/bin/MattermostTG/
sudo chmod +x /usr/local/bin/MattermostTG/MattermostNotifier-Linux
```

## 2. Configurazione dell'Icona di Sistema

Salva l'icona dell'applicazione (es. in formato SVG o PNG) nella cartella delle icone di sistema di utente o di sistema:

```bash
sudo cp path/to/icon.svg /usr/share/icons/hicolor/scalable/apps/mattermosttg.svg
```

(Aggiorna eventualmente la cache delle icone con `sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor` se necessario).

## 3. Creazione del Launcher Desktop (.desktop)

Per fare in modo che l'applicazione compaia nel menu di avvio del tuo ambiente desktop, crea un file di configurazione denominato `mattermosttg.desktop` all'interno della cartella degli launcher utente (`~/.local/share/applications/`) o a livello di sistema (`/usr/share/applications/`):

```bash
nano ~/.local/share/applications/mattermosttg.desktop
```

Incolla il seguente blocco di configurazione:

```bash
[Desktop Entry]
Type=Application
Name=Mattermost to Telegram Notifier
Comment=Cross-platform tray app per notifiche Mattermost
Exec=/usr/local/bin/MattermostTG/MattermostNotifier-Linux
Icon=mattermosttg
Terminal=false
Categories=Utility;Network;
```

## 4. Permessi di Esecuzione

Rendi eseguibile il file `.desktop` appena creato affinché il sistema lo riconosca correttamente:

```bash
chmod +x ~/.local/share/applications/mattermosttg.desktop
```