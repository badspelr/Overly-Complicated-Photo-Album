from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import SiteSettings, Category, Album, Photo, Video, Tag, AlbumShareLink, Favorite, AIProcessingSettings
from .admin_site import custom_admin_site


class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 0
    readonly_fields = ('ai_description', 'ai_tags', 'uploaded_at')

class VideoInline(admin.StackedInline):
    model = Video
    extra = 0
    readonly_fields = ('ai_description', 'ai_tags', 'uploaded_at')

class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'max_album_download_size_mb')
    fieldsets = (
        ('Basic Settings', {
            'fields': ('title', 'description')
        }),
        ('Download Settings', {
            'fields': ('max_album_download_size_mb',),
            'description': 'Configure limits for album downloads'
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'description')
    list_filter = ('created_by',)
    search_fields = ('name', 'description')

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'photo_count', 'video_count', 'created_at')
    list_filter = ('is_public', 'created_at', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    filter_horizontal = ('viewers',)
    readonly_fields = ('created_at',)
    inlines = [PhotoInline, VideoInline]
    actions = ['download_album']
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'
    
    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = 'Videos'
    
    @admin.action(description='Download album(s) as ZIP file')
    def download_album(self, request, queryset):
        """Download selected album(s) as ZIP file(s) - supports multi-part for large albums."""
        import os
        import zipfile
        from io import BytesIO
        from django.http import HttpResponse
        from django.shortcuts import render
        
        # Get max size from settings (default to 2GB if not configured)
        try:
            site_settings = SiteSettings.objects.first()
            max_size_mb = site_settings.max_album_download_size_mb if site_settings else 2048
        except Exception:
            max_size_mb = 2048
        
        MAX_PART_SIZE_BYTES = max_size_mb * 1024 * 1024  # Convert MB to bytes
        
        # If multiple albums selected, show error
        if queryset.count() > 1:
            self.message_user(
                request,
                'Please select only one album at a time for download',
                level='ERROR'
            )
            return
        
        album = queryset.first()
        
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
        
        # Handle download_part in GET request for actual download
        if 'download_part' in request.GET:
            part_number = int(request.GET.get('download_part', 1))
            
            if part_number < 1 or part_number > len(parts):
                self.message_user(request, 'Invalid part number.', level='ERROR')
                return
            
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
                
                response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                self.message_user(
                    request,
                    f'Successfully downloaded part {part_number} of "{album.title}"',
                    level='SUCCESS'
                )
                
                return response
                
            except Exception as e:
                self.message_user(
                    request,
                    f'Error creating ZIP file: {str(e)}',
                    level='ERROR'
                )
                return
        
        # Show confirmation page
        context = {
            'title': f'Download Album: {album.title}',
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
            'photo_count': len(photo_data),
            'video_count': len(video_data),
            'total_size': format_size(total_size),
            'total_size_bytes': total_size,
            'max_size': format_size(MAX_PART_SIZE_BYTES),
            'is_multipart': len(parts) > 1,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/album/download_album.html', context)

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'album_owner', 'category', 'get_tags', 'uploaded_at', 'ai_analyzed')
    list_filter = ('uploaded_at', 'album', 'album__owner', 'category')
    search_fields = ('title', 'ai_description', 'ai_tags', 'album__owner__username', 'tags__name')
    readonly_fields = ('uploaded_at', 'ai_description', 'ai_tags', 'image', 'text_embedding', 'ai_confidence_score', 'nsfw_score', 'is_safe_content', 'ai_processed', 'ai_processing_date', 'perceptual_hash', 'processing_status', 'embedding', 'ai_processing_error')
    actions = ['import_from_server', 'move_to_album']
    
    def get_tags(self, obj):
        """Display comma-separated list of tags"""
        return ", ".join([tag.name for tag in obj.tags.all()]) if obj.tags.exists() else "-"
    get_tags.short_description = 'Tags'
    
    def album_owner(self, obj):
        return obj.album.owner.username if obj.album else None
    album_owner.short_description = 'Owner'
    album_owner.admin_order_field = 'album__owner__username'
    
    def ai_analyzed(self, obj):
        return bool(obj.ai_description)
    ai_analyzed.boolean = True
    ai_analyzed.short_description = 'AI Analyzed'
    
    @admin.action(description='Move selected photos to another album')
    def move_to_album(self, request, queryset):
        """Move selected photos to a different album."""
        from django import forms
        from django.shortcuts import render
        
        # Get all unique owners of the selected photos
        owner_ids = queryset.values_list('album__owner', flat=True).distinct()
        owners = User.objects.filter(id__in=owner_ids)
        
        # Define the form for album selection
        class MoveToAlbumForm(forms.Form):
            owner = forms.ModelChoiceField(
                queryset=owners,
                required=True,
                label='Album Owner',
                help_text='Select the owner whose albums to choose from',
                initial=owners.first() if owners.count() == 1 else None
            )
            album = forms.ModelChoiceField(
                queryset=Album.objects.none(),  # Will be populated based on owner selection
                required=False,
                label='Existing Album',
                help_text='Select an existing album, or create a new one below',
                empty_label='-- Select an album --'
            )
            new_album_title = forms.CharField(
                max_length=100,
                required=False,
                label='Or Create New Album',
                help_text='Enter a name to create a new album for these photos'
            )
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # If owner is selected, filter albums by that owner
                if 'owner' in self.data:
                    try:
                        owner_id = int(self.data.get('owner'))
                        self.fields['album'].queryset = Album.objects.filter(owner_id=owner_id).order_by('title')
                    except (ValueError, TypeError):
                        pass
                elif self.initial.get('owner'):
                    self.fields['album'].queryset = Album.objects.filter(owner=self.initial['owner']).order_by('title')
            
            def clean(self):
                cleaned_data = super().clean()
                album = cleaned_data.get('album')
                new_album_title = cleaned_data.get('new_album_title')
                owner = cleaned_data.get('owner')
                
                if not album and not new_album_title:
                    raise forms.ValidationError('Please select an existing album or enter a name for a new album')
                
                if album and new_album_title:
                    raise forms.ValidationError('Please choose either an existing album OR create a new one, not both')
                
                if not owner:
                    raise forms.ValidationError('Please select an album owner')
                
                return cleaned_data
        
        # If the form was submitted
        if 'apply' in request.POST:
            form = MoveToAlbumForm(request.POST)
            
            if form.is_valid():
                owner = form.cleaned_data['owner']
                
                # Get or create the target album
                if form.cleaned_data['new_album_title']:
                    target_album = Album.objects.create(
                        title=form.cleaned_data['new_album_title'],
                        owner=owner,
                        is_public=False
                    )
                else:
                    target_album = form.cleaned_data['album']
                
                # Move all selected photos
                count = queryset.update(album=target_album)
                
                self.message_user(
                    request,
                    f'Successfully moved {count} photo(s) to "{target_album.title}" album (owner: {owner.username})',
                    level='SUCCESS'
                )
                
                # Redirect back to the changelist
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                return HttpResponseRedirect(reverse('admin:album_photo_changelist'))
            else:
                # Show form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        self.message_user(request, f'{field}: {error}', level='ERROR')
        elif 'refresh_albums' in request.POST:
            # Owner changed, reload form with new albums
            form = MoveToAlbumForm(request.POST)
        else:
            initial_data = {}
            if owners.count() == 1:
                initial_data['owner'] = owners.first()
            form = MoveToAlbumForm(initial=initial_data)
        
        # Show the intermediate page with album selection
        context = {
            'title': f'Move {queryset.count()} Photo(s) to Album',
            'form': form,
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/album/move_to_album.html', context)
    
    @admin.action(description='Import photos from server uploads directory')
    def import_from_server(self, request, queryset):
        """Import photos from media/server_uploads/ directory."""
        from django.conf import settings
        from django.core.files import File
        from pathlib import Path
        from PIL import Image
        from django import forms
        from django.shortcuts import render
        
        server_uploads_path = Path(settings.MEDIA_ROOT) / 'server_uploads'
        
        if not server_uploads_path.exists():
            self.message_user(request, 'Server uploads directory does not exist', level='ERROR')
            return
        
        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
        # Find all image files
        image_files = [
            f for f in server_uploads_path.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            self.message_user(request, 'No image files found in server_uploads directory', level='WARNING')
            return
        
        # Define the form for album selection
        class AlbumSelectionForm(forms.Form):
            album = forms.ModelChoiceField(
                queryset=Album.objects.filter(owner=request.user).order_by('title'),
                required=False,
                label='Existing Album',
                help_text='Select an existing album, or create a new one below',
                empty_label='-- Select an album --'
            )
            new_album_title = forms.CharField(
                max_length=100,
                required=False,
                label='Or Create New Album',
                help_text='Enter a name to create a new album for these photos'
            )
            
            def clean(self):
                cleaned_data = super().clean()
                album = cleaned_data.get('album')
                new_album_title = cleaned_data.get('new_album_title')
                
                if not album and not new_album_title:
                    raise forms.ValidationError('Please select an existing album or enter a name for a new album')
                
                if album and new_album_title:
                    raise forms.ValidationError('Please choose either an existing album OR create a new one, not both')
                
                return cleaned_data
        
        # If the form was submitted
        if 'apply' in request.POST:
            form = AlbumSelectionForm(request.POST)
            
            if form.is_valid():
                # Get or create the target album
                if form.cleaned_data['new_album_title']:
                    target_album = Album.objects.create(
                        title=form.cleaned_data['new_album_title'],
                        owner=request.user,
                        is_public=False
                    )
                else:
                    target_album = form.cleaned_data['album']
                
                imported_count = 0
                error_count = 0
                
                for image_file in image_files:
                    try:
                        # Verify it's actually an image
                        with Image.open(image_file) as img:
                            img.verify()
                        
                        # Create Photo object
                        photo = Photo(
                            album=target_album,
                            title=image_file.stem,  # Filename without extension
                        )
                        
                        # Open and save the file to the photo object
                        with open(image_file, 'rb') as f:
                            photo.image.save(image_file.name, File(f), save=True)
                        
                        # Delete the original file from server_uploads
                        image_file.unlink()
                        
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        self.message_user(
                            request,
                            f'Error importing {image_file.name}: {str(e)}',
                            level='ERROR'
                        )
                
                if imported_count > 0:
                    self.message_user(
                        request,
                        f'Successfully imported {imported_count} photo(s) to "{target_album.title}" album',
                        level='SUCCESS'
                    )
                
                if error_count > 0:
                    self.message_user(
                        request,
                        f'Failed to import {error_count} file(s)',
                        level='WARNING'
                    )
                
                return
        else:
            form = AlbumSelectionForm()
        
        # Show the intermediate page with album selection
        context = {
            'title': 'Select Album for Import',
            'form': form,
            'image_files': [f.name for f in image_files],
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/album/import_select_album.html', context)

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'album_owner', 'category', 'uploaded_at', 'ai_analyzed')
    list_filter = ('uploaded_at', 'album', 'album__owner', 'category')
    search_fields = ('title', 'ai_description', 'ai_tags', 'album__owner__username')
    readonly_fields = ('uploaded_at', 'ai_description', 'ai_tags')
    fields = ('title', 'album', 'video', 'category', 'tags', 'uploaded_at', 'ai_description', 'ai_tags')
    actions = ['import_from_server', 'move_to_album']
    
    def album_owner(self, obj):
        return obj.album.owner.username if obj.album else None
    album_owner.short_description = 'Owner'
    album_owner.admin_order_field = 'album__owner__username'
    
    def ai_analyzed(self, obj):
        return bool(obj.ai_description)
    ai_analyzed.boolean = True
    ai_analyzed.short_description = 'AI Analyzed'
    
    @admin.action(description='Move selected videos to another album')
    def move_to_album(self, request, queryset):
        """Move selected videos to a different album."""
        from django import forms
        from django.shortcuts import render
        
        # Get all unique owners of the selected videos
        owner_ids = queryset.values_list('album__owner', flat=True).distinct()
        owners = User.objects.filter(id__in=owner_ids)
        
        # Define the form for album selection
        class MoveToAlbumForm(forms.Form):
            owner = forms.ModelChoiceField(
                queryset=owners,
                required=True,
                label='Album Owner',
                help_text='Select the owner whose albums to choose from',
                initial=owners.first() if owners.count() == 1 else None
            )
            album = forms.ModelChoiceField(
                queryset=Album.objects.none(),  # Will be populated based on owner selection
                required=False,
                label='Existing Album',
                help_text='Select an existing album, or create a new one below',
                empty_label='-- Select an album --'
            )
            new_album_title = forms.CharField(
                max_length=100,
                required=False,
                label='Or Create New Album',
                help_text='Enter a name to create a new album for these videos'
            )
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # If owner is selected, filter albums by that owner
                if 'owner' in self.data:
                    try:
                        owner_id = int(self.data.get('owner'))
                        self.fields['album'].queryset = Album.objects.filter(owner_id=owner_id).order_by('title')
                    except (ValueError, TypeError):
                        pass
                elif self.initial.get('owner'):
                    self.fields['album'].queryset = Album.objects.filter(owner=self.initial['owner']).order_by('title')
            
            def clean(self):
                cleaned_data = super().clean()
                album = cleaned_data.get('album')
                new_album_title = cleaned_data.get('new_album_title')
                owner = cleaned_data.get('owner')
                
                if not album and not new_album_title:
                    raise forms.ValidationError('Please select an existing album or enter a name for a new album')
                
                if album and new_album_title:
                    raise forms.ValidationError('Please choose either an existing album OR create a new one, not both')
                
                if not owner:
                    raise forms.ValidationError('Please select an album owner')
                
                return cleaned_data
        
        # If the form was submitted
        if 'apply' in request.POST:
            form = MoveToAlbumForm(request.POST)
            
            if form.is_valid():
                owner = form.cleaned_data['owner']
                
                # Get or create the target album
                if form.cleaned_data['new_album_title']:
                    target_album = Album.objects.create(
                        title=form.cleaned_data['new_album_title'],
                        owner=owner,
                        is_public=False
                    )
                else:
                    target_album = form.cleaned_data['album']
                
                # Move all selected videos
                count = queryset.update(album=target_album)
                
                self.message_user(
                    request,
                    f'Successfully moved {count} video(s) to "{target_album.title}" album (owner: {owner.username})',
                    level='SUCCESS'
                )
                
                # Redirect back to the changelist
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                return HttpResponseRedirect(reverse('admin:album_video_changelist'))
            else:
                # Show form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        self.message_user(request, f'{field}: {error}', level='ERROR')
        elif 'refresh_albums' in request.POST:
            # Owner changed, reload form with new albums
            form = MoveToAlbumForm(request.POST)
        else:
            initial_data = {}
            if owners.count() == 1:
                initial_data['owner'] = owners.first()
            form = MoveToAlbumForm(initial=initial_data)
        
        # Show the intermediate page with album selection
        context = {
            'title': f'Move {queryset.count()} Video(s) to Album',
            'form': form,
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/album/move_to_album.html', context)
    
    @admin.action(description='Import videos from server uploads directory')
    def import_from_server(self, request, queryset):
        """Import videos from media/server_uploads/ directory."""
        from django.conf import settings
        from django.core.files import File
        from pathlib import Path
        from django import forms
        from django.shortcuts import render
        
        server_uploads_path = Path(settings.MEDIA_ROOT) / 'server_uploads'
        
        if not server_uploads_path.exists():
            self.message_user(request, 'Server uploads directory does not exist', level='ERROR')
            return
        
        # Supported video extensions
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
        
        # Find all video files
        video_files = [
            f for f in server_uploads_path.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]
        
        if not video_files:
            self.message_user(request, 'No video files found in server_uploads directory', level='WARNING')
            return
        
        # Define the form for album selection
        class AlbumSelectionForm(forms.Form):
            album = forms.ModelChoiceField(
                queryset=Album.objects.filter(owner=request.user).order_by('title'),
                required=False,
                label='Existing Album',
                help_text='Select an existing album, or create a new one below',
                empty_label='-- Select an album --'
            )
            new_album_title = forms.CharField(
                max_length=100,
                required=False,
                label='Or Create New Album',
                help_text='Enter a name to create a new album for these videos'
            )
            
            def clean(self):
                cleaned_data = super().clean()
                album = cleaned_data.get('album')
                new_album_title = cleaned_data.get('new_album_title')
                
                if not album and not new_album_title:
                    raise forms.ValidationError('Please select an existing album or enter a name for a new album')
                
                if album and new_album_title:
                    raise forms.ValidationError('Please choose either an existing album OR create a new one, not both')
                
                return cleaned_data
        
        # If the form was submitted
        if 'apply' in request.POST:
            form = AlbumSelectionForm(request.POST)
            
            if form.is_valid():
                # Get or create the target album
                if form.cleaned_data['new_album_title']:
                    target_album = Album.objects.create(
                        title=form.cleaned_data['new_album_title'],
                        owner=request.user,
                        is_public=False
                    )
                else:
                    target_album = form.cleaned_data['album']
                
                imported_count = 0
                error_count = 0
                
                for video_file in video_files:
                    try:
                        # Create Video object
                        video = Video(
                            album=target_album,
                            title=video_file.stem,  # Filename without extension
                        )
                        
                        # Open and save the file to the video object
                        with open(video_file, 'rb') as f:
                            video.video.save(video_file.name, File(f), save=True)
                        
                        # Delete the original file from server_uploads
                        video_file.unlink()
                        
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        self.message_user(
                            request,
                            f'Error importing {video_file.name}: {str(e)}',
                            level='ERROR'
                        )
                
                if imported_count > 0:
                    self.message_user(
                        request,
                        f'Successfully imported {imported_count} video(s) to "{target_album.title}" album',
                        level='SUCCESS'
                    )
                
                if error_count > 0:
                    self.message_user(
                        request,
                        f'Failed to import {error_count} file(s)',
                        level='WARNING'
                    )
                
                return
        else:
            form = AlbumSelectionForm()
        
        # Show the intermediate page with album selection
        context = {
            'title': 'Select Album for Import',
            'form': form,
            'video_files': [f.name for f in video_files],
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/album/import_select_album.html', context)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    list_filter = ('created_by',)
    search_fields = ('name',)

class AlbumShareLinkAdmin(admin.ModelAdmin):
    list_display = ('album', 'created_by', 'share_token', 'expires_at', 'is_active', 'created_at')
    list_filter = ('is_active', 'expires_at', 'created_at')
    search_fields = ('album__title', 'created_by__username', 'share_token')
    readonly_fields = ('created_at', 'share_token')

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_media_type', 'get_media_title', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'photo__title', 'video__title')
    readonly_fields = ('created',)
    
    def get_media_type(self, obj):
        """Display the type of favorited media"""
        return "Photo" if obj.photo else "Video"
    get_media_type.short_description = 'Type'
    
    def get_media_title(self, obj):
        """Display the title of the favorited media"""
        return obj.photo.title if obj.photo else obj.video.title
    get_media_title.short_description = 'Media Title'


class AIProcessingSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for AI processing settings.
    Singleton model - only one instance exists.
    """
    list_display = (
        'auto_process_on_upload',
        'scheduled_processing', 
        'batch_size',
        'schedule_hour',
        'schedule_minute',
        'last_modified'
    )
    
    fieldsets = (
        ('Processing Modes', {
            'fields': ('auto_process_on_upload', 'scheduled_processing'),
            'description': 'Control when AI processing occurs'
        }),
        ('Batch Processing Settings', {
            'fields': ('batch_size', 'processing_timeout'),
            'description': 'Configure batch processing parameters'
        }),
        ('Schedule Configuration', {
            'fields': ('schedule_hour', 'schedule_minute'),
            'description': 'Set the time for scheduled batch processing (24-hour format)'
        }),
        ('Information', {
            'fields': ('last_modified',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('last_modified',)
    
    def has_add_permission(self, request):
        # Singleton pattern - only allow one instance
        return not AIProcessingSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of the singleton instance
        return False
    
    def changelist_view(self, request, extra_context=None):
        """
        Redirect to the single instance edit page instead of showing a list.
        """
        from django.shortcuts import redirect
        # Get or create the singleton instance
        obj = AIProcessingSettings.load()
        return redirect('admin:album_aiprocessingsettings_change', obj.pk)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Ensure the singleton instance exists before showing the change form.
        """
        # Ensure singleton exists
        AIProcessingSettings.load()
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)


class UserAdmin(DjangoUserAdmin):
    """
    Custom User admin with email functionality.
    """
    actions = ['send_email_to_users']
    
    @admin.action(description='Send email to selected users')
    def send_email_to_users(self, request, queryset):
        """Send an email to selected users."""
        from django import forms
        from django.shortcuts import render
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Define the email form
        class EmailForm(forms.Form):
            subject = forms.CharField(
                max_length=200,
                required=True,
                label='Subject',
                widget=forms.TextInput(attrs={'size': '80'})
            )
            message = forms.CharField(
                required=True,
                label='Message',
                widget=forms.Textarea(attrs={'rows': 10, 'cols': 80})
            )
            send_to_all = forms.BooleanField(
                required=False,
                initial=False,
                label='Send to ALL registered users (ignores selection)',
                help_text='Check this to send email to all users in the system, not just selected ones'
            )
        
        # If the form was submitted
        if 'send' in request.POST:
            form = EmailForm(request.POST)
            
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                send_to_all = form.cleaned_data['send_to_all']
                
                # Determine recipient list
                if send_to_all:
                    recipients = User.objects.filter(is_active=True)
                else:
                    recipients = queryset.filter(is_active=True)
                
                # Get email addresses
                recipient_emails = [user.email for user in recipients if user.email]
                
                if not recipient_emails:
                    self.message_user(
                        request,
                        'No users with email addresses found',
                        level='WARNING'
                    )
                    return
                
                # Send email
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=recipient_emails,
                        fail_silently=False,
                    )
                    
                    self.message_user(
                        request,
                        f'Successfully sent email to {len(recipient_emails)} user(s)',
                        level='SUCCESS'
                    )
                    
                    # Redirect back to the changelist
                    from django.http import HttpResponseRedirect
                    from django.urls import reverse
                    return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
                    
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error sending email: {str(e)}',
                        level='ERROR'
                    )
            else:
                # Show form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        self.message_user(request, f'{field}: {error}', level='ERROR')
        else:
            form = EmailForm()
        
        # Show the email form
        context = {
            'title': 'Send Email to Users',
            'form': form,
            'queryset': queryset,
            'user_count': queryset.count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/album/send_email.html', context)

# Register all models with the custom admin site
custom_admin_site.register(SiteSettings, SiteSettingsAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Album, AlbumAdmin)
custom_admin_site.register(Photo, PhotoAdmin)
custom_admin_site.register(Video, VideoAdmin)
custom_admin_site.register(Tag, TagAdmin)
custom_admin_site.register(AlbumShareLink, AlbumShareLinkAdmin)
custom_admin_site.register(Favorite, FavoriteAdmin)
custom_admin_site.register(AIProcessingSettings, AIProcessingSettingsAdmin)

# Also register User model with custom admin site
custom_admin_site.register(User, UserAdmin)

