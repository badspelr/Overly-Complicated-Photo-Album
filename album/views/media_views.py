"""
Media-related views for photos and videos.
"""
import logging
import hashlib
import os
import zipfile
import mimetypes
from io import BytesIO
from urllib.parse import quote
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from PIL import Image, ExifTags
from moviepy.editor import VideoFileClip
from ..models import Photo, Video, Album, Category, Favorite
from ..forms import PhotoForm
from ..security import ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES, validate_file_type, validate_image_file, validate_video_file
from ..services.media_service import MediaService
from .base_views import AlbumListPermissionMixin, AlbumDetailPermissionMixin, check_object_permission, get_delete_context, log_user_action, log_security_event

logger = logging.getLogger(__name__)

def is_album_admin(user, album):
    return user.is_superuser or album.owner == user or user in album.viewers.all()


@login_required
def photo_edit(request, pk):
    """Edit photo metadata, tags, and custom albums for album admins."""
    photo = get_object_or_404(Photo, pk=pk)
    album = photo.album
    
    # Check permissions - user must be album admin (owner, viewer, or superuser)
    if not is_album_admin(request.user, album):
        messages.error(request, 'You do not have permission to edit this photo.')
        return redirect('album:dashboard')

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Photo updated successfully.')
            return redirect('album:photo_detail', pk=photo.pk)
    else:
        form = PhotoForm(instance=photo, user=request.user)

    return render(request, 'album/photo_edit.html', {'form': form, 'photo': photo})


# New: Photo upload view using the new PhotoForm
@login_required
def photo_upload(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            photo = form.save()
            
            # Queue AI processing if enabled
            from django.conf import settings
            if settings.AI_AUTO_PROCESS_ON_UPLOAD:
                from album.tasks import process_media_on_upload
                process_media_on_upload.delay('photo', photo.id)
                messages.success(request, 'Photo uploaded successfully. AI processing queued.')
            else:
                messages.success(request, 'Photo uploaded successfully.')
            
            return redirect('album:photo_detail', pk=photo.pk)
    else:
        form = PhotoForm(user=request.user)
    return render(request, 'album/photo_upload.html', {'form': form})

class MediaMetadataExtractor:
    """Utility class for extracting metadata from media files."""
    
    @staticmethod
    def extract_photo_metadata(photo):
        """Extract metadata from uploaded photo (orientation already corrected during upload)."""
        try:
            with Image.open(photo.image.path) as img:
                # Get dimensions (should already be set, but ensure accuracy)
                photo.width, photo.height = img.size
                
                # Extract EXIF data for other metadata (camera info, GPS, etc.)
                exif_data = img._getexif()
                if exif_data:
                    MediaMetadataExtractor._parse_exif_data(photo, exif_data)
                
                photo.save()
        except Exception as e:
            logger.warning(f"Error extracting photo metadata: {e}")

    @staticmethod
    def _parse_exif_data(photo, exif_data):
        """Parse EXIF data and update photo object."""
        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == 'DateTime':
                MediaMetadataExtractor._parse_datetime(photo, value)
            elif tag_name == 'Make':
                photo.camera_make = value
            elif tag_name == 'Model':
                photo.camera_model = value
            elif tag_name == 'GPSInfo':
                MediaMetadataExtractor._parse_gps_info(photo, value)

    @staticmethod
    def _parse_datetime(photo, value):
        """Parse datetime from EXIF."""
        from datetime import datetime
        try:
            photo.date_taken = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        except ValueError as e:
            logger.warning(f"Invalid DateTime format in EXIF: {value} ({e})")

    @staticmethod
    def _parse_gps_info(photo, gps_value):
        """Parse GPS information from EXIF."""
        try:
            gps_info = {}
            for t in gps_value:
                sub_tag = ExifTags.GPSTAGS.get(t, t)
                gps_info[sub_tag] = gps_value[t]
            
            if all(key in gps_info for key in ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']):
                lat_ref = gps_info['GPSLatitudeRef']
                lon_ref = gps_info['GPSLongitudeRef']
                lat = gps_info['GPSLatitude']
                lon = gps_info['GPSLongitude']
                
                lat_deg = MediaMetadataExtractor._convert_gps_to_decimal(lat)
                lon_deg = MediaMetadataExtractor._convert_gps_to_decimal(lon)
                
                if lat_ref == 'S':
                    lat_deg = -lat_deg
                if lon_ref == 'W':
                    lon_deg = -lon_deg
                
                photo.latitude = lat_deg
                photo.longitude = lon_deg
        except Exception as e:
            logger.warning(f"Error parsing GPSInfo in EXIF: {e}")

    @staticmethod
    def _convert_gps_to_decimal(gps_coord):
        """Convert GPS coordinate to decimal degrees."""
        return gps_coord[0][0] / gps_coord[0][1] + \
           gps_coord[1][0] / gps_coord[1][1] / 60 + \
           gps_coord[2][0] / gps_coord[2][1] / 3600

    @staticmethod
    def extract_video_metadata(video):
        """Extract metadata from uploaded video."""
        try:
            clip = VideoFileClip(video.video.path)
            video.duration = clip.duration
            video.width, video.height = clip.size

            from datetime import datetime
            file_creation_time = os.path.getctime(video.video.path)
            video.date_recorded = datetime.fromtimestamp(file_creation_time)

            if hasattr(clip, 'reader') and hasattr(clip.reader, 'infos'):
                infos = clip.reader.infos
                if 'creation_time' in infos:
                    creation_time = infos['creation_time']
                    if isinstance(creation_time, str):
                        try:
                            video.date_recorded = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
                        except ValueError as e:
                            logger.warning(f"Invalid creation_time format in video metadata: {creation_time} ({e})")

            video.save()
        except Exception as e:
            logger.warning(f"Error extracting video metadata: {e}")

# Convenience functions for backward compatibility
def extract_photo_metadata(photo):
    """Extract metadata from uploaded photo."""
    MediaMetadataExtractor.extract_photo_metadata(photo)

def extract_video_metadata(video):
    """Extract metadata from uploaded video."""
    MediaMetadataExtractor.extract_video_metadata(video)

@method_decorator(login_required, name='dispatch')
class PhotoListView(AlbumListPermissionMixin, LoginRequiredMixin, ListView):
    """List view for photos."""
    model = Photo
    template_name = 'album/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('album', 'category').order_by('-uploaded_at')

@method_decorator(login_required, name='dispatch')
class PhotoDetailView(AlbumDetailPermissionMixin, LoginRequiredMixin, DetailView):
    """Detail view for individual photos."""
    model = Photo
    template_name = 'album/photo_detail.html'
    
    def get_queryset(self):
        return super().get_queryset().select_related('album', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = self.get_object()
        
        # Parse parameters from return_url to maintain search/filter context
        return_url = self.request.GET.get('return_url', '')
        search_params = {}
        sort = 'date_taken_desc'  # default
        
        if return_url:
            from urllib.parse import urlparse, parse_qs
            import urllib.parse
            decoded_return_url = urllib.parse.unquote(return_url)
            parsed_return_url = urlparse(decoded_return_url)
            return_url_params = parse_qs(parsed_return_url.query)
            
            # Extract search parameters
            search_params = {
                'query': return_url_params.get('q', [''])[0] or return_url_params.get('search', [''])[0],
                'search_type': return_url_params.get('search_type', ['text'])[0],
                'media_type': return_url_params.get('media_type', ['all'])[0],
                'album': return_url_params.get('album', [''])[0],
                'category': return_url_params.get('category', [''])[0],
                'date_from': return_url_params.get('date_from', [''])[0],
                'date_to': return_url_params.get('date_to', [''])[0],
            }
            sort = return_url_params.get('sort', ['date_taken_desc'])[0]
        else:
            # Fallback to direct parameters
            sort = self.request.GET.get('sort', 'date_taken_desc')
        
        # Determine if this is a search context (has search query or filters)
        is_search_context = (search_params.get('query') or 
                           search_params.get('album') or 
                           search_params.get('category') or
                           search_params.get('date_from') or 
                           search_params.get('date_to'))
        
        if is_search_context:
            # Apply search filtering (same logic as search_media view)
            photos_queryset = self._get_search_filtered_photos(search_params)
        else:
            # Standard album view - get photos from the current photo's album
            if photo.album:
                photos_queryset = photo.album.photos.all()
            else:
                photos_queryset = Photo.objects.none()
        
        # Apply sorting
        sort_field, direction = self._parse_sort_params(sort)
        photos_list = list(photos_queryset.order_by(f'-{sort_field}' if direction == 'desc' else sort_field))
        
        try:
            current_index = photos_list.index(photo)
            
            # Navigation based on position in the filtered/sorted list
            if current_index > 0:
                context['previous_photo'] = photos_list[current_index - 1]
            
            if current_index < len(photos_list) - 1:
                context['next_photo'] = photos_list[current_index + 1]
        except ValueError:
            # Photo not found in the list (shouldn't happen, but handle gracefully)
            pass
                
        # Pass through sort parameter to maintain it in navigation links
        context['sort'] = sort
        
        return context
    
    def _get_search_filtered_photos(self, search_params):
        """Apply search filters to get the same photo set as the search results."""
        from django.db.models import Q
        from ..services.embedding_service import generate_text_embedding
        from pgvector.django import CosineDistance
        
        query = search_params.get('query', '').strip()
        search_type = search_params.get('search_type', 'text')
        album_id = search_params.get('album', '')
        category_id = search_params.get('category', '')
        date_from = search_params.get('date_from', '')
        date_to = search_params.get('date_to', '')
        
        # Base queryset with permissions
        photos = Photo.objects.select_related('album', 'category').filter(
            Q(album__owner=self.request.user) | Q(album__viewers=self.request.user) | Q(album__is_public=True)
        )
        
        # Apply album filter
        if album_id and album_id != 'all':
            try:
                photos = photos.filter(album_id=int(album_id))
            except (ValueError, TypeError):
                pass
        
        # Apply category filter
        if category_id and category_id != 'all':
            try:
                photos = photos.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        
        # Apply date filters
        if date_from:
            from datetime import datetime
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                photos = photos.filter(date_taken__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            from datetime import datetime
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                photos = photos.filter(date_taken__lte=date_to_obj)
            except ValueError:
                pass
        
        # Apply search query
        if query:
            if search_type == 'ai':
                # Use hybrid approach: prioritize text-based search over embedding search
                text_results = photos.filter(
                    Q(ai_description__icontains=query) | 
                    Q(ai_tags__contains=[query])
                )
                
                if text_results.exists():
                    # If we have direct text matches in AI descriptions/tags, use those
                    photos = text_results
                else:
                    # Fall back to embedding search if no direct text matches
                    query_embedding = generate_text_embedding(query)
                    if query_embedding:
                        # Use a strict threshold for embedding search
                        similarity_threshold = 0.11
                        
                        photos = photos.annotate(
                            distance=CosineDistance('embedding', query_embedding)
                        ).filter(
                            distance__lt=similarity_threshold
                        ).order_by('distance')[:50]  # Limit to top 50 embedding matches
                    else:
                        photos = photos.none()
            else:
                # Standard text search
                photos = photos.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(album__title__icontains=query)
                )
        
        return photos
    
    def _parse_sort_params(self, sort):
        """Parse sort parameter and return field and direction."""
        sort_field = 'uploaded_at'
        direction = 'desc'
        
        if sort == 'date_newest':
            sort_field = 'uploaded_at'
            direction = 'desc'
        elif sort == 'date_oldest':
            sort_field = 'uploaded_at'
            direction = 'asc'
        elif sort == 'title_asc':
            sort_field = 'title'
            direction = 'asc'
        elif sort == 'title_desc':
            sort_field = 'title'
            direction = 'desc'
        elif sort == 'uploaded_at_desc':
            sort_field = 'uploaded_at'
            direction = 'desc'
        elif sort == 'uploaded_at_asc':
            sort_field = 'uploaded_at'
            direction = 'asc'
        elif sort == 'date_taken_desc':
            sort_field = 'date_taken'
            direction = 'desc'
        elif sort == 'date_taken_asc':
            sort_field = 'date_taken'
            direction = 'asc'
        
        return sort_field, direction

@method_decorator(login_required, name='dispatch')
class VideoListView(AlbumListPermissionMixin, LoginRequiredMixin, ListView):
    """List view for videos."""
    model = Video
    template_name = 'album/video_list.html'
    context_object_name = 'videos'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('album', 'category').order_by('-uploaded_at')

@method_decorator(login_required, name='dispatch')
class VideoDetailView(AlbumDetailPermissionMixin, LoginRequiredMixin, DetailView):
    """Detail view for individual videos."""
    model = Video
    template_name = 'album/video_detail.html'
    
    def get_queryset(self):
        return super().get_queryset().select_related('album', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        
        # Parse parameters from return_url to maintain search/filter context
        return_url = self.request.GET.get('return_url', '')
        search_params = {}
        sort = 'date_taken_desc'  # default
        
        if return_url:
            from urllib.parse import urlparse, parse_qs
            import urllib.parse
            decoded_return_url = urllib.parse.unquote(return_url)
            parsed_return_url = urlparse(decoded_return_url)
            return_url_params = parse_qs(parsed_return_url.query)
            
            # Extract search parameters
            search_params = {
                'query': return_url_params.get('q', [''])[0] or return_url_params.get('search', [''])[0],
                'search_type': return_url_params.get('search_type', ['text'])[0],
                'media_type': return_url_params.get('media_type', ['all'])[0],
                'album': return_url_params.get('album', [''])[0],
                'category': return_url_params.get('category', [''])[0],
                'date_from': return_url_params.get('date_from', [''])[0],
                'date_to': return_url_params.get('date_to', [''])[0],
            }
            sort = return_url_params.get('sort', ['date_taken_desc'])[0]
        else:
            # Fallback to direct parameters
            sort = self.request.GET.get('sort', 'date_taken_desc')
        
        # Determine if this is a search context (has search query or filters)
        is_search_context = (search_params.get('query') or 
                           search_params.get('album') or 
                           search_params.get('category') or
                           search_params.get('date_from') or 
                           search_params.get('date_to'))
        
        if is_search_context:
            # Apply search filtering (same logic as search_media view)
            videos_queryset = self._get_search_filtered_videos(search_params)
        else:
            # Standard album view - get videos from the current video's album
            if video.album:
                videos_queryset = video.album.videos.all()
            else:
                videos_queryset = Video.objects.none()
        
        # Apply sorting
        sort_field, direction = self._parse_sort_params_video(sort)
        videos_list = list(videos_queryset.order_by(f'-{sort_field}' if direction == 'desc' else sort_field))
        
        try:
            current_index = videos_list.index(video)
            
            # Navigation based on position in the filtered/sorted list
            if current_index > 0:
                context['previous_video'] = videos_list[current_index - 1]
            
            if current_index < len(videos_list) - 1:
                context['next_video'] = videos_list[current_index + 1]
        except ValueError:
            # Video not found in the list (shouldn't happen, but handle gracefully)
            pass
                
        # Pass through sort parameter to maintain it in navigation links
        context['sort'] = sort
        
        return context
    
    def _get_search_filtered_videos(self, search_params):
        """Apply search filters to get the same video set as the search results."""
        from django.db.models import Q
        
        query = search_params.get('query', '').strip()
        album_id = search_params.get('album', '')
        category_id = search_params.get('category', '')
        date_from = search_params.get('date_from', '')
        date_to = search_params.get('date_to', '')
        
        # Base queryset with permissions
        videos = Video.objects.select_related('album', 'category').filter(
            Q(album__owner=self.request.user) | Q(album__viewers=self.request.user) | Q(album__is_public=True)
        )
        
        # Apply album filter
        if album_id and album_id != 'all':
            try:
                videos = videos.filter(album_id=int(album_id))
            except (ValueError, TypeError):
                pass
        
        # Apply category filter
        if category_id and category_id != 'all':
            try:
                videos = videos.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        
        # Apply date filters
        if date_from:
            from datetime import datetime
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                videos = videos.filter(date_recorded__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            from datetime import datetime
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                videos = videos.filter(date_recorded__lte=date_to_obj)
            except ValueError:
                pass
        
        # Apply search query (videos don't have AI search, only text search)
        if query:
            videos = videos.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(album__title__icontains=query)
            )
        
        return videos
    
    def _parse_sort_params_video(self, sort):
        """Parse sort parameter and return field and direction for videos."""
        sort_field = 'uploaded_at'
        direction = 'desc'
        
        if sort == 'date_newest':
            sort_field = 'uploaded_at'
            direction = 'desc'
        elif sort == 'date_oldest':
            sort_field = 'uploaded_at'
            direction = 'asc'
        elif sort == 'title_asc':
            sort_field = 'title'
            direction = 'asc'
        elif sort == 'title_desc':
            sort_field = 'title'
            direction = 'desc'
        elif sort == 'uploaded_at_desc':
            sort_field = 'uploaded_at'
            direction = 'desc'
        elif sort == 'uploaded_at_asc':
            sort_field = 'uploaded_at'
            direction = 'asc'
        elif sort == 'date_taken_desc':
            # Videos use date_recorded instead of date_taken
            sort_field = 'date_recorded'
            direction = 'desc'
        elif sort == 'date_taken_asc':
            # Videos use date_recorded instead of date_taken
            sort_field = 'date_recorded'
            direction = 'asc'
        
        return sort_field, direction

def calculate_checksum(file):
    """Calculate the MD5 checksum of a file."""
    hasher = hashlib.md5()
    for chunk in file.chunks():
        hasher.update(chunk)
    file.seek(0)
    return hasher.hexdigest()


@login_required
def bulk_delete(request):
    if request.method == 'POST':
        media_ids = request.POST.getlist('media_ids')
        
        # Get all photos and videos that user has delete permission for
        photos_to_delete = []
        videos_to_delete = []
        album_id = None
        
        for media_id in media_ids:
            try:
                # Parse media_id format: "photo-123" or "video-456"
                if media_id.startswith('photo-'):
                    photo_id = int(media_id.replace('photo-', ''))
                    photo = Photo.objects.get(id=photo_id)
                    if check_object_permission(request.user, photo, 'photo', action='delete'):
                        photos_to_delete.append(photo)
                        if not album_id:
                            album_id = photo.album.id
                elif media_id.startswith('video-'):
                    video_id = int(media_id.replace('video-', ''))
                    video = Video.objects.get(id=video_id)
                    if check_object_permission(request.user, video, 'video', action='delete'):
                        videos_to_delete.append(video)
                        if not album_id:
                            album_id = video.album.id
            except (Photo.DoesNotExist, Video.DoesNotExist, ValueError):
                continue
        
        # Delete the media
        for photo in photos_to_delete:
            photo.delete()
        for video in videos_to_delete:
            video.delete()

        deleted_count = len(photos_to_delete) + len(videos_to_delete)
        if deleted_count > 0:
            messages.success(request, f'Successfully deleted {deleted_count} media item(s).')
        else:
            messages.warning(request, 'No media items were deleted. You may not have permission to delete the selected items.')
        
        if album_id:
            return redirect('album:album_detail', pk=album_id)
    return redirect('album:album_list')

@login_required
def bulk_download(request):
    if request.method == 'POST':
        media_ids = request.POST.getlist('media_ids')
        
        # Check download format preference (zip or individual)
        download_format = request.GET.get('format', 'auto')  # auto, zip, or individual
        
        # Check if user is on mobile device
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
        
        # Get all photos and videos that user has view permission for
        photos_to_download = []
        videos_to_download = []
        
        for media_id in media_ids:
            try:
                # Try photo first
                photo = Photo.objects.get(id=media_id)
                if check_object_permission(request.user, photo, 'photo', action='view'):
                    photos_to_download.append(photo)
            except Photo.DoesNotExist:
                try:
                    # Try video
                    video = Video.objects.get(id=media_id)
                    if check_object_permission(request.user, video, 'video', action='view'):
                        videos_to_download.append(video)
                except Video.DoesNotExist:
                    continue
        
        if not photos_to_download and not videos_to_download:
            messages.error(request, 'No media items found or you do not have permission to download them.')
            return redirect('album:album_list')

        # Handle individual download format or mobile users with multiple items
        if download_format == 'individual' or (download_format == 'auto' and is_mobile and len(photos_to_download) + len(videos_to_download) > 1):
            # Create a download page for individual downloads
            request.session['download_photos'] = [photo.id for photo in photos_to_download]
            request.session['download_videos'] = [video.id for video in videos_to_download]
            messages.info(request, f'Download page created for {len(photos_to_download) + len(videos_to_download)} items. Click each item to download individually.')
            return redirect('album:mobile_download_page')
        
        # Handle single item downloads (works well on mobile)
        if len(photos_to_download) + len(videos_to_download) == 1:
            if photos_to_download:
                photo = photos_to_download[0]
                # Serve the file with download headers
                with open(photo.image.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    filename = f"{photo.title}.{photo.image.name.split('.')[-1]}"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
            else:
                video = videos_to_download[0]
                # Serve the file with download headers
                with open(video.video.path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    filename = f"{video.title}.{video.video.name.split('.')[-1]}"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response

        # Desktop users or mobile users who specifically want ZIP (fallback)
        # Create a descriptive filename
        total_items = len(photos_to_download) + len(videos_to_download)
        photo_count = len(photos_to_download)
        video_count = len(videos_to_download)
        
        # Get the album name if all items are from the same album
        album_name = None
        if photos_to_download:
            first_album = photos_to_download[0].album
            if all(photo.album == first_album for photo in photos_to_download):
                if not videos_to_download or all(video.album == first_album for video in videos_to_download):
                    album_name = first_album.title
        elif videos_to_download:
            first_album = videos_to_download[0].album
            if all(video.album == first_album for video in videos_to_download):
                album_name = first_album.title
        
        # Generate filename
        if album_name:
            # Clean album name for filename (remove invalid characters)
            clean_album_name = "".join(c for c in album_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_album_name = clean_album_name.replace(' ', '_')
            if photo_count > 0 and video_count > 0:
                filename = f"{clean_album_name}_{photo_count}photos_{video_count}videos.zip"
            elif photo_count > 0:
                filename = f"{clean_album_name}_{photo_count}photos.zip"
            else:
                filename = f"{clean_album_name}_{video_count}videos.zip"
        else:
            # Mixed albums or no album context
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if photo_count > 0 and video_count > 0:
                filename = f"media_download_{photo_count}photos_{video_count}videos_{timestamp}.zip"
            elif photo_count > 0:
                filename = f"photos_download_{photo_count}items_{timestamp}.zip"
            else:
                filename = f"videos_download_{video_count}items_{timestamp}.zip"

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for photo in photos_to_download:
                zf.write(photo.image.path, photo.image.name)
            for video in videos_to_download:
                zf.write(video.video.path, video.video.name)

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return redirect('album:album_list')

@login_required
def mobile_download_page(request):
    """Mobile-friendly download page for multiple files."""
    photo_ids = request.session.get('download_photos', [])
    video_ids = request.session.get('download_videos', [])
    
    photos = []
    videos = []
    
    # Get photos user has permission to view
    for photo_id in photo_ids:
        try:
            photo = Photo.objects.get(id=photo_id)
            if check_object_permission(request.user, photo, 'photo', action='view'):
                photos.append(photo)
        except Photo.DoesNotExist:
            continue
    
    # Get videos user has permission to view
    for video_id in video_ids:
        try:
            video = Video.objects.get(id=video_id)
            if check_object_permission(request.user, video, 'video', action='view'):
                videos.append(video)
        except Video.DoesNotExist:
            continue
    
    # Clear session data after use
    if 'download_photos' in request.session:
        del request.session['download_photos']
    if 'download_videos' in request.session:
        del request.session['download_videos']
    
    if not photos and not videos:
        messages.error(request, 'No media items found for download.')
        return redirect('album:album_list')
    
    context = {
        'photos': photos,
        'videos': videos,
        'total_items': len(photos) + len(videos)
    }
    return render(request, 'album/mobile_download.html', context)

@login_required
def download_single_item(request, item_type, item_id):
    """Download a single photo or video file."""
    if item_type == 'photo':
        try:
            photo = Photo.objects.get(id=item_id)
            if not check_object_permission(request.user, photo, 'photo', action='view'):
                return HttpResponse('Permission denied', status=403)
            
            # Get the file path and determine content type
            file_path = photo.image.path
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create a safe filename
            # Get the real extension from the actual stored file path
            _, extension = os.path.splitext(photo.image.name)
            extension = extension.lstrip('.') # remove the leading dot

            # Get the base name from the title field, stripping any extension it might have
            base_name, _ = os.path.splitext(photo.title)

            # Sanitize the base name
            safe_title = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            
            if not safe_title:
                safe_title = f"photo_{photo.id}"
            filename = f"{safe_title}.{extension}"
            
            # Serve the file
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
            return response
        except Photo.DoesNotExist:
            return HttpResponse('Photo not found', status=404)
    
    elif item_type == 'video':
        try:
            video = Video.objects.get(id=item_id)
            if not check_object_permission(request.user, video, 'video', action='view'):
                return HttpResponse('Permission denied', status=403)
            
            # Get the file path and determine content type
            file_path = video.video.path
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create a safe filename
            _, extension = os.path.splitext(video.video.name)
            extension = extension.lstrip('.')

            base_name, _ = os.path.splitext(video.title)

            safe_title = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')

            if not safe_title:
                safe_title = f"video_{video.id}"
            filename = f"{safe_title}.{extension}"
            
            # Serve the file
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
            return response
        except Video.DoesNotExist:
            return HttpResponse('Video not found', status=404)
    
    else:
        return HttpResponse('Invalid item type', status=400)

@login_required
def delete_media(request, pk, model):
    """Delete a media object."""
    media = get_object_or_404(model, pk=pk)
    if not check_object_permission(request.user, media, model._meta.model_name, action='delete'):
        messages.error(request, f'You do not have permission to delete this {model._meta.verbose_name}.')
        log_security_event(f'unauthorized_{model._meta.model_name}_delete', request.user, f'Object ID: {pk}')
        return redirect('album:dashboard')
    
    if request.method == 'POST':
        media_id = media.id
        media_title = media.title
        media.delete()
        
        log_user_action(f'{model._meta.model_name}_deleted', request.user, model._meta.model_name, media_id)
        messages.success(request, f'{model._meta.verbose_name} "{media_title}" deleted successfully.')
        return redirect('album:dashboard')
    
    context = get_delete_context(media, model._meta.verbose_name, f'This will permanently delete the {model._meta.verbose_name} file.')
    return render(request, 'album/delete_confirmation.html', context)

# Search Views
@login_required
def search_media(request):
    """Advanced search view for photos and videos."""
    from django.db.models import Q
    from ..utils.media_utils import MediaQueryUtils, MediaDisplayUtils
    from datetime import datetime
    from ..services.embedding_service import generate_text_embedding
    from pgvector.django import CosineDistance

    # Get search parameters
    query = request.GET.get('q', '').strip() or request.GET.get('search', '').strip()
    media_type = request.GET.get('media_type', 'all')
    album_id = request.GET.get('album', '')
    category_id = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', 'uploaded_at')
    sort_direction = request.GET.get('direction', 'desc')
    search_type = request.GET.get('search_type', 'text')

    # Base querysets
    photos = Photo.objects.select_related('album', 'category').filter(
        Q(album__owner=request.user) | Q(album__viewers=request.user) | Q(album__is_public=True)
    )

    videos = Video.objects.select_related('album', 'category').filter(
        Q(album__owner=request.user) | Q(album__viewers=request.user) | Q(album__is_public=True)
    )

    # Apply search query
    if query:
        if search_type == 'ai' and media_type != 'videos':
            # AI search is for photos only, so clear the videos queryset.
            videos = videos.none()
            
            # Use hybrid approach: prioritize text-based search over embedding search
            text_results = photos.filter(
                Q(ai_description__icontains=query) | 
                Q(ai_tags__contains=[query])
            )
            
            if text_results.exists():
                # If we have direct text matches in AI descriptions/tags, use those
                photos = text_results
            else:
                # Fall back to embedding search if no direct text matches
                query_embedding = generate_text_embedding(query)
                if query_embedding:
                    # Use a strict threshold for embedding search
                    similarity_threshold = 0.11
                    
                    photos = photos.annotate(
                        distance=CosineDistance('embedding', query_embedding)
                    ).filter(
                        distance__lt=similarity_threshold
                    ).order_by('distance')[:50]  # Limit to top 50 embedding matches
                else:
                    messages.error(request, "No photos found matching your AI search query.")
                    photos = photos.none()
        else:
            # Standard text search
            photos = photos.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(album__title__icontains=query) |
                Q(category__name__icontains=query)
            )
            videos = videos.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(album__title__icontains=query) |
                Q(category__name__icontains=query)
            )

    # Apply album filter
    if album_id:
        photos = photos.filter(album_id=album_id)
        videos = videos.filter(album_id=album_id)

    # Apply category filter
    if category_id:
        photos = photos.filter(category_id=category_id)
        videos = videos.filter(category_id=category_id)

    # Apply date filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            photos = photos.filter(uploaded_at__date__gte=date_from_obj.date())
            videos = videos.filter(uploaded_at__date__gte=date_from_obj.date())
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            photos = photos.filter(uploaded_at__date__lte=date_to_obj.date())
            videos = videos.filter(uploaded_at__date__lte=date_to_obj.date())
        except ValueError:
            pass

    # Apply media type filter
    media_list = MediaQueryUtils.filter_media_by_type(media_type, photos, videos)

    # Apply sorting (unless it's an AI search, which is already sorted by distance)
    if media_type == 'all' and search_type != 'ai':
        media_list = MediaQueryUtils.sort_combined_media(media_list, sort_by, sort_direction)

    # Paginate results
    page_obj, pagination_context = MediaQueryUtils.paginate_media(media_list, request.GET.get('page', 1), 24)

    # Get filter options
    user_albums = Album.objects.filter(
        Q(owner=request.user) | Q(viewers=request.user) | Q(is_public=True)
    ).distinct().order_by('title')

    categories = Category.objects.filter(
        Q(photos__album__owner=request.user) |
        Q(videos__album__owner=request.user) |
        Q(photos__album__viewers=request.user) |
        Q(videos__album__viewers=request.user) |
        Q(photos__album__is_public=True) |
        Q(videos__album__is_public=True)
    ).distinct().order_by('name')

    context = {
        'page_obj': page_obj,
        'media': page_obj.object_list,
        'query': query,
        'media_type': media_type,
        'selected_album': album_id,
        'selected_category': category_id,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'sort_direction': sort_direction,
        'search_type': search_type,
        'albums': user_albums,
        'categories': categories,
        'media_type_options': MediaDisplayUtils.get_media_type_options(),
        'sort_options': MediaDisplayUtils.get_sort_options(),
        **pagination_context
    }

    return render(request, 'album/search_results.html', context)

from django import forms
import os
from .album_views import Album

class SimpleUploadForm(forms.Form):
    album = forms.ModelChoiceField(
        queryset=Album.objects.none(),
        required=True,
        label="Select Album",
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    title = forms.CharField(
        max_length=100,
        required=False,
        label="Title (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'}),
        required=False,
        label="Description (optional)"
    )
    files = forms.FileField(required=False)
    dirfiles = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['album'].queryset = Album.objects.filter(owner=user)
        else:
            self.fields['album'].queryset = Album.objects.none()

def minimal_upload(request):
    upload_results = None
    if request.method == 'POST':
        form = SimpleUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            album = form.cleaned_data['album']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            files = request.FILES.getlist('files') + request.FILES.getlist('dirfiles')
            
            successful_uploads = []
            failed_uploads = []
            
            for f in files:
                try:
                    # Determine file type and create appropriate media object
                    file_extension = os.path.splitext(f.name)[1].lower()
                    
                    if f.content_type.startswith('image/') or \
                       (f.content_type == 'application/octet-stream' and file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        # Validate image file
                        validate_file_type(f, ALLOWED_IMAGE_TYPES)
                        validate_image_file(f)
                        
                        # Create Photo object
                        photo = Photo.objects.create(
                            album=album,
                            title=title or f.name,
                            description=description,
                            image=f
                        )
                        # Extract metadata
                        MediaService.extract_photo_metadata(photo)
                        
                        # Queue AI processing if enabled
                        from django.conf import settings
                        if settings.AI_AUTO_PROCESS_ON_UPLOAD:
                            from album.tasks import process_media_on_upload
                            process_media_on_upload.delay('photo', photo.id)
                        
                        successful_uploads.append({
                            'name': f.name,
                            'type': 'photo',
                            'size': f.size,
                            'url': reverse('album:photo_detail', kwargs={'pk': photo.pk})
                        })
                        
                    elif f.content_type.startswith('video/') or \
                         (f.content_type == 'application/octet-stream' and file_extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv']):
                        # Validate video file
                        validate_file_type(f, ALLOWED_VIDEO_TYPES)
                        validate_video_file(f)
                        
                        # Create Video object
                        video = Video.objects.create(
                            album=album,
                            title=title or f.name,
                            description=description,
                            video=f
                        )
                        # Extract metadata
                        MediaService.extract_video_metadata(video)
                        
                        # Queue AI processing if enabled
                        from django.conf import settings
                        if settings.AI_AUTO_PROCESS_ON_UPLOAD:
                            from album.tasks import process_media_on_upload
                            process_media_on_upload.delay('video', video.id)
                        
                        successful_uploads.append({
                            'name': f.name,
                            'type': 'video',
                            'size': f.size,
                            'url': reverse('album:video_detail', kwargs={'pk': video.pk})
                        })
                        
                    else:
                        failed_uploads.append({
                            'name': f.name,
                            'reason': f'Unsupported file type: {f.content_type} (extension: {file_extension})'
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing file {f.name}: {e}")
                    failed_uploads.append({
                        'name': f.name,
                        'reason': str(e)
                    })
            
            upload_results = {
                'album': album,
                'successful': successful_uploads,
                'failed': failed_uploads,
                'total_attempted': len(files),
                'total_successful': len(successful_uploads),
                'total_failed': len(failed_uploads),
                'title': title,
                'description': description
            }
        else:
            upload_results = {
                'error': 'Form validation failed',
                'form_errors': form.errors
            }
    else:
        form = SimpleUploadForm(user=request.user)
    return render(request, 'album/minimal_upload.html', {'form': form, 'upload_results': upload_results})


@require_POST
@login_required
def toggle_favorite(request, photo_id):
    """Toggle favorite status for a photo via AJAX"""
    photo = get_object_or_404(Photo, pk=photo_id)
    
    # Check if user has permission to view the photo (through album access)
    album = photo.album
    if not (request.user.is_superuser or album.is_public or request.user == album.owner or request.user in album.viewers.all()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        photo=photo
    )
    
    if not created:
        # Favorite already exists, remove it
        favorite.delete()
        is_favorited = False
    else:
        # New favorite created
        is_favorited = True
    
    return JsonResponse({
        'is_favorited': is_favorited,
        'message': 'Added to favorites' if is_favorited else 'Removed from favorites'
    })


@login_required
def favorites_list(request):
    """Display user's favorited photos"""
    favorites = Favorite.objects.filter(user=request.user).select_related('photo__album')
    photos = [fav.photo for fav in favorites]
    
    return render(request, 'album/favorites.html', {
        'photos': photos,
        'favorites_count': len(photos)
    })


@login_required
def process_videos_ai(request):
    """
    Album admin and superuser view to trigger AI processing of videos.
    Album admins can only process videos from their own albums.
    """
    # Check basic permissions - must be album owner or superuser
    if not (request.user.is_site_admin or request.user.is_album_owner):
        messages.error(request, 'You do not have permission to process videos with AI.')
        return redirect('album:homepage')
    """
    Admin-only view to trigger AI processing of videos.
    Analyzes video thumbnails and generates descriptions, tags, and embeddings.
    """
    from django.core.management import call_command
    from django.db.models import Q
    from ..models import Video
    from ..services.ai_analysis_service import is_ai_analysis_available
    import time
    
    if request.method == 'POST':
        # Check if this is a cleanup request
        if request.POST.get('cleanup_orphaned'):
            try:
                # Find orphaned videos (database records with missing files)
                orphaned_candidates = Video.objects.filter(
                    Q(ai_description__isnull=True) | Q(ai_description='') | Q(ai_processed=False)
                )
                
                orphaned_count = 0
                orphaned_videos_to_delete = []
                
                for video in orphaned_candidates:
                    import os
                    if not (video.video and os.path.exists(video.video.path)):
                        orphaned_videos_to_delete.append(video.id)
                        orphaned_count += 1
                
                if orphaned_count > 0:
                    # Delete orphaned video records
                    Video.objects.filter(id__in=orphaned_videos_to_delete).delete()
                    messages.success(request, 
                        f'Successfully cleaned up {orphaned_count} orphaned video record{"s" if orphaned_count != 1 else ""} '
                        f'from the database.')
                else:
                    messages.info(request, 'No orphaned video records found to clean up.')
                    
            except Exception as e:
                logger.error(f'Error cleaning up orphaned videos: {e}')
                messages.error(request, f'Error cleaning up orphaned videos: {str(e)}')
            
            return redirect('album:process_videos_ai')
        
        # Regular AI processing request
        # Get parameters from the form
        force_regeneration = request.POST.get('force', False) == 'on'
        album_title = request.POST.get('album', '').strip()
        limit = request.POST.get('limit', '').strip()
        
        # For album admins, validate they can only process their albums
        if album_title and not request.user.is_site_admin:
            try:
                album = Album.objects.get(title=album_title)
                if not is_album_admin(request.user, album):
                    messages.error(request, 'You do not have permission to process AI for this album.')
                    return redirect('album:process_videos_ai')
            except Album.DoesNotExist:
                messages.error(request, 'Album not found.')
                return redirect('album:process_videos_ai')
        
        try:
            # Check if AI analysis is available
            if not is_ai_analysis_available():
                messages.error(request, 'AI analysis service is not available. Please check the model loading.')
                return redirect('album:process_videos_ai')
            
            # Cap limit for album admins based on settings (site admins have no cap)
            if not request.user.is_site_admin:
                from ..models import AIProcessingSettings
                ai_settings = AIProcessingSettings.load()
                max_limit = ai_settings.album_admin_processing_limit
                
                if limit and limit.isdigit():
                    limit = str(min(int(limit), max_limit))
                else:
                    limit = str(max_limit)
            
            # Use synchronous processing for manual UI requests (more efficient for CPU-only)
            # The management command loads the model once and processes sequentially
            from django.core.management import call_command
            import time
            
            # Build parameters for the command
            command_args = []
            if force_regeneration:
                command_args.append('--force')
            if album_title:
                command_args.extend(['--album', album_title])
            if limit and limit.isdigit():
                command_args.extend(['--limit', limit])
            
            # Count videos that will be processed
            if force_regeneration:
                if album_title:
                    videos_count = Video.objects.filter(album__title=album_title).count()
                else:
                    videos_count = Video.objects.all().count()
            else:
                filters = Q(ai_description__isnull=True) | Q(ai_description='')
                if album_title:
                    filters &= Q(album__title=album_title)
                videos_count = Video.objects.filter(filters).count()
            
            if limit and limit.isdigit():
                videos_count = min(videos_count, int(limit))
            
            if videos_count == 0:
                messages.info(request, 'No videos found to process.')
                return redirect('album:process_videos_ai')
            
            # Run the analysis command synchronously (works better on CPU-only servers)
            start_time = time.time()
            call_command('analyze_videos', *command_args)
            elapsed_time = time.time() - start_time
            
            messages.success(request, 
                f'Successfully processed {videos_count} videos in {elapsed_time:.2f} seconds. '
                f'Videos now have AI-generated descriptions and tags.')
            
        except Exception as e:
            logger.error(f'Error processing videos with AI: {e}')
            messages.error(request, f'Error processing videos: {str(e)}')
        
        return redirect('album:process_videos_ai')
    
    # GET request - show the form
    # Get statistics for the template - filter by albums user can admin
    if request.user.is_site_admin:
        # Superusers see all videos
        video_queryset = Video.objects.all()
    else:
        # Album admins see only their own videos
        video_queryset = Video.objects.filter(
            Q(album__owner=request.user) | Q(album__viewers=request.user)
        ).distinct()
    
    total_videos = video_queryset.count()
    processed_videos = video_queryset.filter(ai_processed=True).count()
    
    # Only count unprocessed videos that actually have files
    unprocessed_candidates = video_queryset.filter(
        Q(ai_description__isnull=True) | Q(ai_description='') | Q(ai_processed=False)
    )
    
    # Check which ones actually have files
    unprocessed_videos = 0
    orphaned_videos = 0
    
    for video in unprocessed_candidates:
        import os
        if video.video and os.path.exists(video.video.path):
            unprocessed_videos += 1
        else:
            orphaned_videos += 1
    
    # Get available albums - only albums user can admin
    if request.user.is_site_admin:
        # Superusers can process all albums
        albums = Album.objects.all().order_by('title')
    else:
        # Album admins can only process their own albums
        albums = Album.objects.filter(
            Q(owner=request.user) | Q(viewers=request.user)
        ).distinct().order_by('title')
    
    context = {
        'total_videos': total_videos,
        'processed_videos': processed_videos,
        'unprocessed_videos': unprocessed_videos,
        'orphaned_videos': orphaned_videos,
        'albums': albums,
        'ai_available': is_ai_analysis_available(),
    }
    
    return render(request, 'album/process_videos_ai.html', context)


@login_required
def process_photos_ai(request):
    """
    Album admin and superuser view to trigger AI processing of photos.
    Album admins can only process photos from their own albums.
    """
    # Check basic permissions - must be album owner or superuser
    if not (request.user.is_site_admin or request.user.is_album_owner):
        messages.error(request, 'You do not have permission to process photos with AI.')
        return redirect('album:homepage')
    from django.core.management import call_command
    from django.db.models import Q
    from ..models import Photo
    from ..services.ai_analysis_service import is_ai_analysis_available
    import time
    
    if request.method == 'POST':
        # Check if this is a cleanup request
        if request.POST.get('cleanup_orphaned'):
            try:
                # Find orphaned photos (database records with missing files)
                orphaned_candidates = Photo.objects.filter(
                    Q(ai_description__isnull=True) | Q(ai_description='') | Q(ai_processed=False)
                )
                
                orphaned_count = 0
                orphaned_photos_to_delete = []
                
                for photo in orphaned_candidates:
                    import os
                    if not (photo.image and os.path.exists(photo.image.path)):
                        orphaned_photos_to_delete.append(photo.id)
                        orphaned_count += 1
                
                if orphaned_count > 0:
                    # Delete orphaned photo records
                    Photo.objects.filter(id__in=orphaned_photos_to_delete).delete()
                    messages.success(request, 
                        f'Successfully cleaned up {orphaned_count} orphaned photo record{"s" if orphaned_count != 1 else ""} '
                        f'from the database.')
                else:
                    messages.info(request, 'No orphaned photo records found to clean up.')
                    
            except Exception as e:
                logger.error(f'Error cleaning up orphaned photos: {e}')
                messages.error(request, f'Error cleaning up orphaned photos: {str(e)}')
            
            return redirect('album:process_photos_ai')
        
        # Regular AI processing request
        # Get parameters from the form
        force_regeneration = request.POST.get('force', False) == 'on'
        album_title = request.POST.get('album', '').strip()
        limit = request.POST.get('limit', '').strip()
        
        # For album admins, validate they can only process their albums
        if album_title and not request.user.is_site_admin:
            try:
                album = Album.objects.get(title=album_title)
                if not is_album_admin(request.user, album):
                    messages.error(request, 'You do not have permission to process AI for this album.')
                    return redirect('album:process_photos_ai')
            except Album.DoesNotExist:
                messages.error(request, 'Album not found.')
                return redirect('album:process_photos_ai')
        
        try:
            # Check if AI analysis is available
            if not is_ai_analysis_available():
                messages.error(request, 'AI analysis service is not available. Please check the model loading.')
                return redirect('album:process_photos_ai')
            
            # Cap limit for album admins based on settings (site admins have no cap)
            if not request.user.is_site_admin:
                from ..models import AIProcessingSettings
                ai_settings = AIProcessingSettings.load()
                max_limit = ai_settings.album_admin_processing_limit
                
                if limit and limit.isdigit():
                    limit = str(min(int(limit), max_limit))
                else:
                    limit = str(max_limit)
            
            # Use synchronous processing for manual UI requests (more efficient for CPU-only)
            # The management command loads the model once and processes sequentially
            from django.core.management import call_command
            import time
            
            # Build parameters for the command
            command_args = []
            if force_regeneration:
                command_args.append('--force')
            if album_title:
                command_args.extend(['--album', album_title])
            if limit and limit.isdigit():
                command_args.extend(['--limit', limit])
            
            # Count photos that will be processed
            if force_regeneration:
                if album_title:
                    photos_count = Photo.objects.filter(album__title=album_title).count()
                else:
                    photos_count = Photo.objects.all().count()
            else:
                filters = Q(ai_description__isnull=True) | Q(ai_description='')
                if album_title:
                    filters &= Q(album__title=album_title)
                photos_count = Photo.objects.filter(filters).count()
            
            if limit and limit.isdigit():
                photos_count = min(photos_count, int(limit))
            
            if photos_count == 0:
                messages.info(request, 'No photos found to process.')
                return redirect('album:process_photos_ai')
            
            # Run the analysis command synchronously (works better on CPU-only servers)
            start_time = time.time()
            call_command('analyze_photos', *command_args)
            elapsed_time = time.time() - start_time
            
            messages.success(request, 
                f'Successfully processed {photos_count} photos in {elapsed_time:.2f} seconds. '
                f'Photos now have AI-generated descriptions and tags.')
            
        except Exception as e:
            logger.error(f'Error processing photos with AI: {e}')
            messages.error(request, f'Error processing photos: {str(e)}')
        
        return redirect('album:process_photos_ai')
    
    # GET request - show the form
    # Get statistics for the template - filter by albums user can admin
    if request.user.is_site_admin:
        # Superusers see all photos
        photo_queryset = Photo.objects.all()
    else:
        # Album admins see only their own photos
        photo_queryset = Photo.objects.filter(
            Q(album__owner=request.user) | Q(album__viewers=request.user)
        ).distinct()
    
    total_photos = photo_queryset.count()
    processed_photos = photo_queryset.filter(ai_processed=True).count()
    
    # Only count unprocessed photos that actually have files
    unprocessed_candidates = photo_queryset.filter(
        Q(ai_description__isnull=True) | Q(ai_description='') | Q(ai_processed=False)
    )
    
    # Check which ones actually have files
    unprocessed_photos = 0
    orphaned_photos = 0
    
    for photo in unprocessed_candidates:
        import os
        if photo.image and os.path.exists(photo.image.path):
            unprocessed_photos += 1
        else:
            orphaned_photos += 1
    
    # Get available albums - only albums user can admin
    if request.user.is_site_admin:
        # Superusers can process all albums
        albums = Album.objects.all().order_by('title')
    else:
        # Album admins can only process their own albums
        albums = Album.objects.filter(
            Q(owner=request.user) | Q(viewers=request.user)
        ).distinct().order_by('title')
    
    context = {
        'total_photos': total_photos,
        'processed_photos': processed_photos,
        'unprocessed_photos': unprocessed_photos,
        'orphaned_photos': orphaned_photos,
        'albums': albums,
        'ai_available': is_ai_analysis_available(),
    }
    
    return render(request, 'album/process_photos_ai.html', context)
