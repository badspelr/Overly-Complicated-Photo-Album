"""
Django Photo Album - AI-powered photo management system
"""

# Import version information
from .__version__ import (
    __version__,
    __version_info__,
    __title__,
    __author__,
    __license__,
    get_version,
    get_full_version,
)

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = (
    'celery_app',
    '__version__',
    '__version_info__',
    '__title__',
    '__author__',
    '__license__',
    'get_version',
    'get_full_version',
)
