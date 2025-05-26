from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAdminUser

from ..models import BlogPost, Comment
from ..serializers import CommentSerializer

# Setup logger
logger = logging.getLogger(__name__)

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
def comment_counts(request):
    """Get comment counts by status"""
    try:
        total_count = Comment.objects.count()
        approved_count = Comment.objects.filter(approved=True, is_trash=False).count()
        pending_count = Comment.objects.filter(approved=False, is_trash=False).count()
        trashed_count = Comment.objects.filter(is_trash=True).count()
        
        return Response({
            'total': total_count,
            'approved': approved_count,
            'pending': pending_count,
            'trashed': trashed_count
        })
    except Exception as e:
        logger.error(f"Error fetching comment counts: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    tags=['Comments'],
    operation_id='list_comments',
    operation_description='Get a list of all comments',
    manual_parameters=[
        openapi.Parameter(
            'post', 
            openapi.IN_QUERY, 
            description='Filter by post ID', 
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'approved', 
            openapi.IN_QUERY, 
            description='Filter by approval status (true/false)', 
            type=openapi.TYPE_BOOLEAN,
            required=False
        )
    ],
    responses={
        200: openapi.Response('Successful response', CommentSerializer(many=True))
    }
)
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
        """Get filtered queryset based on query parameters"""
        queryset = self.queryset
        
        # Filter by post ID if provided
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Filter by approval status if provided
        approved = self.request.query_params.get('approved')
        if approved is not None:
            if approved.lower() == 'true':
                queryset = queryset.filter(approved=True)
            elif approved.lower() == 'false':
                queryset = queryset.filter(approved=False)
        
        # Optimize with select_related
        queryset = queryset.select_related('post')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new comment with additional validation and information"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Return 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
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
            
        post = get_object_or_404(BlogPost, pk=post_id)
        approved_comments = Comment.objects.filter(post=post, approved=True)
        pending_comments = Comment.objects.filter(post=post, approved=False)
        
        return Response({
            'approved': CommentSerializer(approved_comments, many=True).data,
            'pending': CommentSerializer(pending_comments, many=True).data,
            'total': approved_comments.count() + pending_comments.count()
        }, status=status.HTTP_200_OK)
    
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
        """Return the count of pending comments"""
        count = Comment.objects.filter(approved=False, is_trash=False).count()
        return Response({'count': count}, status=status.HTTP_200_OK)
    
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
                        'counts': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'approved_samples': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
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
    def debug(self, request):
        """Debug endpoint to check comments data and filter functionality"""
        # Get query parameters
        post_id = request.query_params.get('post')
        approved = request.query_params.get('approved')
        
        # Start with all comments
        comments = Comment.objects.all()
        
        # Apply filters
        filters_applied = {}
        
        if post_id:
            comments = comments.filter(post_id=post_id)
            filters_applied['post_id'] = post_id
        
        if approved is not None:
            if approved.lower() == 'true':
                comments = comments.filter(approved=True)
                filters_applied['approved'] = True
            elif approved.lower() == 'false':
                comments = comments.filter(approved=False)
                filters_applied['approved'] = False
        
        # Sample a few comments for debugging
        sample_comments = comments[:5]
        
        # Count by status
        total_count = comments.count()
        approved_count = comments.filter(approved=True).count()
        unapproved_count = comments.filter(approved=False).count()
        trashed_count = comments.filter(is_trash=True).count()
        
        # Get all request parameters for debugging
        request_params = {}
        for key in request.query_params.keys():
            request_params[key] = request.query_params.get(key)
        
        return Response({
            'counts': {
                'total': total_count,
                'approved': approved_count,
                'unapproved': unapproved_count,
                'trashed': trashed_count
            },
            'filters_applied': filters_applied,
            'request_params': request_params,
            'sample_comments': CommentSerializer(sample_comments, many=True).data
        }, status=status.HTTP_200_OK) 