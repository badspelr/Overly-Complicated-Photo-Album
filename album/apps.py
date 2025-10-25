from django.apps import AppConfig


class AlbumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'album'

    def ready(self):
        """Import signals and initialize Sentry when the app is ready."""
        import album.signals  # noqa
        
        # Initialize Sentry based on database settings
        self._initialize_sentry()
    
    def _initialize_sentry(self):
        """Initialize Sentry if enabled in site settings."""
        try:
            from django.conf import settings
            from django.db import connection
            
            # Check if database tables exist
            if not self._database_ready():
                return
            
            # Import here to avoid circular imports
            from album.models import SiteSettings
            
            # Get site settings
            try:
                site_settings = SiteSettings.get_settings()
                
                # Only initialize if enabled in admin and DSN is configured
                if site_settings.sentry_enabled and settings.SENTRY_DSN and not settings.DEBUG:
                    import sentry_sdk
                    from sentry_sdk.integrations.django import DjangoIntegration
                    from sentry_sdk.integrations.celery import CeleryIntegration
                    from sentry_sdk.integrations.redis import RedisIntegration
                    
                    sentry_sdk.init(
                        dsn=settings.SENTRY_DSN,
                        environment=settings.SENTRY_ENVIRONMENT,
                        integrations=[
                            DjangoIntegration(),
                            CeleryIntegration(),
                            RedisIntegration(),
                        ],
                        traces_sample_rate=float(site_settings.sentry_traces_sample_rate),
                        profiles_sample_rate=float(site_settings.sentry_profiles_sample_rate),
                        send_default_pii=False,
                        before_send=self._scrub_sensitive_data,
                    )
            except Exception:
                # Settings don't exist yet (e.g., during migrations)
                pass
                
        except Exception:
            # Fail silently if Sentry can't be initialized
            pass
    
    def _database_ready(self):
        """Check if database tables are ready."""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM album_sitesettings LIMIT 1")
            return True
        except Exception:
            return False
    
    @staticmethod
    def _scrub_sensitive_data(event, hint):
        """Remove sensitive data from Sentry events."""
        if 'request' in event:
            if 'data' in event['request']:
                data = event['request']['data']
                if isinstance(data, dict):
                    for key in ['password', 'token', 'secret', 'api_key', 'csrf_token']:
                        if key in data:
                            data[key] = '[REDACTED]'
        return event
