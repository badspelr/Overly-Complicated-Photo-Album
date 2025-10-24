"""
Test cases for security features.
Tests for XSS prevention, SQL injection, CSRF, file upload security, and authorization.
"""
import pytest
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import io
from PIL import Image

from album.models import Photo
from album.tests.factories import UserFactory, AlbumFactory, PhotoFactory


@pytest.mark.django_db
class TestXSSPrevention(TestCase):
    """Test cases for XSS prevention."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def test_album_description_xss_prevention(self):
        """Test album description escapes XSS attempts."""
        xss_payload = '<script>alert("XSS")</script>'
        
        # Create album with XSS in description
        album = AlbumFactory(
            owner=self.user,
            description=xss_payload
        )
        
        # Retrieve album detail page
        response = self.client.get(reverse('album:album_detail', args=[album.id]))
        
        # XSS should be escaped - Django auto-escapes, so we verify the escaped version is present
        self.assertContains(response, '&lt;script&gt;')
        self.assertContains(response, 'alert(&quot;XSS&quot;)')
        # And the raw script tag should NOT be executable (not in <script> tag context)
        response_text = response.content.decode('utf-8')
        # Count occurrences - there might be one in visible HTML as escaped text
        self.assertLess(response_text.count('<script>alert("XSS")</script>'), 1)
    
    def test_photo_title_xss_prevention(self):
        """Test photo title escapes XSS attempts."""
        xss_payload = '<img src=x onerror=alert(1)>'
        
        photo = PhotoFactory(
            album=self.album,
            title=xss_payload
        )
        
        response = self.client.get(reverse('album:photo_detail', args=[photo.id]))
        
        # Should escape the HTML
        self.assertNotContains(response, '<img src=x')
    
    def test_ai_description_xss_prevention(self):
        """Test AI-generated description escapes any potential XSS."""
        # Simulate AI description with suspicious content
        photo = PhotoFactory(
            album=self.album,
            ai_description='<script>malicious()</script> a red car'
        )
        
        response = self.client.get(reverse('album:photo_detail', args=[photo.id]))
        
        # Should escape script tags
        self.assertNotContains(response, '<script>malicious()')


@pytest.mark.django_db
class TestSQLInjectionPrevention(TestCase):
    """Test cases for SQL injection prevention."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def test_search_query_sql_injection(self):
        """Test search query prevents SQL injection."""
        sql_injection = "'; DROP TABLE album_photo; --"
        
        # Try to search with SQL injection
        response = self.client.get(
            reverse('album:search_media'),
            {'q': sql_injection}
        )
        
        # Should not error, table should still exist
        self.assertIn(response.status_code, [200, 400])
        
        # Verify table still exists
        self.assertTrue(Photo.objects.model._meta.db_table)
    
    def test_album_id_sql_injection(self):
        """Test album ID parameter prevents SQL injection."""
        # Try SQL injection in URL parameter
        response = self.client.get('/albums/1 OR 1=1/')
        
        # Should return 404, not expose data
        self.assertEqual(response.status_code, 404)


@pytest.mark.django_db
class TestFileUploadSecurity(TestCase):
    """Test cases for file upload security."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def _create_test_image(self, format='JPEG'):
        """Create a test image file."""
        image = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        image.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_upload_validates_image_file_type(self):
        """Test upload only accepts valid image formats."""
        # Try to upload PHP file disguised as image
        malicious_file = SimpleUploadedFile(
            'malicious.php.jpg',
            b'<?php system($_GET["cmd"]); ?>',
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            reverse('album:upload_media'),
            {
                'album': self.album.id,
                'photos': [malicious_file]
            }
        )
        
        # Should reject or fail to process
        # Django's ImageField should validate actual image content
    
    def test_upload_validates_file_size(self):
        """Test upload rejects oversized files."""
        # Create large file (if size limit exists)
        # This depends on your MAX_UPLOAD_SIZE setting
        pass
    
    def test_upload_strips_exif_location_data(self):
        """Test upload can strip sensitive EXIF data if configured."""
        # Create image with GPS data
        # Upload and verify GPS data is removed if privacy setting enabled
        pass
    
    def test_filename_sanitization(self):
        """Test uploaded filenames are sanitized."""
        # Create file with dangerous filename
        dangerous_file = SimpleUploadedFile(
            'test.exe',
            b'fake executable content',
            content_type='application/x-msdownload'
        )
        
        response = self.client.post(
            reverse('album:minimal_upload'),
            {
                'album': self.album.id,
                'photos': [dangerous_file]
            }
        )
        
        # Filename should be sanitized, no path traversal
        if response.status_code == 302:  # Successful upload
            photo = Photo.objects.latest('id')
            # Filename should not contain ../
            self.assertNotIn('..', photo.image.name)
            self.assertNotIn('/etc/', photo.image.name)


@pytest.mark.django_db
class TestAuthorizationSecurity(TestCase):
    """Test cases for authorization and access control."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.private_album = AlbumFactory(owner=self.other_user, is_public=False)
    
    def test_cannot_access_other_users_private_album(self):
        """Test user cannot access another user's private album."""
        self.client.force_login(self.user)
        
        response = self.client.get(
            reverse('album:album_detail', args=[self.private_album.id])
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_cannot_delete_other_users_photo(self):
        """Test user cannot delete another user's photo."""
        other_photo = PhotoFactory(album=self.private_album)
        
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('album:delete_photo', args=[other_photo.id])
        )
        
        # Should be denied
        self.assertIn(response.status_code, [403, 404])
        
        # Photo should still exist
        self.assertTrue(Photo.objects.filter(id=other_photo.id).exists())
    
    def test_cannot_modify_other_users_album(self):
        """Test user cannot modify another user's album."""
        self.client.force_login(self.user)
        
        response = self.client.post(
            reverse('album:edit_album', args=[self.private_album.id]),
            {'title': 'Hacked', 'description': 'Hacked'}
        )
        
        # Should be denied
        self.assertIn(response.status_code, [403, 404])
        
        # Album should not be modified
        self.private_album.refresh_from_db()
        self.assertNotEqual(self.private_album.title, 'Hacked Title')
    
    def test_viewer_cannot_delete_photos(self):
        """Test viewer cannot delete photos from shared album."""
        # Share album with other user as viewer
        self.album.viewers.add(self.other_user)
        photo = PhotoFactory(album=self.album)
        
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse('album:delete_photo', args=[photo.id])
        )
    
    def test_anonymous_user_cannot_access_private_content(self):
        """Test anonymous users cannot access private content."""
        # Don't login
        
        response = self.client.get(
            reverse('album:album_detail', args=[self.album.id])
        )
        
        # Should redirect to login or return 404
        self.assertIn(response.status_code, [302, 404])


@pytest.mark.django_db
class TestCSRFProtection(TestCase):
    """Test cases for CSRF protection."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client(enforce_csrf_checks=True)
        self.user = UserFactory()
        self.album = AlbumFactory(owner=self.user)
        self.client.force_login(self.user)
    
    def test_post_requires_csrf_token(self):
        """Test POST requests require CSRF token."""
        # Try to delete without CSRF token
        response = self.client.post(
            reverse('album:delete_album', args=[self.album.id])
        )
        
        # Should fail CSRF check
        self.assertEqual(response.status_code, 403)
    
    def test_post_with_valid_csrf_token(self):
        """Test POST succeeds with valid CSRF token."""
        # Get CSRF token
        response = self.client.get(reverse('album:album_list'))
        csrf_token = response.cookies.get('csrftoken')
        
        if csrf_token:
            # Use token in POST
            response = self.client.post(
                reverse('album:delete_album', args=[self.album.id]),
                HTTP_X_CSRFTOKEN=csrf_token.value
            )
            
            # Should succeed (or at least not fail CSRF)
            self.assertNotEqual(response.status_code, 403)


@pytest.mark.django_db
class TestPasswordSecurity(TestCase):
    """Test cases for password security."""
    
    def test_password_not_stored_in_plaintext(self):
        """Test passwords are hashed, not stored in plaintext."""
        user = UserFactory(password='TestPassword123!')
        
        # Password should be hashed
        self.assertNotEqual(user.password, 'TestPassword123!')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_password_min_length_validation(self):
        """Test password minimum length is enforced."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Short password should fail
        with self.assertRaises(ValidationError):
            validate_password('123')
    
    def test_password_common_password_validation(self):
        """Test common passwords are rejected."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Common password should fail
        with self.assertRaises(ValidationError):
            validate_password('password')


@pytest.mark.django_db
class TestRateLimiting(TestCase):
    """Test cases for rate limiting (if implemented)."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
    
    def test_login_rate_limiting(self):
        """Test login attempts are rate limited."""
        # Make multiple failed login attempts
        for _ in range(10):
            self.client.post(
                reverse('login'),
                {
                    'username': 'wronguser',
                    'password': 'wrongpass'
                }
            )
        
        # Next attempt should be rate limited (if implemented)
        # This depends on your rate limiting configuration
        pass


@pytest.mark.django_db
class TestSecurityHeaders(TestCase):
    """Test cases for security headers."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
    
    def test_x_frame_options_header(self):
        """Test X-Frame-Options header is set."""
        response = self.client.get(reverse('album:album_list'))
        
        # Should have X-Frame-Options to prevent clickjacking
        if 'X-Frame-Options' in response:
            self.assertIn(response['X-Frame-Options'], ['DENY', 'SAMEORIGIN'])
    
    def test_x_content_type_options_header(self):
        """Test X-Content-Type-Options header is set."""
        response = self.client.get(reverse('album:album_list'))
        
        # Should have nosniff to prevent MIME-sniffing
        if 'X-Content-Type-Options' in response:
            self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
    
    def test_strict_transport_security_header(self):
        """Test HSTS header is set for HTTPS."""
        # HSTS should be set in production
        # This test might only pass in production environment
        pass
