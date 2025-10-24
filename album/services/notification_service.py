"""
Notification system for user interactions.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from ..models import Album, Photo, Video


class Notification(models.Model):
    """Notification model for user activities."""

    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('favorite', 'Favorite'),
        ('share', 'Share'),
        ('mention', 'Mention'),
        ('follow', 'Follow'),
        ('album_shared', 'Album Shared'),
        ('photo_uploaded', 'Photo Uploaded'),
        ('video_uploaded', 'Video Uploaded'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Related objects
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

    def get_absolute_url(self):
        """Get URL to view the related content."""
        if self.photo:
            return reverse('photo_detail', kwargs={'pk': self.photo.pk})
        elif self.video:
            return reverse('video_detail', kwargs={'pk': self.video.pk})
        elif self.album:
            return reverse('album_detail', kwargs={'pk': self.album.pk})
        return None

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


class NotificationService:
    """Service for managing notifications."""

    @staticmethod
    def create_notification(recipient, sender, notification_type, title, message,
                          album=None, photo=None, video=None):
        """Create a new notification."""
        if recipient == sender:
            return None  # Don't notify users about their own actions

        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            album=album,
            photo=photo,
            video=video
        )
        return notification

    @staticmethod
    def notify_like(recipient, sender, photo=None, video=None):
        """Notify when someone likes media."""
        media_type = 'photo' if photo else 'video'
        media = photo or video
        title = f"{sender.username} liked your {media_type}"
        message = f"{sender.username} liked your {media_type}: {media.title}"

        return NotificationService.create_notification(
            recipient, sender, 'like', title, message,
            photo=photo, video=video
        )

    @staticmethod
    def notify_comment(recipient, sender, photo=None, video=None, comment_text=None):
        """Notify when someone comments on media."""
        media_type = 'photo' if photo else 'video'
        media = photo or video
        title = f"{sender.username} commented on your {media_type}"
        message = f"{sender.username} commented: {comment_text[:100]}{'...' if comment_text and len(comment_text) > 100 else ''}"

        return NotificationService.create_notification(
            recipient, sender, 'comment', title, message,
            photo=photo, video=video
        )

    @staticmethod
    def notify_album_shared(recipient, sender, album):
        """Notify when album is shared."""
        title = f"{sender.username} shared an album with you"
        message = f"{sender.username} shared the album '{album.title}' with you"

        return NotificationService.create_notification(
            recipient, sender, 'album_shared', title, message,
            album=album
        )

    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for user."""
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @staticmethod
    def mark_all_read(user):
        """Mark all notifications as read for user."""
        return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)

    @staticmethod
    def get_recent_notifications(user, limit=20):
        """Get recent notifications for user."""
        return Notification.objects.filter(recipient=user).select_related(
            'sender', 'album', 'photo', 'video'
        )[:limit]

    @staticmethod
    def cleanup_old_notifications(days=30):
        """Delete notifications older than specified days."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        return Notification.objects.filter(created_at__lt=cutoff_date).delete()
