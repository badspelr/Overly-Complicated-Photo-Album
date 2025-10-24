"""
Analytics service for tracking user engagement and media statistics.
"""
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from ..models import Photo, Video, Album, Category
from django.contrib.auth.models import User


class AnalyticsService:
    """Service for generating analytics and statistics."""

    @staticmethod
    def get_user_stats(user, days=30):
        """Get comprehensive stats for a user."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Album stats
        albums = Album.objects.filter(owner=user)
        total_albums = albums.count()
        public_albums = albums.filter(is_public=True).count()
        private_albums = total_albums - public_albums

        # Media stats
        photos = Photo.objects.filter(album__owner=user)
        videos = Video.objects.filter(album__owner=user)

        total_photos = photos.count()
        total_videos = videos.count()
        total_media = total_photos + total_videos

        # Recent uploads
        recent_photos = photos.filter(uploaded_at__gte=start_date).count()
        recent_videos = videos.filter(uploaded_at__gte=start_date).count()
        recent_uploads = recent_photos + recent_videos

        # Storage usage (approximate)
        photo_storage = photos.aggregate(
            total_size=Sum('image__size')
        )['total_size'] or 0

        video_storage = videos.aggregate(
            total_size=Sum('video__size')
        )['total_size'] or 0

        total_storage = photo_storage + video_storage

        # Viewer stats
        total_viewers = albums.aggregate(
            total_viewers=Count('viewers', distinct=True)
        )['total_viewers'] or 0

        return {
            'albums': {
                'total': total_albums,
                'public': public_albums,
                'private': private_albums
            },
            'media': {
                'total_photos': total_photos,
                'total_videos': total_videos,
                'total_media': total_media,
                'recent_uploads': recent_uploads
            },
            'storage': {
                'photo_storage_mb': round(photo_storage / (1024 * 1024), 2),
                'video_storage_mb': round(video_storage / (1024 * 1024), 2),
                'total_storage_mb': round(total_storage / (1024 * 1024), 2)
            },
            'engagement': {
                'total_viewers': total_viewers,
                'avg_media_per_album': round(total_media / total_albums, 1) if total_albums > 0 else 0
            }
        }

    @staticmethod
    def get_popular_content(user, limit=10):
        """Get most popular content for a user."""
        # Most viewed albums (by viewer count)
        popular_albums = Album.objects.filter(owner=user).annotate(
            viewer_count=Count('viewers')
        ).order_by('-viewer_count', '-created_at')[:limit]

        # Most uploaded to albums
        active_albums = Album.objects.filter(owner=user).annotate(
            media_count=Count('photos') + Count('videos')
        ).order_by('-media_count', '-created_at')[:limit]

        # Popular categories
        popular_categories = Category.objects.filter(
            Q(photos__album__owner=user) | Q(videos__album__owner=user)
        ).annotate(
            media_count=Count('photos') + Count('videos')
        ).order_by('-media_count')[:limit]

        return {
            'popular_albums': popular_albums,
            'active_albums': active_albums,
            'popular_categories': popular_categories
        }

    @staticmethod
    def get_upload_trends(user, days=30):
        """Get upload trends over time."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Daily upload counts
        daily_uploads = []
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            photos_count = Photo.objects.filter(
                album__owner=user,
                uploaded_at__gte=current_date,
                uploaded_at__lt=next_date
            ).count()

            videos_count = Video.objects.filter(
                album__owner=user,
                uploaded_at__gte=current_date,
                uploaded_at__lt=next_date
            ).count()

            daily_uploads.append({
                'date': current_date.date(),
                'photos': photos_count,
                'videos': videos_count,
                'total': photos_count + videos_count
            })

            current_date = next_date

        return daily_uploads

    @staticmethod
    def get_system_stats():
        """Get system-wide statistics (admin only)."""
        total_users = User.objects.count()
        total_albums = Album.objects.count()
        total_photos = Photo.objects.count()
        total_videos = Video.objects.count()

        public_albums = Album.objects.filter(is_public=True).count()
        private_albums = total_albums - public_albums

        # Storage stats
        total_photo_storage = Photo.objects.aggregate(
            total=Sum('image__size')
        )['total'] or 0

        total_video_storage = Video.objects.aggregate(
            total=Sum('video__size')
        )['total'] or 0

        total_storage = total_photo_storage + total_video_storage

        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_users = User.objects.filter(date_joined__gte=week_ago).count()
        recent_albums = Album.objects.filter(created_at__gte=week_ago).count()
        recent_photos = Photo.objects.filter(uploaded_at__gte=week_ago).count()
        recent_videos = Video.objects.filter(uploaded_at__gte=week_ago).count()

        return {
            'users': {
                'total': total_users,
                'recent': recent_users
            },
            'content': {
                'total_albums': total_albums,
                'total_photos': total_photos,
                'total_videos': total_videos,
                'total_media': total_photos + total_videos,
                'public_albums': public_albums,
                'private_albums': private_albums,
                'recent_albums': recent_albums,
                'recent_photos': recent_photos,
                'recent_videos': recent_videos
            },
            'storage': {
                'photo_storage_gb': round(total_photo_storage / (1024**3), 2),
                'video_storage_gb': round(total_video_storage / (1024**3), 2),
                'total_storage_gb': round(total_storage / (1024**3), 2)
            }
        }

    @staticmethod
    def get_media_insights(user):
        """Get insights about user's media."""
        photos = Photo.objects.filter(album__owner=user)
        videos = Video.objects.filter(album__owner=user)

        # File format distribution
        photo_formats = photos.values('image').annotate(
            count=Count('id')
        ).order_by('-count')

        video_formats = videos.values('video').annotate(
            count=Count('id')
        ).order_by('-count')

        # Upload time patterns
        upload_hours = photos.values('uploaded_at__hour').annotate(
            count=Count('id')
        ).order_by('uploaded_at__hour')

        # Average file sizes
        avg_photo_size = photos.aggregate(avg=Avg('image__size'))['avg'] or 0
        avg_video_size = videos.aggregate(avg=Avg('video__size'))['avg'] or 0

        return {
            'formats': {
                'photos': list(photo_formats),
                'videos': list(video_formats)
            },
            'upload_patterns': list(upload_hours),
            'average_sizes': {
                'photo_mb': round(avg_photo_size / (1024 * 1024), 2),
                'video_mb': round(avg_video_size / (1024 * 1024), 2)
            }
        }
