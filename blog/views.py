from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, renderer_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
import logging
from django.http import JsonResponse
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import traceback
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework import permissions
from django.contrib.auth.models import User
from .models import BlogPost, BlogImage, Comment
from .serializers import (
    BlogPostSerializer, 
    BlogPostListSerializer, 
    BlogImageSerializer, 
    CommentSerializer,
    UserSerializer,
    UserRegisterSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenObtainPairView
import json

# Setup logger 1234
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
    
    def get_permissions(self):
        """
        Override permissions:
        - Allow anyone to list and retrieve posts
        - Require authentication for create, update, delete
        """
        logger.info(f"BlogPostViewSet - Action: {self.action}")
        
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
            
        logger.info(f"BlogPostViewSet - Using permission classes: {permission_classes}")
        return [permission() for permission in permission_classes]
    
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
        """
        Alternative endpoint for deleting a post using POST method
        """
        logger.info(f"Delete action called with slug/id: {slug}")
        logger.info(f"Request user: {request.user}, authenticated: {request.user.is_authenticated}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request query params: {request.query_params}")
        
        try:
            # Check if slug is a numeric ID
            if slug and slug.isdigit():
                # If it's a numeric ID, find the post by ID
                try:
                    logger.info(f"Looking up post with ID: {slug}")
                    post = BlogPost.objects.get(id=int(slug))
                    logger.info(f"Found post with ID {slug}, slug: {post.slug}")
                    
                    # Instead of calling destroy directly, perform the deletion here
                    post.delete()
                    logger.info(f"Successfully deleted post with ID: {slug}")
                    return Response(status=status.HTTP_204_NO_CONTENT)
                    
                except BlogPost.DoesNotExist:
                    logger.error(f"Post with ID {slug} not found")
                    return Response(
                        {"detail": f"Post with ID {slug} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # If it's a slug, use get_object() from the viewset
                logger.info(f"Using slug directly: {slug}")
                instance = get_object_or_404(BlogPost, slug=slug)
                instance.delete()
                logger.info(f"Successfully deleted post with slug: {slug}")
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            logger.error(f"Error in delete action: {str(e)}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
        return super().partial_update(request, *args, **kwargs)

class BlogImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog images.
    """
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # Allow any user to access blog images

    @swagger_auto_schema(
        operation_description="List all blog images",
        responses={
            200: BlogImageSerializer(many=True)
        },
        tags=['Images']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Retrieve a specific blog image",
        responses={
            200: BlogImageSerializer(),
            404: "Image not found"
        },
        tags=['Images']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Create a new blog image",
        request_body=BlogImageSerializer,
        responses={
            201: BlogImageSerializer(),
            400: "Bad request"
        },
        tags=['Images']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Update a blog image",
        request_body=BlogImageSerializer,
        responses={
            200: BlogImageSerializer(),
            400: "Bad request",
            404: "Image not found"
        },
        tags=['Images']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Partially update a blog image",
        request_body=BlogImageSerializer,
        responses={
            200: BlogImageSerializer(),
            400: "Bad request",
            404: "Image not found"
        },
        tags=['Images']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Delete a blog image",
        responses={
            204: "No content - image deleted successfully",
            404: "Image not found"
        },
        tags=['Images']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog comments.
    
    list:
    Return a list of all comments.
    
    retrieve:
    Return a specific comment by ID.
    
    create:
    Create a new comment.
    
    update:
    Update an existing comment.
    
    partial_update:
    Partially update an existing comment.
    
    destroy:
    Delete a comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        """
        Override permissions:
        - Allow anyone to create comments and view approved comments
        - Require authentication for moderation actions
        """
        if self.action in ['create', 'list', 'retrieve', 'approved_for_post', 'counts']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        operation_description="List comments with optional filtering by post, approval status, and trash status",
        manual_parameters=[
            openapi.Parameter(
                name='post',
                in_=openapi.IN_QUERY,
                description='Filter comments by post ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                name='approved',
                in_=openapi.IN_QUERY,
                description='Filter comments by approval status (true/false)',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='is_trash',
                in_=openapi.IN_QUERY,
                description='Filter comments by trash status (true/false)',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='page',
                in_=openapi.IN_QUERY,
                description='Page number for pagination',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                name='limit',
                in_=openapi.IN_QUERY,
                description='Number of items per page',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: CommentSerializer(many=True)
        },
        tags=['Comments']
    )
    def list(self, request, *args, **kwargs):
        """List comments with optional filtering by post, approval status, and trash status"""
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = self.queryset
        # Filter by post ID
        post = self.request.query_params.get('post')
        if post is not None:
            queryset = queryset.filter(post=post)
            
        # Filter by approval status
        approved = self.request.query_params.get('approved')
        if approved is not None:
            if approved.lower() == 'true':
                queryset = queryset.filter(approved=True)
                logger.info(f"Filtering for APPROVED comments only for post {post}")
            elif approved.lower() == 'false':
                queryset = queryset.filter(approved=False)
                logger.info(f"Filtering for UNAPPROVED comments only for post {post}")
        
        # Filter by trash status
        is_trash = self.request.query_params.get('is_trash')
        if is_trash is not None:
            if is_trash.lower() == 'true':
                queryset = queryset.filter(is_trash=True)
                logger.info(f"Filtering for TRASHED comments only")
            elif is_trash.lower() == 'false':
                queryset = queryset.filter(is_trash=False)
                logger.info(f"Filtering for NON-TRASHED comments only")
                
        # Log the query for debugging
        logger.debug(f"Comment queryset filters: post={post}, approved={approved}, is_trash={is_trash}")
        logger.debug(f"Comment queryset SQL: {str(queryset.query)}")
        count = queryset.count()
        logger.debug(f"Comment queryset count: {count}")
        
        # Additional logging for debugging
        if count == 0 and approved == 'true':
            # If we're looking for approved comments but found none, log all comments for this post
            all_comments = Comment.objects.filter(post=post)
            approved_count = all_comments.filter(approved=True).count()
            logger.info(f"Found {approved_count} approved comments out of {all_comments.count()} total for post {post}")
            
            # Log the first few comments with their approval status for debugging
            for comment in all_comments[:5]:
                logger.info(f"Comment {comment.id}: approved={comment.approved}, content={comment.content[:30]}")
        
        return queryset

    @swagger_auto_schema(
        operation_description="Retrieve a specific comment by ID",
        responses={
            200: CommentSerializer(),
            404: "Comment not found"
        },
        tags=['Comments']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Create a new comment",
        request_body=CommentSerializer,
        responses={
            201: CommentSerializer(),
            400: "Bad request"
        },
        tags=['Comments']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Update an existing comment",
        request_body=CommentSerializer,
        responses={
            200: CommentSerializer(),
            400: "Bad request",
            404: "Comment not found"
        },
        tags=['Comments']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Partially update an existing comment",
        request_body=CommentSerializer,
        responses={
            200: CommentSerializer(),
            400: "Bad request",
            404: "Comment not found"
        },
        tags=['Comments']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="Delete a comment",
        responses={
            204: "No content - comment deleted successfully",
            404: "Comment not found"
        },
        tags=['Comments']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve the count of pending comments",
        responses={
            200: openapi.Response(
                description="Pending comment count",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of pending comments')
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """Get the count of pending comments"""
        count = Comment.objects.filter(approved=False).count()
        return Response({'count': count})
        
    @swagger_auto_schema(
        operation_description="Debug endpoint to check comments data and filter functionality",
        manual_parameters=[
            openapi.Parameter(
                name='post',
                in_=openapi.IN_QUERY,
                description='Post ID to filter comments',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                name='approved',
                in_=openapi.IN_QUERY,
                description='Approval status to filter by (true/false)',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='is_trash',
                in_=openapi.IN_QUERY,
                description='Trash status to filter by (true/false)',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Debug information",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'counts': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'request_params': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'sample_comments': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        )
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def debug(self, request):
        """Debug endpoint to check comments data and filter functionality"""
        # Get counts
        total_comments = Comment.objects.count()
        approved_comments = Comment.objects.filter(approved=True).count()
        pending_comments = Comment.objects.filter(approved=False).count()
        trashed_comments = Comment.objects.filter(is_trash=True).count()
        non_trashed_comments = Comment.objects.filter(is_trash=False).count()
        
        # Check if filtering works
        post_filter = request.query_params.get('post')
        approved_filter = request.query_params.get('approved')
        is_trash_filter = request.query_params.get('is_trash')
        
        filtered_queryset = self.get_queryset()
        filtered_count = filtered_queryset.count()
        
        # Sample data
        sample_comments = []
        for comment in filtered_queryset[:5]:  # Get first 5 comments
            sample_comments.append({
                'id': comment.id,
                'post_id': comment.post_id,
                'content_preview': comment.content[:50] + ('...' if len(comment.content) > 50 else ''),
                'approved': comment.approved,
                'is_trash': comment.is_trash,
                'created_at': comment.created_at
            })
        
        # Return debug info
        debug_info = {
            'counts': {
                'total': total_comments,
                'approved': approved_comments,
                'pending': pending_comments,
                'trashed': trashed_comments,
                'non_trashed': non_trashed_comments,
                'filtered': filtered_count,
            },
            'filters_applied': {
                'post': post_filter,
                'approved': approved_filter,
                'is_trash': is_trash_filter
            },
            'request_params': dict(request.query_params),
            'sample_comments': sample_comments
        }
        
        return Response(debug_info, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        methods=['post', 'patch'],
        operation_description="Approve a comment",
        responses={
            200: openapi.Response(
                description="Comment approved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                        'comment': openapi.Schema(type=openapi.TYPE_OBJECT, description='The approved comment data')
                    }
                )
            ),
            404: "Comment not found"
        }
    )
    @action(detail=True, methods=['post', 'patch'])
    def approve(self, request, pk=None):
        """Approve a comment"""
        comment = self.get_object()
        logger.info(f"Approving comment {comment.id} for post {comment.post.id}")
        logger.info(f"Comment status before: approved={comment.approved}")
        
        # Explicitly set approved to True
        comment.approved = True
        comment.save()
        
        # Verify the change was saved
        comment.refresh_from_db()
        logger.info(f"Comment status after: approved={comment.approved}")
        
        # Get all approved comments for this post for verification
        approved_count = Comment.objects.filter(post=comment.post, approved=True).count()
        logger.info(f"Post {comment.post.id} now has {approved_count} approved comments")
        
        # Return the updated comment data
        serializer = CommentSerializer(comment)
        return Response({
            'status': 'comment approved',
            'comment': serializer.data,
            'approved_count': approved_count
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        methods=['post', 'patch'],
        operation_description="Reject a comment",
        responses={
            200: openapi.Response(
                description="Comment rejected successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'comment': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: "Comment not found"
        }
    )
    @action(detail=True, methods=['post', 'patch'])
    def reject(self, request, pk=None):
        """Reject (unapprove) a comment"""
        comment = self.get_object()
        logger.info(f"Rejecting comment {comment.id} for post {comment.post.id if comment.post else 'unknown'}")
        logger.info(f"Comment status before: approved={comment.approved}")
        
        # Set approved to False instead of deleting
        comment.approved = False
        comment.save()
        
        # Verify the change was saved
        comment.refresh_from_db()
        logger.info(f"Comment status after: approved={comment.approved}")
        
        # Return the updated comment data
        serializer = CommentSerializer(comment)
        return Response({
            'status': 'comment rejected',
            'comment': serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Bulk approve multiple comments",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of comment IDs to approve'
                )
            },
            required=['comment_ids']
        ),
        responses={
            200: openapi.Response(
                description="Comments approved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'approved_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'approved_ids': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER)
                        )
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Approve multiple comments at once"""
        comment_ids = request.data.get('comment_ids', [])
        if not comment_ids:
            return Response(
                {'error': 'No comment IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Log for debugging
        logger.info(f"Bulk approving comments: {comment_ids}")
        
        # Filter comments that aren't already approved
        comments = Comment.objects.filter(id__in=comment_ids, approved=False)
        count = comments.count()
        
        # Update the comments
        comments.update(approved=True, is_trash=False)
        
        logger.info(f"Bulk approved {count} comments")
        
        return Response({'status': f'{count} comments approved'}, status=status.HTTP_200_OK)
        
    @swagger_auto_schema(
        operation_description="Bulk reject (unapprove) multiple comments",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of comment IDs to reject'
                )
            },
            required=['comment_ids']
        ),
        responses={
            200: openapi.Response(
                description="Comments rejected successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_reject(self, request):
        """Reject (unapprove) multiple comments at once"""
        comment_ids = request.data.get('comment_ids', [])
        if not comment_ids:
            return Response(
                {'error': 'No comment IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Log for debugging
        logger.info(f"Bulk rejecting comments: {comment_ids}")
        
        # Filter comments that are currently approved
        comments = Comment.objects.filter(id__in=comment_ids, approved=True)
        count = comments.count()
        
        # Update comments to be unapproved (not deleted)
        comments.update(approved=False)
        
        logger.info(f"Bulk rejected {count} comments")
        
        return Response({'status': f'{count} comments rejected'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Return all comments (approved and pending) for a post",
        manual_parameters=[
            openapi.Parameter(
                name='post',
                in_=openapi.IN_QUERY,
                description='Post ID to filter comments',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Comments fetched successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'approved': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'pending': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Return all comments (approved and pending) for a post"""
        post_id = request.query_params.get('post')
        if not post_id:
            return Response(
                {'error': 'Post ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        post = get_object_or_404(BlogPost, slug=post_id)
        approved_comments = Comment.objects.filter(post=post, approved=True)
        pending_comments = Comment.objects.filter(post=post, approved=False)
        
        return Response({
            'approved': CommentSerializer(approved_comments, many=True).data,
            'pending': CommentSerializer(pending_comments, many=True).data,
            'total': approved_comments.count() + pending_comments.count()
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Check the status of approved comments for a post",
        manual_parameters=[
            openapi.Parameter(
                name='post',
                in_=openapi.IN_QUERY,
                description='Post ID to check comments for',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Comment status retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'post_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'counts': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'approved': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'unapproved': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'approved_samples': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'unapproved_samples': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        )
                    }
                )
            ),
            400: "Bad request",
            404: "Post not found"
        }
    )
    @action(detail=False, methods=['get'])
    def check_approved(self, request):
        """Check the status of approved comments for a specific post"""
        post_id = request.query_params.get('post')
        if not post_id:
            return Response(
                {'error': 'Post ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = BlogPost.objects.get(slug=post_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': f'Post with ID {post_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all comments for this post
        all_comments = Comment.objects.filter(post=post)
        
        # Count by approval status
        total_count = all_comments.count()
        approved_count = all_comments.filter(approved=True).count()
        unapproved_count = all_comments.filter(approved=False).count()
        
        # Get sample comments
        approved_samples = all_comments.filter(approved=True)[:5]
        unapproved_samples = all_comments.filter(approved=False)[:5]
        
        # Serialize sample comments
        approved_samples_data = CommentSerializer(approved_samples, many=True).data
        unapproved_samples_data = CommentSerializer(unapproved_samples, many=True).data
        
        return Response({
            'post_id': post_id,
            'post_title': post.title,
            'counts': {
                'total': total_count,
                'approved': approved_count,
                'unapproved': unapproved_count
            },
            'approved_samples': approved_samples_data,
            'unapproved_samples': unapproved_samples_data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get only approved comments for a specific post",
        manual_parameters=[
            openapi.Parameter(
                name='post',
                in_=openapi.IN_QUERY,
                description='Post ID to get approved comments for',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: CommentSerializer(many=True),
            400: "Bad request",
            404: "Post not found"
        }
    )
    @action(detail=False, methods=['get'])
    def approved_for_post(self, request):
        """Get only approved comments for a specific post (dedicated endpoint)"""
        post_id = request.query_params.get('post')
        if not post_id:
            return Response(
                {'error': 'Post ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = BlogPost.objects.get(slug=post_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': f'Post with ID {post_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Explicitly filter for approved comments only
        approved_comments = Comment.objects.filter(post=post, approved=True)
        
        # Log details for debugging
        logger.info(f"Getting approved comments for post {post_id}")
        logger.info(f"Found {approved_comments.count()} approved comments")
        
        # Return serialized data
        serializer = CommentSerializer(approved_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        methods=['post', 'patch', 'put', 'delete'],
        operation_description="Reply to a comment or manage reply",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Reply text content'
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Name of the person replying'
                ),
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Email of the person replying'
                )
            },
            required=['content']
        ),
        responses={
            200: openapi.Response(
                description="Reply operation successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'reply': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: "Comment not found"
        }
    )
    @action(detail=True, methods=['post', 'patch', 'put', 'delete'])
    def reply(self, request, pk=None):
        """Add, update or delete an admin reply to a comment"""
        comment = self.get_object()
        
        # Handle DELETE request - remove admin reply
        if request.method == 'DELETE':
            comment.admin_reply = None
            comment.save()
            
            # Log for debugging
            logger.info(f"Deleted admin reply from comment {comment.id} for post {comment.post.id}")
            
            return Response({
                'status': 'reply deleted',
                'comment': CommentSerializer(comment).data
            }, status=status.HTTP_200_OK)
        
        # Handle POST, PATCH, PUT requests - add or update admin reply
        reply_text = request.data.get('admin_reply')
        
        if not reply_text:
            return Response(
                {'error': 'Reply content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        comment.admin_reply = reply_text
        comment.save()
        
        # Log for debugging
        logger.info(f"Added/updated admin reply to comment {comment.id} for post {comment.post.id}")
        
        # Return the updated comment data
        serializer = CommentSerializer(comment)
        return Response({
            'status': 'reply added' if request.method == 'POST' else 'reply updated',
            'comment': serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get comment counts by status",
        responses={
            200: openapi.Response(
                description="Comment counts",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'all': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'pending': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'approved': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'trash': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def counts(self, request):
        """Get counts for comments in different states (all, pending, approved, trash)"""
        try:
            # Log the request for debugging
            logger.info(f"Received request to counts endpoint: {request.path}")
            
            # Force evaluate the counts to ensure they're accurate
            all_count = Comment.objects.filter(is_trash=False).count()
            pending_count = Comment.objects.filter(approved=False, is_trash=False).count()
            approved_count = Comment.objects.filter(approved=True, is_trash=False).count()
            trash_count = Comment.objects.filter(is_trash=True).count()
            
            # Log counts for debugging
            logger.info(f"Comment counts: all={all_count}, pending={pending_count}, approved={approved_count}, trash={trash_count}")
            
            response_data = {
                'all': all_count,
                'pending': pending_count,
                'approved': approved_count,
                'trash': trash_count,
                'status': 'success',
                'message': 'Comment counts retrieved successfully'
            }
            
            # Return the response
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error getting comment counts: {str(e)}", exc_info=True)
            return Response({'error': str(e), 'detail': 'An error occurred while fetching comment counts'}, status=500)

@api_view(['GET'])
def list_urls(request):
    """Debug view to list all URLs in the Django project."""
    urlconf = __import__(get_resolver().urlconf_name, fromlist=[''])
    
    def list_urls_recursive(patterns, parent_path=""):
        urls = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                # Get the pattern string or regex pattern
                pattern_str = str(pattern.pattern)
                # Append to parent path
                full_path = parent_path + pattern_str
                # Get the name if available
                name = pattern.name if hasattr(pattern, 'name') else ''
                # Get the callback function
                callback = pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else str(pattern.callback)
                urls.append({
                    'path': full_path,
                    'name': name,
                    'callback': callback
                })
            elif isinstance(pattern, URLResolver):
                # Get resolver pattern
                resolver_path = str(pattern.pattern)
                # Recursively get patterns from resolver
                urls.extend(list_urls_recursive(pattern.url_patterns, parent_path + resolver_path))
        return urls
    
    try:
        all_urls = list_urls_recursive(urlconf.urlpatterns)
        # Filter for comment URLs to make output manageable
        comment_urls = [url for url in all_urls if 'comment' in url['path'].lower()]
        return JsonResponse({'comment_urls': comment_urls})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@swagger_auto_schema(
    method='post',
    tags=['Comments'],
    operation_description="Perform actions on comments (approve, unapprove, trash, restore, delete)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'comment_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the comment to act upon'
            )
        },
        required=['comment_id']
    ),
    responses={
        200: openapi.Response(
            description="Action performed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_action(request, action, comment_id=None):
    """Handle comment actions from admin interface"""
    try:
        # Get comment_id from URL parameter or request body
        comment_id = comment_id or request.data.get('comment_id')
        if not comment_id:
            return JsonResponse({'error': 'Comment ID is required'}, status=400)
        
        # Log the request data for debugging
        logger.info(f"Comment action request: action={action}, comment_id={comment_id}, data={request.data}")
        
        comment = get_object_or_404(Comment, id=comment_id)
        
        if action == 'approve':
            comment.approved = True
            comment.is_trash = False
            comment.save()
            return JsonResponse({'status': 'success', 'message': 'Comment approved'})
            
        elif action == 'unapprove':
            comment.approved = False
            comment.save()
            return JsonResponse({'status': 'success', 'message': 'Comment unapproved'})
            
        elif action == 'trash':
            comment.is_trash = True
            comment.save()
            return JsonResponse({'status': 'success', 'message': 'Comment moved to trash'})
            
        elif action == 'restore':
            comment.is_trash = False
            comment.save()
            return JsonResponse({'status': 'success', 'message': 'Comment restored from trash'})
            
        elif action == 'delete':
            comment.delete()
            return JsonResponse({'status': 'success', 'message': 'Comment permanently deleted'})
            
        else:
            return JsonResponse({'error': f'Unknown action: {action}'}, status=400)
    
    except Exception as e:
        logger.error(f"Error performing comment action: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@swagger_auto_schema(
    method='get',
    tags=['Comments'],
    operation_description="Get comment counts by status",
    responses={
        200: openapi.Response(
            description="Comment counts",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'approved': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'pending': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'trashed': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def comment_counts(request):
    """Get counts for comments in different states (all, pending, approved, trash)"""
    try:
        # Log the request for debugging
        logger.info(f"Received request to comment_counts endpoint: {request.path}")
        
        # Force evaluate the counts to ensure they're accurate
        all_count = Comment.objects.filter(is_trash=False).count()
        pending_count = Comment.objects.filter(approved=False, is_trash=False).count()
        approved_count = Comment.objects.filter(approved=True, is_trash=False).count()
        trash_count = Comment.objects.filter(is_trash=True).count()
        
        # Log counts for debugging
        logger.info(f"Comment counts: all={all_count}, pending={pending_count}, approved={approved_count}, trash={trash_count}")
        
        # Verify the counts match expectations
        total_count = Comment.objects.count()
        expected_sum = all_count + trash_count
        if total_count != expected_sum:
            logger.warning(f"Total comment count ({total_count}) doesn't match sum of all + trash ({expected_sum})")
        
        response_data = {
            'all': all_count,
            'pending': pending_count,
            'approved': approved_count,
            'trash': trash_count,
            'status': 'success',
            'message': 'Comment counts retrieved successfully',
            'path': request.path
        }
        
        # Return the response
        logger.info(f"Returning comment counts: {response_data}")
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error getting comment counts: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e), 'detail': 'An error occurred while fetching comment counts'}, status=500)

@api_view(['GET'])
def debug_swagger(request):
    """Debug endpoint to help diagnose Swagger issues"""
    from drf_yasg.generators import OpenAPISchemaGenerator
    from drf_yasg.codecs import OpenAPICodecJson
    import traceback
    
    try:
        # Get the schema generator
        generator = OpenAPISchemaGenerator(
            info=openapi.Info(
                title="Blog CMS API",
                default_version='v1',
                description="Debug schema generation"
            )
        )
        
        # Try to generate the schema
        schema = generator.get_schema(request=request, public=True)
        
        # Convert to JSON
        codec = OpenAPICodecJson()
        schema_json = codec.encode(schema).decode('utf-8')
        
        # Get ViewSet information
        viewsets_info = {}
        for viewset_name, viewset_class in [
            ('BlogPostViewSet', BlogPostViewSet),
            ('BlogImageViewSet', BlogImageViewSet),
            ('CommentViewSet', CommentViewSet)
        ]:
            viewsets_info[viewset_name] = get_viewset_methods(viewset_class)
        
        # Return debug information
        return JsonResponse({
            'status': 'success',
            'message': 'Schema generated successfully',
            'schema_sample': schema_json[:500] + '...',  # First 500 chars of schema
            'viewsets': viewsets_info,
            'routes': list_urls_recursive(get_resolver().url_patterns),
        })
        
    except Exception as e:
        # Capture the full exception details
        tb = traceback.format_exc()
        
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'error_type': type(e).__name__,
            'traceback': tb,
            'swagger_decorators': find_swagger_decorators(),
        }, status=500)

@api_view(['GET'])
def debug_swagger_schema(request):
    """Debug endpoint to help diagnose Swagger schema generation issues"""
    from drf_yasg.generators import OpenAPISchemaGenerator
    from drf_yasg.codecs import OpenAPICodecJson
    import traceback
    import json
    
    results = {
        'status': 'checking',
        'errors': [],
        'tests': []
    }
    
    # Test serializing each model
    try:
        # Test BlogPostSerializer
        from .serializers import BlogPostSerializer
        from .models import BlogPost
        post = BlogPost.objects.first()
        if post:
            serializer = BlogPostSerializer(post)
            results['tests'].append({
                'model': 'BlogPost',
                'serializer': 'BlogPostSerializer',
                'status': 'success',
                'sample': serializer.data
            })
        else:
            results['tests'].append({
                'model': 'BlogPost',
                'serializer': 'BlogPostSerializer',
                'status': 'skipped',
                'reason': 'No instances available'
            })
    except Exception as e:
        results['errors'].append({
            'model': 'BlogPost',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
    
    # Test CommentSerializer
    try:
        from .serializers import CommentSerializer
        from .models import Comment
        comment = Comment.objects.first()
        if comment:
            serializer = CommentSerializer(comment)
            results['tests'].append({
                'model': 'Comment',
                'serializer': 'CommentSerializer',
                'status': 'success',
                'sample': serializer.data
            })
        else:
            results['tests'].append({
                'model': 'Comment',
                'serializer': 'CommentSerializer',
                'status': 'skipped',
                'reason': 'No instances available'
            })
    except Exception as e:
        results['errors'].append({
            'model': 'Comment',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
    
    # Test BlogImageSerializer
    try:
        from .serializers import BlogImageSerializer
        from .models import BlogImage
        image = BlogImage.objects.first()
        if image:
            serializer = BlogImageSerializer(image)
            results['tests'].append({
                'model': 'BlogImage',
                'serializer': 'BlogImageSerializer',
                'status': 'success',
                'sample': serializer.data
            })
        else:
            results['tests'].append({
                'model': 'BlogImage',
                'serializer': 'BlogImageSerializer',
                'status': 'skipped',
                'reason': 'No instances available'
            })
    except Exception as e:
        results['errors'].append({
            'model': 'BlogImage',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
    
    # Now try to generate the schema
    try:
        generator = OpenAPISchemaGenerator(
            info=openapi.Info(
                title="Blog CMS API",
                default_version='v1',
                description="Debug schema generation"
            )
        )
        
        # Try to generate the schema
        schema = generator.get_schema(request=request, public=True)
        
        # Convert to JSON
        codec = OpenAPICodecJson()
        schema_json = codec.encode(schema).decode('utf-8')
        
        results['schema_generation'] = 'success'
        results['schema_sample'] = schema_json[:500] + '...'  # First 500 chars of schema
    except Exception as e:
        results['schema_generation'] = 'failed'
        results['schema_error'] = str(e)
        results['schema_traceback'] = traceback.format_exc()
    
    results['status'] = 'completed'
    return JsonResponse(results)

def find_swagger_decorators():
    """Find all swagger_auto_schema decorators in the codebase"""
    import inspect
    import sys
    
    results = []
    
    # Check BlogPostViewSet
    for name, method in inspect.getmembers(BlogPostViewSet, predicate=inspect.isfunction):
        if hasattr(method, '_swagger_auto_schema'):
            results.append(f"BlogPostViewSet.{name} has swagger_auto_schema")
    
    # Check BlogImageViewSet
    for name, method in inspect.getmembers(BlogImageViewSet, predicate=inspect.isfunction):
        if hasattr(method, '_swagger_auto_schema'):
            results.append(f"BlogImageViewSet.{name} has swagger_auto_schema")
    
    # Check CommentViewSet
    for name, method in inspect.getmembers(CommentViewSet, predicate=inspect.isfunction):
        if hasattr(method, '_swagger_auto_schema'):
            results.append(f"CommentViewSet.{name} has swagger_auto_schema")
    
    return results

# Function to get all viewset methods
def get_viewset_methods(viewset_class):
    methods = {}
    for method_name in dir(viewset_class):
        if not method_name.startswith('_'):
            method = getattr(viewset_class, method_name)
            if callable(method) and hasattr(method, '__doc__') and method.__doc__:
                methods[method_name] = method.__doc__.strip()
    return methods

class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile"""
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
        }
        return Response(data)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        """
        Custom token view to handle CORS and provide better error messages
        """
        try:
            response = super().post(request, *args, **kwargs)
            
            # Allow credentials
            response["Access-Control-Allow-Credentials"] = "true"
            
            # For development, could also be set to specific origins
            response["Access-Control-Allow-Origin"] = request.META.get('HTTP_ORIGIN', 'http://localhost:3000')
            
            return response
        except Exception as e:
            logger.error(f"Token error: {str(e)}")
            return Response(
                {"detail": "Invalid credentials or server error", "error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    def options(self, request, *args, **kwargs):
        """
        Handle pre-flight CORS request
        """
        response = super().options(request, *args, **kwargs)
        
        # Set CORS headers for preflight requests
        response["Access-Control-Allow-Origin"] = request.META.get('HTTP_ORIGIN', 'http://localhost:3000')
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"  # 24 hours
        
        return response

@api_view(['POST', 'GET', 'OPTIONS'])
@permission_classes([AllowAny])
def debug_token(request):
    """Debug endpoint for token issues"""
    if request.method == 'OPTIONS':
        response = JsonResponse({'message': 'OPTIONS request received'})
        return response
        
    if request.method == 'GET':
        response = JsonResponse({
            'message': 'This is the token debug endpoint. Send a POST request with username and password to test token generation.',
            'endpoints': {
                'token': '/api/token/',
                'token_refresh': '/api/token/refresh/',
                'token_verify': '/api/token/verify/',
                'debug': '/api/debug-token/'
            }
        })
        return response
    
    try:
        # Get request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'error': 'Missing credentials',
                'message': 'Please provide both username and password',
                'received_data': data
            }, status=400)
            
        # Try to authenticate
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # User authenticated, now generate token manually
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return JsonResponse({
                'success': True,
                'message': 'Authentication successful',
                'user': username,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            # Authentication failed
            return JsonResponse({
                'error': 'Authentication failed',
                'message': 'Invalid username or password',
                'username': username
            }, status=401)
            
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'request_method': request.method,
            'content_type': request.content_type,
            'headers': dict(request.headers)
        }, status=500)
