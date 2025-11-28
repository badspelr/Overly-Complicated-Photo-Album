"""
Test cases for models.
"""
import pytest
from django.test import TestCase
from django.db import IntegrityError
from ..models import Album, Photo, Video, Category
from .factories import UserFactory, AlbumFactory, PhotoFactory, VideoFactory, CategoryFactory, SiteSettingsFactory


@pytest.mark.django_db
class ModelTestCase(TestCase):
    """Base test case for model tests."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.category = CategoryFactory(created_by=self.user)
        self.album = AlbumFactory(owner=self.user, category=self.category)


@pytest.mark.django_db
class AlbumModelTest(ModelTestCase):
    """Test cases for Album model."""
    
    def test_album_creation(self):
        """Test album creation."""
        album = AlbumFactory(owner=self.user)
        self.assertEqual(album.owner, self.user)
        self.assertFalse(album.is_public)
        self.assertIsNotNone(album.created_at)
    
    def test_album_str_representation(self):
        """Test album string representation."""
        album = AlbumFactory(title="Test Album")
        self.assertEqual(str(album), "Test Album")
    
    def test_album_ordering(self):
        """Test album ordering by created_at."""
        album1 = AlbumFactory(owner=self.user)
        album2 = AlbumFactory(owner=self.user)
        albums = Album.objects.filter(owner=self.user)
        self.assertEqual(albums[0], album2)  # Most recent first
    
    def test_album_viewers_relationship(self):
        """Test album viewers many-to-many relationship."""
        viewer = UserFactory()
        self.album.viewers.add(viewer)
        self.assertIn(viewer, self.album.viewers.all())


@pytest.mark.django_db
class PhotoModelTest(ModelTestCase):
    """Test cases for Photo model."""
    
    def setUp(self):
        super().setUp()
        self.model = Photo
        self.factory = PhotoFactory

    def test_media_creation(self):
        """Test media creation."""
        media = self.factory(album=self.album)
        self.assertEqual(media.album, self.album)
        self.assertIsNotNone(media.uploaded_at)
    
    def test_media_str_representation(self):
        """Test media string representation."""
        media = self.factory(title="Test Media")
        self.assertEqual(str(media), "Test Media")
    
    def test_media_ordering(self):
        """Test media ordering by uploaded_at."""
        media1 = self.factory(album=self.album)
        media2 = self.factory(album=self.album)
        media = self.model.objects.filter(album=self.album)
        self.assertEqual(media[0], media2)  # Most recent first


@pytest.mark.django_db
class VideoModelTest(ModelTestCase):
    """Test cases for Video model."""
    
    def setUp(self):
        super().setUp()
        self.model = Video
        self.factory = VideoFactory

    def test_media_creation(self):
        """Test media creation."""
        media = self.factory(album=self.album)
        self.assertEqual(media.album, self.album)
        self.assertIsNotNone(media.uploaded_at)
    
    def test_media_str_representation(self):
        """Test media string representation."""
        media = self.factory(title="Test Media")
        self.assertEqual(str(media), "Test Media")
    
    def test_media_ordering(self):
        """Test media ordering by uploaded_at."""
        media1 = self.factory(album=self.album)
        media2 = self.factory(album=self.album)
        media = self.model.objects.filter(album=self.album)
        self.assertEqual(media[0], media2)  # Most recent first


@pytest.mark.django_db
class CategoryModelTest(ModelTestCase):
    """Test cases for Category model."""
    
    def test_category_creation(self):
        """Test category creation."""
        category = CategoryFactory(created_by=self.user)
        self.assertEqual(category.created_by, self.user)
    
    def test_category_str_representation(self):
        """Test category string representation."""
        category = CategoryFactory(name="Test Category")
        self.assertEqual(str(category), "Test Category")
    
    def test_category_unique_name(self):
        """Test category name uniqueness."""
        CategoryFactory(name="Unique Category", created_by=self.user)
        with self.assertRaises(IntegrityError):
            CategoryFactory(name="Unique Category", created_by=self.user)
    
    def test_category_ordering(self):
        """Test category ordering by name."""
        category1 = CategoryFactory(name="Z Category", created_by=self.user)
        category2 = CategoryFactory(name="A Category", created_by=self.user)
        categories = Category.objects.filter(created_by=self.user)
        self.assertEqual(categories[0], category2)  # Alphabetical order


@pytest.mark.django_db
class SiteSettingsModelTest(ModelTestCase):
    """Test cases for SiteSettings model."""
    
    def test_site_settings_creation(self):
        """Test site settings creation."""
        settings = SiteSettingsFactory()
        self.assertIsNotNone(settings.title)
    
    def test_site_settings_str_representation(self):
        """Test site settings string representation."""
        settings = SiteSettingsFactory(title="Test Site")
        self.assertEqual(str(settings), "Test Site")
