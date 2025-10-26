from django.urls import path
from .views import album_views
from .views.user_views import homepage, dashboard, UserUpdateView, invite_user, ManageUsersView, UserEditView, UserDeleteView, register, user_manual, AccountDeleteView, AppPasswordChangeView, AppPasswordChangeDoneView, terms_of_conduct, csam_policy
from .views.album_views import AlbumListView, AlbumDetailView, create_album, delete_album, album_viewers, remove_viewer, create_share_link, shared_album, manage_share_links, delete_share_link
from .views.media_views import PhotoListView, PhotoDetailView, VideoListView, VideoDetailView, delete_media, bulk_delete, bulk_download, search_media, photo_edit, minimal_upload, toggle_favorite, favorites_list, mobile_download_page, download_single_item, process_videos_ai, process_photos_ai
from .views.category_views import CategoryCreateView, CategoryUpdateView, CategoryDeleteView, CategoryListView
from .views.base_views import about_view, contact_view, ai_settings_view, cookie_policy_view
from .models import Photo, Video

app_name = 'album'

urlpatterns = [
    path('user-manual/', user_manual, name='user_manual'),
    path('', homepage, name='homepage'),
    path('dashboard/', dashboard, name='dashboard'),
    path('accounts/register/', register, name='register'),
    path('terms/', terms_of_conduct, name='terms'),
    path('csam-policy/', csam_policy, name='csam_policy'),
    path('albums/', AlbumListView.as_view(), name='album_list'),
    path('albums/create/', create_album, name='create_album'),
    path('albums/<int:pk>/edit/', create_album, name='edit_album'),
    path('albums/<int:pk>/delete/', delete_album, name='delete_album'),
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album_detail'),
    path('albums/<int:pk>/viewers/', album_viewers, name='album_viewers'),
    path('albums/<int:pk>/viewers/<int:user_id>/remove/', remove_viewer, name='remove_viewer'),
    path('albums/<int:pk>/share/', create_share_link, name='create_share_link'),
    path('albums/<int:pk>/share/manage/', manage_share_links, name='manage_share_links'),
    path('share/<str:token>/', shared_album, name='shared_album'),
    path('share/link/<int:link_id>/delete/', delete_share_link, name='delete_share_link'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='create_category'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='edit_category'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='delete_category'),
    path('photos/', PhotoListView.as_view(), name='photo_list'),
    path('photos/<int:pk>/', PhotoDetailView.as_view(), name='photo_detail'),
    path('photos/<int:pk>/edit/', photo_edit, name='photo_edit'),
    path('photos/<int:pk>/delete/', delete_media, {'model': Photo}, name='delete_photo'),
    path('videos/<int:pk>/delete/', delete_media, {'model': Video}, name='delete_video'),
    path('videos/', VideoListView.as_view(), name='video_list'),
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
    path('profile/', UserUpdateView.as_view(), name='profile_edit'),
    path('profile/delete/', AccountDeleteView.as_view(), name='delete_account'),
    path('users/invite/', invite_user, name='invite_user'),
    path('users/manage/', ManageUsersView.as_view(), name='manage_users'),
    # REMOVED: Album admin users view - no longer needed with per-album ownership model
    # path('users/my-users/', AlbumAdminUsersView.as_view(), name='album_admin_users'),
    path('users/<int:user_id>/edit/', UserEditView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='delete_user'),
    path('bulk_delete/', bulk_delete, name='bulk_delete'),
    path('bulk_download/', bulk_download, name='bulk_download'),
    path('mobile_download/', mobile_download_page, name='mobile_download_page'),
    path('download/<str:item_type>/<int:item_id>/', download_single_item, name='download_single_item'),
    path('search/', search_media, name='search_media'),
    path('favorites/', favorites_list, name='favorites'),
    path('photos/<int:photo_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('offline/', album_views.offline_view, name='offline'),
    path('minimal-upload/', minimal_upload, name='minimal_upload'),
    path('process-videos-ai/', process_videos_ai, name='process_videos_ai'),
    path('process-photos-ai/', process_photos_ai, name='process_photos_ai'),
    path('ai-settings/', ai_settings_view, name='ai_settings'),
    path('account/password/change/', AppPasswordChangeView.as_view(), name='password_change_app'),
    path('account/password/change/done/', AppPasswordChangeDoneView.as_view(), name='password_change_done_app'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('cookie-policy/', cookie_policy_view, name='cookie_policy'),
]
