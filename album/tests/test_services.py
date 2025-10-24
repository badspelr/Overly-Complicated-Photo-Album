import pytest
from django.test import TestCase
from ..models import Photo
from ..services.bulk_operations_service import BulkOperationsService
from .factories import UserFactory, AlbumFactory, PhotoFactory, CategoryFactory

@pytest.mark.django_db
class MediaServiceTest(TestCase):
    """Test cases for MediaService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    def test_extract_photo_metadata(self):
        """Test metadata extraction from photo."""
        # This test would require a sample image with EXIF data
        pass
    
    def test_extract_video_metadata(self):
        """Test metadata extraction from video."""
        # This test would require a sample video file
        pass

@pytest.mark.django_db
class BulkOperationsServiceTest(TestCase):
    """Test cases for BulkOperationsService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.photo1 = PhotoFactory(album=self.album)
        self.photo2 = PhotoFactory(album=self.album)
    
    def test_bulk_delete_media(self):
        """Test bulk deletion of media."""
        media_ids = [('photo', self.photo1.pk), ('photo', self.photo2.pk)]
        result = BulkOperationsService.bulk_delete_media(media_ids, self.user)
        self.assertEqual(result['deleted'], 2)
        self.assertEqual(result['failed'], 0)
        
        # Verify photos are deleted
        with self.assertRaises(Photo.DoesNotExist):
            Photo.objects.get(pk=self.photo1.pk)
        with self.assertRaises(Photo.DoesNotExist):
            Photo.objects.get(pk=self.photo2.pk)
    
    def test_bulk_move_media(self):
        """Test bulk moving of media."""
        target_album = AlbumFactory(owner=self.user)
        media_ids = [('photo', self.photo1.pk), ('photo', self.photo2.pk)]
        result = BulkOperationsService.bulk_move_media(media_ids, target_album.pk, self.user)
        self.assertEqual(result['moved'], 2)
        self.assertEqual(result['failed'], 0)
        
        # Verify photos are moved
        self.photo1.refresh_from_db()
        self.photo2.refresh_from_db()
        self.assertEqual(self.photo1.album, target_album)
        self.assertEqual(self.photo2.album, target_album)
    
    def test_bulk_update_category(self):
        """Test bulk updating of media category."""
        category = CategoryFactory(created_by=self.user)
        media_ids = [('photo', self.photo1.pk), ('photo', self.photo2.pk)]
        result = BulkOperationsService.bulk_update_category(media_ids, category.pk, self.user)
        self.assertEqual(result['updated'], 2)
        self.assertEqual(result['failed'], 0)
        
        # Verify categories are updated
        self.photo1.refresh_from_db()
        self.photo2.refresh_from_db()
        self.assertEqual(self.photo1.category, category)
        self.assertEqual(self.photo2.category, category)
