"""
URL configuration for photo_album project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from album.views.user_views import AppPasswordChangeView, AppPasswordChangeDoneView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # OpenAPI Schema & Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('admin/', admin.site.urls),
    # Custom auth URLs with our templates
    path('accounts/password_change/', AppPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', AppPasswordChangeDoneView.as_view(), name='password_change_done'),
    # Other auth URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(email_template_name='emails/password_reset.txt'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('api/', include('album.api.urls', namespace='api')),
    path('', include('album.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all pattern temporarily disabled - causing issues with static file serving
# urlpatterns += [
#     # Catch-all for React Router to serve the React app
#     re_path(r'^(?!api/|admin/|accounts/|albums/|favorites/|photos/|videos/|search/|minimal-upload/|dashboard/|profile/|users/|categories/|bulk_delete/|bulk_download/|offline/|share/|static/|media/).*$', dashboard, name='react_app'),
# ]
