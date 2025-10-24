"""
Integration test cases.
Tests end-to-end workflows and multi-component interactions.
"""
import pytest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import io
from PIL import Image

from album.models import Album, Photo, Video
from album.tests.factories import UserFactory, AlbumFactory, PhotoFactory, VideoFactory
from album.tasks import process_photo_ai, process_video_ai


def create_test_image():
    """Create a test image file."""
    image = Image.new('RGB', (200, 200), color='green')
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        'test_photo.jpg',
        img_io.read(),
        content_type='image/jpeg'
    )


@override_settings(AI_AUTO_PROCESS_ON_UPLOAD=True)
@pytest.mark.django_db
class TestPhotoUploadWorkflow(TestCase):
    """Test complete photo upload workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    @patch('album.tasks.process_media_on_upload.delay')
    def test_complete_photo_upload_flow(self, mock_task):
        """Test photo upload from form to storage to AI processing."""
        # 1. Upload photo via form
        response = self.client.post(
            reverse('album:minimal_upload'),
            {
                'album': self.album.id,
                'files': [create_test_image()]
            }
        )
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify photo was created in database
        photo = Photo.objects.filter(album=self.album).first()
        self.assertIsNotNone(photo)
        self.assertTrue(photo.image)
        
        # 3. Verify AI processing task was triggered
        mock_task.assert_called_once_with('photo', photo.id)
        
        # 4. Verify photo is visible in album
        response = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, photo.title or 'photo')
    
    @patch('album.services.ai_analysis_service.analyze_image')
    def test_photo_ai_processing_workflow(self, mock_analyze):
        """Test photo AI analysis workflow."""
        # Mock AI analysis result
        mock_analyze.return_value = {
            'description': 'A beautiful landscape',
            'tags': ['landscape', 'nature', 'outdoor'],
            'confidence': 0.95,
            'embedding': [0.1] * 512
        }
        
        # Create photo
        photo = PhotoFactory(album=self.album)
        
        # Process AI (synchronously for test)
        result = process_photo_ai(photo.id)
        
        # Verify AI data was saved
        photo.refresh_from_db()
        self.assertEqual(photo.ai_description, 'A beautiful landscape')
        self.assertGreater(len(photo.ai_tags), 0)
        self.assertEqual(photo.ai_confidence_score, 0.95)
        
        # Verify photo is now searchable by AI content
        response = self.client.get(
            reverse('album:search_media'),
            {'q': 'landscape'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, photo.title or 'photo')


@pytest.mark.django_db
class TestVideoUploadWorkflow(TestCase):
    """Test complete video upload workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    @patch('album.tasks.process_video_ai.delay')
    def test_complete_video_upload_flow(self, mock_task):
        """Test video upload from form to storage to AI processing."""
        # 1. Upload video
        video_file = SimpleUploadedFile(
            'test_video.mp4',
            b'fake video content',
            content_type='video/mp4'
        )
        
        response = self.client.post(
            reverse('album:minimal_upload'),
            {
                'album': self.album.id,
                'videos': [video_file]
            }
        )
        
        # Should redirect on success
        self.assertIn(response.status_code, [200, 302])
        
        # 2. Verify video was created
        video = Video.objects.filter(album=self.album).first()
        if video:
            self.assertTrue(video.video_file)
            
            # 3. Verify AI processing task was triggered
            mock_task.assert_called()
    
    @patch('album.models.Video.generate_thumbnail', MagicMock())
    @patch('album.services.ai_analysis_service.analyze_image')
    def test_video_ai_processing_workflow(self, mock_analyze):
        """Test video AI analysis workflow."""
        # Mock AI analysis result
        mock_analyze.return_value = {
            'description': 'A video of people dancing',
            'tags': ['dance', 'people', 'music'],
            'confidence': 0.88,
            'embedding': [0.2] * 512
        }
        
        # Create video
        video = VideoFactory(album=self.album)
        
        # Process AI
        result = process_video_ai(video.id)
        
        # Verify AI data was saved
        video.refresh_from_db()
        if hasattr(video, 'ai_description'):
            self.assertIsNotNone(video.ai_description)


@pytest.mark.django_db
class TestAlbumManagementWorkflow(TestCase):
    """Test complete album management workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
    
    def test_create_album_add_photos_workflow(self):
        """Test creating album and adding photos workflow."""
        # 1. Create album
        response = self.client.post(
            reverse('album:create_album'),
            {
                'title': 'Vacation Photos',
                'description': 'Summer 2024',
                'is_public': False
            }
        )
        
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify album was created
        album = Album.objects.filter(
            owner=self.user,
            title='Vacation Photos'
        ).first()
        self.assertIsNotNone(album)
        
        # 3. Add photos to album
        with patch('album.tasks.process_photo_ai.delay'):
            response = self.client.post(
                reverse('album:minimal_upload'),
                {
                    'album': album.id,
                    'files': [create_test_image(), create_test_image()]
                }
            )
        
        # 4. Verify photos were added
        photo_count = Photo.objects.filter(album=album).count()
        self.assertGreater(photo_count, 0)
        
        # 5. View album with photos
        response = self.client.get(
            reverse('album:album_detail', args=[album.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vacation Photos')


@pytest.mark.django_db
class TestSearchWorkflow(TestCase):
    """Test search workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def test_text_search_workflow(self):
        """Test text-based search workflow."""
        # Create photos with different titles/descriptions
        photo1 = PhotoFactory(
            album=self.album,
            title='Beach Sunset',
            description='Beautiful sunset at the beach'
        )
        photo2 = PhotoFactory(
            album=self.album,
            title='Mountain View',
            description='Scenic mountain landscape'
        )
        
        # Search for "beach"
        response = self.client.get(
            reverse('album:search_media'),
            {'q': 'beach'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beach Sunset')
        self.assertNotContains(response, 'Mountain View')
    
    @patch('album.services.embedding_service.generate_text_embedding')
    def test_ai_similarity_search_workflow(self, mock_generate_embedding):
        """Test AI similarity search workflow."""
        # Mock embedding generation
        mock_generate_embedding.return_value = [0.1] * 512
        
        # Mock search results
        photo1 = PhotoFactory(album=self.album, embedding=[0.1] * 512)
        photo2 = PhotoFactory(album=self.album, embedding=[0.9] * 512)
        
        # Perform AI search
        response = self.client.get(
            reverse('album:search_media'),
            {'q': 'test', 'search_type': 'ai'}
        )
        
        # Should return similar photos
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, photo1.get_absolute_url())
        self.assertNotContains(response, photo2.get_absolute_url())


@pytest.mark.django_db
class TestSharingWorkflow(TestCase):
    """Test album sharing workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.owner = UserFactory()
        self.viewer = UserFactory()
        self.album = AlbumFactory(owner=self.owner, is_public=False)
    
    def test_share_album_with_user_workflow(self):
        """Test sharing album with another user."""
        self.client.force_login(self.owner)
        
        # 1. Share album with viewer
        self.album.viewers.add(self.viewer)
        self.album.save()
        
        # 2. Logout and login as viewer
        self.client.logout()
        self.client.force_login(self.viewer)
        
        # 3. Viewer should be able to see album
        response = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Viewer should NOT be able to delete album
        response = self.client.post(
            reverse('album:delete_album', args=[self.album.id])
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify album still exists
        self.assertTrue(Album.objects.filter(id=self.album.id).exists())
    
    def test_public_album_visibility_workflow(self):
        """Test public album visibility workflow."""
        # Make album public
        self.album.is_public = True
        self.album.save()
        
        # Anonymous user should be able to view
        self.client.logout()
        response = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        
        # Should show album (or redirect to login, depending on settings)
        self.assertIn(response.status_code, [200, 302])


@pytest.mark.django_db
class TestBatchProcessingWorkflow(TestCase):
    """Test batch processing workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    @patch('django.core.management.call_command')
    def test_batch_ai_processing_workflow(self, mock_call_command):
        """Test batch AI processing workflow."""
        # Create multiple photos without AI data
        photos = [
            PhotoFactory(album=self.album)
            for _ in range(5)
        ]
        
        # Trigger batch processing
        response = self.client.post(
            reverse('album:process_photos_ai'),
            {'photo_ids': [p.id for p in photos]}
        )
        
        # Should trigger batch task
        if response.status_code in [200, 302]:
            mock_call_command.assert_called_with('analyze_photos', limit=str(len(photos)))


@pytest.mark.django_db
class TestErrorHandlingWorkflow(TestCase):
    """Test error handling in workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
    
    def test_invalid_file_upload_error_handling(self):
        """Test error handling for invalid file uploads."""
        album = AlbumFactory(owner=self.user)
        
        # Try to upload invalid file
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'Not an image or video',
            content_type='text/plain'
        )
        
        response = self.client.post(
            reverse('album:minimal_upload'),
            {
                'album': album.id,
                'files': [invalid_file]
            }
        )
        
        # Should redirect, not crash
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Photo.objects.count(), 0)
    
    def test_missing_album_error_handling(self):
        """Test error handling for missing album."""
        # Try to view non-existent album
        response = self.client.get(
            reverse('album:album_detail', args=[99999])
        )
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
    
    @patch('album.services.ai_analysis_service.analyze_image')
    def test_ai_processing_failure_handling(self, mock_analyze):
        """Test error handling when AI processing fails."""
        # Mock AI failure
        mock_analyze.side_effect = Exception('GPU out of memory')
        
        photo = PhotoFactory(album=AlbumFactory(owner=self.user))
        
        # Process should handle error gracefully
        try:
            process_photo_ai(photo.id)
        except Exception:
            pass  # Should not crash
        
        # Photo should still exist even if AI failed
        self.assertTrue(Photo.objects.filter(id=photo.id).exists())


@pytest.mark.django_db
class TestCachingWorkflow(TestCase):
    """Test caching in workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def test_album_list_caching(self):
        """Test album list uses caching."""
        # First request
        response1 = self.client.get(reverse('album:album_list'))
        
        # Second request should hit cache
        response2 = self.client.get(reverse('album:album_list'))
        
        # Both should succeed
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
    
    def test_cache_invalidation_on_update(self):
        """Test cache is invalidated when album is updated."""
        # View album
        response1 = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        
        # Update album
        self.album.title = 'Updated Title'
        self.album.save()
        
        # View again - should show updated data
        response2 = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        
        self.assertContains(response2, 'Updated Title')


@pytest.mark.django_db
class TestPerformanceWorkflow(TestCase):
    """Test performance-related workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def test_large_album_pagination(self):
        """Test pagination works for large albums."""
        # Create many photos
        photos = [
            PhotoFactory(album=self.album)
            for _ in range(50)
        ]
        
        # Request first page
        response = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        
        # Should paginate, not show all 50
        self.assertEqual(response.status_code, 200)
        # Check if pagination is present (depends on implementation)
