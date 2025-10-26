from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import SiteSettings, Category, Album, Photo, Video, Tag, AlbumShareLink, Favorite, AIProcessingSettings


class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 0
    readonly_fields = ('ai_description', 'ai_tags', 'uploaded_at')

class VideoInline(admin.StackedInline):
    model = Video
    extra = 0
    readonly_fields = ('ai_description', 'ai_tags', 'uploaded_at')

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

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'photo_count', 'video_count', 'created_at')
    list_filter = ('is_public', 'created_at', 'owner')
    search_fields = ('title', 'description', 'owner__username')
    filter_horizontal = ('viewers',)
    readonly_fields = ('created_at',)
    inlines = [PhotoInline, VideoInline]
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'
    
    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = 'Videos'

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'category', 'uploaded_at', 'ai_analyzed')
    list_filter = ('uploaded_at', 'album', 'category')
    search_fields = ('title', 'ai_description', 'ai_tags')
    readonly_fields = ('uploaded_at', 'ai_description', 'ai_tags')
    
    def ai_analyzed(self, obj):
        return bool(obj.ai_description)
    ai_analyzed.boolean = True
    ai_analyzed.short_description = 'AI Analyzed'

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'category', 'uploaded_at', 'ai_analyzed')
    list_filter = ('uploaded_at', 'album', 'category')
    search_fields = ('title', 'ai_description', 'ai_tags')
    readonly_fields = ('uploaded_at', 'ai_description', 'ai_tags')
    
    def ai_analyzed(self, obj):
        return bool(obj.ai_description)
    ai_analyzed.boolean = True
    ai_analyzed.short_description = 'AI Analyzed'

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

