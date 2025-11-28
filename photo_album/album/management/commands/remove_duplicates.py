"""
Management command to remove duplicate photos based on MD5 hash.
Keeps the oldest upload and removes newer duplicates.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from album.models import Album, Photo
import hashlib
from collections import defaultdict

User = get_user_model()


class Command(BaseCommand):
    help = 'Remove duplicate photos from an album based on MD5 hash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the album owner',
            required=True
        )
        parser.add_argument(
            '--album',
            type=str,
            help='Album title',
            required=True
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        username = options['username']
        album_title = options['album']
        dry_run = options['dry_run']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return

        try:
            album = Album.objects.get(owner=user, title=album_title)
        except Album.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'Album "{album_title}" not found for user "{username}"'
            ))
            return

        photos = Photo.objects.filter(album=album)
        self.stdout.write(f'Checking {photos.count()} photos in "{album_title}"...\n')

        # Build hash map
        hash_map = defaultdict(list)
        for photo in photos:
            try:
                photo.image.open('rb')
                file_hash = hashlib.md5(photo.image.read()).hexdigest()
                photo.image.close()
                hash_map[file_hash].append(photo)
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f'Could not hash photo ID {photo.id}: {e}'
                ))

        # Find duplicates
        duplicates = {h: photos for h, photos in hash_map.items() if len(photos) > 1}

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicates found!'))
            return

        self.stdout.write(self.style.WARNING(
            f'Found {len(duplicates)} sets of duplicate files\n'
        ))

        total_to_delete = 0
        total_space_freed = 0

        for file_hash, dupes in duplicates.items():
            # Sort by upload date (oldest first)
            dupes.sort(key=lambda p: p.uploaded_at)
            
            # Keep the first (oldest), delete the rest
            keep = dupes[0]
            to_delete = dupes[1:]
            
            total_to_delete += len(to_delete)
            
            self.stdout.write(f'\nHash: {file_hash}')
            self.stdout.write(self.style.SUCCESS(
                f'  KEEP: ID {keep.id}, Title: {keep.title}, '
                f'Size: {keep.image.size:,} bytes, Uploaded: {keep.uploaded_at}'
            ))
            
            for photo in to_delete:
                total_space_freed += photo.image.size
                action = 'WOULD DELETE' if dry_run else 'DELETING'
                self.stdout.write(self.style.ERROR(
                    f'  {action}: ID {photo.id}, Title: {photo.title}, '
                    f'Size: {photo.image.size:,} bytes, Uploaded: {photo.uploaded_at}'
                ))
                
                if not dry_run:
                    # Delete the file and database entry
                    try:
                        photo.image.delete(save=False)
                        photo.delete()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'    Error deleting photo ID {photo.id}: {e}'
                        ))

        # Summary
        self.stdout.write('\n' + '='*70)
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: Would delete {total_to_delete} duplicate photos'
            ))
            self.stdout.write(self.style.WARNING(
                f'Would free {total_space_freed:,} bytes '
                f'({total_space_freed / (1024*1024):.2f} MB)'
            ))
            self.stdout.write('\nRun without --dry-run to actually delete the duplicates')
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Deleted {total_to_delete} duplicate photos'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Freed {total_space_freed:,} bytes '
                f'({total_space_freed / (1024*1024):.2f} MB)'
            ))
