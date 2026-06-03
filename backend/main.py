"""
Compatibility entrypoint for platforms that default to `main:app`.
Internally we keep the real app in `app.main`.
"""

from app.main import app

