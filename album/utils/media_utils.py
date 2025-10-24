"""
Utility functions for media operations used across views.
"""
import logging
import os
from typing import List, Dict, Any, Tuple
from django.db.models import QuerySet
from django.core.paginator import Paginator, Page
from django.http import HttpRequest
from django.core.files.base import ContentFile
from PIL import Image
import moviepy.editor as mp
from ..models import Video

logger = logging.getLogger(__name__)


class MediaQueryUtils:
    """Utility class for common media query operations."""
    
    @staticmethod
    def get_sort_config(request: HttpRequest) -> Tuple[str, str]:
        """
        Extract and validate sort configuration from request.
        
        Returns:
            Tuple of (sort_field, sort_direction)
        """
        sort_by = request.GET.get('sort', 'uploaded_at')
        direction = request.GET.get('direction', 'desc')
        
        # Validate sort field
        valid_sort_fields = {
            'uploaded_at', 'date_taken', 'date_recorded', 'title', 
            'width', 'height', 'duration', 'file_size'
        }
        
        if sort_by not in valid_sort_fields:
            sort_by = 'uploaded_at'
            
        # Validate direction
        if direction not in ['asc', 'desc']:
            direction = 'desc'
            
        return sort_by, direction
    
    @staticmethod
    def filter_media_by_type(media_type: str, photos: QuerySet, videos: QuerySet) -> QuerySet:
        """
        Filter media by type.
        
        Args:
            media_type: 'all', 'photos', or 'videos'
            photos: Photo queryset
            videos: Video queryset
            
        Returns:
            Combined queryset of filtered media
        """
        if media_type == 'photos':
            return photos
        elif media_type == 'videos':
            return videos
        else:  # 'all'
            return MediaQueryUtils._combine_media_querysets(photos, videos)
    
    @staticmethod
    def _combine_media_querysets(photos: QuerySet, videos: QuerySet) -> List:
        """Combine photo and video querysets into a single list."""
        combined = []
        combined.extend(photos)
        combined.extend(videos)
        return combined
    
    @staticmethod
    def sort_combined_media(media_list: List, sort_field: str, direction: str) -> List:
        """
        Sort combined media list by field and direction.
        
        Args:
            media_list: List of Photo/Video objects
            sort_field: Field to sort by
            direction: 'asc' or 'desc'
            
        Returns:
            Sorted list of media objects
        """
        reverse = direction == 'desc'
        
        def get_sort_value(obj):
            """Get the value to sort by for a media object."""
            # Handle field mapping for different media types
            actual_field = sort_field
            if sort_field == 'date_taken':
                # Use date_recorded for videos, date_taken for photos
                if hasattr(obj, 'date_recorded'):  # Video object
                    actual_field = 'date_recorded'
                elif hasattr(obj, 'date_taken'):  # Photo object
                    actual_field = 'date_taken'
                else:
                    actual_field = 'uploaded_at'  # Fallback
            
            if hasattr(obj, actual_field):
                value = getattr(obj, actual_field)
                # Handle None values by putting them at the end
                return (value is None, value)
            else:
                # Fallback for objects that don't have the sort field
                return (True, '')
        
        try:
            return sorted(media_list, key=get_sort_value, reverse=reverse)
        except Exception as e:
            logger.warning(f"Error sorting media: {e}")
            return media_list
    
    @staticmethod
    def paginate_media(media_list: List, page_number: int, per_page: int) -> Tuple[Page, Dict[str, Any]]:
        """
        Paginate media list and return pagination context.
        
        Returns:
            Tuple of (page_object, pagination_context)
        """
        paginator = Paginator(media_list, per_page)
        page_obj = paginator.get_page(page_number)
        
        # Calculate display page numbers
        current_page = page_obj.number
        total_pages = paginator.num_pages
        
        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)
        
        if end_page - start_page < 4:
            if start_page == 1:
                end_page = min(total_pages, start_page + 4)
            elif end_page == total_pages:
                start_page = max(1, end_page - 4)
        
        page_numbers = list(range(start_page, end_page + 1))
        
        pagination_context = {
            'page_obj': page_obj,
            'page_numbers': page_numbers,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        }
        
        return page_obj, pagination_context


class MediaDisplayUtils:
    """Utility class for media display operations."""
    
    @staticmethod
    def get_page_size_options() -> List[int]:
        """Get available page size options for display."""
        return [10, 20, 50, 100]
    
    @staticmethod
    def get_sort_options() -> List[Tuple[str, str]]:
        """Get available sort options for display."""
        return [
            ('uploaded_at', 'Date Added'),
            ('date_taken', 'Date Taken/Recorded'),  # Unified field for both photos and videos
            ('title', 'Title'),
            ('width', 'Width'),
            ('height', 'Height'),
            ('duration', 'Duration'),
            ('file_size', 'File Size'),
        ]
    
    @staticmethod
    def get_media_type_options() -> List[Tuple[str, str]]:
        """Get available media type filter options."""
        return [
            ('all', 'All Media'),
            ('photos', 'Photos Only'),
            ('videos', 'Videos Only'),
        ]


# Convenience functions for backward compatibility
def get_sort_config(request):
    """Extract and validate sort configuration from request."""
    return MediaQueryUtils.get_sort_config(request)


def filter_media_by_type(media_type, photos, videos):
    """Filter media by type."""
    return MediaQueryUtils.filter_media_by_type(media_type, photos, videos)


def sort_combined_media(media_list, sort_field, direction):
    """Sort combined media list."""
    return MediaQueryUtils.sort_combined_media(media_list, sort_field, direction)


def paginate_media(media_list, page_number, per_page):
    """Paginate media list."""
    return MediaQueryUtils.paginate_media(media_list, page_number, per_page)


class VideoThumbnailGenerator:
    """Utility class for generating video thumbnails."""
    
    @staticmethod
    def generate_thumbnail(video_path: str, thumbnail_path: str, time: float = 1.0, size: Tuple[int, int] = (320, 240)) -> bool:
        """
        Generate a thumbnail from a video file.
        
        Args:
            video_path: Path to the video file
            thumbnail_path: Path where to save the thumbnail
            time: Time in seconds to extract frame from (default: 1.0)
            size: Size of the thumbnail (width, height)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the video clip
            clip = mp.VideoFileClip(video_path)
            
            # Get frame at specified time
            frame = clip.get_frame(time)
            
            # Convert to PIL Image
            img = Image.fromarray(frame)
            
            # Resize to thumbnail size
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save the thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            # Close the clip
            clip.close()
            
            logger.info(f"Generated thumbnail for video: {video_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating thumbnail for {video_path}: {e}")
            return False
    
    @staticmethod
    def generate_video_thumbnail(video_instance: Video) -> bool:
        """
        Generate thumbnail for a Video model instance.

        Args:
            video_instance: Video model instance

        Returns:
            True if successful, False otherwise
        """
        if not video_instance.video:
            logger.warning(f"No video file for video {video_instance.id}")
            return False

        try:
            # Get video file path
            video_path = video_instance.video.path

            # Create thumbnail filename
            video_filename = os.path.basename(video_instance.video.name)
            thumbnail_filename = f"{os.path.splitext(video_filename)[0]}_thumb.jpg"

            # Generate thumbnail in memory
            clip = mp.VideoFileClip(video_path)

            # Use a time within the video duration (prefer 1 second, but use half duration if shorter)
            duration = clip.duration
            frame_time = min(1.0, duration / 2) if duration > 0 else 0.0

            frame = clip.get_frame(frame_time)
            img = Image.fromarray(frame)
            img.thumbnail((320, 240), Image.Resampling.LANCZOS)

            # Save to Django's storage
            from io import BytesIO
            thumb_io = BytesIO()
            img.save(thumb_io, 'JPEG', quality=85)
            thumb_io.seek(0)

            # Save to model
            video_instance.thumbnail.save(thumbnail_filename, ContentFile(thumb_io.getvalue()), save=True)

            clip.close()

            logger.info(f"Generated thumbnail for video {video_instance.id}: {video_instance.title}")
            return True

        except Exception as e:
            logger.error(f"Error generating thumbnail for video {video_instance.id}: {e}")
            return False
