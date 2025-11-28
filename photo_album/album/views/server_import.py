"""
Views for server-side media import functionality.
Allows users to import photos/videos from their personal server upload directory.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.files import File
from pathlib import Path
from PIL import Image
from django import forms
import hashlib

from album.models import Album, Photo, Video


class ServerImportForm(forms.Form):
    """Form for selecting target album for server imports."""
    media_type = forms.ChoiceField(
        choices=[('photos', 'Photos'), ('videos', 'Videos')],
        widget=forms.RadioSelect,
        initial='photos',
        label='Media Type'
    )
    album = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        label='Existing Album',
        help_text='Select an existing album, or create a new one below',
        empty_label='-- Select an album --'
    )
    new_album_title = forms.CharField(
        max_length=100,
        required=False,
        label='Or Create New Album',
        help_text='Enter a name to create a new album'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].queryset = Album.objects.filter(owner=user).order_by('title')
    
    def clean(self):
        cleaned_data = super().clean()
        album = cleaned_data.get('album')
        new_album_title = cleaned_data.get('new_album_title')
        
        if not album and not new_album_title:
            raise forms.ValidationError('Please select an existing album or enter a name for a new album')
        
        if album and new_album_title:
            raise forms.ValidationError('Please choose either an existing album OR create a new one, not both')
        
        return cleaned_data


@login_required
def server_import_view(request):
    """
    Display files in user's server upload directory and handle imports.
    Recursively scans all subdirectories in user's personal upload folder.
    """
    # Get user's personal upload directory
    user_upload_path = Path(settings.MEDIA_ROOT) / 'server_uploads' / request.user.username
    
    # Create directory if it doesn't exist
    user_upload_path.mkdir(parents=True, exist_ok=True)
    
    # Supported file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
    
    # Recursively find all files in all subdirectories
    all_files = []
    if user_upload_path.exists():
        all_files = list(user_upload_path.rglob('*'))  # rglob recursively searches
    
    image_files = [f for f in all_files if f.is_file() and f.suffix.lower() in image_extensions]
    video_files = [f for f in all_files if f.is_file() and f.suffix.lower() in video_extensions]
    
    if request.method == 'POST':
        form = ServerImportForm(request.user, request.POST)
        
        if form.is_valid():
            # Get or create target album
            if form.cleaned_data['new_album_title']:
                target_album = Album.objects.create(
                    title=form.cleaned_data['new_album_title'],
                    owner=request.user,
                    is_public=False
                )
            else:
                target_album = form.cleaned_data['album']
            
            media_type = form.cleaned_data['media_type']
            files_to_import = image_files if media_type == 'photos' else video_files
            
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            # Import photos
            if media_type == 'photos':
                for image_file in files_to_import:
                    try:
                        # Verify it's actually an image
                        with Image.open(image_file) as img:
                            img.verify()
                        
                        # Calculate MD5 hash to check for duplicates
                        with open(image_file, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        
                        # Check if photo with same hash already exists in this album
                        existing_photo = Photo.objects.filter(
                            album=target_album,
                            checksum=file_hash
                        ).first()
                        
                        if existing_photo:
                            # Skip duplicate
                            skipped_count += 1
                            messages.info(request, f'Skipped duplicate: {image_file.name}')
                            # Delete the duplicate file from server_uploads
                            image_file.unlink()
                            continue
                        
                        # Create Photo object
                        photo = Photo(
                            album=target_album,
                            title=image_file.stem,
                            checksum=file_hash,
                        )
                        
                        # Save the file
                        with open(image_file, 'rb') as f:
                            photo.image.save(image_file.name, File(f), save=True)
                        
                        # Delete original
                        image_file.unlink()
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        messages.error(request, f'Error importing {image_file.name}: {str(e)}')
            
            # Import videos
            else:
                for video_file in files_to_import:
                    try:
                        # Create Video object
                        video = Video(
                            album=target_album,
                            title=video_file.stem,
                        )
                        
                        # Save the file
                        with open(video_file, 'rb') as f:
                            video.video.save(video_file.name, File(f), save=True)
                        
                        # Delete original
                        video_file.unlink()
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        messages.error(request, f'Error importing {video_file.name}: {str(e)}')
            
            # Show results
            if imported_count > 0:
                messages.success(
                    request,
                    f'Successfully imported {imported_count} {media_type} to "{target_album.title}" album'
                )
            
            if skipped_count > 0:
                messages.info(
                    request,
                    f'Skipped {skipped_count} duplicate {media_type} (already in album)'
                )
            
            if error_count > 0:
                messages.warning(request, f'Failed to import {error_count} file(s)')
            
            return redirect('album:server_import')
    else:
        form = ServerImportForm(request.user)
    
    # Create list of files with their relative paths for display
    image_file_list = []
    for f in image_files:
        rel_path = f.relative_to(user_upload_path)
        image_file_list.append(str(rel_path))
    
    video_file_list = []
    for f in video_files:
        rel_path = f.relative_to(user_upload_path)
        video_file_list.append(str(rel_path))
    
    context = {
        'form': form,
        'image_files': image_file_list,
        'video_files': video_file_list,
        'user_upload_path': str(user_upload_path),
        'has_files': len(image_files) > 0 or len(video_files) > 0,
        'image_count': len(image_files),
        'video_count': len(video_files),
    }
    
    return render(request, 'album/server_import.html', context)
