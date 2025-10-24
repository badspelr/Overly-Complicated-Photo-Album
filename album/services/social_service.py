"""
Social features for media interaction.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Photo, Video


class Like(models.Model):
    """Like model for photos and videos."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [
            ('user', 'photo'),
            ('user', 'video')
        ]
        indexes = [
            models.Index(fields=['user', 'photo']),
            models.Index(fields=['user', 'video']),
        ]

    def __str__(self):
        media_type = 'photo' if self.photo else 'video'
        media = self.photo or self.video
        return f"{self.user.username} liked {media_type}: {media.title}"


class Comment(models.Model):
    """Comment model for photos and videos."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['photo', 'created_at']),
            models.Index(fields=['video', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]

    def __str__(self):
        media_type = 'photo' if self.photo else 'video'
        media = self.photo or self.video
        return f"Comment by {self.user.username} on {media_type}: {media.title}"

    @property
    def is_reply(self):
        return self.parent is not None

    def get_replies(self):
        """Get all direct replies to this comment."""
        return Comment.objects.filter(parent=self).order_by('created_at')


class Favorite(models.Model):
    """Favorite model for bookmarking media."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [
            ('user', 'photo'),
            ('user', 'video')
        ]
        indexes = [
            models.Index(fields=['user', 'photo']),
            models.Index(fields=['user', 'video']),
        ]

    def __str__(self):
        media_type = 'photo' if self.photo else 'video'
        media = self.photo or self.video
        return f"{self.user.username} favorited {media_type}: {media.title}"


class SocialService:
    """Service for handling social interactions."""

    @staticmethod
    def toggle_like(user, photo=None, video=None):
        """Toggle like on a photo or video."""
        if photo:
            like, created = Like.objects.get_or_create(
                user=user, photo=photo,
                defaults={'video': None}
            )
        elif video:
            like, created = Like.objects.get_or_create(
                user=user, video=video,
                defaults={'photo': None}
            )
        else:
            raise ValueError("Must provide either photo or video")

        if not created:
            like.delete()
            return False  # Unliked
        return True  # Liked

    @staticmethod
    def add_comment(user, text, photo=None, video=None, parent=None):
        """Add a comment to a photo or video."""
        if not text.strip():
            raise ValueError("Comment text cannot be empty")

        if parent and ((photo and parent.photo != photo) or (video and parent.video != video)):
            raise ValueError("Parent comment must belong to the same media")

        comment = Comment.objects.create(
            user=user,
            photo=photo,
            video=video,
            text=text.strip(),
            parent=parent
        )
        return comment

    @staticmethod
    def toggle_favorite(user, photo=None, video=None):
        """Toggle favorite on a photo or video."""
        if photo:
            favorite, created = Favorite.objects.get_or_create(
                user=user, photo=photo,
                defaults={'video': None}
            )
        elif video:
            favorite, created = Favorite.objects.get_or_create(
                user=user, video=video,
                defaults={'photo': None}
            )
        else:
            raise ValueError("Must provide either photo or video")

        if not created:
            favorite.delete()
            return False  # Unfavorited
        return True  # Favorited

    @staticmethod
    def get_media_stats(photo=None, video=None):
        """Get social stats for a photo or video."""
        if photo:
            likes_count = Like.objects.filter(photo=photo).count()
            comments_count = Comment.objects.filter(photo=photo, parent=None).count()
            favorites_count = Favorite.objects.filter(photo=photo).count()
        elif video:
            likes_count = Like.objects.filter(video=video).count()
            comments_count = Comment.objects.filter(video=video, parent=None).count()
            favorites_count = Favorite.objects.filter(video=video).count()
        else:
            raise ValueError("Must provide either photo or video")

        return {
            'likes': likes_count,
            'comments': comments_count,
            'favorites': favorites_count
        }

    @staticmethod
    def get_user_activity(user, limit=20):
        """Get recent social activity for a user."""
        recent_likes = Like.objects.filter(user=user).select_related(
            'photo', 'video', 'photo__album', 'video__album'
        ).order_by('-created_at')[:limit//3]

        recent_comments = Comment.objects.filter(user=user).select_related(
            'photo', 'video', 'photo__album', 'video__album'
        ).order_by('-created_at')[:limit//3]

        recent_favorites = Favorite.objects.filter(user=user).select_related(
            'photo', 'video', 'photo__album', 'video__album'
        ).order_by('-created_at')[:limit//3]

        activity = []
        for like in recent_likes:
            activity.append({
                'type': 'like',
                'object': like,
                'timestamp': like.created_at
            })

        for comment in recent_comments:
            activity.append({
                'type': 'comment',
                'object': comment,
                'timestamp': comment.created_at
            })

        for favorite in recent_favorites:
            activity.append({
                'type': 'favorite',
                'object': favorite,
                'timestamp': favorite.created_at
            })

        # Sort by timestamp
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        return activity[:limit]
