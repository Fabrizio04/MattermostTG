import json

from unittest.mock import patch
from PyQt6.QtWidgets import QWidget
from ui.LanguageDialog import LanguageDialog

def test_language_dialog_init(qtbot, tmp_path):
    i18n_dir = tmp_path / ".mattermost_notifier" / "i18n"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    
    lang_file = i18n_dir / "en.json"
    lang_data = {
        "_metadata": {
            "language_name": "English",
            "version": "1.0",
            "author": "Test Author",
            "contact": "https://example.com"
        }
    }
    lang_file.write_text(json.dumps(lang_data), encoding="utf-8")

    with patch("pathlib.Path.home", return_value=tmp_path), \
         patch("ui.LanguageDialog.get", side_effect=lambda k: k):
        
        dlg = LanguageDialog()
        qtbot.addWidget(dlg)
        
        assert dlg.table.rowCount() == 1
        assert dlg.table.item(0, 0).text() == "English"
        assert dlg.table.item(0, 1).text() == "1.0"
        assert dlg.table.item(0, 2).text() == "Test Author"
        assert dlg.table.item(0, 4).text() == "en.json"
        
        dlg.close()

@patch("subprocess.Popen")
@patch("os.startfile", create=True)
def test_language_dialog_open_folder(qtbot, tmp_path):
    with patch("pathlib.Path.home", return_value=tmp_path), \
         patch("ui.LanguageDialog.get", side_effect=lambda k: k):
        
        dlg = LanguageDialog()
        qtbot.addWidget(dlg)
        
        dlg.open_i18n_folder()
        dlg.close()

def test_language_dialog_apply_language(qtbot, monkeypatch, tmp_path):
    i18n_dir = tmp_path / ".mattermost_notifier" / "i18n"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    lang_file = i18n_dir / "it.json"
    lang_file.write_text(json.dumps({"_metadata": {"language_name": "Italiano"}}), encoding="utf-8")

    monkeypatch.setattr("ui.LanguageDialog.config", {"THEME": "light"})

    with patch("pathlib.Path.home", return_value=tmp_path), \
         patch("ui.LanguageDialog.save_settings") as mock_save, \
         patch("ui.LanguageDialog.load_language") as mock_load_lang, \
         patch("ui.LanguageDialog.CustomMessageBox.show_info") as mock_show_info, \
         patch("ui.LanguageDialog.i18n_bridge") as mock_bridge, \
         patch("ui.LanguageDialog.get", side_effect=lambda k: k):
        
        dlg = LanguageDialog()
        qtbot.addWidget(dlg)
        
        dlg.table.selectRow(0)
        
        dlg.on_apply_clicked()
        
        mock_save.assert_called_once()
        mock_load_lang.assert_called_once()
        mock_bridge.status_changed.emit.assert_called_with("it")
        mock_show_info.assert_called_once()
        
        dlg.close()

@patch("ui.LanguageDialog.exec_with_parent_dim")
def test_open_language_dialog_static(mock_exec_dim, qtbot, tmp_path):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    with patch("pathlib.Path.home", return_value=tmp_path), \
         patch("ui.LanguageDialog.get", side_effect=lambda k: k):
        
        LanguageDialog.open_LanguageDialog(parent=parent)
        
    mock_exec_dim.assert_called_once()
    args, _ = mock_exec_dim.call_args
    assert isinstance(args[0], LanguageDialog)
    assert args[1] == parent