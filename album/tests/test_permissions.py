"""
Test cases for permissions.
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from .factories import UserFactory, AlbumFactory

@pytest.mark.django_db
class AlbumPermissionViewTest(TestCase):
    """Test cases for album view permissions."""

    def setUp(self):
        """Set up test data."""
        self.owner = UserFactory()
        self.viewer = UserFactory()
        self.unauthorized_user = UserFactory()
        
        self.private_album = AlbumFactory(owner=self.owner, is_public=False)
        self.private_album.viewers.add(self.viewer)
        
        self.public_album = AlbumFactory(owner=self.owner, is_public=True)

    def test_owner_can_access_private_album(self):
        """Test that the owner can access their own private album."""
        self.client.force_login(self.owner)
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.private_album.pk}))
        self.assertEqual(response.status_code, 200)

    def test_viewer_can_access_private_album(self):
        """Test that a designated viewer can access a private album."""
        self.client.force_login(self.viewer)
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.private_album.pk}))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_cannot_access_private_album(self):
        """Test that an unauthorized user is redirected from a private album."""
        self.client.force_login(self.unauthorized_user)
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.private_album.pk}))
        # Expecting a redirect to the dashboard or a 404, depending on implementation
        self.assertIn(response.status_code, [302, 404])

    def test_unauthenticated_user_cannot_access_private_album(self):
        """Test that an unauthenticated user receives a 404 for a private album."""
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.private_album.pk}))
        self.assertEqual(response.status_code, 404)

    def test_any_authenticated_user_can_access_public_album(self):
        """Test that any authenticated user can access a public album."""
        self.client.force_login(self.unauthorized_user)
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.public_album.pk}))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_can_access_public_album(self):
        """Test that an unauthenticated user can access a public album."""
        response = self.client.get(reverse('album:album_detail', kwargs={'pk': self.public_album.pk}))
        self.assertEqual(response.status_code, 200)

from .factories import PhotoFactory, CategoryFactory

@pytest.mark.django_db
class BulkEditAPITest(TestCase):
    """Test cases for the bulk edit API endpoint permissions."""

    def setUp(self):
        """Set up test data."""
        self.owner = UserFactory()
        self.unauthorized_user = UserFactory()
        
        self.album = AlbumFactory(owner=self.owner)
        self.photo1 = PhotoFactory(album=self.album)
        self.photo2 = PhotoFactory(album=self.album)
        
        self.category = CategoryFactory(created_by=self.owner)
        
        self.bulk_edit_url = reverse('api:bulk_edit')
        self.payload = {
            'action': 'update_category',
            'media_ids': [f'photo-{self.photo1.id}', f'photo-{self.photo2.id}'],
            'category_id': self.category.id
        }

    def test_unauthenticated_user_cannot_bulk_edit(self):
        """Test that an unauthenticated user gets a 403 from the bulk edit endpoint."""
        response = self.client.post(self.bulk_edit_url, self.payload, content_type='application/json')
        # Django REST Framework returns 403 for unauthenticated users on protected endpoints
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_cannot_bulk_edit(self):
        """Test that a user cannot bulk edit media in an album they do not own."""
        self.client.force_login(self.unauthorized_user)
        response = self.client.post(self.bulk_edit_url, self.payload, content_type='application/json')
        # The service layer should prevent the update and return a failure
        self.assertEqual(response.status_code, 200) # The view itself returns 200
        json_response = response.json()
        self.assertEqual(json_response['updated'], 0)
        self.assertGreater(json_response['failed'], 0)
        self.assertIn('No permission', json_response['errors'][0])

    def test_owner_can_bulk_edit(self):
        """Test that the album owner can successfully perform a bulk edit."""
        self.client.force_login(self.owner)
        response = self.client.post(self.bulk_edit_url, self.payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['updated'], 2)
        self.assertEqual(json_response['failed'], 0)

        # Verify the change in the database
        self.photo1.refresh_from_db()
        self.photo2.refresh_from_db()
        self.assertEqual(self.photo1.category, self.category)
        self.assertEqual(self.photo2.category, self.category)
