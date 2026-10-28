from unittest.mock import patch
from ui.LogViewerDialog import LogViewerDialog

def test_log_viewer_dialog_init_and_load(qtbot, tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("[INFO] Messaggio di test INFO\n[ERROR] Messaggio di test ERROR\n", encoding="utf-8")

    with patch("ui.LogViewerDialog.LOG_FILE_PATH", str(log_file)), \
         patch("ui.LogViewerDialog.get", side_effect=lambda k: k), \
         patch("ui.LogViewerDialog.fade_animation"):
        
        dlg = LogViewerDialog()
        qtbot.addWidget(dlg)
        
        html_content = dlg.text_area.toHtml()
        assert "Messaggio di test INFO" in html_content
        assert "Messaggio di test ERROR" in html_content
        assert dlg.timer.isActive()
        
        dlg.close()

def test_log_viewer_dialog_clear_log(qtbot, tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("[INFO] Log da cancellare", encoding="utf-8")

    with patch("ui.LogViewerDialog.LOG_FILE_PATH", str(log_file)), \
         patch("ui.LogViewerDialog.CustomMessageBox.ask_yes_no", return_value="yes"), \
         patch("ui.LogViewerDialog.CustomMessageBox.show_critical") as mock_critical, \
         patch("ui.LogViewerDialog.get", side_effect=lambda k: k), \
         patch("ui.LogViewerDialog.fade_animation"):
        
        dlg = LogViewerDialog()
        qtbot.addWidget(dlg)
        
        dlg.clear_log_file()
        
        assert log_file.read_text() == ""
        assert dlg.text_area.toPlainText() == ""
        mock_critical.assert_not_called()
        
        dlg.close()

def test_log_viewer_dialog_change_log_level(qtbot, tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("", encoding="utf-8")

    with patch("ui.LogViewerDialog.LOG_FILE_PATH", str(log_file)), \
         patch("ui.LogViewerDialog.save_settings") as mock_save, \
         patch("ui.LogViewerDialog.config", {"LOG_LEVEL": "INFO", "THEME": "light", "LANGUAGE": "it"}), \
         patch("ui.LogViewerDialog.get", side_effect=lambda k: k), \
         patch("ui.LogViewerDialog.fade_animation"):
        
        dlg = LogViewerDialog()
        qtbot.addWidget(dlg)
        
        dlg.combo_level.setCurrentText("DEBUG")
        
        mock_save.assert_called_once()
        
        dlg.close()

def test_log_viewer_dialog_read_new_logs(qtbot, tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("[INFO] Primo log\n", encoding="utf-8")

    with patch("ui.LogViewerDialog.LOG_FILE_PATH", str(log_file)), \
         patch("ui.LogViewerDialog.get", side_effect=lambda k: k), \
         patch("ui.LogViewerDialog.fade_animation"):
        
        dlg = LogViewerDialog()
        qtbot.addWidget(dlg)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("[WARNING] Secondo log incrementale\n")
            
        dlg.read_new_logs()
        
        content = dlg.text_area.toHtml()
        assert "Primo log" in content
        assert "Secondo log incrementale" in content
        
        dlg.close()