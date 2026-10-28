import json
import logger
import logging

from unittest.mock import patch

def test_get_initial_log_level_headless_cli_config(tmp_path):
    cfg_file = tmp_path / "custom.json"
    cfg_file.write_text(json.dumps({"LOG_LEVEL": "debug"}), encoding="utf-8")

    with patch("sys.argv", ["script.py", "--headless", "--config", str(cfg_file)]):
        level = logger.get_initial_log_level()
        assert level == "DEBUG"

def test_get_initial_log_level_headless_cli_level():
    with patch("sys.argv", ["script.py", "--headless", "--log-level", "warning"]):
        level = logger.get_initial_log_level()
        assert level == "WARNING"

def test_get_initial_log_level_headless_env():
    with patch("sys.argv", ["script.py", "--headless"]), \
         patch.dict("os.environ", {"LOG_LEVEL": "error"}):
        level = logger.get_initial_log_level()
        assert level == "ERROR"

def test_get_initial_log_level_gui_config(tmp_path):
    cfg_file = tmp_path / "mattermostttg.json"
    cfg_file.write_text(json.dumps({"LOG_LEVEL": "debug"}), encoding="utf-8")

    with patch("sys.argv", ["script.py"]), \
         patch("logger.CONFIG_FILE_PATH", str(cfg_file)), \
         patch.dict("os.environ", {}, clear=True):
        level = logger.get_initial_log_level()
        assert level == "DEBUG"

def test_get_initial_log_level_default():
    with patch("sys.argv", ["script.py"]), \
         patch("os.path.exists", return_value=False), \
         patch.dict("os.environ", {}, clear=True):
        level = logger.get_initial_log_level()
        assert level == "INFO"

def test_setup_logger(tmp_path):
    log_file = tmp_path / "mattermostttg.log"
    test_logger = logging.getLogger("MattermostNotifier")
    test_logger.handlers.clear()

    with patch("logger.LOG_FILE_PATH", str(log_file)), \
         patch("logger.get_initial_log_level", return_value="DEBUG"):
        
        test_logger.handlers.clear()
        
        lg = logger.setup_logger()
        assert lg.level == logging.DEBUG
        assert len(lg.handlers) >= 0