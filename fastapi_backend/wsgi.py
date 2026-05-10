"""
WSGI config for FastAPI backend.

FastAPI is an ASGI framework, but this wrapper allows it to run on WSGI servers.
For most deployments, use the ASGI server directly (see asgi.py).

Example:
    # For ASGI (recommended)
    uvicorn asgi:app --reload
    
    # For WSGI (legacy servers)
    gunicorn wsgi:application
    
Note: Install asgiref for WSGI support:
    pip install asgiref
"""

from asgiref.wsgi import WsgiToAsgi
from main import app

# Wrap the ASGI app to work with WSGI servers
application = WsgiToAsgi(app)

__all__ = ["application", "app"]
