from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from middleware.trace_middleware import SecurityShieldMiddleware

BRANDED_CSS = """
.swagger-ui {
    background-color: #1a1a1a !important;
    color: #00ffff !important;
    font-family: monospace !important;
}
.swagger-ui .topbar { display: none !important; }
.swagger-ui .info .title { color: #00ffff !important; }
.swagger-ui .opblock { border: 1px solid #00ffff !important; background: rgba(0, 255, 255, 0.05) !important; }
.swagger-ui .opblock .opblock-summary-method { background: #00ffff !important; color: #1a1a1a !important; }
.swagger-ui .errors-wrapper { background: #ff0033 !important; color: white !important; }
body { background-color: #1a1a1a !important; margin: 0; padding: 0; }
"""

def create_app() -> FastAPI:
    description = """
    ## Engine Operational Manual
    CoreGraph is a planetary-scale topological OSINT instrument. 
    It leverages 3.81M simulated nodes wrapped in a high-velocity asynchronous framework.

    ## Cybersecurity Disclaimer
    This API provides extremely powerful network isolation and vulnerability tracking. 
    Unauthorized use, exfiltration, and non-compliant operations will be logged and audited.
    """

    app = FastAPI(
        title="CoreGraph Sovereign Titan",
        description=description,
        version="1.0.0",
        contact={
            "name": "CoreGraph OSINT Architect",
            "url": "https://coregraph.internal",
        },
        docs_url=None, 
        redoc_url=None  
    )

    app.add_middleware(SecurityShieldMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Restricted to specific gateway in prod
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization"],
    )

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - OSINT Documentation",
            swagger_css_url=None, # Disable default
        )
    
    # We will patch the CSS returned by swagger_ui by injecting our own tag if needed.
    # Actually, get_swagger_ui_html allows providing a custom CSS URL or just returning a modified HTML.
    # Let's build the swagger page manually to inject the <style> block directly for a zero-dependency local experience.

    @app.get("/v1/swagger", include_in_schema=False)
    async def branded_swagger_ui():
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>CoreGraph Sovereign Documentation</title>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <style>
        {BRANDED_CSS}
        </style>
        </head>
        <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
        window.onload = function() {{
            window.ui = SwaggerUIBundle({{
                url: "/openapi.json",
                dom_id: "#swagger-ui",
                deepLinking: true,
                presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
                layout: "BaseLayout",
            }});
        }};
        </script>
        </body>
        </html>
        """
        from fastapi.responses import HTMLResponse
        return HTMLResponse(html)

    # Re-route standard /docs to our branded swagger
    @app.get("/docs", include_in_schema=False)
    async def redirect_swagger():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/v1/swagger")

    return app

