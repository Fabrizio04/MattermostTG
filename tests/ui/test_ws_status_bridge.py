from ui.WSStatusBridge import WSStatusBridge, ws_bridge

def test_ws_status_bridge_instance():
    assert isinstance(ws_bridge, WSStatusBridge)

def test_ws_status_bridge_signal(qtbot):
    bridge = WSStatusBridge()
    received_statuses = []
    
    bridge.status_changed.connect(received_statuses.append)
    
    bridge.status_changed.emit(True)
    bridge.status_changed.emit(False)
    
    assert received_statuses == [True, False]