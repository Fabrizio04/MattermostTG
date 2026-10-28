import json
import asyncio
import mattermost_listener

from unittest.mock import patch, MagicMock, AsyncMock

def test_is_websocket_connected():
    mattermost_listener.current_ws = None
    assert mattermost_listener.is_websocket_connected() is False

    mattermost_listener.current_ws = MagicMock()
    assert mattermost_listener.is_websocket_connected() is True
    mattermost_listener.current_ws = None

def test_reconnect_websocket_no_loop():
    mattermost_listener.current_ws = None
    mattermost_listener.main_loop = None
    mattermost_listener.reconnect_websocket()

def test_reconnect_websocket_active():
    mock_ws = AsyncMock()
    mock_loop = MagicMock()
    mock_loop.is_running.return_value = True

    mattermost_listener.current_ws = mock_ws
    mattermost_listener.main_loop = mock_loop

    mattermost_listener.reconnect_websocket()
    mock_loop.call_soon_threadsafe.assert_called_once()
    
    mattermost_listener.current_ws = None
    mattermost_listener.main_loop = None

def test_mattermost_listener_flow():
    with patch("mattermost_listener.config", {"MATTERMOST_WS_URL": "wss://test.com", "MATTERMOST_TOKEN": "token123", "WS_RECONNECT_TIMEOUT": 1}), \
         patch("mattermost_listener.fetch_user_id", return_value="user_id_1"), \
         patch("mattermost_listener.websockets.connect") as mock_connect, \
         patch("asyncio.sleep", side_effect=AsyncMock(side_effect=lambda x: setattr(mattermost_listener, 'running', False))):
         
        mock_ws = AsyncMock()
        mock_ws.recv.return_value = json.dumps({
            "event": "posted",
            "data": json.dumps({
                "message": "Hello",
                "channel_display_name": "General",
                "sender_name": "Alice",
                "user_id": "user_2",
                "create_at": 1234567890
            })
        })
        mock_connect.return_value.__aenter__.return_value = mock_ws

        mattermost_listener.running = True
        mattermost_listener.service_active = True

        try:
            asyncio.run(asyncio.wait_for(mattermost_listener.mattermost_listener(), timeout=1.0))
        except asyncio.TimeoutError:
            pass
        finally:
            mattermost_listener.running = False