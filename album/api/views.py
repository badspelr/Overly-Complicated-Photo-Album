"""
API views for the album app.
"""
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from ..models import Album, Photo, Video, Category, SiteSettings
from .serializers import (
    AlbumSerializer, AlbumListSerializer, PhotoSerializer, VideoSerializer,
    CategorySerializer, UserSerializer, SiteSettingsSerializer, MediaSerializer
)
from .permissions import (
    IsOwnerOrViewer, IsCategoryOwner,
    IsAdminOrReadOnly
)
from ..services.media_service import MediaService
from ..services.bulk_operations_service import BulkOperationsService
from itertools import chain
from django.template.loader import render_to_string
from django.http import HttpResponse

from rest_framework.exceptions import NotFound

from django.core.mail import send_mail

class RegistrationView(APIView):
    """
    API view for user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({'error': 'Please provide all required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Send welcome email
        message = render_to_string('emails/welcome.txt', {'user': user})
        send_mail(
            'Welcome to Photo Album!',
            message,
            'noreply@photoalbum.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    API view for user login.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'user': UserSerializer(user).data})
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    """
    Provides the currently logged-in user's data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class MediaUploadView(APIView):
    """API view for handling media uploads."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        album_id = request.data.get('album_id')
        
        if not file or not album_id:
            return Response(
                {'error': 'File and album_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            return Response(
                {'error': 'Album not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not (request.user.is_superuser or album.owner == request.user):
            return Response(
                {'error': 'You do not have permission to upload to this album'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if file.content_type.startswith('image/'):
            media_obj = Photo.objects.create(album=album, image=file, title=file.name)
            MediaService.extract_photo_metadata(media_obj)
            serializer = PhotoSerializer(media_obj, context={'request': request})
        elif file.content_type.startswith('video/'):
            media_obj = Video.objects.create(album=album, video=file, title=file.name)
            MediaService.extract_video_metadata(media_obj)
            serializer = VideoSerializer(media_obj, context={'request': request})
        else:
            return Response(
                {'error': 'Unsupported file type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AlbumViewSet(viewsets.ModelViewSet):
    """ViewSet for Album model."""
    
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrViewer]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public', 'category']
    search_fields = ['title', 'description', 'owner__username']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Album.objects.all().select_related('owner', 'category').prefetch_related('viewers', 'photos')
        return Album.objects.filter(
            Q(owner=user) | Q(viewers=user) | Q(is_public=True)
        ).select_related('owner', 'category').prefetch_related('viewers', 'photos')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AlbumListSerializer
        return AlbumSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_viewer(self, request, pk=None):
        album = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            if user in album.viewers.all():
                album.viewers.remove(user)
                message = f'User {user.username} removed as viewer'
            else:
                album.viewers.add(user)
                message = f'User {user.username} added as viewer'
            return Response({'message': message})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def media(self, request, pk=None):
        album = self.get_object()
        media_type = request.query_params.get('media_type')
        sort = request.query_params.get('sort', '-uploaded_at')

        # Basic validation for sort parameter to prevent arbitrary ordering
        if sort not in ['uploaded_at', '-uploaded_at', 'title', '-title']:
            sort = '-uploaded_at'

        if media_type == 'photos':
            media_list = album.photos.all().select_related('category').order_by(sort)
        elif media_type == 'videos':
            media_list = album.videos.all().select_related('category').order_by(sort)
        else:
            # Note: Sorting combined, different models in Python is inefficient.
            # This approach is kept for consistency with original logic but is not ideal for large datasets.
            media_list = sorted(
                chain(album.photos.all().select_related('category'), album.videos.all().select_related('category')),
                key=lambda instance: getattr(instance, sort.strip('-'), instance.uploaded_at),
                reverse=sort.startswith('-')
            )

        try:
            page = self.paginate_queryset(media_list)
        except NotFound:
            return HttpResponse(status=204)

        if request.query_params.get('format') == 'html':
            if not page:
                return HttpResponse(status=204)
            
            html = render_to_string(
                'album/media_list_partial.html',
                {'media': page, 'request': request}
            )
            if not html.strip():
                return HttpResponse(status=204)
            return HttpResponse(html)
        
        # Default to JSON response
        if page is not None:
            serializer = MediaSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MediaSerializer(media_list, many=True, context={'request': request})
        return Response(serializer.data)


class PhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for Photo model."""
    
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrViewer]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['album', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['uploaded_at', 'date_taken', 'title']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Photo.objects.all().select_related('album', 'category')
        return Photo.objects.filter(
            Q(album__owner=user) | Q(album__viewers=user) | Q(album__is_public=True)
        ).select_related('album', 'category')
    
    def perform_create(self, serializer):
        photo = serializer.save()
        try:
            MediaService.extract_photo_metadata(photo)
        except Exception:
            pass


class VideoViewSet(viewsets.ModelViewSet):
    """ViewSet for Video model."""
    
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrViewer]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['album', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['uploaded_at', 'date_recorded', 'title']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Video.objects.all().select_related('album', 'category')
        return Video.objects.filter(
            Q(album__owner=user) | Q(album__viewers=user) | Q(album__is_public=True)
        ).select_related('album', 'category')
    
    def perform_create(self, serializer):
        video = serializer.save()
        try:
            MediaService.extract_video_metadata(video)
        except Exception:
            pass


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsCategoryOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Category.objects.all().select_related('created_by')
        return Category.objects.filter(created_by=user).select_related('created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        # Allow users to view and edit their own profile at `/api/users/me/`
        if self.kwargs.get(self.lookup_field) == 'me':
            return self.request.user
        return super().get_object()


class SiteSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for SiteSettings model."""
    
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        return SiteSettings.objects.all()
    
    def get_object(self):
        obj, created = SiteSettings.objects.get_or_create()
        return obj

class BulkEditView(APIView):
    """API view for bulk editing of media."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        media_ids_str = request.data.get('media_ids', [])
        user = request.user

        # Convert media_ids from strings to tuples of (type, id)
        media_ids = []
        for item_str in media_ids_str:
            try:
                # Assuming format "photo-123" or "video-456"
                media_type, media_id = item_str.split('-')
                if media_type not in ['photo', 'video']:
                    continue
                media_ids.append((media_type, int(media_id)))
            except ValueError:
                continue # Ignore malformed IDs

        if not action or not media_ids:
            return Response(
                {'error': 'Action and media_ids are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'update_category':
            category_id = request.data.get('category_id')
            if category_id is None:
                return Response({'error': 'category_id is required for this action.'}, status=status.HTTP_400_BAD_REQUEST)
            # Handle 'None' case for removing category
            category_id = None if category_id == 'None' else int(category_id)
            
            results = BulkOperationsService.bulk_update_category(media_ids, category_id, user)
            return Response(results)

        elif action == 'add_tags':
            tags_string = request.data.get('tags')
            if not tags_string:
                return Response({'error': 'tags are required for this action.'}, status=status.HTTP_400_BAD_REQUEST)
            
            results = BulkOperationsService.bulk_add_tags(media_ids, tags_string, user)
            return Response(results)

        return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)


