from ui.LangStatusBridge import LangStatusBridge, i18n_bridge

def test_lang_status_bridge_instance():
    assert isinstance(i18n_bridge, LangStatusBridge)

def test_lang_status_bridge_signal(qtbot):
    bridge = LangStatusBridge()
    
    received_messages = []
    
    bridge.status_changed.connect(received_messages.append)
    
    bridge.status_changed.emit("en")
    
    assert received_messages == ["en"]