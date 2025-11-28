"""
Management command to clean up orphaned media file references in the database.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from album.models import Photo, Video

class Command(BaseCommand):
    help = 'Clean up orphaned media file references where files no longer exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )
        parser.add_argument(
            '--fix-thumbnails',
            action='store_true',
            help='Regenerate missing thumbnails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_thumbnails = options['fix_thumbnails']
        
        self.stdout.write(self.style.SUCCESS('🔍 Scanning for orphaned media references...'))
        
        # Check Photos
        photos_fixed = 0
        photos_deleted = 0
        
        for photo in Photo.objects.all():
            issues = []
            
            # Check main image file
            if photo.image:
                try:
                    if not os.path.exists(photo.image.path):
                        issues.append(f"Missing image: {photo.image.path}")
                except (ValueError, FileNotFoundError):
                    issues.append(f"Invalid image path: {photo.image}")
                
            # Check thumbnail file (careful with ImageKit auto-generation)
            if hasattr(photo, 'thumbnail') and photo.thumbnail:
                try:
                    # Get the thumbnail path without triggering generation
                    thumbnail_path = photo.thumbnail.path
                    if not os.path.exists(thumbnail_path):
                        issues.append(f"Missing thumbnail: {thumbnail_path}")
                except (ValueError, FileNotFoundError, AttributeError):
                    issues.append("Invalid thumbnail reference")
                
            if issues:
                self.stdout.write(f"📸 Photo {photo.pk}: {photo.title}")
                for issue in issues:
                    self.stdout.write(f"  ❌ {issue}")
                
                if not dry_run:
                    # Try to find the file with similar name
                    if photo.image:
                        try:
                            if not os.path.exists(photo.image.path):
                                original_name = os.path.basename(photo.image.path)
                                base_name = original_name.split('_')[0]  # Remove Django suffix
                                
                                # Look for files with similar base name
                                media_dir = os.path.dirname(photo.image.path)
                                if os.path.exists(media_dir):
                                    for file in os.listdir(media_dir):
                                        if file.startswith(base_name) and file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                                            # Found a similar file, update the reference
                                            new_path = os.path.join(media_dir, file)
                                            relative_path = os.path.relpath(new_path, settings.MEDIA_ROOT)
                                            photo.image = relative_path
                                            photo.save()
                                            self.stdout.write(f"  ✅ Fixed: Updated to {file}")
                                            photos_fixed += 1
                                            break
                                    else:
                                        # No similar file found, delete the photo record
                                        photo.delete()
                                        self.stdout.write("  🗑️  Deleted orphaned photo record")
                                        photos_deleted += 1
                                else:
                                    photo.delete()
                                    self.stdout.write("  🗑️  Deleted orphaned photo record")
                                    photos_deleted += 1
                        except (ValueError, FileNotFoundError):
                            # Invalid image reference, delete the photo
                            photo.delete()
                            self.stdout.write("  🗑️  Deleted photo with invalid reference")
                            photos_deleted += 1
        
        # Check Videos
        videos_fixed = 0
        videos_deleted = 0
        
        for video in Video.objects.all():
            issues = []
            
            # Check main video file
            if video.video_file and not os.path.exists(video.video_file.path):
                issues.append(f"Missing video: {video.video_file.path}")
                
            # Check thumbnail file
            if video.thumbnail and not os.path.exists(video.thumbnail.path):
                issues.append(f"Missing thumbnail: {video.thumbnail.path}")
                
            if issues:
                self.stdout.write(f"🎬 Video {video.pk}: {video.title}")
                for issue in issues:
                    self.stdout.write(f"  ❌ {issue}")
                
                if not dry_run:
                    # Try to find the file with similar name
                    if video.video_file and not os.path.exists(video.video_file.path):
                        original_name = os.path.basename(video.video_file.path)
                        base_name = original_name.split('_')[0]
                        
                        # Look for files with similar base name
                        media_dir = os.path.dirname(video.video_file.path)
                        if os.path.exists(media_dir):
                            for file in os.listdir(media_dir):
                                if file.startswith(base_name) and file.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                                    # Found a similar file, update the reference
                                    new_path = os.path.join(media_dir, file)
                                    relative_path = os.path.relpath(new_path, settings.MEDIA_ROOT)
                                    video.video_file = relative_path
                                    video.save()
                                    self.stdout.write(f"  ✅ Fixed: Updated to {file}")
                                    videos_fixed += 1
                                    break
                            else:
                                # No similar file found, delete the video record
                                video.delete()
                                self.stdout.write("  🗑️  Deleted orphaned video record")
                                videos_deleted += 1
                        else:
                            video.delete()
                            self.stdout.write("  🗑️  Deleted orphaned video record")
                            videos_deleted += 1
        
        # Generate missing thumbnails if requested
        if fix_thumbnails and not dry_run:
            self.stdout.write(self.style.SUCCESS('🖼️  Regenerating missing thumbnails...'))
            from django.core.management import call_command
            call_command('generate_thumbnails')
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\\n📊 Summary:'))
        if dry_run:
            self.stdout.write('🔍 Dry run - no changes made')
        else:
            self.stdout.write(f'📸 Photos fixed: {photos_fixed}')
            self.stdout.write(f'📸 Photos deleted: {photos_deleted}')
            self.stdout.write(f'🎬 Videos fixed: {videos_fixed}')
            self.stdout.write(f'🎬 Videos deleted: {videos_deleted}')
            
            if fix_thumbnails:
                self.stdout.write('🖼️  Thumbnails regenerated')
        
        self.stdout.write(self.style.SUCCESS('✅ Media cleanup complete!'))