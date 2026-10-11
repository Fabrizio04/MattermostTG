# 🚀 Guida all'Avvio Automatico (Autostart)

Questa guida spiega come configurare MattermostTG affinché si avvii automaticamente all'accesso dell'utente su **Windows**, **Linux** e **macOS**.

## 🪟 Windows (.exe)

Su Windows il metodo più semplice e pulito è posizionare un collegamento all'eseguibile all'interno della cartella di avvio automatico dell'utente.

1. **Premi la combinazione di tasti `Win + R` per aprire la finestra Esegui.**

2. **Digita `shell:startup` e premi Invio (questo aprirà la cartella Esecuzione automatica dell'utente corrente).**

3. **Crea un collegamento al tuo eseguibile `MattermostNotifier-Win.exe`:**
   * Fai clic destro sull'eseguibile → **Crea collegamento**.
   * Sposta o incolla il collegamento appena creato all'interno della cartella `shell:startup` aperta al punto 2.

In alternativa, puoi aggiungere una chiave nel Registro di sistema sotto `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.

## 🐧 Linux

Su Linux (GNOME, Cinnamon, XFCE, KDE) gli ambienti desktop supportano la specifica XDG Autostart tramite file `.desktop` posizionati nella cartella personale dell'utente.

1. **Apri il terminale e crea (se non esiste) la cartella di autostart nella tua home:**
```bash
mkdir -p ~/.config/autostart
```

2. **Crea un file di configurazione per l'avvio automatico:**
```bash
nano ~/.config/autostart/mattermosttg.desktop
```

3. **Incolla il seguente contenuto (assicurati che il percorso dell'eseguibile corrisponda a dove lo hai posizionato, ad esempio in `/usr/local/bin/MattermostTG/`):**
```bash
[Desktop Entry]
Type=Application
Name=Mattermost to Telegram Notifier
Comment=Avvia automaticamente MattermostTG nel system tray
Exec=/usr/local/bin/MattermostTG/MattermostNotifier-Linux
Terminal=false
X-GNOME-Autostart-enabled=true
```

4. **Salva il file (`Ctrl+O`, poi `Enter` e `Ctrl+X` su nano). Al prossimo accesso al sistema, l'app si avvierà in autonomia nella tray.**

## 🍏 macOS

Su macOS l'avvio automatico si gestisce tramite gli **Elementi di login** (Login Items) nelle impostazioni di sistema o creando un semplice file `LaunchAgents`.

Metodo rapido tramite Impostazioni di Sistema:

1. Apri **Impostazioni di Sistema** (System Settings) su macOS.

2. Cerca o vai su **Generali** → **Elementi di login** (Login Items).

3. Nella sezione **Apri al login** (Open at Login), clicca sul pulsante `+` (più).

4. Seleziona l'applicazione o l'eseguibile compilato di MattermostTG e confermare.