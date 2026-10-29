import json
from unittest.mock import patch, MagicMock

import version
from func.check_for_updates import check_for_updates

def test_version_string_exists():
    assert hasattr(version, "__version__")
    assert hasattr(version, "GITHUB_REPO")
    assert isinstance(version.__version__, str)
    assert isinstance(version.GITHUB_REPO, str)
    assert len(version.__version__) > 0
    assert len(version.GITHUB_REPO) > 0

@patch("urllib.request.urlopen")
def test_check_for_updates_available(mock_urlopen):

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "tag_name": "v99.9.9",
        "html_url": "https://github.com/Fabrizio04/MattermostTG/releases/tag/v99.9.9"
    }).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = mock_response

    has_update, latest_ver, url = check_for_updates()
    assert has_update is True
    assert latest_ver == "99.9.9"
    assert "github.com" in url


@patch("urllib.request.urlopen")
def test_check_for_updates_not_available(mock_urlopen):

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "tag_name": f"v{version.__version__}",
        "html_url": f"https://github.com/fabrizio04/MattermostTG/releases/tag/v{version.__version__}"
    }).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = mock_response

    has_update, latest_ver, url = check_for_updates()
    assert has_update is False
    assert latest_ver == version.__version__
    assert url

@patch("urllib.request.urlopen", side_effect=Exception("Network error"))
def test_check_for_updates_network_failure(mock_urlopen):

    has_update, latest_ver, url = check_for_updates()
    assert has_update is False
    assert latest_ver == version.__version__
    assert url == ""