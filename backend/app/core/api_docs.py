"""
OpenAPI documentation enhancement functionality.
"""
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
import json
from pathlib import Path

from app.core.config import settings

def custom_openapi(app: FastAPI) -> dict:
    """
    Generate a custom OpenAPI schema for the API documentation.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        OpenAPI schema as a dictionary
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
    )
    
    # Add additional documentation information
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "support@example.com",
        "url": "https://example.com/support",
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key authentication"
        }
    }
    
    # Enhance tag descriptions
    openapi_schema["tags"] = [
        {
            "name": "Characters",
            "description": "Operations related to character management.",
            "externalDocs": {
                "description": "Character documentation",
                "url": "/docs#tag/Characters"
            }
        },
        {
            "name": "Chat",
            "description": "Operations related to chatting with characters.",
            "externalDocs": {
                "description": "Chat documentation",
                "url": "/docs#tag/Chat"
            }
        },
        {
            "name": "Tools",
            "description": "Operations related to tool management.",
            "externalDocs": {
                "description": "Tools documentation",
                "url": "/docs#tag/Tools"
            }
        }
    ]
    
    # Add global response schemas
    openapi_schema["components"]["responses"] = {
        "NotFound": {
            "description": "The specified resource was not found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/NotFoundErrorResponse"
                    }
                }
            }
        },
        "ValidationError": {
            "description": "Validation error in request data",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ValidationErrorResponse"
                    }
                }
            }
        },
        "InternalError": {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
                }
            }
        }
    }
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    
    # Optionally save the schema to a file
    if settings.DEBUG_MODE:
        schema_path = Path(settings.BASE_DIR) / "openapi.json"
        with open(schema_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)
    
    return app.openapi_schema

def setup_api_docs(app: FastAPI) -> None:
    """
    Set up custom API documentation for a FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Set custom OpenAPI schema generator
    app.openapi = lambda: custom_openapi(app)
