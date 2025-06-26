from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Prefetch
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import BlogPost, BlogImage, Comment
from .serializers import BlogPostSerializer, BlogPostListSerializer, BlogImageSerializer

# Setup logger
logger = logging.getLogger(__name__)

class BlogPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog posts.
    
    list:
    Return a list of all blog posts.
    
    retrieve:
    Return a specific blog post by slug.
    
    create:
    Create a new blog post.
    
    update:
    Update an existing blog post.
    
    partial_update:
    Partially update an existing blog post.
    
    destroy:
    Delete a blog post.
    """
    queryset = BlogPost.objects.all().order_by('-created_at')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'  # Use slug instead of pk for all operations
    permission_classes = [AllowAny]
    
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
                    queryset = queryset.filter(published=True).order_by('position', '-created_at')
                elif published.lower() == 'false':
                    queryset = queryset.filter(published=False)
            
            # Filter by slug if provided
            slug_search = self.request.query_params.get('slug')
            if slug_search:
                queryset = queryset.filter(slug__icontains=slug_search)
            
            # Filter by title if provided
            title_search = self.request.query_params.get('title')
            if title_search:
                queryset = queryset.filter(title__icontains=title_search)
        
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
        operation_description="Create a new blog post with optional image uploads",
        request_body=BlogPostSerializer,
        responses={
            201: BlogPostSerializer,
            400: "Bad request"
        },
        consumes=['multipart/form-data', 'application/json'],
        tags=['Posts']
    )
    def create(self, request, *args, **kwargs):
        """Create a new blog post, handling both JSON and multipart requests"""
        logger.info(f"Creating blog post with content type: {request.content_type}")
        
        # Log request data for debugging
        logger.debug(f"Request data: {request.data}")
        
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
        manual_parameters=[
            openapi.Parameter(
                name='images',
                in_=openapi.IN_FORM,
                description='List of image files to upload',
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
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
        consumes=['multipart/form-data'],
        tags=['Posts']
    )
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, slug=None):
        """Upload additional images to a blog post"""
        post = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image in images:
            blog_image = BlogImage.objects.create(post=post, image=image)
            created_images.append(BlogImageSerializer(blog_image).data)
        
        return Response(created_images, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Delete a blog post",
        responses={
            204: "No content - post deleted successfully",
            401: "Authentication required",
            404: "Post not found",
            500: "Server error"
        },
        tags=['Posts']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to add better error handling and debugging
        """
        try:
            slug = kwargs.get('slug')
            logger.info(f"Destroy method called with args: {args}, kwargs: {kwargs}")
            logger.info(f"Attempting to delete post with slug: {slug}")
            logger.info(f"User: {request.user}, is_authenticated: {request.user.is_authenticated}")
            
            # Check permissions explicitly
            if not request.user.is_authenticated:
                logger.warning("Delete attempt by unauthenticated user")
                return Response(
                    {"detail": "Authentication required to delete posts."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get the object
            try:
                instance = self.get_object()
                logger.info(f"Found post to delete: {instance.title} (ID: {instance.id}, slug: {instance.slug})")
                
                # Perform the deletion
                self.perform_destroy(instance)
                logger.info(f"Successfully deleted post with slug: {slug}")
                
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                logger.error(f"Error getting or deleting post object: {str(e)}", exc_info=True)
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return Response(
                    {"detail": f"Failed to delete post: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error in destroy method: {str(e)}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"detail": f"Failed to delete post: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Alternative endpoint for deleting a post using POST method",
        responses={
            204: "No content - post deleted successfully",
            401: "Authentication required",
            404: "Post not found"
        },
        tags=['Posts']
    )
    @action(detail=True, methods=['post'])
    def delete(self, request, slug=None):
        """Alternative endpoint for deleting a post using POST method"""
        try:
            logger.info(f"Delete action called for post with slug or ID: {slug}")
            
            # Handle the case where we might receive a numeric ID instead of a slug
            post = None
            if slug and slug.isdigit():
                # If it's a numeric ID, try to get the post by ID
                try:
                    post_id = int(slug)
                    post = BlogPost.objects.get(id=post_id)
                    logger.info(f"Found post by ID {post_id}: {post.title}")
                except (BlogPost.DoesNotExist, ValueError) as e:
                    logger.error(f"Error finding post with ID {slug}: {str(e)}")
                    return Response(
                        {"detail": f"Post with ID {slug} not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Otherwise use the default get_object which uses the lookup_field (slug)
                try:
                    post = self.get_object()
                    logger.info(f"Found post by slug {slug}: {post.title} (ID: {post.id})")
                except Exception as e:
                    logger.error(f"Error finding post with slug {slug}: {str(e)}")
                    return Response(
                        {"detail": f"Post with slug '{slug}' not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Check permissions
            if not request.user.is_authenticated:
                logger.warning("Delete attempt by unauthenticated user")
                return Response(
                    {"detail": "Authentication required to delete posts."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Perform the deletion
            post.delete()
            logger.info(f"Successfully deleted post: {post.title} (ID: {post.id})")
            
            return Response({"detail": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"Error in delete action: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"Failed to delete post: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="List all blog posts",
        manual_parameters=[
            openapi.Parameter(
                name='published',
                in_=openapi.IN_QUERY,
                description='Filter by published status (true/false)',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='slug',
                in_=openapi.IN_QUERY,
                description='Filter by slug (partial match)',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='title',
                in_=openapi.IN_QUERY,
                description='Filter by title (partial match)',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: BlogPostListSerializer(many=True)
        },
        tags=['Posts']
    )
    def list(self, request, *args, **kwargs):
        """List all blog posts with optional filtering"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific blog post by slug",
        responses={
            200: BlogPostSerializer(),
            404: "Post not found"
        },
        tags=['Posts']
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific blog post by slug"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a blog post",
        request_body=BlogPostSerializer,
        responses={
            200: BlogPostSerializer(),
            400: "Bad request",
            404: "Post not found"
        },
        tags=['Posts']
    )
    def update(self, request, *args, **kwargs):
        """Update a blog post"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a blog post",
        request_body=BlogPostSerializer,
        responses={
            200: BlogPostSerializer(),
            400: "Bad request",
            404: "Post not found"
        },
        tags=['Posts']
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a blog post"""
        return super().partial_update(request, *args, **kwargs)


@swagger_auto_schema(
    method='get',
    tags=['Posts'],
    operation_description="Get a blog post by its slug using the /posts/by-slug/{slug}/ format",
    responses={
        200: BlogPostSerializer(),
        404: "Post not found"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_by_slug(request, slug):
    """Get a blog post by its slug"""
    post = get_object_or_404(BlogPost, slug=slug)
    serializer = BlogPostSerializer(post)
    return Response(serializer.data) 