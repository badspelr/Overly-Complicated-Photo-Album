"""
Bulk operations service for managing multiple media items.
"""
import os
from django.db import transaction
from django.core.files.storage import default_storage
from django.utils import timezone
from ..models import Photo, Video, Album, Category
from ..views.base_views import check_object_permission


class BulkOperationsService:
    """Service for bulk operations on media items."""

    @staticmethod
    @transaction.atomic
    def bulk_delete_media(media_ids, user):
        """
        Bulk delete photos and videos.

        Args:
            media_ids: List of tuples [(type, id), ...] where type is 'photo' or 'video'
            user: User performing the operation

        Returns:
            Dict with success/failure counts and details
        """
        results = {
            'deleted': 0,
            'failed': 0,
            'errors': [],
            'deleted_files': []
        }

        for media_type, media_id in media_ids:
            try:
                if media_type == 'photo':
                    media = Photo.objects.get(pk=media_id)
                    # Check permissions using action-based system
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to delete photo {media_id}")
                        results['failed'] += 1
                        continue

                    # Delete files
                    if media.image:
                        media.image.delete()
                    if media.thumbnail:
                        media.thumbnail.delete()
                    if media.optimized:
                        media.optimized.delete()

                    media.delete()
                    results['deleted'] += 1
                    results['deleted_files'].append(f"photo_{media_id}")

                elif media_type == 'video':
                    media = Video.objects.get(pk=media_id)
                    # Check permissions using action-based system
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to delete video {media_id}")
                        results['failed'] += 1
                        continue

                    # Delete file
                    if media.video:
                        media.video.delete()

                    media.delete()
                    results['deleted'] += 1
                    results['deleted_files'].append(f"video_{media_id}")

            except Exception as e:
                results['errors'].append(f"Error deleting {media_type} {media_id}: {str(e)}")
                results['failed'] += 1

        return results

    @staticmethod
    @transaction.atomic
    def bulk_move_media(media_ids, target_album_id, user):
        """
        Bulk move media to different album.

        Args:
            media_ids: List of tuples [(type, id), ...]
            target_album_id: ID of target album
            user: User performing the operation

        Returns:
            Dict with success/failure counts
        """
        results = {
            'moved': 0,
            'failed': 0,
            'errors': []
        }

        try:
            target_album = Album.objects.get(pk=target_album_id)
            # Check if user can add to target album
            if not check_object_permission(user, target_album, 'album', action='delete'):
                return {'moved': 0, 'failed': len(media_ids), 'errors': ['No permission to add to target album']}
        except Album.DoesNotExist:
            return {'moved': 0, 'failed': len(media_ids), 'errors': ['Target album not found']}

        for media_type, media_id in media_ids:
            try:
                if media_type == 'photo':
                    media = Photo.objects.get(pk=media_id)
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to move photo {media_id}")
                        results['failed'] += 1
                        continue

                    media.album = target_album
                    media.save()
                    results['moved'] += 1

                elif media_type == 'video':
                    media = Video.objects.get(pk=media_id)
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to move video {media_id}")
                        results['failed'] += 1
                        continue

                    media.album = target_album
                    media.save()
                    results['moved'] += 1

            except Exception as e:
                results['errors'].append(f"Error moving {media_type} {media_id}: {str(e)}")
                results['failed'] += 1

        return results

    @staticmethod
    @transaction.atomic
    def bulk_update_category(media_ids, category_id, user):
        """
        Bulk update category for media items.

        Args:
            media_ids: List of tuples [(type, id), ...]
            category_id: ID of target category (None to remove category)
            user: User performing the operation

        Returns:
            Dict with success/failure counts
        """
        results = {
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        category = None
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
                # Check if user owns the category
                if not (user.is_superuser or category.created_by == user):
                    return {'updated': 0, 'failed': len(media_ids), 'errors': ['No permission to use this category']}
            except Category.DoesNotExist:
                return {'updated': 0, 'failed': len(media_ids), 'errors': ['Category not found']}

        for media_type, media_id in media_ids:
            try:
                if media_type == 'photo':
                    media = Photo.objects.get(pk=media_id)
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to update photo {media_id}")
                        results['failed'] += 1
                        continue

                    media.category = category
                    media.save()
                    results['updated'] += 1

                elif media_type == 'video':
                    media = Video.objects.get(pk=media_id)
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to update video {media_id}")
                        results['failed'] += 1
                        continue

                    media.category = category
                    media.save()
                    results['updated'] += 1

            except Exception as e:
                results['errors'].append(f"Error updating {media_type} {media_id}: {str(e)}")
                results['failed'] += 1

        return results

    @staticmethod
    @transaction.atomic
    def bulk_add_tags(media_ids, tags_string, user):
        """
        Bulk add tags to media items.

        Args:
            media_ids: List of tuples [(type, id), ...]
            tags_string: Comma-separated string of tags
            user: User performing the operation

        Returns:
            Dict with success/failure counts
        """
        from ..models import Tag

        results = {
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        # Parse and prepare tags
        tag_names = [name.strip() for name in tags_string.split(',') if name.strip()]
        if not tag_names:
            return {'updated': 0, 'failed': len(media_ids), 'errors': ['No valid tags provided']}

        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name, defaults={'created_by': user})
            tags.append(tag)

        for media_type, media_id in media_ids:
            try:
                if media_type == 'photo':
                    media = Photo.objects.get(pk=media_id)
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to tag photo {media_id}")
                        results['failed'] += 1
                        continue
                    media.tags.add(*tags)
                    results['updated'] += 1

                elif media_type == 'video':
                    media = Video.objects.get(pk=media_id)
                    if not check_object_permission(user, media.album, 'album', action='delete'):
                        results['errors'].append(f"No permission to tag video {media_id}")
                        results['failed'] += 1
                        continue
                    media.tags.add(*tags)
                    results['updated'] += 1

            except Exception as e:
                results['errors'].append(f"Error tagging {media_type} {media_id}: {str(e)}")
                results['failed'] += 1
        
        return results

    @staticmethod
    def bulk_download_media(media_ids, user, temp_dir=None):
        """
        Prepare bulk download of media files.

        Args:
            media_ids: List of tuples [(type, id), ...]
            user: User requesting download
            temp_dir: Temporary directory for zip creation

        Returns:
            Path to zip file or None if failed
        """
        import zipfile
        import tempfile

        if not temp_dir:
            temp_dir = tempfile.mkdtemp()

        zip_path = os.path.join(temp_dir, f'bulk_download_{user.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip')

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for media_type, media_id in media_ids:
                    try:
                        if media_type == 'photo':
                            media = Photo.objects.get(pk=media_id)
                            if not check_object_permission(user, media.album, 'album', action='view'):
                                continue

                            # Add original image
                            if media.image and default_storage.exists(media.image.name):
                                zip_file.write(
                                    default_storage.path(media.image.name),
                                    f"photos/{media.title}_{media_id}{os.path.splitext(media.image.name)[1]}"
                                )

                        elif media_type == 'video':
                            media = Video.objects.get(pk=media_id)
                            if not check_object_permission(user, media.album, 'album', action='view'):
                                continue

                            # Add video file
                            if media.video and default_storage.exists(media.video.name):
                                zip_file.write(
                                    default_storage.path(media.video.name),
                                    f"videos/{media.title}_{media_id}{os.path.splitext(media.video.name)[1]}"
                                )

                    except Exception as e:
                        print(f"Error adding {media_type} {media_id} to zip: {e}")
                        continue

            return zip_path

        except Exception as e:
            print(f"Error creating zip file: {e}")
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return None
