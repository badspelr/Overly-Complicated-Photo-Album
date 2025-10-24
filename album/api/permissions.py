"""
API permissions for the album app.
"""
from rest_framework import permissions
from ..models import Album, Photo, Video


class IsOwnerOrViewer(permissions.BasePermission):
    """
    Custom permission for albums and media - allows access to owners and viewers.
    """
    
    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        
        # Determine the album based on the object type
        if isinstance(obj, Album):
            album = obj
        elif isinstance(obj, (Photo, Video)):
            album = obj.album
        else:
            return False
            
        # If no album, only owner can access
        if not album:
            return False
        
        # Owners can do anything
        if album.owner == request.user:
            return True
        
        # Viewers can only read
        if request.method in permissions.SAFE_METHODS:
            return (album.viewers.filter(id=request.user.id).exists() or 
                   album.is_public)
        
        return False


class IsCategoryOwner(permissions.BasePermission):
    """
    Custom permission for categories - only creator can modify.
    """
    
    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        
        # Only creator can modify
        return obj.created_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission for admin-only operations.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to superusers.
        return request.user.is_superuser
