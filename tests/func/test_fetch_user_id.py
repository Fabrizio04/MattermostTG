from unittest.mock import patch, MagicMock
from func.fetch_user_id import fetch_user_id

@patch("func.fetch_user_id.requests.get")
def test_fetch_user_id_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "user_12345_abc"}
    mock_get.return_value = mock_response

    ws_url = "wss://chat.dominio.it/api/v4/websocket"
    token = "mio_token_segreto"

    result = fetch_user_id(ws_url, token)

    assert result == "user_12345_abc"
    
    mock_get.assert_called_once_with(
        "https://chat.dominio.it/api/v4/users/me",
        headers={"Authorization": "Bearer mio_token_segreto"},
        timeout=5
    )

@patch("func.fetch_user_id.requests.get")
def test_fetch_user_id_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    ws_url = "ws://chat.dominio.it/api/v4"
    token = "token_errato"

    result = fetch_user_id(ws_url, token)
    assert result is None

@patch("func.fetch_user_id.requests.get")
def test_fetch_user_id_exception(mock_get):
    mock_get.side_effect = Exception("Connection timeout")

    ws_url = "wss://chat.dominio.it/api/v4/websocket"
    token = "un_token"

    result = fetch_user_id(ws_url, token)
    assert result is None