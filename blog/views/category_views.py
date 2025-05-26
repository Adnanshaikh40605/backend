from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Category, BlogPost
from ..serializers import CategorySerializer, BlogPostListSerializer

# Setup logger
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    tags=['Categories'],
    operation_id='list_categories',
    operation_description='Get a list of all categories',
    responses={
        200: openapi.Response('Successful response', CategorySerializer(many=True))
    }
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog categories.
    
    list:
    Return a list of all categories.
    
    retrieve:
    Return a specific category by ID.
    
    create:
    Create a new category.
    
    update:
    Update an existing category.
    
    partial_update:
    Partially update an existing category.
    
    destroy:
    Delete a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @swagger_auto_schema(
        operation_description="Get posts in a specific category",
        responses={
            200: openapi.Response('Successful response', BlogPostListSerializer(many=True))
        }
    )
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts in a specific category"""
        category = self.get_object()
        posts = BlogPost.objects.filter(category=category, published=True).order_by('-created_at')
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_all_categories(request):
    """Get a list of all categories with post counts"""
    try:
        categories = Category.objects.all().order_by('name')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_category_by_slug(request, slug):
    """Get a specific category by its slug"""
    try:
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching category by slug: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 