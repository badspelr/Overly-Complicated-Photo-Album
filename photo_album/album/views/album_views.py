"""
Album-related views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from ..models import Album, Photo, Category
from ..forms import AlbumForm
from ..utils.media_utils import MediaQueryUtils, MediaDisplayUtils
from .base_views import AlbumListPermissionMixin, AlbumDetailPermissionMixin, check_object_permission, get_delete_context, log_user_action, log_security_event


@method_decorator(login_required, name='dispatch')
class AlbumListView(AlbumListPermissionMixin, LoginRequiredMixin, ListView):
    """List view for albums with search and filtering."""
    model = Album
    template_name = 'album/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            # Enhanced search: albums by title/description AND albums containing matching media content
            # Search albums by title, description, or owner
            album_match = models.Q(title__icontains=query) | \
                         models.Q(description__icontains=query) | \
                         models.Q(owner__username__icontains=query)
            
            # Search albums containing photos/videos with matching AI content
            content_match = models.Q(photos__ai_description__icontains=query) | \
                           models.Q(photos__ai_tags__contains=[query]) | \
                           models.Q(videos__ai_description__icontains=query) | \
                           models.Q(videos__ai_tags__contains=[query]) | \
                           models.Q(photos__title__icontains=query) | \
                           models.Q(photos__description__icontains=query) | \
                           models.Q(videos__title__icontains=query) | \
                           models.Q(videos__description__icontains=query)
            
            queryset = queryset.filter(album_match | content_match).distinct()
        
        return queryset.select_related('owner', 'category').prefetch_related('viewers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AlbumDetailView(AlbumDetailPermissionMixin, DetailView):
    """Detail view for individual albums."""
    model = Album
    template_name = 'album/album_detail.html'
    
    def get_queryset(self):
        return super().get_queryset().select_related('owner', 'category').prefetch_related(
            'viewers', 'photos', 'videos'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object
        request = self.request
        
        # Get query parameters with defaults
        media_type = request.GET.get('media_type', 'all')
        # Default to "Date Taken newest" for album view sorting
        sort = request.GET.get('sort', 'date_taken_desc')
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        category_filter = request.GET.get('category', 'all')
        search_query = request.GET.get('search', '').strip()
        search_type = request.GET.get('search_type', 'text')

        # Set default sort values
        sort_field = 'uploaded_at'
        direction = 'desc'

        # Handle search
        if search_query:
            from ..services.search_service import MediaSearchService
            photos, videos = MediaSearchService.search_album_by_text(
                search_query, album.id, request.user, search_type
            )
        else:
            # Get sort configuration using utility
            sort_field, direction = MediaQueryUtils.get_sort_config(request)
            
            # Map legacy sort parameter to new format and handle field differences
            if sort == 'date_newest':
                sort_field = 'uploaded_at'
                direction = 'desc'
            elif sort == 'date_oldest':
                sort_field = 'uploaded_at'
                direction = 'asc'
            elif sort == 'title_az':
                sort_field = 'title'
                direction = 'asc'
            elif sort == 'title_za':
                sort_field = 'title'
                direction = 'desc'
            # Explicit Date Added options
            elif sort == 'uploaded_at_desc':
                sort_field = 'uploaded_at'
                direction = 'desc'
            elif sort == 'uploaded_at_asc':
                sort_field = 'uploaded_at'
                direction = 'asc'
            # New explicit date taken options for album view
            elif sort == 'date_taken_desc':
                sort_field = 'date_taken'
                direction = 'desc'
            elif sort == 'date_taken_asc':
                sort_field = 'date_taken'
                direction = 'asc'

            # Handle different field names for photos vs videos
            photo_sort_field = sort_field
            video_sort_field = sort_field

            # Map date_taken to date_recorded for videos
            if sort_field == 'date_taken':
                video_sort_field = 'date_recorded'

            # Get filtered media with appropriate sort fields
            photos = album.photos.select_related('album').order_by(f'-{photo_sort_field}' if direction == 'desc' else photo_sort_field)
            videos = album.videos.select_related('album').order_by(f'-{video_sort_field}' if direction == 'desc' else video_sort_field)
        
        # Apply category filter (only if not searching)
        if not search_query and category_filter and category_filter != 'all':
            if category_filter == 'uncategorized':
                photos = photos.filter(category__isnull=True)
                videos = videos.filter(category__isnull=True)
            else:
                photos = photos.filter(category__name__iexact=category_filter)
                videos = videos.filter(category__name__iexact=category_filter)
        
        # Apply media type filter using utility
        media_list = MediaQueryUtils.filter_media_by_type(media_type, photos, videos)
        
        # Apply secondary sorting for combined media using utility (only if not searching)
        if media_type == 'all' and not search_query:
            media_list = MediaQueryUtils.sort_combined_media(media_list, sort_field, direction)

        # Paginate media using utility
        page_obj, pagination_info = MediaQueryUtils.paginate_media(media_list, page, page_size)
        
        logger.info(f"Media list: {media_list}")
        logger.info(f"Page object: {page_obj.object_list}")

        # Get unique categories from album's media
        if self.request.user.is_superuser:
            media_categories = Category.objects.all()
        elif self.request.user.is_authenticated:
            media_categories = Category.objects.filter(created_by=self.request.user)
        else:
            media_categories = Category.objects.none()
        
        # Update context with all necessary data
        context.update({
            'media': page_obj.object_list,
            'media_type': media_type,
            'sort': sort,
            'page_size': page_size,
            'page': page,
            'category_filter': category_filter,
            'search_query': search_query,
            'search_type': search_type,
            'media_categories': media_categories.order_by('name'),
            # Album-specific sort options: include Date Taken, Date Added, and Title
            'sort_options': [
                ('date_taken_desc', 'Date Taken newest'),
                ('date_taken_asc', 'Date Taken oldest'),
                ('uploaded_at_desc', 'Date Added newest'),
                ('uploaded_at_asc', 'Date Added oldest'),
                ('title_az', 'Title A–Z'),
                ('title_za', 'Title Z–A'),
            ],
            'media_type_options': MediaDisplayUtils.get_media_type_options(),
            'page_size_options': MediaDisplayUtils.get_page_size_options(),
            **pagination_info
        })
        
        return context


import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def create_album(request, pk=None):
    """Create or edit an album."""
    album = None
    if pk:
        album = get_object_or_404(Album, pk=pk)
        if not check_object_permission(request.user, album, 'album'):
            messages.error(request, 'You do not have permission to edit this album.')
            log_security_event('unauthorized_album_edit', request.user, f'Album ID: {pk}')
            return redirect('album:dashboard')
    
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, user=request.user, instance=album)
        if form.is_valid():
            album = form.save(commit=False)
            if not pk:  # Only set owner for new albums
                album.owner = request.user
            album.save()
            form.save_m2m()  # Save many-to-many relationships

            # Handle photo uploads with orientation correction
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                # Create photo object but don't save yet
                photo = Photo(album=album, title=photo_file.name)
                
                # Correct orientation before saving
                from django.core.files.base import ContentFile
                from PIL import Image, ImageOps
                from io import BytesIO
                
                # Read and correct orientation
                img = Image.open(photo_file)
                img_corrected = ImageOps.exif_transpose(img)
                
                # Convert to bytes
                output = BytesIO()
                img_corrected.save(output, format=img.format or 'JPEG', quality=95)
                corrected_image_data = output.getvalue()
                
                # Create ContentFile with corrected image
                corrected_file = ContentFile(corrected_image_data, name=photo_file.name)
                
                # Set corrected image and save
                photo.image = corrected_file
                photo.save()
                
                # Extract additional metadata
                try:
                    photo.width, photo.height = img_corrected.size
                    exif_data = img._getexif()
                    if exif_data:
                        from .media_views import MediaMetadataExtractor
                        MediaMetadataExtractor._parse_exif_data(photo, exif_data)
                    photo.save()
                except Exception as e:
                    logger.warning(f"Error extracting photo metadata: {e}")
            
            action = "updated" if pk else "created"
            log_user_action(f"album_{action}", request.user, 'album', album.id)
            messages.success(request, f'Album {action} successfully.')
            return redirect('album:dashboard')
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = AlbumForm(user=request.user, instance=album)
    
    context = {
        'form': form,
        'is_edit': bool(pk),
        'album': album
    }
    return render(request, 'album/create_album.html', context)


@login_required
def delete_album(request, pk):
    """Delete an album."""
    album = get_object_or_404(Album, pk=pk)
    if not check_object_permission(request.user, album, 'album', action='delete'):
        messages.error(request, 'You do not have permission to delete this album.')
        log_security_event('unauthorized_album_delete', request.user, f'Album ID: {pk}')
        return redirect('album:dashboard')
    
    if request.method == 'POST':
        album_id = album.id
        album_title = album.title
        album.delete()
        
        log_user_action('album_deleted', request.user, 'album', album_id)
        messages.success(request, f'Album "{album_title}" and all its photos/videos deleted successfully.')
        return redirect('album:dashboard')
    
    context = get_delete_context(album, 'Album', 'This will permanently delete the album and all its photos and videos.')
    return render(request, 'album/delete_confirmation.html', context)


@login_required
def album_viewers(request, pk):
    """View and manage album viewers."""
    album = get_object_or_404(Album, pk=pk)
    if not check_object_permission(request.user, album, 'album'):
        messages.error(request, 'You do not have permission to view this album\'s viewers.')
        log_security_event('unauthorized_viewer_access', request.user, f'Album ID: {pk}')
        return redirect('album:dashboard')
    
    viewers = album.viewers.all()
    return render(request, 'album/album_viewers.html', {'album': album, 'viewers': viewers})


@login_required
def remove_viewer(request, pk, user_id):
    """Remove a viewer from an album."""
    album = get_object_or_404(Album, pk=pk)
    if not check_object_permission(request.user, album, 'album', action='delete'):
        messages.error(request, 'You do not have permission to manage this album\'s viewers.')
        log_security_event('unauthorized_viewer_removal', request.user, f'Album ID: {pk}')
        return redirect('album:dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    album.viewers.remove(user)
    
    log_user_action('viewer_removed', request.user, 'album', album.id)
    messages.success(request, f'Removed {user.username} from {album.title} viewers')
    return redirect('album_viewers', pk=pk)


# Shareable Link Views
@login_required
def create_share_link(request, pk):
    """Create a shareable link for an album."""
    album = get_object_or_404(Album, pk=pk)
    
    if not check_object_permission(request.user, album, 'album', action='view'):
        messages.error(request, 'You do not have permission to share this album.')
        return redirect('album:album_detail', pk=pk)
    
    if request.method == 'POST':
        from datetime import timedelta
        from django.utils import timezone
        import secrets
        
        # Generate unique token
        share_token = secrets.token_urlsafe(32)
        
        # Get expiration from form
        expires_days = request.POST.get('expires_days')
        expires_at = None
        if expires_days and expires_days.isdigit():
            expires_at = timezone.now() + timedelta(days=int(expires_days))
        
        # Create share link
        from ..models import AlbumShareLink
        share_link = AlbumShareLink.objects.create(
            album=album,
            created_by=request.user,
            share_token=share_token,
            expires_at=expires_at
        )
        
        # Generate full URL
        from django.urls import reverse
        share_url = request.build_absolute_uri(reverse('album:shared_album', kwargs={'token': share_token}))
        
        log_user_action('share_link_created', request.user, 'album', album.id)
        messages.success(request, f'Share link created! URL: {share_url}')
        
        return render(request, 'album/share_link_created.html', {
            'album': album,
            'share_url': share_url,
            'share_link': share_link
        })
    
    return render(request, 'album/create_share_link.html', {'album': album})


def shared_album(request, token):
    """Access an album via shareable link (public access)."""
    from ..models import AlbumShareLink
    
    try:
        share_link = AlbumShareLink.objects.select_related('album', 'album__owner').get(
            share_token=token,
            is_active=True
        )
    except AlbumShareLink.DoesNotExist:
        messages.error(request, 'This share link is invalid or has expired.')
        return render(request, 'album/share_link_invalid.html')
    
    # Check if link has expired
    if share_link.is_expired():
        share_link.is_active = False
        share_link.save()
        messages.error(request, 'This share link has expired.')
        return render(request, 'album/share_link_invalid.html')
    
    # Increment view count
    share_link.view_count += 1
    share_link.save(update_fields=['view_count'])
    
    album = share_link.album
    
    # Get media for the album (similar to album detail view)
    photos = album.photos.select_related('album').order_by('-uploaded_at')
    videos = album.videos.select_related('album').order_by('-uploaded_at')
    
    # Combine and sort media
    from ..utils.media_utils import MediaQueryUtils
    media_list = MediaQueryUtils.filter_media_by_type('all', photos, videos)
    media_list = MediaQueryUtils.sort_combined_media(media_list, 'uploaded_at', 'desc')
    
    # Paginate
    page_obj, pagination_context = MediaQueryUtils.paginate_media(media_list, 1, 50)
    
    context = {
        'album': album,
        'page_obj': page_obj,
        'media': page_obj.object_list,
        'is_shared_view': True,
        'share_link': share_link,
        **pagination_context
    }
    
    return render(request, 'album/shared_album.html', context)


@login_required
def manage_share_links(request, pk):
    """Manage shareable links for an album."""
    album = get_object_or_404(Album, pk=pk)
    
    if not check_object_permission(request.user, album, 'album', action='view'):
        messages.error(request, 'You do not have permission to manage this album.')
        return redirect('album:album_detail', pk=pk)
    
    from ..models import AlbumShareLink
    share_links = AlbumShareLink.objects.filter(
        album=album,
        created_by=request.user
    ).order_by('-created_at')
    
    return render(request, 'album/manage_share_links.html', {
        'album': album,
        'share_links': share_links
    })


@login_required
def delete_share_link(request, link_id):
    """Delete a shareable link."""
    from ..models import AlbumShareLink
    
    share_link = get_object_or_404(AlbumShareLink, id=link_id, created_by=request.user)
    album = share_link.album
    
    if request.method == 'POST':
        share_link.delete()
        log_user_action('share_link_deleted', request.user, 'album', album.id)
        messages.success(request, 'Share link deleted successfully.')
    
    return redirect('album:manage_share_links', pk=album.pk)


def offline_view(request):
    """View for offline page when user is not connected to internet."""
    return render(request, 'album/offline.html')


@login_required
def download_full_album(request, pk):
    """Download an entire album as ZIP file(s) - supports multi-part for large albums."""
    import os
    import zipfile
    from io import BytesIO
    from django.http import HttpResponse
    from ..models import SiteSettings
    
    album = get_object_or_404(Album, pk=pk)
    
    # Check permissions - only owner or superuser can download
    if not (request.user.is_superuser or album.owner == request.user):
        log_security_event('unauthorized_album_download', request.user, {
            'album_id': album.id,
            'album_title': album.title
        })
        messages.error(request, 'You do not have permission to download this album.')
        return redirect('album:album_detail', pk=album.pk)
    
    # Get max size from settings
    try:
        site_settings = SiteSettings.objects.first()
        max_size_mb = site_settings.max_album_download_size_mb if site_settings else 2048
    except Exception:
        max_size_mb = 2048
    
    MAX_PART_SIZE_BYTES = max_size_mb * 1024 * 1024  # Convert MB to bytes
    
    # Get all photos and videos
    photos = list(album.photos.all())
    videos = list(album.videos.all())
    
    # Helper function to format size
    def format_size(bytes_size):
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    # Calculate sizes and organize into parts
    photo_data = []
    for photo in photos:
        try:
            size = os.path.getsize(photo.image.path)
            photo_data.append({
                'object': photo,
                'size': size,
                'path': photo.image.path,
                'arcname': os.path.join('photos', os.path.basename(photo.image.name)),
                'type': 'photo'
            })
        except (OSError, ValueError):
            pass
    
    video_data = []
    for video in videos:
        try:
            size = os.path.getsize(video.video.path)
            video_data.append({
                'object': video,
                'size': size,
                'path': video.video.path,
                'arcname': os.path.join('videos', os.path.basename(video.video.name)),
                'type': 'video'
            })
        except (OSError, ValueError):
            pass
    
    # Combine all media
    all_media = photo_data + video_data
    total_size = sum(item['size'] for item in all_media)
    
    # Check if album is empty
    if not all_media or total_size == 0:
        messages.warning(request, 'This album appears to be empty or the media files cannot be accessed.')
        return redirect('album:album_detail', pk=album.pk)
    
    # Calculate how many parts we need
    parts = []
    current_part = []
    current_size = 0
    
    for item in all_media:
        # If adding this item exceeds limit and current part isn't empty, start new part
        if current_size + item['size'] > MAX_PART_SIZE_BYTES and current_part:
            parts.append({
                'items': current_part,
                'size': current_size,
                'photo_count': sum(1 for i in current_part if i['type'] == 'photo'),
                'video_count': sum(1 for i in current_part if i['type'] == 'video')
            })
            current_part = []
            current_size = 0
        
        current_part.append(item)
        current_size += item['size']
    
    # Add the last part
    if current_part:
        parts.append({
            'items': current_part,
            'size': current_size,
            'photo_count': sum(1 for i in current_part if i['type'] == 'photo'),
            'video_count': sum(1 for i in current_part if i['type'] == 'video')
        })
    
    # If user hasn't confirmed, show confirmation page
    if 'confirm' not in request.POST and 'download_part' not in request.GET:
        context = {
            'album': album,
            'parts': [
                {
                    'number': idx + 1,
                    'size': format_size(part['size']),
                    'photo_count': part['photo_count'],
                    'video_count': part['video_count']
                }
                for idx, part in enumerate(parts)
            ],
            'total_parts': len(parts),
            'total_size': format_size(total_size),
            'total_photos': len(photo_data),
            'total_videos': len(video_data),
            'is_multipart': len(parts) > 1
        }
        return render(request, 'album/download_album_confirm.html', context)
    
    # Handle actual download
    part_number = int(request.GET.get('download_part', 1))
    
    if part_number < 1 or part_number > len(parts):
        messages.error(request, 'Invalid part number.')
        return redirect('album:album_detail', pk=album.pk)
    
    # Get the requested part
    part = parts[part_number - 1]
    
    # Clean album name for filename
    clean_album_name = "".join(c for c in album.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_album_name = clean_album_name.replace(' ', '_')
    
    if len(parts) > 1:
        filename = f"{clean_album_name}_part{part_number}_of_{len(parts)}.zip"
    else:
        filename = f"{clean_album_name}_complete.zip"
    
    # Create ZIP file
    zip_buffer = BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in part['items']:
                try:
                    zf.write(item['path'], item['arcname'])
                except (OSError, ValueError):
                    # Skip files that can't be read
                    continue
        
        # Log the download
        log_user_action('album_downloaded', request.user, 'album', album.id)
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error creating ZIP file: {str(e)}')
        return redirect('album:album_detail', pk=album.pk)
