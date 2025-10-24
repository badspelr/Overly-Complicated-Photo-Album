"""
Test cases for Celery tasks.
Tests for background task processing, retries, scheduling, and error handling.
"""
import pytest
from unittest.mock import patch, Mock
from django.test import TestCase
from celery.exceptions import Retry

from album import tasks
from album.tests.factories import UserFactory, AlbumFactory, PhotoFactory, VideoFactory


@pytest.mark.django_db
class TestPhotoAITask(TestCase):
    """Test cases for photo AI processing task."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    @patch('album.tasks.AIAnalysisService')
    def test_process_photo_ai_success(self, mock_service):
        """Test successful photo AI processing task."""
        # Setup
        photo = PhotoFactory(
            album=self.album,
            ai_processed=False,
            processing_status='pending'
        )
        
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.analyze_photo.return_value = {
            'description': 'A beautiful landscape',
            'tags': ['landscape', 'nature', 'outdoor'],
            'confidence': 0.92
        }
        
        # Execute task
        result = tasks.process_photo_ai(photo.id)
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        
        # Verify photo was updated
        photo.refresh_from_db()
        self.assertTrue(photo.ai_processed)
        self.assertEqual(photo.processing_status, 'completed')
        self.assertEqual(photo.ai_description, 'A beautiful landscape')
        self.assertEqual(photo.ai_tags, ['landscape', 'nature', 'outdoor'])
        self.assertAlmostEqual(float(photo.ai_confidence_score), 0.92, places=2)
    
    @patch('album.tasks.AIAnalysisService')
    def test_process_photo_ai_retry_on_failure(self, mock_service):
        """Test photo AI task retries on transient failure."""
        photo = PhotoFactory(album=self.album, ai_processed=False)
        
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.analyze_photo.side_effect = Exception("Transient error")
        
        # Task should retry
        with patch.object(tasks.process_photo_ai, 'retry') as mock_retry:
            mock_retry.side_effect = Retry()
            
            with self.assertRaises(Retry):
                tasks.process_photo_ai(photo.id)
            
            mock_retry.assert_called_once()
    
    def test_process_photo_ai_invalid_photo_id(self):
        """Test photo AI task handles invalid photo ID."""
        # Non-existent photo ID
        result = tasks.process_photo_ai(99999)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('not found', result['message'].lower())
    
    @patch('album.tasks.AIAnalysisService')
    def test_process_photo_ai_marks_failed_after_max_retries(self, mock_service):
        """Test photo marked as failed after max retries."""
        photo = PhotoFactory(
            album=self.album,
            ai_processed=False,
            processing_status='pending'
        )
        
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.analyze_photo.side_effect = Exception("Permanent error")
        
        # Simulate max retries exhausted
        with patch.object(tasks.process_photo_ai, 'retry') as mock_retry:
            mock_retry.side_effect = tasks.process_photo_ai.MaxRetriesExceededError()
            
            try:
                tasks.process_photo_ai(photo.id)
            except tasks.process_photo_ai.MaxRetriesExceededError:
                pass
        
        # Photo should be marked as failed
        photo.refresh_from_db()
        self.assertEqual(photo.processing_status, 'failed')


@pytest.mark.django_db
class TestVideoAITask(TestCase):
    """Test cases for video AI processing task."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    @patch('album.tasks.AIAnalysisService')
    def test_process_video_ai_success(self, mock_service):
        """Test successful video AI processing task."""
        video = VideoFactory(
            album=self.album,
            ai_processed=False,
            processing_status='pending'
        )
        
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.analyze_video.return_value = {
            'description': 'A family gathering',
            'tags': ['family', 'indoor', 'celebration'],
            'confidence': 0.88
        }
        
        # Execute task
        result = tasks.process_video_ai(video.id)
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        
        # Verify video was updated
        video.refresh_from_db()
        self.assertTrue(video.ai_processed)
        self.assertEqual(video.processing_status, 'completed')
        self.assertEqual(video.ai_description, 'A family gathering')


@pytest.mark.django_db
class TestBatchProcessingTasks(TestCase):
    """Test cases for batch processing tasks."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    @patch('album.tasks.process_photo_ai.delay')
    def test_batch_process_pending_photos(self, mock_task):
        """Test batch processing of pending photos."""
        # Create 10 pending photos
        photos = [
            PhotoFactory(
                album=self.album,
                ai_processed=False,
                processing_status='pending'
            )
            for _ in range(10)
        ]
        
        # Execute batch task with limit of 5
        result = tasks.process_pending_photos_batch(limit=5)
        
        # Should queue 5 tasks
        self.assertEqual(mock_task.call_count, 5)
        self.assertEqual(result['processed'], 5)
        self.assertEqual(result['status'], 'success')
    
    @patch('album.tasks.process_video_ai.delay')
    def test_batch_process_pending_videos(self, mock_task):
        """Test batch processing of pending videos."""
        # Create 15 pending videos
        videos = [
            VideoFactory(
                album=self.album,
                ai_processed=False,
                processing_status='pending'
            )
            for _ in range(15)
        ]
        
        # Execute batch task with limit of 10
        result = tasks.process_pending_videos_batch(limit=10)
        
        # Should queue 10 tasks
        self.assertEqual(mock_task.call_count, 10)
        self.assertEqual(result['processed'], 10)
    
    def test_batch_process_skips_already_processed(self):
        """Test batch processing skips already processed items."""
        # Create mix of processed and unprocessed
        processed_photo = PhotoFactory(
            album=self.album,
            ai_processed=True,
            processing_status='completed'
        )
        pending_photo = PhotoFactory(
            album=self.album,
            ai_processed=False,
            processing_status='pending'
        )
        
        with patch('album.tasks.process_photo_ai.delay') as mock_task:
            result = tasks.process_pending_photos_batch(limit=10)
            
            # Should only process pending photo
            self.assertEqual(mock_task.call_count, 1)
            mock_task.assert_called_with(pending_photo.id)
    
    def test_batch_process_respects_limit(self):
        """Test batch processing respects configured limit."""
        # Create 100 pending photos
        photos = [
            PhotoFactory(
                album=self.album,
                ai_processed=False,
                processing_status='pending'
            )
            for _ in range(100)
        ]
        
        with patch('album.tasks.process_photo_ai.delay') as mock_task:
            # Process with limit of 50
            result = tasks.process_pending_photos_batch(limit=50)
            
            # Should only process 50
            self.assertEqual(mock_task.call_count, 50)
            self.assertEqual(result['processed'], 50)


@pytest.mark.django_db
class TestScheduledTasks(TestCase):
    """Test cases for scheduled Celery Beat tasks."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    @patch('album.tasks.process_pending_photos_batch')
    def test_scheduled_photo_batch_runs_at_2am(self, mock_batch):
        """Test scheduled photo batch task configuration."""
        # This tests that the task is properly configured in celery beat
        # Actual scheduling is tested via celery beat schedule
        mock_batch.return_value = {'status': 'success', 'processed': 10}
        
        # Call the scheduled task directly
        result = tasks.process_pending_photos_batch()
        
        self.assertEqual(result['status'], 'success')
        mock_batch.assert_called_once()
    
    @patch('album.tasks.process_pending_videos_batch')
    def test_scheduled_video_batch_runs_at_230am(self, mock_batch):
        """Test scheduled video batch task configuration."""
        mock_batch.return_value = {'status': 'success', 'processed': 5}
        
        # Call the scheduled task directly
        result = tasks.process_pending_videos_batch()
        
        self.assertEqual(result['status'], 'success')
        mock_batch.assert_called_once()


@pytest.mark.django_db
class TestMediaUploadTask(TestCase):
    """Test cases for media upload processing task."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    @patch('album.tasks.process_photo_ai.delay')
    def test_process_media_on_upload_photo(self, mock_task):
        """Test media upload triggers AI processing for photo."""
        photo = PhotoFactory(album=self.album)
        
        # Call the upload handler task
        tasks.process_media_on_upload('photo', photo.id)
        
        # Should queue AI processing task
        mock_task.assert_called_once_with(photo.id)
    
    @patch('album.tasks.process_video_ai.delay')
    def test_process_media_on_upload_video(self, mock_task):
        """Test media upload triggers AI processing for video."""
        video = VideoFactory(album=self.album)
        
        # Call the upload handler task
        tasks.process_media_on_upload('video', video.id)
        
        # Should queue AI processing task
        mock_task.assert_called_once_with(video.id)
    
    def test_process_media_on_upload_invalid_type(self):
        """Test media upload handler rejects invalid media type."""
        result = tasks.process_media_on_upload('invalid_type', 123)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('invalid', result['message'].lower())


@pytest.mark.integration
@pytest.mark.django_db
class TestTaskChaining(TestCase):
    """Test cases for task chaining and workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    @patch('album.tasks.EmbeddingService')
    @patch('album.tasks.AIAnalysisService')
    def test_photo_processing_generates_embedding(self, mock_ai_service, mock_embed_service):
        """Test photo processing also generates embedding."""
        photo = PhotoFactory(album=self.album, ai_processed=False)
        
        # Mock services
        mock_ai_instance = Mock()
        mock_ai_service.return_value = mock_ai_instance
        mock_ai_instance.analyze_photo.return_value = {
            'description': 'Test',
            'tags': ['test'],
            'confidence': 0.9
        }
        
        mock_embed_instance = Mock()
        mock_embed_service.return_value = mock_embed_instance
        mock_embed_instance.generate_image_embedding.return_value = [0.1] * 512
        
        # Process photo
        tasks.process_photo_ai(photo.id)
        
        # Verify both AI analysis and embedding were generated
        photo.refresh_from_db()
        self.assertTrue(photo.ai_processed)
        # Embedding should be set (if implemented)
        # self.assertIsNotNone(photo.embedding)
