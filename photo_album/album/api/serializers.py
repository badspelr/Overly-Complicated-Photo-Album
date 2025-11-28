"""
API serializers for the album app.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Album, Photo, Video, Category, SiteSettings


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_by']


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for detailed album view."""
    owner = UserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'description', 'owner', 'category', 
            'viewers', 'is_public', 'created_at', 'is_owner'
        ]

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.owner == request.user
        return False


class BaseMediaSerializer(serializers.ModelSerializer):
    """Base serializer for media models."""
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.album.owner == request.user
        return False


class PhotoSerializer(BaseMediaSerializer):
    """Serializer for Photo model."""
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'description', 'album', 'category', 'image', 
            'thumbnail', 'uploaded_at', 'is_owner'
        ]


class VideoSerializer(BaseMediaSerializer):
    """Serializer for Video model."""

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'album', 'category', 'video', 
            'uploaded_at', 'is_owner'
        ]


class MediaSerializer(serializers.Serializer):
    """Serializer for combined media (photos and videos)."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    uploaded_at = serializers.DateTimeField()
    is_owner = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    thumbnail = serializers.ImageField(required=False)

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.album.owner == request.user
        return False

class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SiteSettings model."""
    
    class Meta:
        model = SiteSettings
        fields = ['id', 'title', 'description']


class AlbumListSerializer(serializers.ModelSerializer):
    """Simplified serializer for album lists."""
    owner = UserSerializer(read_only=True)
    cover_photo = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'description', 'owner', 'is_public',
            'created_at', 'cover_photo'
        ]

    def get_cover_photo(self, obj):
        request = self.context.get('request')
        first_photo = obj.photos.first()
        if first_photo:
            return request.build_absolute_uri(first_photo.thumbnail.url)
        return None