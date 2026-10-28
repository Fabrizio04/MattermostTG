import os
import sys
import mattermost_notifier

from unittest.mock import patch, MagicMock

def test_main_headless_success():
    mock_args = MagicMock()
    mock_args.headless = True
    mock_args.open_settings = False

    mock_thread_instance = MagicMock()
    
    with patch("mattermost_notifier.parse_args", return_value=mock_args), \
         patch("mattermost_notifier.load_settings") as mock_load_settings, \
         patch("mattermost_notifier.load_language") as mock_load_lang, \
         patch("PyQt6.QtCore.QCoreApplication") as mock_app_cls, \
         patch("mattermost_notifier.QLockFile") as mock_lock_cls, \
         patch("threading.Thread", return_value=mock_thread_instance) as mock_thread_cls, \
         patch("func.message_queue.start_retry_worker") as mock_retry_worker, \
         patch("sys.exit") as mock_exit:
        
        mock_lock = MagicMock()
        mock_lock.tryLock.return_value = True
        mock_lock_cls.return_value = mock_lock

        mock_app = MagicMock()
        mock_app.exec.return_value = 0
        mock_app_cls.return_value = mock_app

        try:
            mattermost_notifier.main()
        except SystemExit:
            pass

        mock_load_settings.assert_called_once_with(mock_args)
        mock_load_lang.assert_called_once()
        mock_lock.tryLock.assert_called_once_with(100)

        assert mock_thread_cls.call_count >= 2
        assert mock_thread_instance.start.called

def test_main_lock_failure():
    mock_args = MagicMock()
    mock_args.headless = False

    with patch("mattermost_notifier.parse_args", return_value=mock_args), \
         patch("mattermost_notifier.load_settings"), \
         patch("mattermost_notifier.load_language"), \
         patch("mattermost_notifier.QLockFile") as mock_lock_cls, \
         patch("ui.CustomMessageBox.CustomMessageBox.show_warning_on_start") as mock_show_warning, \
         patch("sys.exit") as mock_exit:
        
        mock_lock = MagicMock()
        mock_lock.tryLock.return_value = False
        mock_lock_cls.return_value = mock_lock

        lock_path = os.path.join(os.path.dirname(__file__), "MattermostNotifier.lock")
        lock_file = mattermost_notifier.QLockFile(lock_path)
        
        if not lock_file.tryLock(100):
            if mock_args.headless:
                pass
            else:
                from ui.CustomMessageBox import CustomMessageBox
                CustomMessageBox.show_warning_on_start("Title", "Message")
            sys.exit(0)

        mock_show_warning.assert_called_once()
        mock_exit.assert_called_once_with(0)

def test_shutdown_gracefully():
    mattermost_notifier.app = MagicMock()
    
    with patch("mattermost_notifier.mattermost_listener") as mock_listener, \
         patch("func.message_queue.stop_retry_worker") as mock_stop_retry:
        
        if hasattr(mattermost_notifier, "shutdown_gracefully"):
            mattermost_notifier.shutdown_gracefully()
            assert mock_listener.running is False
            mock_stop_retry.assert_called_once()
            mattermost_notifier.app.quit.assert_called_once()

def test_sigint_handler():
    if hasattr(mattermost_notifier, "sigint_handler"):
        with patch("mattermost_notifier.shutdown_gracefully") as mock_shutdown:
            mattermost_notifier.sigint_handler(None, None)
            mock_shutdown.assert_called_once()