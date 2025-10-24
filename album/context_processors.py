"""Context processors for making data available to all templates."""

from .models import SiteSettings


def site_settings(request):
    """Make site settings available to all templates."""
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
    return {
        'site_settings': settings
    }
