"""
Caching utilities for the album app.
"""
import hashlib
import json
from django.core.cache import cache
from django.db.models import Model
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Centralized cache management."""
    
    # Cache timeouts (in seconds)
    TIMEOUTS = {
        'album_list': 300,      # 5 minutes
        'album_detail': 600,    # 10 minutes
        'photo_list': 300,       # 5 minutes
        'video_list': 300,      # 5 minutes
        'category_list': 1800,  # 30 minutes
        'user_stats': 600,      # 10 minutes
        'site_settings': 3600,  # 1 hour
    }
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key."""
        # Convert args and kwargs to a consistent string
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        
        # Hash long keys to keep them manageable
        if len(key_string) > 200:
            key_string = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_string}"
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            return cache.get(key, default)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return default
    
    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete value from cache."""
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            # Use Redis-specific iter_keys for efficiency
            if hasattr(cache, 'iter_keys'):
                keys = list(cache.iter_keys(pattern))
                if keys:
                    cache.delete_many(keys)
                return len(keys)
            else:
                # Fallback for non-Redis caches (less efficient)
                # Note: This can be slow on large caches
                keys = cache.keys(pattern)
                for key in keys:
                    cache.delete(key)
                return len(keys)
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    @staticmethod
    def clear():
        """Clear the entire cache."""
        try:
            cache.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    @staticmethod
    def invalidate_model_cache(model_class: Model, instance_id: Optional[int] = None):
        """Invalidate cache for a model."""
        model_name = model_class.__name__.lower()
        
        # Delete list caches
        CacheManager.delete_pattern(f"{model_name}_list:*")
        
        # Delete detail caches
        if instance_id:
            CacheManager.delete_pattern(f"{model_name}_detail:{instance_id}:*")
        else:
            CacheManager.delete_pattern(f"{model_name}_detail:*")
        
        # Delete related caches
        CacheManager.delete_pattern("user_stats:*")
        CacheManager.delete_pattern("dashboard:*")


def cache_result(timeout: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = CacheManager.generate_cache_key(
                key_prefix or func.__name__, 
                *args, 
                **kwargs
            )
            
            # Try to get from cache
            result = CacheManager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


class ModelCacheMixin:
    """Mixin to add caching to model managers."""
    
    def get_cached(self, cache_key: str, timeout: int = 300):
        """Get queryset from cache or database."""
        result = CacheManager.get(cache_key)
        if result is not None:
            return result
        
        # Execute query and cache result
        queryset = self.all()
        CacheManager.set(cache_key, queryset, timeout)
        return queryset
    
    def invalidate_cache(self):
        """Invalidate all caches for this model."""
        CacheManager.invalidate_model_cache(self.model)


def get_user_albums_cache_key(user_id: int, filters: Dict = None) -> str:
    """Generate cache key for user albums."""
    filter_str = ""
    if filters:
        filter_str = f":{json.dumps(filters, sort_keys=True)}"
    return CacheManager.generate_cache_key(
        "user_albums", 
        user_id, 
        filter_str
    )


def get_album_photos_cache_key(album_id: int) -> str:
    """Generate cache key for album photos."""
    return CacheManager.generate_cache_key("album_photos", album_id)


def get_album_videos_cache_key(album_id: int) -> str:
    """Generate cache key for album videos."""
    return CacheManager.generate_cache_key("album_videos", album_id)


def get_dashboard_cache_key(user_id: int, role: str) -> str:
    """Generate cache key for dashboard data."""
    return CacheManager.generate_cache_key("dashboard", user_id, role)


def get_site_settings_cache_key() -> str:
    """Generate cache key for site settings."""
    return CacheManager.generate_cache_key("site_settings")


# Cache warming functions
def warm_album_cache(album_id: int):
    """Warm cache for a specific album."""
    from ..models import Album
    
    try:
        album = Album.objects.select_related('owner', 'category').prefetch_related('viewers').get(id=album_id)
        
        # Cache album detail
        cache_key = CacheManager.generate_cache_key("album_detail", album_id)
        CacheManager.set(cache_key, album, CacheManager.TIMEOUTS['album_detail'])
        
        # Cache album photos
        photos = album.photos.select_related('category').all()
        photos_key = get_album_photos_cache_key(album_id)
        CacheManager.set(photos_key, list(photos), CacheManager.TIMEOUTS['photo_list'])
        
        # Cache album videos
        videos = album.videos.select_related('category').all()
        videos_key = get_album_videos_cache_key(album_id)
        CacheManager.set(videos_key, list(videos), CacheManager.TIMEOUTS['video_list'])
        
        logger.info(f"Warmed cache for album {album_id}")
        
    except Album.DoesNotExist:
        logger.warning(f"Album {album_id} not found for cache warming")


def warm_user_cache(user_id: int):
    """Warm cache for a specific user."""
    from ..models import Album, Category
    
    try:
        # Cache user albums
        albums = Album.objects.filter(owner_id=user_id).select_related('owner', 'category')
        albums_key = get_user_albums_cache_key(user_id)
        CacheManager.set(albums_key, list(albums), CacheManager.TIMEOUTS['album_list'])
        
        # Cache user categories
        categories = Category.objects.filter(created_by_id=user_id)
        categories_key = CacheManager.generate_cache_key("user_categories", user_id)
        CacheManager.set(categories_key, list(categories), CacheManager.TIMEOUTS['category_list'])
        
        logger.info(f"Warmed cache for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error warming cache for user {user_id}: {e}")
