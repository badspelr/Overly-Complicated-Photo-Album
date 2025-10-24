from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Transpose
from pgvector.django import VectorField

# ...existing code...

# Tag model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

# User-defined custom album/collection
class CustomAlbum(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_albums')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Custom Album'
        verbose_name_plural = 'Custom Albums'
        indexes = [models.Index(fields=['owner']), models.Index(fields=['title'])]

    def __str__(self):
        return self.title

class SiteSettings(models.Model):
    title = models.CharField(max_length=100, default='Photo Album Site', help_text='The main title displayed on the homepage.')
    description = models.TextField(blank=True, help_text='Optional description for the site.')
    allow_registration = models.BooleanField(
        default=True, 
        help_text='Allow new users to register. Uncheck to disable public registration.'
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.title
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='Category name.')
    description = models.TextField(blank=True, help_text='Optional description.')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', help_text='User who created this category.')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=100, help_text='Name of the album.')
    description = models.TextField(blank=True, help_text='Optional description of the album.')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_albums', help_text='User who owns this album.')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='albums', help_text='Optional category for this album.')
    viewers = models.ManyToManyField(User, related_name='viewable_albums', blank=True, help_text='Users who can view this album.')
    is_public = models.BooleanField(default=False, verbose_name='Is Public', help_text='If true, album is visible to all users.')
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='album_covers/', null=True, blank=True, help_text='Optional cover image for the album.')

    class Meta:
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_public']),
            models.Index(fields=['created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title


class AlbumShareLink(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='share_links', help_text='Album being shared.')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_share_links', help_text='User who created this share link.')
    share_token = models.CharField(max_length=64, unique=True, db_index=True, help_text='Unique token for the share link.')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='When this share link expires.')
    is_active = models.BooleanField(default=True, help_text='Whether this share link is active.')
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0, help_text='Number of times this link has been accessed.')

    class Meta:
        verbose_name = 'Album Share Link'
        verbose_name_plural = 'Album Share Links'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Share link for {self.album.title}"

    def is_expired(self):
        """Check if the share link has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def can_access(self):
        """Check if this share link can be used to access the album."""
        return self.is_active and not self.is_expired()


class Media(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='%(class)ss', null=True, blank=True, help_text='Album this media belongs to.')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)ss', help_text='Optional category.')
    title = models.CharField(max_length=100, help_text='Title of the media.')
    description = models.TextField(blank=True, help_text='Optional description of the media.')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width = models.PositiveIntegerField(null=True, blank=True, help_text='Media width in pixels.')
    height = models.PositiveIntegerField(null=True, blank=True, help_text='Media height in pixels.')
    checksum = models.CharField(max_length=32, blank=True, null=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['album']),
            models.Index(fields=['category']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['title']),
            models.Index(fields=['checksum']),
        ]

    def __str__(self):
        return self.title


class Photo(Media):
    image = models.ImageField(upload_to='photos/', help_text='Upload the photo file.')
    # Tagging and custom albums
    tags = models.ManyToManyField('Tag', related_name='photos', blank=True)
    custom_albums = models.ManyToManyField('CustomAlbum', related_name='photos', blank=True)
    # Optimized versions
    thumbnail = ImageSpecField(source='image', processors=[Transpose(), ResizeToFit(300, 300)], format='JPEG', options={'quality': 95})
    thumbnail_2x = ImageSpecField(source='image', processors=[Transpose(), ResizeToFit(600, 600)], format='JPEG', options={'quality': 95})
    medium = ImageSpecField(source='image', processors=[Transpose(), ResizeToFit(800, 600)], format='JPEG', options={'quality': 90})
    large = ImageSpecField(source='image', processors=[Transpose(), ResizeToFit(1200, 900)], format='JPEG', options={'quality': 90})
    optimized = ImageSpecField(source='image', processors=[Transpose(), ResizeToFit(1200, 900)], format='JPEG', options={'quality': 90})
    # Metadata fields
    date_taken = models.DateTimeField(null=True, blank=True, help_text='Date and time the photo was taken.')
    camera_make = models.CharField(max_length=100, null=True, blank=True, help_text='Camera make.')
    camera_model = models.CharField(max_length=100, null=True, blank=True, help_text='Camera model.')
    latitude = models.FloatField(null=True, blank=True, help_text='GPS latitude.')
    longitude = models.FloatField(null=True, blank=True, help_text='GPS longitude.')
    
    # AI fields
    ai_description = models.TextField(blank=True, help_text="AI-generated description")
    ai_tags = models.JSONField(default=list, blank=True, help_text="AI-generated tags")
    ai_confidence_score = models.FloatField(default=0.0, help_text="AI prediction confidence")
    text_embedding = VectorField(dimensions=384, null=True, blank=True)
    nsfw_score = models.FloatField(default=0.0, help_text="NSFW detection score")
    is_safe_content = models.BooleanField(default=True)
    ai_processed = models.BooleanField(default=False)
    ai_processing_date = models.DateTimeField(null=True, blank=True)
    ai_processing_error = models.TextField(blank=True)
    perceptual_hash = models.CharField(max_length=64, blank=True, db_index=True)
    
    # Processing status for background tasks
    class ProcessingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        help_text="Status of AI processing"
    )
    
    embedding = VectorField(dimensions=512, null=True, blank=True)  # Keep existing field

    @property
    def media_type(self):
        return "Photo"

    def get_absolute_url(self):
        """Return the URL for this photo's detail view."""
        from django.urls import reverse
        return reverse('album:photo_detail', kwargs={'pk': self.pk})

    class Meta(Media.Meta):
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        indexes = Media.Meta.indexes + [
            models.Index(fields=['date_taken']),
        ]


class Video(Media):
    video = models.FileField(upload_to='videos/', help_text='Upload the video file.')
    # Tagging and custom albums
    tags = models.ManyToManyField('Tag', related_name='videos', blank=True)
    custom_albums = models.ManyToManyField('CustomAlbum', related_name='videos', blank=True)
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True, help_text='Video thumbnail image.')
    date_recorded = models.DateTimeField(null=True, blank=True, help_text='Date and time the video was recorded.')
    # Metadata fields
    duration = models.FloatField(null=True, blank=True, help_text='Video duration in seconds.')
    codec = models.CharField(max_length=50, null=True, blank=True, help_text='Video codec.')
    
    # AI fields
    ai_description = models.TextField(blank=True)
    ai_tags = models.JSONField(default=list, blank=True)
    ai_confidence_score = models.FloatField(default=0.0)
    thumbnail_embedding = VectorField(dimensions=512, null=True, blank=True)
    text_embedding = VectorField(dimensions=384, null=True, blank=True)
    nsfw_score = models.FloatField(default=0.0)
    is_safe_content = models.BooleanField(default=True)
    ai_processed = models.BooleanField(default=False)
    ai_processing_date = models.DateTimeField(null=True, blank=True)
    ai_processing_error = models.TextField(blank=True)
    
    # Processing status for background tasks
    class ProcessingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        help_text="Status of AI processing"
    )

    @property
    def media_type(self):
        return "Video"

    def get_absolute_url(self):
        """Return the URL for this video's detail view."""
        from django.urls import reverse
        return reverse('album:video_detail', kwargs={'pk': self.pk})

    class Meta(Media.Meta):
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        indexes = Media.Meta.indexes + [
            models.Index(fields=['date_recorded']),
        ]


class Favorite(models.Model):
    """Model to track user's favorite photos"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='favorited_by')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'photo')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ['-created']

    def __str__(self):
        return f"{self.user.username} - {self.photo.title}"


class AIProcessingSettings(models.Model):
    """Singleton model for AI processing configuration"""
    auto_process_on_upload = models.BooleanField(
        default=False,
        help_text="[FUTURE FEATURE] Automatically process photos/videos with AI when uploaded. Currently disabled - use scheduled processing or manual processing instead."
    )
    scheduled_processing = models.BooleanField(
        default=True,
        help_text="Enable scheduled batch processing of pending items"
    )
    batch_size = models.IntegerField(
        default=500,
        help_text="Maximum number of items to process per scheduled run"
    )
    processing_timeout = models.IntegerField(
        default=30,
        help_text="Timeout in seconds for processing each item"
    )
    schedule_hour = models.IntegerField(
        default=2,
        help_text="Hour of the day (0-23) to run scheduled processing"
    )
    schedule_minute = models.IntegerField(
        default=0,
        help_text="Minute of the hour (0-59) to run scheduled processing"
    )
    album_admin_processing_limit = models.IntegerField(
        default=50,
        help_text="Maximum number of photos an album admin can process in one batch (site admins have no limit)"
    )
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'AI Processing Settings'
        verbose_name_plural = 'AI Processing Settings'
    
    def __str__(self):
        return "AI Processing Settings"
    
    def clean(self):
        """Validate field values"""
        from django.core.exceptions import ValidationError
        
        if self.schedule_hour < 0 or self.schedule_hour > 23:
            raise ValidationError({'schedule_hour': 'Hour must be between 0 and 23'})
        
        if self.schedule_minute < 0 or self.schedule_minute > 59:
            raise ValidationError({'schedule_minute': 'Minute must be between 0 and 59'})
        
        if self.batch_size < 1:
            raise ValidationError({'batch_size': 'Batch size must be at least 1'})
        
        if self.processing_timeout < 1:
            raise ValidationError({'processing_timeout': 'Timeout must be at least 1 second'})
        
        if self.album_admin_processing_limit < 1:
            raise ValidationError({'album_admin_processing_limit': 'Album admin limit must be at least 1'})
    
    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """Get or create the singleton settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class UserProfile(models.Model):
    """Extended user profile to track terms acceptance and other user metadata."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    terms_accepted = models.BooleanField(default=False, help_text='User has accepted Terms of Conduct')
    terms_accepted_date = models.DateTimeField(null=True, blank=True, help_text='Date when user accepted terms')
    terms_accepted_ip = models.GenericIPAddressField(null=True, blank=True, help_text='IP address when terms were accepted')
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

