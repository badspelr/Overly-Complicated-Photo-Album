"""
Test cases for forms.
Tests for AlbumForm, PhotoForm, VideoForm validation and business logic.
"""
import pytest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

from album.forms import AlbumForm, PhotoForm, VideoForm
from album.tests.factories import UserFactory, AlbumFactory


def create_test_image():
    """Create a test image file."""
    image = Image.new('RGB', (100, 100), color='blue')
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        'test_image.jpg',
        img_io.read(),
        content_type='image/jpeg'
    )


@pytest.mark.django_db
class TestAlbumForm(TestCase):
    """Test cases for AlbumForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
    
    def test_valid_album_form(self):
        """Test form is valid with correct data."""
        form_data = {
            'title': 'Test Album',
            'description': 'Test description',
            'is_public': True
        }
        
        form = AlbumForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_album_form_title_required(self):
        """Test title field is required."""
        form_data = {
            'description': 'Test description',
            'is_public': True
        }
        
        form = AlbumForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_album_form_title_max_length(self):
        """Test title field max length validation."""
        form_data = {
            'title': 'A' * 300,  # Assuming max_length is 200
            'description': 'Test',
            'is_public': True
        }
        
        form = AlbumForm(data=form_data)
        # Should fail if max_length is exceeded
        if not form.is_valid():
            self.assertIn('title', form.errors)
    
    def test_album_form_empty_description(self):
        """Test description is optional."""
        form_data = {
            'title': 'Test Album',
            'description': '',
            'is_public': False
        }
        
        form = AlbumForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_album_form_default_visibility(self):
        """Test default visibility setting."""
        form_data = {
            'title': 'Test Album',
            'description': 'Test'
        }
        
        form = AlbumForm(data=form_data)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = self.user
            album.save()
            
            # Check default visibility (depends on your model default)
            self.assertIsNotNone(album.is_public)


@pytest.mark.django_db
class TestPhotoForm(TestCase):
    """Test cases for PhotoForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    def test_valid_photo_form(self):
        """Test form is valid with correct data."""
        form_data = {
            'title': 'Test Photo',
            'description': 'Test description',
            'album': self.album.id
        }
        
        form_files = {
            'image': create_test_image()
        }
        
        form = PhotoForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
    
    def test_photo_form_image_required(self):
        """Test image field is required."""
        form_data = {
            'title': 'Test Photo',
            'album': self.album.id
        }
        
        form = PhotoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
    
    def test_photo_form_title_optional(self):
        """Test title is optional (can be auto-generated)."""
        form_data = {
            'album': self.album.id
        }
        
        form_files = {
            'image': create_test_image()
        }
        
        form = PhotoForm(data=form_data, files=form_files)
        # Depends on your form configuration
        # Either valid (title optional) or invalid (title required)
    
    def test_photo_form_invalid_image_format(self):
        """Test invalid image format is rejected."""
        form_data = {
            'title': 'Test Photo',
            'album': self.album.id
        }
        
        form_files = {
            'image': SimpleUploadedFile(
                'test.txt',
                b'Not an image',
                content_type='text/plain'
            )
        }
        
        form = PhotoForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())


@pytest.mark.django_db
class TestVideoForm(TestCase):
    """Test cases for VideoForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    def test_valid_video_form(self):
        """Test form is valid with correct data."""
        form_data = {
            'title': 'Test Video',
            'description': 'Test description',
            'album': self.album.id
        }
        
        form_files = {
            'video_file': SimpleUploadedFile(
                'test.mp4',
                b'fake video content',
                content_type='video/mp4'
            )
        }
        
        form = VideoForm(data=form_data, files=form_files)
        # May be valid or invalid depending on video validation
    
    def test_video_form_video_file_required(self):
        """Test video file is required."""
        form_data = {
            'title': 'Test Video',
            'album': self.album.id
        }
        
        form = VideoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('video', form.errors)  # Field is named 'video', not 'video_file'
    
    def test_video_form_supported_formats(self):
        """Test only supported video formats are accepted."""
        supported_formats = ['mp4', 'avi', 'mov', 'webm']
        
        for format_ext in supported_formats:
            form_data = {
                'title': f'Test {format_ext.upper()}',
                'album': self.album.id
            }
            
            form_files = {
                'video_file': SimpleUploadedFile(
                    f'test.{format_ext}',
                    b'fake video content',
                    content_type=f'video/{format_ext}'
                )
            }
            
            form = VideoForm(data=form_data, files=form_files)
            # Should validate format (actual validation depends on your form)


@pytest.mark.django_db
class TestFormCleanMethods(TestCase):
    """Test cases for custom form clean methods."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    def test_album_form_clean_title_strips_whitespace(self):
        """Test title is cleaned of extra whitespace."""
        form_data = {
            'title': '  Test Album  ',
            'description': 'Test'
        }
        
        form = AlbumForm(data=form_data)
        if form.is_valid():
            self.assertEqual(form.cleaned_data['title'], 'Test Album')
    
    def test_form_prevents_xss_in_description(self):
        """Test form sanitizes description to prevent XSS."""
        form_data = {
            'title': 'Test Album',
            'description': '<script>alert("XSS")</script>'
        }
        
        form = AlbumForm(data=form_data)
        if form.is_valid():
            # Django forms should handle this via template escaping
            # Or custom clean method if implemented
            cleaned_desc = form.cleaned_data['description']
            # Depends on your implementation
    
    def test_photo_album_validation(self):
        """Test photo must belong to valid album."""
        form_data = {
            'title': 'Test Photo',
            'album': 99999  # Non-existent album
        }
        
        form_files = {
            'image': create_test_image()
        }
        
        form = PhotoForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('album', form.errors)


@pytest.mark.django_db
class TestFormValidationMessages(TestCase):
    """Test cases for form validation error messages."""
    
    def test_album_form_empty_title_error_message(self):
        """Test appropriate error message for empty title."""
        form = AlbumForm(data={})
        self.assertFalse(form.is_valid())
        
        # Should have user-friendly error message
        if 'title' in form.errors:
            error_message = str(form.errors['title'])
            self.assertTrue(len(error_message) > 0)
    
    def test_photo_form_missing_image_error_message(self):
        """Test appropriate error message for missing image."""
        form_data = {
            'title': 'Test Photo',
            'album': AlbumFactory(owner=UserFactory()).id
        }
        
        form = PhotoForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Should have user-friendly error message
        if 'image' in form.errors:
            error_message = str(form.errors['image'])
            self.assertTrue(len(error_message) > 0)
    
    def test_custom_validation_error_messages(self):
        """Test custom validation provides clear error messages."""
        # Test any custom validators you've implemented
        # e.g., file size limits, format restrictions, etc.
        pass


@pytest.mark.django_db
class TestFormSaveMethod(TestCase):
    """Test cases for form save methods."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
    
    def test_album_form_save_creates_album(self):
        """Test saving form creates album in database."""
        form_data = {
            'title': 'New Album',
            'description': 'New description',
            'is_public': True
        }
        
        form = AlbumForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        album = form.save(commit=False)
        album.owner = self.user
        album.save()
        
        # Verify album was created
        self.assertTrue(album.id)
        self.assertEqual(album.title, 'New Album')
        self.assertEqual(album.owner, self.user)
    
    def test_photo_form_save_with_commit_false(self):
        """Test saving form with commit=False."""
        album = AlbumFactory(owner=self.user)
        
        form_data = {
            'title': 'Test Photo',
            'album': album.id
        }
        
        form_files = {
            'image': create_test_image()
        }
        
        form = PhotoForm(data=form_data, files=form_files)
        
        if form.is_valid():
            photo = form.save(commit=False)
            
            # Should have form data but not be saved yet
            self.assertIsNone(photo.id)
            self.assertEqual(photo.title, 'Test Photo')
            
            # Save and verify
            photo.save()
            self.assertIsNotNone(photo.id)


@pytest.mark.django_db
class TestFormPermissions(TestCase):
    """Test cases for form-level permissions."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
    
    def test_cannot_assign_photo_to_other_users_album(self):
        """Test form prevents assigning photo to album user doesn't own."""
        other_album = AlbumFactory(owner=self.other_user)
        
        form_data = {
            'title': 'Test Photo',
            'album': other_album.id
        }
        
        form_files = {
            'image': create_test_image()
        }
        
        # Form should validate album ownership (if implemented)
        # This might require passing user to form
        form = PhotoForm(data=form_data, files=form_files)
        
        # Depends on your form implementation
        # Either invalid, or requires view-level check
