"""
Advanced search functionality for media content.
"""
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from pgvector.django import CosineDistance
from ..models import Photo, Video
from .embedding_service import generate_text_embedding


class MediaSearchService:
    """Advanced search service for photos and videos."""

    @staticmethod
    def search_album_by_text(query, album_id, user, search_type='text'):
        """
        Search within a specific album using AI or text search.
        
        Args:
            query: Search query string
            album_id: ID of the album to search in
            user: User performing the search
            search_type: 'ai' or 'text'
            
        Returns:
            Tuple of (photos_queryset, videos_queryset)
        """
        # Get base querysets for the album with user permissions
        if user.is_superuser:
            # Superusers can access any album
            photos = Photo.objects.filter(album_id=album_id).select_related('album', 'category')
            videos = Video.objects.filter(album_id=album_id).select_related('album', 'category')
        else:
            photos = Photo.objects.filter(
                album_id=album_id
            ).filter(
                Q(album__owner=user) | 
                Q(album__viewers=user) | 
                Q(album__is_public=True)
            ).select_related('album', 'category')
            
            videos = Video.objects.filter(
                album_id=album_id
            ).filter(
                Q(album__owner=user) | 
                Q(album__viewers=user) | 
                Q(album__is_public=True)
            ).select_related('album', 'category')
        
        if not query:
            # Return all media from album if no query
            return photos.order_by('-uploaded_at'), videos.order_by('-uploaded_at')
        
        if search_type == 'ai':
            # Hybrid AI search: combine semantic similarity with text matching
            query_embedding = generate_text_embedding(query)
            
            # First, try text search on AI descriptions for exact matches
            photo_text_matches = photos.filter(
                Q(ai_description__icontains=query) |
                Q(ai_tags__contains=[query])  # Use contains for array fields
            ).distinct()
            
            video_text_matches = videos.filter(
                Q(ai_description__icontains=query) |
                Q(ai_tags__contains=[query])  # Use contains for array fields
            ).distinct()
            
            if photo_text_matches.exists() or video_text_matches.exists():
                # If we have text matches, return them prioritized
                return photo_text_matches.order_by('-uploaded_at'), video_text_matches.order_by('-uploaded_at')
                
            elif query_embedding:
                # Fallback to pure semantic search only if no text matches
                photos_with_distance = photos.annotate(
                    distance=CosineDistance('embedding', query_embedding)
                ).filter(
                    embedding__isnull=False
                ).order_by('distance')
                
                # For videos, use thumbnail_embedding field
                videos_with_distance = videos.annotate(
                    distance=CosineDistance('thumbnail_embedding', query_embedding)
                ).filter(
                    thumbnail_embedding__isnull=False
                ).order_by('distance')
                
                def apply_threshold(queryset_with_distance):
                    if queryset_with_distance.exists():
                        # Use more restrictive threshold for semantic-only search
                        min_distance = queryset_with_distance.first().distance
                        all_distances = [item.distance for item in queryset_with_distance]
                        mean_distance = sum(all_distances) / len(all_distances)
                        
                        # More restrictive threshold for semantic search
                        adaptive_threshold = min_distance + (mean_distance - min_distance) * 0.2
                        max_threshold = 0.09  # More restrictive
                        similarity_threshold = min(adaptive_threshold, max_threshold)
                        
                        semantic_results = queryset_with_distance.filter(distance__lt=similarity_threshold)
                        return semantic_results if semantic_results.exists() else queryset_with_distance.none()
                    return queryset_with_distance.none()
                
                semantic_photos = apply_threshold(photos_with_distance)
                semantic_videos = apply_threshold(videos_with_distance)
                
                return semantic_photos, semantic_videos
            else:
                # Pure text search fallback if no embeddings
                photo_fallback = photos.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(ai_description__icontains=query) |
                    Q(ai_tags__contains=[query])  # Use contains for array fields
                ).order_by('-uploaded_at')
                
                video_fallback = videos.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(ai_description__icontains=query) |
                    Q(ai_tags__contains=[query])  # Use contains for array fields
                ).order_by('-uploaded_at')
                
                return photo_fallback, video_fallback
        else:
            # Standard text search
            photo_results = photos.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(ai_description__icontains=query) |
                Q(ai_tags__contains=[query])  # Use contains for array fields
            ).order_by('-uploaded_at')
            
            video_results = videos.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(ai_description__icontains=query) |
                Q(ai_tags__contains=[query])  # Use contains for array fields
            ).order_by('-uploaded_at')
            
            return photo_results, video_results

    @staticmethod
    def search_media(query, user, filters=None):
        """
        Perform advanced search across photos and videos.

        Args:
            query: Search query string
            user: User performing the search
            filters: Dict of additional filters (date_range, album, category, etc.)

        Returns:
            Queryset of matching media
        """
        filters = filters or {}

        # Base querysets with user permissions
        if user.is_superuser:
            # Superusers can access all media
            photos = Photo.objects.all().distinct()
            videos = Video.objects.all().distinct()
        else:
            photos = Photo.objects.filter(
                Q(album__owner=user) |
                Q(album__viewers=user) |
                Q(album__is_public=True)
            ).distinct()

            videos = Video.objects.filter(
                Q(album__owner=user) |
                Q(album__viewers=user) |
                Q(album__is_public=True)
            ).distinct()

        if query:
            # Full-text search on title and description
            search_vector = SearchVector('title', weight='A') + \
                          SearchVector('description', weight='B')

            search_query = SearchQuery(query)

            photos = photos.annotate(
                search_rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(search_rank__gte=0.1)
            )

            videos = videos.annotate(
                search_rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(search_rank__gte=0.1)
            )

        # Apply additional filters
        if filters.get('album'):
            photos = photos.filter(album_id=filters['album'])
            videos = videos.filter(album_id=filters['album'])

        if filters.get('category'):
            photos = photos.filter(category_id=filters['category'])
            videos = videos.filter(category_id=filters['category'])

        if filters.get('date_from'):
            photos = photos.filter(uploaded_at__gte=filters['date_from'])
            videos = videos.filter(uploaded_at__gte=filters['date_from'])

        if filters.get('date_to'):
            photos = photos.filter(uploaded_at__lte=filters['date_to'])
            videos = videos.filter(uploaded_at__lte=filters['date_to'])

        if filters.get('media_type') == 'photos':
            return photos.order_by('-search_rank', '-uploaded_at')
        elif filters.get('media_type') == 'videos':
            return videos.order_by('-search_rank', '-uploaded_at')

        # Combine and sort by relevance
        combined = []
        for photo in photos:
            combined.append(('photo', photo))
        for video in videos:
            combined.append(('video', video))

        # Sort by search rank if query provided, otherwise by date
        if query:
            combined.sort(key=lambda x: (getattr(x[1], 'search_rank', 0), x[1].uploaded_at), reverse=True)
        else:
            combined.sort(key=lambda x: x[1].uploaded_at, reverse=True)

        return combined
        """
        Perform advanced search across photos and videos.

        Args:
            query: Search query string
            user: User performing the search
            filters: Dict of additional filters (date_range, album, category, etc.)

        Returns:
            Queryset of matching media
        """
        filters = filters or {}

        # Base querysets with user permissions
        photos = Photo.objects.filter(
            Q(album__owner=user) |
            Q(album__viewers=user) |
            Q(album__is_public=True)
        ).distinct()

        videos = Video.objects.filter(
            Q(album__owner=user) |
            Q(album__viewers=user) |
            Q(album__is_public=True)
        ).distinct()

        if query:
            # Full-text search on title and description
            search_vector = SearchVector('title', weight='A') + \
                          SearchVector('description', weight='B')

            search_query = SearchQuery(query)

            photos = photos.annotate(
                search_rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(search_rank__gte=0.1)
            )

            videos = videos.annotate(
                search_rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(search_rank__gte=0.1)
            )

        # Apply additional filters
        if filters.get('album'):
            photos = photos.filter(album_id=filters['album'])
            videos = videos.filter(album_id=filters['album'])

        if filters.get('category'):
            photos = photos.filter(category_id=filters['category'])
            videos = videos.filter(category_id=filters['category'])

        if filters.get('date_from'):
            photos = photos.filter(uploaded_at__gte=filters['date_from'])
            videos = videos.filter(uploaded_at__gte=filters['date_from'])

        if filters.get('date_to'):
            photos = photos.filter(uploaded_at__lte=filters['date_to'])
            videos = videos.filter(uploaded_at__lte=filters['date_to'])

        if filters.get('media_type') == 'photos':
            return photos.order_by('-search_rank', '-uploaded_at')
        elif filters.get('media_type') == 'videos':
            return videos.order_by('-search_rank', '-uploaded_at')

        # Combine and sort by relevance
        combined = []
        for photo in photos:
            combined.append(('photo', photo))
        for video in videos:
            combined.append(('video', video))

        # Sort by search rank if query provided, otherwise by date
        if query:
            combined.sort(key=lambda x: (getattr(x[1], 'search_rank', 0), x[1].uploaded_at), reverse=True)
        else:
            combined.sort(key=lambda x: x[1].uploaded_at, reverse=True)

        return combined

    @staticmethod
    def get_search_suggestions(user, limit=10):
        """Get popular search terms for autocomplete."""

        # Get most common words from titles and descriptions
        photos = Photo.objects.filter(
            Q(album__owner=user) |
            Q(album__viewers=user) |
            Q(album__is_public=True)
        )

        common_words = []
        for field in ['title', 'description']:
            words = photos.values_list(field, flat=True)
            # Simple word frequency analysis
            word_freq = {}
            for text in words:
                if text:
                    for word in text.lower().split():
                        if len(word) > 2:  # Skip short words
                            word_freq[word] = word_freq.get(word, 0) + 1

            common_words.extend([
                word for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:limit//2]
            ])

        return list(set(common_words))[:limit]
