"""
Django management command to manage cache.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from album.cache_utils import CacheManager, warm_user_cache, warm_album_cache
from album.models import Album


class Command(BaseCommand):
    help = 'Manage application cache'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['clear', 'warm', 'status'],
            help='Action to perform: clear, warm, or status'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID for warming user-specific cache'
        )
        parser.add_argument(
            '--album-id',
            type=int,
            help='Album ID for warming album-specific cache'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Pattern for selective cache clearing'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the command without making any changes to the cache.',
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'clear':
            self.clear_cache(options)
        elif action == 'warm':
            self.warm_cache(options)
        elif action == 'status':
            self.show_cache_status()

    def clear_cache(self, options):
        """Clear cache."""
        pattern = options.get('pattern')
        dry_run = options.get('dry_run')

        if dry_run:
            self.stdout.write(self.style.SUCCESS('Dry run: Cache would not be cleared.'))
            return
        
        if pattern:
            deleted_count = CacheManager.delete_pattern(pattern)
            self.stdout.write(
                self.style.SUCCESS(f'Cleared {deleted_count} cache entries matching pattern: {pattern}')
            )
        else:
            CacheManager.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all cache')
            )

    def warm_cache(self, options):
        """Warm cache."""
        user_id = options.get('user_id')
        album_id = options.get('album_id')
        dry_run = options.get('dry_run')

        if dry_run:
            self.stdout.write(self.style.SUCCESS('Dry run: Cache would not be warmed.'))
            return
        
        if user_id:
            try:
                User.objects.get(id=user_id)
                warm_user_cache(user_id)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully warmed cache for user {user_id}')
                )
            except User.DoesNotExist:
                raise CommandError(f'User with ID {user_id} does not exist')
        
        if album_id:
            try:
                Album.objects.get(id=album_id)
                warm_album_cache(album_id)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully warmed cache for album {album_id}')
                )
            except Album.DoesNotExist:
                raise CommandError(f'Album with ID {album_id} does not exist')
        
        if not user_id and not album_id:
            # Warm cache for all users
            users = User.objects.all()
            for user in users:
                warm_user_cache(user.id)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully warmed cache for {users.count()} users')
            )

    def show_cache_status(self):
        """Show cache status."""
        try:
            # Test cache connectivity
            test_key = 'cache_test'
            test_value = 'test_value'
            
            CacheManager.set(test_key, test_value, 60)
            retrieved_value = CacheManager.get(test_key)
            
            if retrieved_value == test_value:
                CacheManager.delete(test_key)
                self.stdout.write(
                    self.style.SUCCESS('Cache is working correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Cache is not working correctly')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Cache error: {e}')
            )
