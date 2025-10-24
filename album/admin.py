from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import SiteSettings, Category, Album, Photo, Video, Tag, AlbumShareLink, Favorite, AIProcessingSettings


# Removed PhotoInline and VideoInline - they cause performance issues
# by loading all media when editing an album

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    fieldsets = (
        ('Basic Settings', {
            'fields': ('title', 'description')
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'description')
    list_filter = ('created_by',)
    search_fields = ('name', 'description')

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'photo_count', 'video_count', 'created_at', 'manage_media_link')
    list_filter = ('is_public', 'created_at', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    # Use raw_id_fields instead of filter_horizontal for better performance with many users
    raw_id_fields = ('viewers',)
    readonly_fields = ('created_at', 'photo_count', 'video_count', 'view_photos_link', 'view_videos_link')
    # Explicitly exclude any reverse relations that might be auto-added
    inlines = []  # No inlines for photos or videos
    show_full_result_count = False  # Performance optimization
    
    def get_inline_instances(self, request, obj=None):
        """Override to ensure no inlines are ever loaded"""
        return []
    
    def get_formsets_with_inlines(self, request, obj=None):
        """Override to prevent any formsets from being generated"""
        return []
    
    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        """Override to prevent inline formsets"""
        return []
    
    # Only show essential fields by default - media counts are readonly
    fieldsets = (
        ('Album Information', {
            'fields': ('title', 'description', 'owner', 'is_public')
        }),
        ('Access Control', {
            'fields': ('viewers',),
            'description': 'Select users who can view this album (only applies to private albums)'
        }),
        ('Statistics', {
            'fields': ('photo_count', 'video_count'),
            'classes': ('collapse',),
            'description': 'Photo and video counts (click "Manage Photos/Videos" buttons below to edit media)'
        }),
        ('Media Management', {
            'fields': ('view_photos_link', 'view_videos_link'),
            'description': 'Use these links to manage photos and videos separately for better performance'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def photo_count(self, obj):
        """Display count of photos in this album"""
        if obj.pk:
            # Use only() to optimize the count query
            count = obj.photos.only('id').count()
            return f"{count} photo{'s' if count != 1 else ''}"
        return "0 photos"
    photo_count.short_description = 'Photos'
    
    def video_count(self, obj):
        """Display count of videos in this album"""
        if obj.pk:
            # Use only() to optimize the count query
            count = obj.videos.only('id').count()
            return f"{count} video{'s' if count != 1 else ''}"
        return "0 videos"
    video_count.short_description = 'Videos'
    
    def view_photos_link(self, obj):
        """Link to manage photos in this album"""
        if obj.pk:
            url = reverse('admin:album_photo_changelist') + f'?album__id__exact={obj.pk}'
            count = obj.photos.count()
            return format_html(
                '<a class="button" href="{}">Manage Photos ({})</a>',
                url, count
            )
        return "Save the album first to manage photos"
    view_photos_link.short_description = 'Manage Photos'
    
    def view_videos_link(self, obj):
        """Link to manage videos in this album"""
        if obj.pk:
            url = reverse('admin:album_video_changelist') + f'?album__id__exact={obj.pk}'
            count = obj.videos.count()
            return format_html(
                '<a class="button" href="{}">Manage Videos ({})</a>',
                url, count
            )
        return "Save the album first to manage videos"
    view_videos_link.short_description = 'Manage Videos'
    
    def manage_media_link(self, obj):
        """Quick link in list view to manage media"""
        if obj.pk:
            photo_url = reverse('admin:album_photo_changelist') + f'?album__id__exact={obj.pk}'
            video_url = reverse('admin:album_video_changelist') + f'?album__id__exact={obj.pk}'
            return format_html(
                '<a href="{}">Photos ({})</a> | <a href="{}">Videos ({})</a>',
                photo_url, obj.photos.count(),
                video_url, obj.videos.count()
            )
        return "-"
    manage_media_link.short_description = 'Manage Media'

# Unregister and re-register to ensure clean state
try:
    admin.site.unregister(Album)
except admin.sites.NotRegistered:
    pass
admin.site.register(Album, AlbumAdmin)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'album', 'category', 'uploaded_at', 'ai_analyzed')
    list_filter = ('uploaded_at', 'album', 'category', 'album__owner')
    search_fields = ('title', 'ai_description', 'ai_tags', 'album__title')
    readonly_fields = ('uploaded_at', 'ai_description', 'ai_tags', 'image_preview')
    list_per_page = 50  # Pagination for better performance
    
    fieldsets = (
        ('Photo Information', {
            'fields': ('title', 'album', 'category', 'image', 'image_preview')
        }),
        ('AI Analysis', {
            'fields': ('ai_description', 'ai_tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def ai_analyzed(self, obj):
        """Show if photo has been AI analyzed"""
        return bool(obj.ai_description)
    ai_analyzed.boolean = True
    ai_analyzed.short_description = 'AI Analyzed'
    
    def thumbnail_preview(self, obj):
        """Show small thumbnail in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    thumbnail_preview.short_description = 'Preview'
    
    def image_preview(self, obj):
        """Show larger image in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 500px; border-radius: 8px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'album', 'category', 'uploaded_at', 'ai_analyzed')
    list_filter = ('uploaded_at', 'album', 'category', 'album__owner')
    search_fields = ('title', 'ai_description', 'ai_tags', 'album__title')
    readonly_fields = ('uploaded_at', 'ai_description', 'ai_tags', 'video_preview')
    list_per_page = 50  # Pagination for better performance
    
    fieldsets = (
        ('Video Information', {
            'fields': ('title', 'album', 'category', 'video', 'video_preview')
        }),
        ('AI Analysis', {
            'fields': ('ai_description', 'ai_tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def ai_analyzed(self, obj):
        """Show if video has been AI analyzed"""
        return bool(obj.ai_description)
    ai_analyzed.boolean = True
    ai_analyzed.short_description = 'AI Analyzed'
    
    def thumbnail_preview(self, obj):
        """Show video thumbnail in list view"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url
            )
        return "🎥"
    thumbnail_preview.short_description = 'Preview'
    
    def video_preview(self, obj):
        """Show video player in detail view"""
        if obj.video:
            return format_html(
                '<video controls style="max-width: 500px; border-radius: 8px;"><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>',
                obj.video.url
            )
        return "No video"
    video_preview.short_description = 'Video Preview'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    list_filter = ('created_by',)
    search_fields = ('name',)

@admin.register(AlbumShareLink)
class AlbumShareLinkAdmin(admin.ModelAdmin):
    list_display = ('album', 'created_by', 'share_token', 'expires_at', 'is_active', 'created_at')
    list_filter = ('is_active', 'expires_at', 'created_at')
    search_fields = ('album__title', 'created_by__username', 'share_token')
    readonly_fields = ('created_at', 'share_token')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'photo__title')
    readonly_fields = ('created',)


@admin.register(AIProcessingSettings)
class AIProcessingSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for AI processing settings.
    Singleton model - only one instance exists.
    """
    list_display = (
        'auto_process_on_upload',
        'scheduled_processing', 
        'batch_size',
        'album_admin_processing_limit',
        'schedule_hour',
        'schedule_minute',
        'last_modified'
    )
    
    fieldsets = (
        ('Processing Modes', {
            'fields': ('auto_process_on_upload', 'scheduled_processing'),
            'description': 'Control when AI processing occurs'
        }),
        ('Batch Processing Settings', {
            'fields': ('batch_size', 'processing_timeout'),
            'description': 'Configure batch processing parameters'
        }),
        ('Permission Limits', {
            'fields': ('album_admin_processing_limit',),
            'description': 'Set limits for album admins (site admins have no limits)'
        }),
        ('Schedule Configuration', {
            'fields': ('schedule_hour', 'schedule_minute'),
            'description': 'Set the time for scheduled batch processing (24-hour format)'
        }),
        ('Information', {
            'fields': ('last_modified',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('last_modified',)
    
    def has_add_permission(self, request):
        # Singleton pattern - only allow one instance
        return not AIProcessingSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of the singleton instance
        return False
    
    def changelist_view(self, request, extra_context=None):
        """
        Redirect to the single instance edit page instead of showing a list.
        """
        from django.shortcuts import redirect
        # Get or create the singleton instance
        obj = AIProcessingSettings.load()
        return redirect('admin:album_aiprocessingsettings_change', obj.pk)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Ensure the singleton instance exists before showing the change form.
        """
        # Ensure singleton exists
        AIProcessingSettings.load()
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)

