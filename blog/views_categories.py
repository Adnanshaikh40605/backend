from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db.models import Count, Q
from django.utils.html import strip_tags
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Category, BlogPost
from .serializers import CategorySerializer, BlogPostListSerializer

# Setup logger
logger = logging.getLogger(__name__)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing categories.
    
    list:
    Return a list of all categories with post counts.
    
    retrieve:
    Return a specific category by slug.
    
    create:
    Create a new category (requires authentication).
    
    update:
    Update an existing category (requires authentication).
    
    destroy:
    Delete a category (requires authentication).
    """
    queryset = Category.objects.all().annotate(
        post_count=Count('posts', filter=Q(posts__published=True))
    ).order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Require authentication for ALL actions
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all categories with post counts",
        responses={
            200: openapi.Response(
                description="List of categories",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'color': openapi.Schema(type=openapi.TYPE_STRING),
                            'post_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        }
                    )
                )
            )
        },
        tags=['Categories']
    )
    def list(self, request, *args, **kwargs):
        """List all categories with post counts"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific category by slug",
        responses={
            200: CategorySerializer(),
            404: "Category not found"
        },
        tags=['Categories']
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific category by slug"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new category",
        request_body=CategorySerializer,
        responses={
            201: CategorySerializer(),
            400: "Bad request - validation errors",
            401: "Authentication required"
        },
        tags=['Categories']
    )
    def create(self, request, *args, **kwargs):
        """Create a new category (requires authentication)"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing category",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer(),
            400: "Bad request - validation errors",
            401: "Authentication required",
            404: "Category not found"
        },
        tags=['Categories']
    )
    def update(self, request, *args, **kwargs):
        """Update an existing category (requires authentication)"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an existing category",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer(),
            400: "Bad request - validation errors",
            401: "Authentication required",
            404: "Category not found"
        },
        tags=['Categories']
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update an existing category (requires authentication)"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a category",
        responses={
            204: "Category deleted successfully",
            401: "Authentication required",
            404: "Category not found"
        },
        tags=['Categories']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a category (requires authentication)"""
        return super().destroy(request, *args, **kwargs)


@swagger_auto_schema(
    method='get',
    tags=['Posts'],
    operation_description="Get related posts for a specific blog post by slug",
    manual_parameters=[
        openapi.Parameter(
            name='limit',
            in_=openapi.IN_QUERY,
            description='Number of related posts to return (default: 4, max: 10)',
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="List of related blog posts",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of related posts found'),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    )
                }
            )
        ),
        404: "Post not found"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_related_posts(request, slug):
    """
    Get related posts for a specific blog post.
    
    Related posts are determined by:
    1. Same category (highest priority)
    2. Similar content/title keywords (medium priority)
    3. Recent posts (lowest priority)
    """
    # Get the current post
    current_post = get_object_or_404(BlogPost, slug=slug, published=True)
    
    # Get limit parameter (default 4, max 10)
    try:
        limit = int(request.query_params.get('limit', 4))
        limit = min(max(limit, 1), 10)  # Ensure limit is between 1 and 10
    except (ValueError, TypeError):
        limit = 4
    
    # Start with all published posts except the current one
    related_posts = BlogPost.objects.filter(
        published=True
    ).exclude(id=current_post.id).prefetch_related('images')
    
    # Strategy 1: Posts from the same category (if current post has a category)
    category_posts = []
    if current_post.category:
        category_posts = list(related_posts.filter(
            category=current_post.category
        ).order_by('-created_at')[:limit])
    
    # Strategy 2: Posts with similar keywords in title or content
    similar_posts = []
    if len(category_posts) < limit:
        # Extract keywords from current post title
        title_keywords = _extract_keywords(current_post.title)
        
        if title_keywords:
            # Build query for posts with similar keywords
            keyword_query = Q()
            for keyword in title_keywords[:5]:  # Use top 5 keywords
                keyword_query |= (
                    Q(title__icontains=keyword) |
                    Q(content__icontains=keyword)
                )
            
            # Get posts with similar keywords, excluding category posts already found
            exclude_ids = [post.id for post in category_posts] + [current_post.id]
            similar_posts = list(related_posts.filter(keyword_query).exclude(
                id__in=exclude_ids
            ).order_by('-created_at')[:limit - len(category_posts)])
    
    # Strategy 3: Recent posts to fill remaining slots
    recent_posts = []
    total_found = len(category_posts) + len(similar_posts)
    if total_found < limit:
        exclude_ids = [post.id for post in category_posts + similar_posts] + [current_post.id]
        recent_posts = list(related_posts.exclude(
            id__in=exclude_ids
        ).order_by('-created_at')[:limit - total_found])
    
    # Combine all related posts with priority order
    final_related_posts = category_posts + similar_posts + recent_posts
    
    # Serialize the results
    serializer = BlogPostListSerializer(
        final_related_posts[:limit], 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'count': len(final_related_posts),
        'results': serializer.data
    })


def _extract_keywords(text, min_length=3, max_keywords=10):
    """
    Extract meaningful keywords from text for similarity matching.
    
    Args:
        text (str): Text to extract keywords from
        min_length (int): Minimum length of keywords to consider
        max_keywords (int): Maximum number of keywords to return
    
    Returns:
        list: List of keywords sorted by relevance
    """
    if not text:
        return []
    
    # Remove HTML tags and convert to lowercase
    clean_text = strip_tags(text).lower()
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
        'its', 'our', 'their', 'from', 'up', 'about', 'into', 'over', 'after'
    }
    
    # Split into words and filter
    words = []
    for word in clean_text.split():
        # Remove punctuation and keep only alphanumeric characters
        clean_word = ''.join(char for char in word if char.isalnum())
        
        # Filter by length, stop words, and ensure it's not just numbers
        if (len(clean_word) >= min_length and 
            clean_word not in stop_words and 
            not clean_word.isdigit()):
            words.append(clean_word)
    
    # Count word frequency and return most common words
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]