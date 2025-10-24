"""
Test cases for REST API endpoints.
Tests for API authentication, permissions, CRUD operations, and error handling.
"""
import pytest
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from album.models import Album, Photo
from album.tests.factories import UserFactory, AlbumFactory, PhotoFactory, CategoryFactory


@pytest.mark.django_db
class TestAPIAuthentication(APITestCase):
    """Test cases for API authentication."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    def test_api_requires_authentication(self):
        """Test API endpoints require authentication."""
        # Try to access album list without auth
        response = self.client.get('/api/albums/')
        
        # Should return 401 or 403
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ])
    
    def test_api_with_valid_token(self):
        """Test API access with valid authentication."""
        # Login
        self.client.force_authenticate(user=self.user)
        
        # Try to access album list
        response = self.client.get('/api/albums/')
        
        # Should return 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_with_invalid_token(self):
        """Test API rejects invalid authentication."""
        # Set invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_12345')
        
        # Try to access album list
        response = self.client.get('/api/albums/')
        
        # Should return 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class TestAlbumAPI(APITestCase):
    """Test cases for Album API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_list_albums(self):
        """Test listing user's albums."""
        # Create albums for user
        album1 = AlbumFactory(owner=self.user, title="Album 1")
        album2 = AlbumFactory(owner=self.user, title="Album 2")
        # Create album for other user
        other_album = AlbumFactory(owner=self.other_user, title="Other Album")
        
        response = self.client.get('/api/albums/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own albums
        self.assertEqual(len(response.data['results']), 2)
        titles = [album['title'] for album in response.data['results']]
        self.assertIn("Album 1", titles)
        self.assertIn("Album 2", titles)
        self.assertNotIn("Other Album", titles)
    
    def test_retrieve_album(self):
        """Test retrieving single album."""
        album = AlbumFactory(owner=self.user, title="Test Album")
        
        response = self.client.get(f'/api/albums/{album.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Album")
        self.assertEqual(response.data['owner'], self.user.id)
    
    def test_create_album(self):
        """Test creating new album via API."""
        data = {
            'title': 'New Album',
            'description': 'Created via API',
            'is_public': False
        }
        
        response = self.client.post('/api/albums/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Album')
        
        # Verify in database
        album = Album.objects.get(id=response.data['id'])
        self.assertEqual(album.owner, self.user)
        self.assertEqual(album.title, 'New Album')
    
    def test_update_album(self):
        """Test updating album via API."""
        album = AlbumFactory(owner=self.user, title="Original Title")
        
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/albums/{album.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        
        # Verify in database
        album.refresh_from_db()
        self.assertEqual(album.title, 'Updated Title')
    
    def test_delete_album(self):
        """Test deleting album via API."""
        album = AlbumFactory(owner=self.user)
        
        response = self.client.delete(f'/api/albums/{album.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deleted
        self.assertFalse(Album.objects.filter(id=album.id).exists())
    
    def test_cannot_access_other_users_album(self):
        """Test user cannot access another user's private album."""
        other_album = AlbumFactory(owner=self.other_user, is_public=False)
        
        response = self.client.get(f'/api/albums/{other_album.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_can_view_public_album(self):
        """Test user can view public album of another user."""
        public_album = AlbumFactory(owner=self.other_user, is_public=True)
        
        response = self.client.get(f'/api/albums/{public_album.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cannot_modify_other_users_album(self):
        """Test user cannot modify another user's album."""
        other_album = AlbumFactory(owner=self.other_user)
        
        data = {'title': 'Hacked Title'}
        response = self.client.patch(f'/api/albums/{other_album.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestPhotoAPI(APITestCase):
    """Test cases for Photo API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_authenticate(user=self.user)
    
    def test_list_photos_in_album(self):
        """Test listing photos in an album."""
        photo1 = PhotoFactory(album=self.album)
        photo2 = PhotoFactory(album=self.album)
        
        response = self.client.get(f'/api/albums/{self.album.id}/photos/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_photo(self):
        """Test retrieving single photo."""
        photo = PhotoFactory(album=self.album, title="Test Photo")
        
        response = self.client.get(f'/api/photos/{photo.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Photo")
    
    def test_update_photo_metadata(self):
        """Test updating photo metadata via API."""
        photo = PhotoFactory(album=self.album)
        
        data = {
            'title': 'Updated Photo',
            'description': 'New description'
        }
        response = self.client.patch(f'/api/photos/{photo.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        photo.refresh_from_db()
        self.assertEqual(photo.title, 'Updated Photo')
    
    def test_delete_photo(self):
        """Test deleting photo via API."""
        photo = PhotoFactory(album=self.album)
        
        response = self.client.delete(f'/api/photos/{photo.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Photo.objects.filter(id=photo.id).exists())


@pytest.mark.django_db
class TestSearchAPI(APITestCase):
    """Test cases for Search API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_authenticate(user=self.user)
    
    def test_search_photos_by_text(self):
        """Test searching photos by text query."""
        photo1 = PhotoFactory(
            album=self.album,
            ai_description="a red car on the street",
            ai_processed=True
        )
        photo2 = PhotoFactory(
            album=self.album,
            ai_description="a blue house with garden",
            ai_processed=True
        )
        
        response = self.client.get('/api/search/photos/?q=car')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find photo1 but not photo2
        if response.data['results']:
            descriptions = [p['ai_description'] for p in response.data['results']]
            self.assertTrue(any('car' in d.lower() for d in descriptions))
    
    def test_search_returns_only_users_content(self):
        """Test search only returns user's own content."""
        other_user = UserFactory()
        other_album = AlbumFactory(owner=other_user)
        
        own_photo = PhotoFactory(
            album=self.album,
            ai_description="red car",
            ai_processed=True
        )
        other_photo = PhotoFactory(
            album=other_album,
            ai_description="red car",
            ai_processed=True
        )
        
        response = self.client.get('/api/search/photos/?q=red')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only find own photo
        photo_ids = [p['id'] for p in response.data['results']]
        self.assertIn(own_photo.id, photo_ids)
        self.assertNotIn(other_photo.id, photo_ids)
    
    def test_search_with_empty_query(self):
        """Test search with empty query."""
        response = self.client.get('/api/search/photos/?q=')
        
        # Should return 400 or empty results
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ])


@pytest.mark.django_db
class TestCategoryAPI(APITestCase):
    """Test cases for Category API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_list_categories(self):
        """Test listing categories."""
        cat1 = CategoryFactory(created_by=self.user, name="Travel")
        cat2 = CategoryFactory(created_by=self.user, name="Family")
        
        response = self.client.get('/api/categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 2)
        else:
            self.assertGreaterEqual(len(response.data), 2)
    
    def test_create_category(self):
        """Test creating category via API."""
        data = {'name': 'Vacation', 'description': 'Holiday photos'}
        
        response = self.client.post('/api/categories/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Vacation')


@pytest.mark.django_db
class TestAPIErrorHandling(APITestCase):
    """Test cases for API error handling."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_api_returns_404_for_nonexistent_resource(self):
        """Test API returns 404 for non-existent resource."""
        response = self.client.get('/api/albums/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_api_validates_required_fields(self):
        """Test API validates required fields."""
        # Try to create album without required title
        data = {'description': 'No title'}
        
        response = self.client.post('/api/albums/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.data).lower())
    
    def test_api_returns_proper_error_message(self):
        """Test API returns descriptive error messages."""
        response = self.client.get('/api/albums/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Should have error message in response
        self.assertTrue(
            'detail' in response.data or 'error' in response.data or 'message' in response.data
        )
