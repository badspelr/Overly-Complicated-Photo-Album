"""
Template tags for the album app.
"""
from django import template
from ..views.base_views import check_object_permission
from ..models import Favorite

register = template.Library()


@register.simple_tag
def check_delete_permission(user, obj, obj_type='album'):
    """
    Check if user has delete permission for an object.
    Usage: {% check_delete_permission user album 'album' as can_delete %}
    """
    return check_object_permission(user, obj, obj_type, action='delete')


@register.simple_tag
def check_view_permission(user, obj, obj_type='album'):
    """
    Check if user has view permission for an object.
    Usage: {% check_view_permission user photo 'photo' as can_view %}
    """
    return check_object_permission(user, obj, obj_type, action='view')


@register.simple_tag
def is_favorited(user, photo):
    """
    Check if a photo is favorited by the current user.
    Usage: {% is_favorited user photo as favorited %}
    """
    if not user.is_authenticated:
        return False
    return Favorite.objects.filter(user=user, photo=photo).exists()


@register.simple_tag
def get_pagination_range(page_obj, max_pages=7):
    """
    Generate a smart pagination range that shows relevant page numbers.
    Shows first page, last page, current page and surrounding pages, with ellipsis.
    Usage: {% get_pagination_range page_obj as page_range %}
    """
    current = page_obj.number
    total = page_obj.paginator.num_pages
    
    if total <= max_pages:
        return list(range(1, total + 1))
    
    # Always show first page
    pages = [1]
    
    # Calculate range around current page
    start = max(2, current - 2)
    end = min(total - 1, current + 2)
    
    # Add ellipsis if there's a gap after first page
    if start > 2:
        pages.append('...')
    
    # Add pages around current
    for i in range(start, end + 1):
        pages.append(i)
    
    # Add ellipsis if there's a gap before last page
    if end < total - 1:
        pages.append('...')
    
    # Always show last page (if different from first)
    if total > 1:
        pages.append(total)
    
    return pages