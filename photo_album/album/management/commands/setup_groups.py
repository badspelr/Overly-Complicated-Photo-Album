"""
Management command to set up initial user groups and permissions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from album.models import Album, Photo, Video, Category


class Command(BaseCommand):
    help = 'Create initial user groups and assign permissions'

    def handle(self, *args, **options):
        # Create Album Admin group
        album_admin_group, created = Group.objects.get_or_create(name='Album Admin')
        if created:
            self.stdout.write('Created "Album Admin" group')
        else:
            self.stdout.write('"Album Admin" group already exists')

        # Create Viewer group
        viewer_group, created = Group.objects.get_or_create(name='Viewer')
        if created:
            self.stdout.write('Created "Viewer" group')
        else:
            self.stdout.write('"Viewer" group already exists')

        # Get content types
        album_ct = ContentType.objects.get_for_model(Album)
        photo_ct = ContentType.objects.get_for_model(Photo)
        video_ct = ContentType.objects.get_for_model(Video)
        category_ct = ContentType.objects.get_for_model(Category)
        user_ct = ContentType.objects.get_for_model(User)
        group_ct = ContentType.objects.get_for_model(Group)

        # Album Admin permissions (including user management)
        album_admin_permissions = [
            # Album permissions
            Permission.objects.get(content_type=album_ct, codename='add_album'),
            Permission.objects.get(content_type=album_ct, codename='change_album'),
            Permission.objects.get(content_type=album_ct, codename='delete_album'),
            Permission.objects.get(content_type=album_ct, codename='view_album'),

            # Photo permissions
            Permission.objects.get(content_type=photo_ct, codename='add_photo'),
            Permission.objects.get(content_type=photo_ct, codename='change_photo'),
            Permission.objects.get(content_type=photo_ct, codename='delete_photo'),
            Permission.objects.get(content_type=photo_ct, codename='view_photo'),

            # Video permissions
            Permission.objects.get(content_type=video_ct, codename='add_video'),
            Permission.objects.get(content_type=video_ct, codename='change_video'),
            Permission.objects.get(content_type=video_ct, codename='delete_video'),
            Permission.objects.get(content_type=video_ct, codename='view_video'),

            # Category permissions
            Permission.objects.get(content_type=category_ct, codename='add_category'),
            Permission.objects.get(content_type=category_ct, codename='change_category'),
            Permission.objects.get(content_type=category_ct, codename='view_category'),

            # User management permissions
            Permission.objects.get(content_type=user_ct, codename='add_user'),
            Permission.objects.get(content_type=user_ct, codename='change_user'),
            Permission.objects.get(content_type=user_ct, codename='view_user'),

            # Group management permissions
            Permission.objects.get(content_type=group_ct, codename='add_group'),
            Permission.objects.get(content_type=group_ct, codename='change_group'),
            Permission.objects.get(content_type=group_ct, codename='view_group'),
        ]

        # Viewer permissions (read-only)
        viewer_permissions = [
            Permission.objects.get(content_type=album_ct, codename='view_album'),
            Permission.objects.get(content_type=photo_ct, codename='view_photo'),
            Permission.objects.get(content_type=video_ct, codename='view_video'),
            Permission.objects.get(content_type=category_ct, codename='view_category'),
        ]

        # Assign permissions to groups
        album_admin_group.permissions.set(album_admin_permissions)
        viewer_group.permissions.set(viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully configured permissions:\n'
                f'- Album Admin: {len(album_admin_permissions)} permissions\n'
                f'- Viewer: {len(viewer_permissions)} permissions'
            )
        )