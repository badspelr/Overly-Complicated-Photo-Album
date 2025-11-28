"""
API URLs for the album app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    AlbumViewSet, CategoryViewSet, UserViewSet, SiteSettingsViewSet,
    MediaUploadView, CurrentUserView, LoginView, RegistrationView, BulkEditView,
    CreatePhotoShareLinkView, SharedPhotoView
)

app_name = 'album'

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet)
router.register(r'settings', SiteSettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', MediaUploadView.as_view(), name='media_upload'),
    path('bulk-edit/', BulkEditView.as_view(), name='bulk_edit'),
    path('user/me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/register/', RegistrationView.as_view(), name='api_register'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('photos/<int:photo_id>/share/', CreatePhotoShareLinkView.as_view(), name='create_photo_share'),
    path('share/photo/<str:token>/', SharedPhotoView.as_view(), name='shared_photo'),
]