# Palette dei colori per i due temi
DARK_THEME = {
    "bg_color": "#2b2b2b",
    "fg_color": "#ffffff",
    "input_bg": "#3c3f41",
    "input_fg": "#ffffff",
    "btn_bg": "#007acc",
    "btn_fg": "#ffffff",
    "border_color": "#555555"
}

LIGHT_THEME = {
    "bg_color": "#f0f0f0",
    "fg_color": "#000000",
    "input_bg": "#ffffff",
    "input_fg": "#000000",
    "btn_bg": "#007acc",
    "btn_fg": "#ffffff",
    "border_color": "#cccccc"
}

def get_stylesheet(theme_name="light"):
    theme = DARK_THEME if theme_name == "dark" else LIGHT_THEME
    
    # Colori specifici basati sul tema corrente
    menu_hover_bg = "#383838" if theme_name == "dark" else "#e0e0e0"
    menu_hover_fg = "#ffffff" if theme_name == "dark" else "#000000"
    active_bg = "#444444" if theme_name == "dark" else "#d0d0d0"
    active_fg = "#ffffff" if theme_name == "dark" else "#000000"

    return f"""

        /* --- CONTAINER PRINCIPALE ARROTONDATO E SOLIDO --- */
        #MainContainer {{
            background-color: {theme["bg_color"]};
            border: 1px solid {theme["border_color"]};
            border-radius: 12px;
        }}

        /* La barra del titolo custom segue l'arrotondamento in alto */
        #CustomTitleBar {{
            border-top-left-radius: 11px;
            border-top-right-radius: 11px;
            background-color: {theme["bg_color"]};
            border-bottom: 1px solid {theme["border_color"]};
            margin: 0px 1px;
        }}

        /* Pulsante Chiudi nella Custom Title Bar */
        #TitleBarMinBtn, #TitleBarCloseBtn {{
            background-color: transparent;
            border: none;
            color: {theme["fg_color"]};
            font-size: 13px;
            font-weight: bold;
            min-width: 25px;
            max-width: 25px;
            min-height: 25px;
            max-height: 25px;
            border-top-right-radius: 11px; /* Si adatta perfettamente all'angolo arrotondato della finestra */
            padding: 0px 14px;
        }}

        #TitleBarCloseBtn:hover {{
            background-color: #e81123; /* Il classico rosso elegante di Windows/macOS al passaggio */
        }}

        #TitleBarCloseBtn:hover {{
            background-color: #e81123; /* Rosso Windows/Mac */
            color: white;
        }}

        /* Evitiamo che il corpo del message box tocchi i bordi arrotondati esterni */
        #MessageBoxBody {{
            background-color: transparent;
        }}

        /* Allineamento pulito per la title bar nei popup custom */
        CustomMessageBox #CustomTitleBar {{
            border-top-left-radius: 11px;
            border-top-right-radius: 11px;
            margin: 0px 1px;
        }}

        QWidget {{
            background-color: {theme["bg_color"]};
            color: {theme["fg_color"]};
        }}
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {theme["input_bg"]};
            color: {theme["input_fg"]};
            border: 1px solid {theme["border_color"]};
            border-radius: 4px;
            padding: 6px 4px;
        }}
        QPushButton {{
            background-color: {theme["btn_bg"]};
            color: {theme["btn_fg"]};
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #1c90ff;
        }}

        /* --- BARRA DEI MENU --- */
        QMenuBar {{
            background-color: {theme["bg_color"]};
            color: {theme["fg_color"]};
            margin: 0px 1px; /* La facciamo rientrare di 1 pixel ai lati per non farla toccare il bordo */
            border-left: 1px solid transparent;
            border-right: 1px solid transparent;
        }}
        QMenuBar::item {{
            background-color: {theme["bg_color"]}; /* Forziamo lo sfondo del tema anche sui singoli item non attivi */
            color: {theme["fg_color"]};
            padding: 4px 8px;
        }}
        QMenu::indicator {{
            width: 10px;  /* Larghezza dell'area della spunta */
            height: 10px; /* Altezza dell'area della spunta */
            left: 10px;    /* Sposta la spunta verso sinistra, avvicinandola al bordo */
        }}
        QMenuBar::item:selected {{ 
            background-color: {menu_hover_bg};
            color: {menu_hover_fg};
            border-radius: 3px;
        }}
        QMenuBar::item:pressed, QMenuBar::item:active, QMenuBar::item:on {{
            background-color: {active_bg};
            color: {active_fg};
            border-radius: 3px;
        }}

        /* --- MENU A TENDINA E CONTESTUALE --- */
        QMenu {{
            background-color: {theme["bg_color"]};
            color: {theme["fg_color"]};
            border: 1px solid {theme["border_color"]};
        }}
        QMenu::item {{
            padding: 6px 20px;
        }}
        QMenu::item:selected {{ 
            background-color: {menu_hover_bg};
            color: {menu_hover_fg};
        }}
        QMenu::separator {{
            height: 1px;
            background: {theme["border_color"]};
            margin: 4px 0px;
        }}

        /* --- STATO DISABILITATO --- */
        QWidget:disabled, QLineEdit:disabled, QLabel:disabled, QCheckBox:disabled, QRadioButton:disabled, QGroupBox::title:disabled {{
            color: #888888; /* Un grigio intermedio per rendere chiaro che non è attivo */
            opacity: 0.6;
        }}
        QMenu::item:disabled {{
            color: #888888; /* Sbiadisce anche le voci disabilitate nei menu a tendina */
        }}

        QGroupBox {{
            border: 1px solid {theme["border_color"]};
            border-radius: 8px;
            margin-top: 10px;
            color: {theme["fg_color"]};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {theme["fg_color"]};
        }}
    """

