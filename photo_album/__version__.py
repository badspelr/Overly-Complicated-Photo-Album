"""
Django Photo Album Version Information

Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible new features
- PATCH: Backwards-compatible bug fixes
"""

__version__ = "1.3.0"
__version_info__ = (1, 3, 0)

# Release metadata
__author__ = "Daniel Nielsen"
__email__ = "your.email@example.com"  # Update with your email
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Daniel Nielsen"

# Application metadata
__title__ = "Django Photo Album"
__description__ = "AI-powered photo management system with semantic search"
__url__ = "https://github.com/badspelr/Overly-Complicated-Photo-Album"

# Release information
__release_date__ = "2025-10-24"
__status__ = "Production/Stable"

# Version history
VERSION_HISTORY = {
    "1.3.0": {
        "date": "2025-10-24",
        "name": "Public Release Ready",
        "highlights": [
            "Removed default admin account (security)",
            "Marked Auto Process on Upload as future feature",
            "Added comprehensive TODO roadmap (98 tasks)",
            "Created RELEASE_READY.md documentation",
            "Assessment grade: A- (89/100)",
            "Production-ready for public distribution"
        ]
    },
    "1.2.0": {
        "date": "2024-10-18",
        "name": "Feature Complete",
        "highlights": [
            "Comprehensive test suite (167 tests, 37% coverage)",
            "AI Settings admin interface",
            "Cookie consent system",
            "About and Contact pages",
            "Comprehensive user manual (991 lines)",
            "Registration control feature"
        ]
    },
    "1.1.0": {
        "date": "2024-09-15",
        "name": "AI Enhancement",
        "highlights": [
            "Automatic AI processing with Celery",
            "Scheduled batch processing",
            "Video metadata editing",
            "Album admin processing limits",
            "Performance optimizations"
        ]
    },
    "1.0.0": {
        "date": "2024-08-01",
        "name": "Initial Release",
        "highlights": [
            "Core photo/video management",
            "AI-powered search (CLIP, BLIP)",
            "REST API",
            "Docker deployment",
            "User authentication and permissions"
        ]
    }
}


def get_version():
    """Return the version string."""
    return __version__


def get_version_info():
    """Return the version tuple."""
    return __version_info__


def get_full_version():
    """Return the full version string with metadata."""
    return f"{__title__} v{__version__} ({__status__})"


def print_version_info():
    """Print detailed version information."""
    print(f"{__title__} v{__version__}")
    print(f"Release: {__release_date__}")
    print(f"Status: {__status__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print(f"URL: {__url__}")


if __name__ == "__main__":
    print_version_info()
