from func.openapi import get_openapi_spec

def test_get_openapi_spec_structure_and_values(monkeypatch):
    monkeypatch.setattr("func.openapi.get", lambda key_path, default=None: f"val_{key_path}")
    
    spec = get_openapi_spec()
    
    assert isinstance(spec, dict)
    assert spec["openapi"] == "3.0.0"
    assert spec["info"]["title"] == "Mattermost Notifier API"
    assert spec["info"]["version"] == "1.0.0"
    assert spec["info"]["description"] == "val_openapi.description"
    
    paths = spec["paths"]
    assert "/status" in paths
    assert "/config" in paths
    assert "/notify_service" in paths
    assert "/decrypter" in paths
    
    assert paths["/status"]["get"]["summary"] == "val_openapi.status.summary"
    assert paths["/status"]["get"]["responses"]["200"]["description"] == "val_openapi.status.responses"
    
    assert paths["/config"]["put"]["requestBody"]["required"] is True
    assert paths["/config"]["put"]["responses"]["200"]["description"] == "val_openapi.config.put.responses"
    
    assert paths["/notify_service"]["put"]["summary"] == "val_openapi.notify_service.summary"
    assert paths["/decrypter"]["get"]["parameters"][0]["name"] == "includeKey"
    assert paths["/decrypter"]["get"]["parameters"][0]["in"] == "query"