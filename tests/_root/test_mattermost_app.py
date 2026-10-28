import sys
import pytest

from MattermostApp import MattermostApp
from PyQt6.QtWidgets import QApplication
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

def test_mattermost_app_init(qapp):
    with patch("MattermostApp.QSystemTrayIcon") as mock_tray_cls, \
         patch("MattermostApp.QMenu") as mock_menu_cls, \
         patch("MattermostApp.QAction") as mock_action_cls, \
         patch("MattermostApp.threading.Thread") as mock_thread_cls, \
         patch("MattermostApp.start_retry_worker") as mock_retry, \
         patch("MattermostApp.mattermost_listener.is_websocket_connected", return_value=True):
        
        mock_tray = MagicMock()
        mock_tray_cls.return_value = mock_tray

        app_instance = MattermostApp(qapp)

        assert app_instance.qapp == qapp
        assert app_instance.settings_dialog is None
        mock_tray.show.assert_called_once()
        assert mock_thread_cls.called
        mock_retry.assert_called_once()

def test_update_tray_menu(qapp):
    with patch("MattermostApp.QSystemTrayIcon"), \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"), \
         patch("MattermostApp.mattermost_listener.is_websocket_connected", return_value=False):
        
        app_instance = MattermostApp(qapp)
        app_instance.tray_ws_action = MagicMock()
        
        app_instance.update_tray_menu(None)
        app_instance.tray_ws_action.setText.assert_called()

def test_update_tray_ws_status(qapp):
    with patch("MattermostApp.QSystemTrayIcon"), \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"):
        
        app_instance = MattermostApp(qapp)
        app_instance.tray_ws_action = MagicMock()
        
        app_instance.update_tray_ws_status(True)
        app_instance.tray_ws_action.setText.assert_called()

def test_toggle_service(qapp):
    with patch("MattermostApp.QSystemTrayIcon"), \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"), \
         patch("MattermostApp.mattermost_listener") as mock_listener:
        
        app_instance = MattermostApp(qapp)
        app_instance.action_active = MagicMock()
        app_instance.update_icon = MagicMock()
        
        app_instance.toggle_service(True)
        assert mock_listener.service_active is True
        app_instance.update_icon.assert_called_once()

def test_on_tray_activated_double_click(qapp):
    with patch("MattermostApp.QSystemTrayIcon") as mock_tray_cls, \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"):
        
        mock_tray = MagicMock()
        mock_tray_cls.return_value = mock_tray
        
        app_instance = MattermostApp(qapp)
        app_instance.toggle_service = MagicMock()
        app_instance.action_active = MagicMock()
        
        mattermost_app_mod = sys.modules['MattermostApp']
        reason = mattermost_app_mod.QSystemTrayIcon.ActivationReason.DoubleClick
        
        app_instance.on_tray_activated(reason)
        app_instance.toggle_service.assert_called_once()

def test_update_icon(qapp):
    with patch("MattermostApp.QSystemTrayIcon") as mock_tray_cls, \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"), \
         patch("MattermostApp.get_tray_icon") as mock_get_icon:
        
        mock_tray = MagicMock()
        mock_tray_cls.return_value = mock_tray
        
        app_instance = MattermostApp(qapp)
        app_instance.update_icon()
        mock_get_icon.assert_called()
        mock_tray.setIcon.assert_called()

def test_open_settings(qapp):
    with patch("MattermostApp.QSystemTrayIcon"), \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"), \
         patch("MattermostApp.SettingsDialog") as mock_dialog_cls:
        
        mock_dialog = MagicMock()
        mock_dialog_cls.return_value = mock_dialog
        
        app_instance = MattermostApp(qapp)
        app_instance.open_settings()
        
        mock_dialog_cls.assert_called_once_with(controller=app_instance)
        mock_dialog.show.assert_called_once()

def test_on_save_settings(qapp):
    with patch("MattermostApp.QSystemTrayIcon"), \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.start_retry_worker"), \
         patch("MattermostApp.config") as mock_config, \
         patch("MattermostApp.get_stylesheet", return_value="stylesheet_string") as mock_stylesheet:
        
        mock_config.get.return_value = "dark"
        app_instance = MattermostApp(qapp)
        
        with patch.object(qapp, "setStyleSheet") as mock_set_style:
            app_instance.on_save_settings()
            mock_stylesheet.assert_called_once_with("dark")
            mock_set_style.assert_called_once_with("stylesheet_string")

def test_quit(qapp):
    with patch("MattermostApp.QSystemTrayIcon") as mock_tray_cls, \
         patch("MattermostApp.QMenu"), \
         patch("MattermostApp.QAction"), \
         patch("MattermostApp.threading.Thread"), \
         patch("MattermostApp.stop_retry_worker") as mock_stop_retry, \
         patch("MattermostApp.mattermost_listener") as mock_listener:
        
        mock_tray = MagicMock()
        mock_tray_cls.return_value = mock_tray
        
        app_instance = MattermostApp(qapp)
        
        with patch.object(qapp, "quit") as mock_qapp_quit:
            app_instance.quit()
            
            assert mock_listener.running is False
            mock_stop_retry.assert_called_once()
            mock_tray.hide.assert_called_once()
            mock_qapp_quit.assert_called_once()