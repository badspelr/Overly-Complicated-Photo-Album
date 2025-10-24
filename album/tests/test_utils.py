"""
Test cases for utilities and mixins.
"""
import pytest
from django.test import TestCase
from unittest.mock import MagicMock
from django.views.generic import ListView
from ..models import Album, Photo, Category
from ..views.base_views import check_object_permission, get_delete_context, AlbumListPermissionMixin, CategoryPermissionMixin
from .factories import UserFactory, AlbumFactory, PhotoFactory, CategoryFactory


@pytest.mark.django_db
class UtilityFunctionTest(TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.superuser = UserFactory(is_superuser=True)
        self.album = AlbumFactory(owner=self.user)
        self.photo = PhotoFactory(album=self.album)
        self.category = CategoryFactory(created_by=self.user)
    
    def test_check_object_permission_superuser(self):
        """Test permission check for superuser."""
        # Superuser should have access to everything
        self.assertTrue(check_object_permission(self.superuser, self.album, 'album'))
        self.assertTrue(check_object_permission(self.superuser, self.photo, 'photo'))
        self.assertTrue(check_object_permission(self.superuser, self.category, 'category'))
    
    def test_check_object_permission_album_owner(self):
        """Test permission check for album owner."""
        # Owner should have access to their own objects
        self.assertTrue(check_object_permission(self.user, self.album, 'album'))
        self.assertTrue(check_object_permission(self.user, self.photo, 'photo'))
        self.assertTrue(check_object_permission(self.user, self.category, 'category'))
        
        # Other user should not have access
        self.assertFalse(check_object_permission(self.other_user, self.album, 'album'))
        self.assertFalse(check_object_permission(self.other_user, self.photo, 'photo'))
        self.assertFalse(check_object_permission(self.other_user, self.category, 'category'))
    
    def test_check_object_permission_photo_video(self):
        """Test permission check for photos and videos."""
        # Photo/video permission is based on album ownership
        self.assertTrue(check_object_permission(self.user, self.photo, 'photo'))
        self.assertFalse(check_object_permission(self.other_user, self.photo, 'photo'))
        
        # Test photo without album
        photo_no_album = PhotoFactory(album=None)
        self.assertFalse(check_object_permission(self.user, photo_no_album, 'photo'))
    
    def test_get_delete_context(self):
        """Test delete context generation."""
        # Test with album
        context = get_delete_context(self.album, 'Album', 'Test warning')
        self.assertEqual(context['object_type'], 'Album')
        self.assertEqual(context['object_name'], self.album.title)
        self.assertEqual(context['warning_message'], 'Test warning')
        
        # Test with category
        context = get_delete_context(self.category, 'Category', 'Test warning')
        self.assertEqual(context['object_type'], 'Category')
        self.assertEqual(context['object_name'], self.category.name)
        
        # Test with photo
        context = get_delete_context(self.photo, 'Photo', 'Test warning')
        self.assertEqual(context['object_type'], 'Photo')
        self.assertEqual(context['object_name'], self.photo.title)


@pytest.mark.django_db
class AlbumListPermissionMixinTest(TestCase):
    """Test cases for AlbumListPermissionMixin."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.superuser = UserFactory(is_superuser=True)
        self.album = AlbumFactory(owner=self.user)
        self.public_album = AlbumFactory(owner=self.other_user, is_public=True)
        self.private_album = AlbumFactory(owner=self.other_user, is_public=False)
        
        # Add user as viewer to private album
        self.private_album.viewers.add(self.user)
        
        self.photo = PhotoFactory(album=self.album)
        self.public_photo = PhotoFactory(album=self.public_album)
        self.private_photo = PhotoFactory(album=self.private_album)
    
    def test_album_permission_mixin_superuser(self):
        """Test mixin for superuser."""
        class TestAlbumListView(AlbumListPermissionMixin, ListView):
            model = Album
        
        view = TestAlbumListView()
        view.request = MagicMock()
        view.request.user = self.superuser
        
        # Superuser should see all albums
        queryset = view.get_queryset()
        self.assertIn(self.album, queryset)
        self.assertIn(self.public_album, queryset)
        self.assertIn(self.private_album, queryset)
    
    def test_album_permission_mixin_regular_user(self):
        """Test mixin for regular user."""
        class TestAlbumListView(AlbumListPermissionMixin, ListView):
            model = Album

        view = TestAlbumListView()
        view.request = MagicMock()
        view.request.user = self.user
        
        # Regular user should see owned, public, and viewable albums
        queryset = view.get_queryset()
        self.assertIn(self.album, queryset)  # Owned
        self.assertIn(self.public_album, queryset)  # Public
        self.assertIn(self.private_album, queryset)  # Viewable
    
    def test_photo_permission_mixin(self):
        """Test mixin for photos."""
        class TestPhotoListView(AlbumListPermissionMixin, ListView):
            model = Photo

        view = TestPhotoListView()
        view.request = MagicMock()
        view.request.user = self.user
        
        # User should see photos from owned, public, and viewable albums
        queryset = view.get_queryset()
        self.assertIn(self.photo, queryset)  # From owned album
        self.assertIn(self.public_photo, queryset)  # From public album
        self.assertIn(self.private_photo, queryset)  # From viewable album


@pytest.mark.django_db
class CategoryPermissionMixinTest(TestCase):
    """Test cases for CategoryPermissionMixin."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.superuser = UserFactory(is_superuser=True)
        self.category = CategoryFactory(created_by=self.user)
    
    def test_category_permission_mixin_superuser(self):
        """Test mixin for superuser."""
        class TestCategoryListView(CategoryPermissionMixin, ListView):
            model = Category

        view = TestCategoryListView()
        view.request = MagicMock()
        view.request.user = self.superuser
        
        # Superuser should have access to all categories
        queryset = view.get_queryset()
        self.assertIn(self.category, queryset)
    
    def test_category_permission_mixin_regular_user(self):
        """Test mixin for regular user."""
        class TestCategoryListView(CategoryPermissionMixin, ListView):
            model = Category

        view = TestCategoryListView()
        view.request = MagicMock()
        view.request.user = self.user
        
        # Regular user should only see their own categories
        queryset = view.get_queryset()
        self.assertIn(self.category, queryset)
        
        # Other user should not see this category
        other_category = CategoryFactory(created_by=self.other_user)
        view.request.user = self.other_user
        queryset = view.get_queryset()
        self.assertNotIn(self.category, queryset)
        self.assertIn(other_category, queryset)