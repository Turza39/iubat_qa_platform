"""
ASGI config for FastAPI backend.

Exposes the ASGI callable as a module-level variable named ``app``.

This allows the application to be run with any ASGI server such as:
- uvicorn (recommended for development)
- gunicorn with uvicorn workers (production)
- daphne
- hypercorn

Example:
    uvicorn asgi:app --reload
    gunicorn asgi:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
"""

from main import app

# The ASGI callable
application = app

__all__ = ["application", "app"]
