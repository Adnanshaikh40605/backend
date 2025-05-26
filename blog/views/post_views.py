from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import BlogPost, Comment
from ..serializers import BlogPostSerializer, BlogPostListSerializer

# Setup logger
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    tags=['Posts'],
    operation_id='list_posts',
    operation_description='Get a list of all blog posts',
    manual_parameters=[
        openapi.Parameter(
            'published', 
            openapi.IN_QUERY, 
            description='Filter by published status (true/false)', 
            type=openapi.TYPE_BOOLEAN,
            required=False
        )
    ],
    responses={
        200: openapi.Response('Successful response', BlogPostListSerializer(many=True))
    }
)
class BlogPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog posts.
    
    list:
    Return a list of all blog posts.
    
    retrieve:
    Return a specific blog post by ID.
    
    create:
    Create a new blog post.
    
    update:
    Update an existing blog post.
    
    partial_update:
    Partially update an existing blog post.
    
    destroy:
    Delete a blog post.
    """
    queryset = BlogPost.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        return BlogPostSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            # Filter by published status for list view
            published = self.request.query_params.get('published')
            if published is not None:
                if published.lower() == 'true':
                    queryset = queryset.filter(published=True)
                elif published.lower() == 'false':
                    queryset = queryset.filter(published=False)
        
        # Optimize with prefetch_related
        if self.action == 'retrieve':
            # For single post view, prefetch related images and approved comments
            queryset = queryset.prefetch_related(
                'images',
                Prefetch(
                    'comments',
                    queryset=Comment.objects.filter(approved=True),
                    to_attr='approved_comments'
                )
            )
        elif self.action == 'list':
            # For list view, just prefetch images
            queryset = queryset.prefetch_related('images')
            
        return queryset

    @swagger_auto_schema(
        operation_id='retrieve_post',
        operation_description='Retrieve a specific blog post by ID',
        responses={
            200: openapi.Response('Successful response', BlogPostSerializer),
            404: 'Post not found'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='create_post',
        operation_description="Create a new blog post with optional image uploads",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Post title'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Post content (HTML)'),
                'featured_image': openapi.Schema(type=openapi.TYPE_FILE, description='Featured image file'),
                'published': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the post is published')
            },
        ),
        responses={
            201: openapi.Response('Post created successfully', BlogPostSerializer),
            400: openapi.Response('Bad request')
        },
        consumes=['multipart/form-data', 'application/json']
    )
    def create(self, request, *args, **kwargs):
        """Create a new blog post, handling both JSON and multipart requests"""
        logger.info(f"Creating blog post with content type: {request.content_type}")
        
        # Extract additional images from form data if present
        additional_images = []
        additional_image_keys = [key for key in request.data.keys() if key.startswith('additional_images[')]
        
        if additional_image_keys:
            logger.info(f"Found additional image keys: {additional_image_keys}")
            for key in additional_image_keys:
                additional_images.append(request.data[key])
            
            # Create a mutable copy of the request data
            data = request.data.copy()
            
            # Remove the individual image fields
            for key in additional_image_keys:
                del data[key]
            
            # Add the collected images as a list
            if additional_images:
                data._mutable = True
                data['additional_images'] = additional_images
                data._mutable = False
                
            # Update the request data
            request._full_data = data
        
        # Continue with normal processing
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @swagger_auto_schema(
        methods=['post'],
        operation_description="Upload additional images to a blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'images': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_FILE),
                    description='List of image files to upload'
                )
            },
            required=['images']
        ),
        responses={
            201: openapi.Response(
                description="Images uploaded successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            ),
            400: "Bad request"
        },
        consumes=['multipart/form-data']
    )
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
        """Upload additional images to an existing blog post"""
        post = self.get_object()
        images = request.FILES.getlist('images')
        
        # Validate that we have images
        if not images:
            return Response(
                {'error': 'No images provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process and save each image
        uploaded_images = []
        for image_file in images:
            post_image = post.images.create(image=image_file)
            uploaded_images.append({
                'id': post_image.id,
                'url': request.build_absolute_uri(post_image.image.url) if post_image.image else None
            })
        
        return Response(uploaded_images, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_id='update_post',
        operation_description="Update an existing blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Post title'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Post content (HTML)'),
                'featured_image': openapi.Schema(type=openapi.TYPE_FILE, description='Featured image file'),
                'published': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the post is published')
            },
        ),
        responses={
            200: openapi.Response('Post updated successfully', BlogPostSerializer),
            400: openapi.Response('Bad request'),
            404: openapi.Response('Post not found')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='partial_update_post',
        operation_description="Partially update an existing blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Post title'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Post content (HTML)'),
                'featured_image': openapi.Schema(type=openapi.TYPE_FILE, description='Featured image file'),
                'published': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the post is published')
            },
        ),
        responses={
            200: openapi.Response('Post updated successfully', BlogPostSerializer),
            400: openapi.Response('Bad request'),
            404: openapi.Response('Post not found')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='delete_post',
        operation_description="Delete a blog post",
        responses={
            204: openapi.Response('Post deleted successfully'),
            404: openapi.Response('Post not found')
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get related posts for a blog post",
        responses={
            200: openapi.Response('Successful response', BlogPostListSerializer(many=True))
        }
    )
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related posts for a specific blog post"""
        post = self.get_object()
        
        # Get up to 3 related posts (same category, tags, etc.)
        # This is a simple implementation - in production you might use more sophisticated relevance algorithms
        related_posts = BlogPost.objects.filter(published=True).exclude(id=post.id)[:3]
        
        serializer = BlogPostListSerializer(related_posts, many=True, context={'request': request})
        return Response(serializer.data) 