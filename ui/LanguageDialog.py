import json
import base64

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QHeaderView, QWidget, QLabel
)

from pathlib import Path
from settings import config, save_settings

from ui.LangStatusBridge import i18n_bridge
from ui.CustomTitleBar import CustomTitleBar
from ui.CustomMessageBox import CustomMessageBox

from func.i18n import load_language, get, I18N_PATH
from func.window import initialize_window, exec_with_parent_dim

class LanguageDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        initialize_window(self, 700, 350)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title=get("language.title"))
        container_layout.addWidget(self.title_bar)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)
        
        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([get("language.col0"), get("language.col1"), get("language.col2"), get("language.col3"), get("language.col4")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.table.setTabKeyNavigation(False)

        self.table.setStyleSheet("""
            QTableWidget {
                outline: none;
                /*background-color: #ffffff;*/
                selection-background-color: #007acc;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                border: none;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QTableWidget::item:focus, QTableWidget::item:hover {
                border: none;
                outline: none;
                /*background-color: #007acc;*/
                /*color: #ffffff;*/
            }
        """)

        self.table.cellDoubleClicked.connect(self.on_language_double_clicked)
        self.table.verticalHeader().setVisible(False) if hasattr(self.table.verticalHeader(), "setVisible") else self.table.verticalHeader().hide()
        
        layout.addWidget(self.table)
        self.load_installed_languages()
        
        # Bottoni inferiori
        btn_layout = QHBoxLayout()
        self.btn_open_folder = QPushButton(get("language.btn_open_folder"))
        self.btn_open_folder.clicked.connect(self.open_i18n_folder)

        # Pulsante Applica
        self.btn_apply = QPushButton(get("language.btn_apply"))
        self.btn_apply.clicked.connect(self.on_apply_clicked)
        
        self.btn_close = QPushButton(get("language.btn_close"))
        self.btn_close.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_open_folder)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def load_installed_languages(self):
        i18n_dir = Path.home() / ".mattermost_notifier" / "i18n"
        if not i18n_dir.exists():
            i18n_dir.mkdir(parents=True, exist_ok=True)
            
        json_files = list(i18n_dir.glob("*.json"))
        self.table.setRowCount(len(json_files))
        
        for row, file_path in enumerate(json_files):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta = data.get("_metadata", {})
                    
                    icon = QIcon()
                    flag_b64 = meta.get("flag_base64", "")
                    if flag_b64:
                        try:
                            pixmap_data = base64.b64decode(flag_b64)
                            pixmap = QPixmap()
                            pixmap.loadFromData(pixmap_data)
                            if not pixmap.isNull():
                                icon = QIcon(pixmap)
                        except Exception:
                            pass

                    item_lang = QTableWidgetItem(icon, meta.get("language_name", file_path.stem))
                    
                    item_ver = QTableWidgetItem(meta.get("version", "1.0"))
                    item_author = QTableWidgetItem(meta.get("author", "n/d"))

                    contact_text = meta.get("contact", "")
                    if contact_text.startswith("http://") or contact_text.startswith("https://"):
                        
                        lbl = QLabel(f'<a href="{contact_text}" style="color: #66b2ff; text-decoration: underline;">{contact_text}</a>')
                        lbl.setOpenExternalLinks(True)
                        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                        lbl.setContentsMargins(4, 0, 0, 0)
                        lbl.setToolTip(contact_text)
                        lbl.setStyleSheet("""
                            QLabel {
                                background: transparent;
                            }
                            QToolTip {
                                background-color: #ffffde;
                                color: #000000;
                                border: 1px solid #767676;
                                padding: 4px;
                            }
                        """)
                        
                        self.table.setCellWidget(row, 3, lbl)
                        item_contact = QTableWidgetItem(contact_text)
                    else:
                        item_contact = QTableWidgetItem(contact_text)
                        self.table.setItem(row, 3, item_contact)
                    
                    item_file = QTableWidgetItem(file_path.name)
                    
                    self.table.setItem(row, 0, item_lang)
                    self.table.setItem(row, 1, item_ver)
                    self.table.setItem(row, 2, item_author)
                    self.table.setItem(row, 4, item_file)
            except Exception:
                pass

    def open_i18n_folder(self):
        import os, sys, subprocess
        i18n_dir = str(I18N_PATH)
        if sys.platform.startswith("win"):
            os.startfile(i18n_dir)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", i18n_dir])
        else:
            subprocess.Popen(["xdg-open", i18n_dir])

    def on_language_double_clicked(self, row, _):
        self.apply_language_from_row(row)

    def on_apply_clicked(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        self.apply_language_from_row(row)

    def apply_language_from_row(self, row):
        file_item = self.table.item(row, 4)

        if not file_item:
            return
        
        file_name = file_item.text() 
        lang_code = file_name.replace(".json", "")
        
        save_settings(
            config.get("MATTERMOST_WS_URL", ""),
            config.get("MATTERMOST_TOKEN", ""),
            config.get("TELEGRAM_BOT_TOKEN", ""),
            config.get("TELEGRAM_CHAT_ID", ""),
            config.get("EXCLUDED_SENDERS", ""),
            config.get("EXCLUDED_CHANNELS", ""),
            config.get("ECHO_SUPPRESSION_ENABLED", True),
            config.get("ANONYMOUS_MODE", False),
            config.get("INCLUDE_SENDER", True),
            config.get("INCLUDE_CHANNEL", True),
            config.get("INCLUDE_MESSAGE", True),
            config.get("AES_ENCRYPTION_ENABLED", False),
            config.get("ALWAYS_ON_TOP", False),
            config.get("WS_RECONNECT_TIMEOUT", 5),
            config.get("RETRY_LOGIC_TIMEOUT", 10),
            config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5),
            config.get("TG_HTTP_TIMEOUT", 5),
            config.get("LOG_LEVEL", "INFO"),
            config.get("THEME", "light"),
            lang_code
        )

        load_language()

        self.table.setHorizontalHeaderLabels([get("language.col0"), get("language.col1"), get("language.col2"), get("language.col3"), get("language.col4")])
        self.btn_open_folder.setText(get("language.btn_open_folder"))
        self.btn_apply.setText(get("language.btn_apply"))
        self.btn_close.setText(get("language.btn_close"))
        self.title_bar.title_label.setText(get("language.title"))

        i18n_bridge.status_changed.emit(lang_code)

        CustomMessageBox.show_info(self, get("language.alert_title"), get("language.alert_message"))

    @staticmethod
    def open_LanguageDialog(parent):
        dlg = LanguageDialog(parent=parent)
        exec_with_parent_dim(dlg, parent)