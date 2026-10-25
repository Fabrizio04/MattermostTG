from func.i18n import get

def get_openapi_spec():
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Mattermost Notifier API",
            "version": "1.0.0",
            "description": get("openapi.description")
        },
        "paths": {
            "/status": {
                "get": {
                    "summary": get("openapi.status.summary"),
                    "responses": {"200": {"description": get("openapi.status.responses")}}
                }
            },
            "/config": {
                "get": {
                    "summary": get("openapi.config.get.summary"),
                    "responses": {"200": {"description": get("openapi.config.get.responses")}}
                },
                "put": {
                    "summary": get("openapi.config.put.summary"),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": get("openapi.config.put.responses")}}
                }
            },
            "/notify_service": {
                "put": {
                    "summary": get("openapi.notify_service.summary"),
                    "responses": {
                        "200": {
                            "description": get("openapi.notify_service.responses"),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "service_active": {"type": "boolean"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/decrypter": {
                "get": {
                    "summary": get("openapi.decrypter.summary"),
                    "parameters": [
                        {
                            "name": "includeKey",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": get("openapi.decrypter.includeKey")
                        }
                    ],
                    "responses": {"200": {"description": get("openapi.decrypter.responses")}}
                }
            }
        }
    }