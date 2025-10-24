"""
Test cases for views.
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Album, Photo, Category
from .factories import UserFactory, AlbumFactory, PhotoFactory, VideoFactory, CategoryFactory


@pytest.mark.django_db
class ViewTestCase(TestCase):
    """Base test case for view tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.category = CategoryFactory(created_by=self.user)
        self.album = AlbumFactory(owner=self.user, category=self.category)
        self.public_album = AlbumFactory(owner=self.user, is_public=True)


@pytest.mark.django_db
class AlbumViewTest(ViewTestCase):
    """Test cases for album views."""
    
    def test_album_list_view_requires_login(self):
        """Test that album list view requires login."""
        response = self.client.get(reverse('album:album_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_album_list_view_authenticated(self):
        """Test album list view for authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('album:album_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.album.title)
    
    def test_album_detail_view_permissions(self):
        """Test album detail view permissions."""
        # Test unauthorized access
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.album.pk}))
        self.assertEqual(response.status_code, 404)
        
        # Test authorized access
        self.client.force_login(self.user)
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.album.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.album.title)
    
    def test_create_album_view(self):
        """Test album creation view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('album:create_album'))
        self.assertEqual(response.status_code, 200)
        
        # Test album creation
        data = {
            'title': 'New Album',
            'description': 'Test description',
            'category': self.category.pk,
            'is_public': False
        }
        response = self.client.post(reverse('album:create_album'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verify album was created
        album = Album.objects.get(title='New Album')
        self.assertEqual(album.owner, self.user)
    
    def test_edit_album_view_permissions(self):
        """Test album edit view permissions."""
        self.client.force_login(self.user)
        
        # Test editing own album
        response = self.client.get(reverse('album:edit_album', kwargs={'pk': self.album.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test editing other user's album
        other_album = AlbumFactory(owner=self.other_user)
        response = self.client.get(reverse('album:edit_album', kwargs={'pk': other_album.pk}))
        self.assertEqual(response.status_code, 302)  # Forbidden
    
    def test_delete_album_view(self):
        """Test album deletion."""
        self.client.force_login(self.user)
        
        # Test delete confirmation page
        response = self.client.get(reverse('album:delete_album', kwargs={'pk': self.album.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test actual deletion
        response = self.client.post(reverse('album:delete_album', kwargs={'pk': self.album.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verify album was deleted
        with self.assertRaises(Album.DoesNotExist):
            Album.objects.get(pk=self.album.pk)


@pytest.mark.django_db
class MediaViewTest(ViewTestCase):
    """Test cases for media views."""
    
    def test_photo_list_view(self):
        """Test photo list view."""
        photo = PhotoFactory(album=self.album)
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('album:photo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, photo.title)
    
    def test_video_list_view(self):
        """Test video list view."""
        video = VideoFactory(album=self.album)
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('album:video_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, video.title)
    
    def test_upload_media_view_permissions(self):
        """Test upload media view permissions."""
        self.client.force_login(self.user)
        
        # Test GET request
        response = self.client.get(reverse('api:media_upload'))
        self.assertEqual(response.status_code, 405) # Method Not Allowed
        
        # Test POST with no files
        response = self.client.post(reverse('api:media_upload'), {})
        self.assertEqual(response.status_code, 400)  # Bad Request
    
    def test_delete_media_view(self):
        """Test media deletion."""
        photo = PhotoFactory(album=self.album)
        
        self.client.force_login(self.user)
        
        # Test delete confirmation page
        response = self.client.get(reverse('album:delete_photo', kwargs={'pk': photo.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test actual deletion
        response = self.client.post(reverse('album:delete_photo', kwargs={'pk': photo.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verify photo was deleted
        with self.assertRaises(Photo.DoesNotExist):
            Photo.objects.get(pk=photo.pk)


@pytest.mark.django_db
class CategoryViewTest(ViewTestCase):
    """Test cases for category views."""
    
    def test_create_category_view(self):
        """Test category creation view."""
        self.client.force_login(self.user)
        
        # Test GET request
        response = self.client.get(reverse('album:create_category'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'name': 'New Category',
            'description': 'Test category description'
        }
        response = self.client.post(reverse('album:create_category'), data)
        self.assertEqual(response.status_code, 302)
        
        # Verify category was created
        category = Category.objects.get(name='New Category')
        self.assertEqual(category.created_by, self.user)
    
    def test_edit_category_view_permissions(self):
        """Test category edit view permissions."""
        self.client.force_login(self.user)
        
        # Test editing own category
        response = self.client.get(reverse('album:edit_category', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test editing other user's category
        other_category = CategoryFactory(created_by=self.other_user)
        response = self.client.get(reverse('album:edit_category', kwargs={'pk': other_category.pk}))
        self.assertEqual(response.status_code, 404)  # Not Found


@pytest.mark.django_db
class UserViewTest(ViewTestCase):
    """Test cases for user views."""
    
    def test_dashboard_view_requires_login(self):
        """Test that dashboard view requires login."""
        response = self.client.get(reverse('album:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('album:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
    
    def test_homepage_view(self):
        """Test homepage view."""
        response = self.client.get(reverse('album:homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Photo Album')
    
    def test_profile_edit_view(self):
        """Test profile edit view."""
        self.client.force_login(self.user)
        
        # Test GET request
        response = self.client.get(reverse('album:profile_edit'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'username': self.user.username,
            'email': 'newemail@example.com',
            'first_name': 'New First Name',
            'last_name': 'New Last Name'
        }
        response = self.client.post(reverse('album:profile_edit'), data)
        self.assertEqual(response.status_code, 302)
        
        # Verify profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
