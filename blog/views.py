from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Count, Q
import logging
from django.http import JsonResponse
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver
import traceback
from django.http import HttpResponse
from rest_framework import serializers
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.permissions import IsAdminUser

from .models import BlogPost, BlogImage, Comment, Category
from .serializers import (
    BlogPostSerializer, 
    BlogPostListSerializer, 
    BlogImageSerializer, 
    CommentSerializer,
    CategorySerializer
)

# Setup logger
logger = logging.getLogger(__name__)

def get_client_ip(request):
    """
    Get the client IP address from the request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
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

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Return related posts for a specific blog post"""
        post = self.get_object()
        
        # Get posts with the same categories/tags or similar titles
        # For now, just return a few random posts excluding the current one
        related_posts = BlogPost.objects.filter(published=True).exclude(pk=post.pk)[:3]
        
        serializer = BlogPostListSerializer(related_posts, many=True)
        return Response(serializer.data)

class BlogImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog images.
    """
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
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
    filterset_fields = ['post', 'approved', 'is_trash']
    
    def get_permissions(self):
        """
        Comments can be created by anyone, but only staff can update/delete.
        Listing comments is also allowed for public users when filtering for approved comments.
        """
        # Allow unrestricted access for create action and for retrieving approved comments
        if self.action in ['create', 'list', 'retrieve', 'approve', 'reject', 'approved_for_post']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by approved status if specified in query params
        approved = self.request.query_params.get('approved')
        if approved is not None:
            is_approved = approved.lower() in ['true', '1', 't', 'y', 'yes']
            queryset = queryset.filter(approved=is_approved)
        
        # Filter by post if specified in query params
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Add prefetch for post
        queryset = queryset.select_related('post')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new comment, capturing IP and user agent
        """
        # Add IP address and user agent to request data
        mutable_data = request.data.copy()
        mutable_data['ip_address'] = get_client_ip(request)
        mutable_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Log the request data for debugging
        logger.debug(f"Comment create data: {mutable_data}")
        
        # Process the serializer
        try:
            serializer = self.get_serializer(data=mutable_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """Get the count of pending comments"""
        count = Comment.objects.filter(approved=False).count()
        return Response({'count': count})
        
    @action(detail=False, methods=['get'])
    def debug(self, request):
        """Debug endpoint to check comments data and filter functionality"""
        # Get counts
        total_comments = Comment.objects.count()
        approved_comments = Comment.objects.filter(approved=True).count()
        pending_comments = Comment.objects.filter(approved=False).count()
        
        # Check if filtering works
        post_filter = request.query_params.get('post')
        approved_filter = request.query_params.get('approved')
        
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
                'created_at': comment.created_at
            })
        
        # Return debug info
        debug_info = {
            'counts': {
                'total': total_comments,
                'approved': approved_comments,
                'pending': pending_comments,
                'filtered': filtered_count,
            },
            'filters_applied': {
                'post': post_filter,
                'approved': approved_filter,
            },
            'request_params': dict(request.query_params),
            'sample_comments': sample_comments
        }
        
        return Response(debug_info, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Return all comments (approved and pending) for a post"""
        post_id = request.query_params.get('post')
        if not post_id:
            return Response(
                {'error': 'Post ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        post = get_object_or_404(BlogPost, pk=post_id)
        approved_comments = Comment.objects.filter(post=post, approved=True)
        pending_comments = Comment.objects.filter(post=post, approved=False)
        
        return Response({
            'approved': CommentSerializer(approved_comments, many=True).data,
            'pending': CommentSerializer(pending_comments, many=True).data,
            'total': approved_comments.count() + pending_comments.count()
        }, status=status.HTTP_200_OK)

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
            post = BlogPost.objects.get(pk=post_id)
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
            # Explicitly filter for approved comments only
            approved_comments = Comment.objects.filter(
                post_id=post_id, 
                approved=True,
                is_trash=False
            ).select_related('post')
            
            # Log details for debugging
            logger.info(f"Getting approved comments for post {post_id}")
            logger.info(f"Found {approved_comments.count()} approved comments")
            
            # Return serialized data
            serializer = CommentSerializer(approved_comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching approved comments: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['GET'])
def list_urls(request):
    """List all API URLs for debugging"""
    try:
        from django.urls import get_resolver
        
        def list_urls_recursive(patterns, parent_path=""):
            url_list = []
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is a URL include, recurse into it
                    nested_urls = list_urls_recursive(pattern.url_patterns, parent_path + pattern.pattern.regex.pattern)
                    url_list.extend(nested_urls)
                else:
                    # This is a URL pattern
                    url = parent_path + pattern.pattern.regex.pattern
                    view_name = pattern.callback.__name__ if pattern.callback else "None"
                    url_list.append({
                        'url': url,
                        'view': view_name,
                        'name': pattern.name or "None"
                    })
            return url_list
        
        resolver = get_resolver()
        all_urls = list_urls_recursive(resolver.url_patterns)
        
        # Filter out non-API URLs for clarity
        api_urls = [url for url in all_urls if '/api/' in url['url']]
        
        # Sort by URL for easier reading
        api_urls.sort(key=lambda x: x['url'])
        
        return Response({
            'count': len(api_urls),
            'urls': api_urls
        })
    except Exception as e:
        logger.error(f"Error listing URLs: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@csrf_exempt
def comment_action(request, action):
    """Handle various comment actions"""
    try:
        comment_id = request.data.get('comment_id')
        if not comment_id:
            return JsonResponse({'error': 'Comment ID is required'}, status=400)
        
        # Log the request data for debugging
        logger.info(f"Comment action request: action={action}, comment_id={comment_id}, data={request.data}")
        
        # For approve and unapprove actions, allow without authentication
        if action in ['approve', 'unapprove']:
            # No authentication required for these actions
            pass
        elif not request.user.is_authenticated or not request.user.is_staff:
            # For other actions, require staff authentication
            return JsonResponse({'error': 'Authentication required'}, status=403)
        
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

@api_view(['GET'])
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
def test_api(request):
    """Simple test endpoint to verify API routing"""
    return JsonResponse({
        'status': 'success',
        'message': 'API test endpoint successful',
        'path': request.path,
        'method': request.method
    })

@api_view(['GET'])
def debug_swagger(request):
    """Debug endpoint (kept for backward compatibility)"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is working, Swagger has been removed',
    })

@api_view(['GET'])
def approved_comments_for_post(request):
    """Get only approved comments for a specific post (direct function-based view)"""
    post_id = request.query_params.get('post')
    if not post_id:
        return Response(
            {'error': 'Post ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Explicitly filter for approved comments only
        approved_comments = Comment.objects.filter(
            post_id=post_id, 
            approved=True,
            is_trash=False
        ).select_related('post')
        
        # Log details for debugging
        logger.info(f"Getting approved comments for post {post_id} (direct function)")
        logger.info(f"Found {approved_comments.count()} approved comments")
        
        # Return serialized data
        serializer = CommentSerializer(approved_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching approved comments: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def test_approved_comments(request):
    """Test endpoint for approved comments"""
    post_id = request.query_params.get('post')
    return JsonResponse({
        'status': 'success',
        'message': 'Test endpoint for approved comments',
        'post_id': post_id,
        'endpoint': 'test_approved_comments'
    })

@api_view(['GET'])
def public_test(request):
    """Public test endpoint to verify API access and auth status"""
    is_authenticated = request.user and request.user.is_authenticated
    is_staff = request.user and request.user.is_staff if is_authenticated else False
    
    return JsonResponse({
        'status': 'success',
        'message': 'Public test endpoint successful',
        'auth': {
            'is_authenticated': is_authenticated,
            'username': request.user.username if is_authenticated else None,
            'is_staff': is_staff,
        },
        'path': request.path,
        'method': request.method,
        'comment_permissions': 'Public users can view approved comments and create new ones. Admin users can manage all comments.'
    })

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing categories.
    """
    queryset = Category.objects.all().annotate(post_count=Count('blogpost'))
    serializer_class = CategorySerializer
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get posts in a specific category"""
        category = self.get_object()
        posts = BlogPost.objects.filter(category=category, published=True)
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_all_categories(request):
    """Get all categories with post counts"""
    categories = Category.objects.all().annotate(post_count=Count('blogpost'))
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_category_by_slug(request, slug):
    """Get a category by its slug"""
    category = get_object_or_404(Category.objects.annotate(post_count=Count('blogpost')), slug=slug)
    serializer = CategorySerializer(category)
    return Response(serializer.data)

@api_view(['GET'])
def search_posts(request):
    """Search posts by query term"""
    query = request.query_params.get('q', '')
    
    if not query:
        return Response({'error': 'Search query is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Search in title, content, and excerpt
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            published=True
        ).prefetch_related('images').order_by('-created_at')
        
        # Serialize and return
        serializer = BlogPostListSerializer(posts, many=True)
        return Response({
            'query': query,
            'result_count': posts.count(),
            'results': serializer.data
        })
    except Exception as e:
        logger.error(f"Error searching posts: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_latest_posts(request):
    """Get the latest published blog posts"""
    count = int(request.query_params.get('count', 5))
    
    try:
        posts = BlogPost.objects.filter(
            published=True
        ).prefetch_related('images').order_by('-created_at')[:count]
        
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching latest posts: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_post_by_slug(request, slug):
    """Get a specific post by its slug"""
    try:
        post = get_object_or_404(
            BlogPost.objects.prefetch_related(
                'images',
                Prefetch(
                    'comments',
                    queryset=Comment.objects.filter(approved=True),
                    to_attr='approved_comments'
                )
            ),
            slug=slug, 
            published=True
        )
        
        serializer = BlogPostSerializer(post)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching post by slug: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def featured_posts(request):
    """Get featured blog posts"""
    count = int(request.query_params.get('count', 3))
    
    try:
        posts = BlogPost.objects.filter(
            featured=True,
            published=True
        ).prefetch_related('images').order_by('-created_at')[:count]
        
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching featured posts: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
