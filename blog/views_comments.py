from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count
import logging

from .models import BlogPost, Comment, CommentLike
from .serializers import CommentSerializer

# Setup logger
logger = logging.getLogger(__name__)

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # Remove all authentication for this viewset
    
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_name'],
            properties={
                'user_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the user liking the comment'),
            },
        ),
        responses={200: 'Comment liked successfully', 400: 'Bad request', 404: 'Comment not found'}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a comment"""
        try:
            comment = self.get_object()
            user_name = request.data.get('user_name')
            
            if not user_name:
                return Response({
                    'status': 'error',
                    'message': 'User name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already liked this comment
            if CommentLike.objects.filter(comment=comment, user_name=user_name).exists():
                return Response({
                    'status': 'error',
                    'message': 'You have already liked this comment'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the like
            CommentLike.objects.create(comment=comment, user_name=user_name)
            
            # Return updated comment data
            serializer = self.get_serializer(comment)
            return Response({
                'status': 'success',
                'message': 'Comment liked successfully',
                'comment': serializer.data
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_name'],
            properties={
                'user_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the user unliking the comment'),
            },
        ),
        responses={200: 'Comment unliked successfully', 400: 'Bad request', 404: 'Comment not found'}
    )
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """Unlike a comment"""
        try:
            comment = self.get_object()
            user_name = request.data.get('user_name')
            
            if not user_name:
                return Response({
                    'status': 'error',
                    'message': 'User name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to find and delete the like
            try:
                like = CommentLike.objects.get(comment=comment, user_name=user_name)
                like.delete()
            except CommentLike.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'You have not liked this comment'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Return updated comment data
            serializer = self.get_serializer(comment)
            return Response({
                'status': 'success',
                'message': 'Comment unliked successfully',
                'comment': serializer.data
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Create a new comment with better error handling"""
        try:
            # Log the incoming data for debugging
            logger.info(f"Attempting to create comment with data: {request.data}")
            
            # Extract the data from the request
            data = request.data.copy()
            
            # Handle the post field specifically
            if 'post' in data:
                try:
                    # Convert post to integer if it's a string
                    post_id = data['post']
                    if isinstance(post_id, str) and post_id.isdigit():
                        post_id = int(post_id)
                    
                    # Verify the post exists
                    post = BlogPost.objects.get(id=post_id)
                    data['post'] = post.id  # Ensure it's an ID
                    
                    logger.info(f"Found post with ID {post.id}: {post.title}")
                except BlogPost.DoesNotExist:
                    logger.error(f"Post with ID {data['post']} not found")
                    return Response(
                        {"post": ["The specified blog post does not exist."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except ValueError:
                    logger.error(f"Invalid post ID format: {data['post']}")
                    return Response(
                        {"post": ["Invalid post ID format."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error("No post ID provided in the comment data")
                return Response(
                    {"post": ["Post ID is required."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create serializer with request data
            serializer = self.get_serializer(data=data)
            
            # Check if the data is valid
            if not serializer.is_valid():
                logger.error(f"Comment validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the comment
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            logger.info(f"Comment created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            # Log any exceptions that occur
            logger.exception(f"Error creating comment: {str(e)}")
            return Response(
                {"detail": f"Failed to create comment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_queryset(self):
        """Get filtered queryset based on query parameters"""
        queryset = self.queryset
        
        # Filter by post ID if provided
        post_id = self.request.query_params.get('post')
        if post_id:
            try:
                post_id = int(post_id)
                queryset = queryset.filter(post_id=post_id)
            except ValueError:
                # Handle invalid post ID
                pass
        
        # Filter by approval status if provided
        approved = self.request.query_params.get('approved')
        if approved is not None:
            if approved.lower() == 'true':
                queryset = queryset.filter(approved=True)
            elif approved.lower() == 'false':
                queryset = queryset.filter(approved=False)
        
        # Filter by trash status if provided
        is_trash = self.request.query_params.get('is_trash')
        if is_trash is not None:
            if is_trash.lower() == 'true':
                queryset = queryset.filter(is_trash=True)
            elif is_trash.lower() == 'false':
                queryset = queryset.filter(is_trash=False)
        
        # Filter to only include top-level comments (not replies)
        queryset = queryset.filter(parent__isnull=True)
        
        # Default ordering
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """Get count of pending (unapproved) comments"""
        count = Comment.objects.filter(approved=False, is_trash=False).count()
        return Response({'count': count})
    
    @action(detail=False, methods=['get'])
    def counts(self, request):
        """Get comment counts by status"""
        all_count = Comment.objects.count()
        pending_count = Comment.objects.filter(approved=False, is_trash=False).count()
        approved_count = Comment.objects.filter(approved=True, is_trash=False).count()
        trash_count = Comment.objects.filter(is_trash=True).count()
        
        return Response({
            'all': all_count,
            'pending': pending_count,
            'approved': approved_count,
            'trash': trash_count
        })
        
    @action(detail=True, methods=['post', 'patch'])
    def approve(self, request, pk=None):
        """Approve a comment"""
        try:
            # Handle case where pk might be an object reference
            comment_id = pk
            if isinstance(pk, str) and pk.startswith('[object'):
                logger.warning(f"Received object reference as pk: {pk}")
                # Try to get comment_id from request data
                comment_id = request.data.get('id')
                if not comment_id:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid comment ID format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the comment by ID
            try:
                comment = Comment.objects.get(id=comment_id)
            except (Comment.DoesNotExist, ValueError):
                return Response({
                    'status': 'error',
                    'message': f'Comment with ID {comment_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Update approval status
            comment.approved = True
            comment.is_trash = False  # Ensure it's not in trash
            comment.save()
            
            # Serialize and return the updated comment
            serializer = self.get_serializer(comment)
            
            return Response({
                'status': 'Comment approved successfully',
                'comment': serializer.data
            })
            
        except Exception as e:
            logger.exception(f"Error approving comment: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['post', 'patch'])
    def reject(self, request, pk=None):
        """Reject (unapprove) a comment"""
        try:
            # Handle case where pk might be an object reference
            comment_id = pk
            if isinstance(pk, str) and pk.startswith('[object'):
                logger.warning(f"Received object reference as pk: {pk}")
                # Try to get comment_id from request data
                comment_id = request.data.get('id')
                if not comment_id:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid comment ID format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the comment by ID
            try:
                comment = Comment.objects.get(id=comment_id)
            except (Comment.DoesNotExist, ValueError):
                return Response({
                    'status': 'error',
                    'message': f'Comment with ID {comment_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Update approval status
            comment.approved = False
            comment.save()
            
            # Serialize and return the updated comment
            serializer = self.get_serializer(comment)
            
            return Response({
                'status': 'Comment rejected successfully',
                'comment': serializer.data
            })
            
        except Exception as e:
            logger.exception(f"Error rejecting comment: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        """Move comment to trash"""
        try:
            # Handle case where pk might be an object reference
            comment_id = pk
            if isinstance(pk, str) and pk.startswith('[object'):
                logger.warning(f"Received object reference as pk: {pk}")
                # Try to get comment_id from request data
                comment_id = request.data.get('id')
                if not comment_id:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid comment ID format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the comment by ID
            try:
                comment = Comment.objects.get(id=comment_id)
            except (Comment.DoesNotExist, ValueError):
                return Response({
                    'status': 'error',
                    'message': f'Comment with ID {comment_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Mark as trash
            comment.is_trash = True
            comment.save()
            
            # Serialize and return the updated comment
            serializer = self.get_serializer(comment)
            
            return Response({
                'status': 'Comment moved to trash successfully',
                'comment': serializer.data
            })
            
        except Exception as e:
            logger.exception(f"Error trashing comment: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore comment from trash"""
        try:
            # Handle case where pk might be an object reference
            comment_id = pk
            if isinstance(pk, str) and pk.startswith('[object'):
                logger.warning(f"Received object reference as pk: {pk}")
                # Try to get comment_id from request data
                comment_id = request.data.get('id')
                if not comment_id:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid comment ID format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the comment by ID
            try:
                comment = Comment.objects.get(id=comment_id)
            except (Comment.DoesNotExist, ValueError):
                return Response({
                    'status': 'error',
                    'message': f'Comment with ID {comment_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Unmark as trash
            comment.is_trash = False
            comment.save()
            
            # Serialize and return the updated comment
            serializer = self.get_serializer(comment)
            
            return Response({
                'status': 'Comment restored from trash successfully',
                'comment': serializer.data
            })
            
        except Exception as e:
            logger.exception(f"Error restoring comment: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to a comment"""
        try:
            # Handle case where pk might be an object reference
            comment_id = pk
            if isinstance(pk, str) and (pk.startswith('[object') or pk == 'undefined'):
                logger.warning(f"Received object reference as pk: {pk}")
                # Try to get comment_id from request data
                comment_id = request.data.get('id')
                if not comment_id:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid comment ID format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the comment by ID
            try:
                parent_comment = Comment.objects.get(id=comment_id)
            except (Comment.DoesNotExist, ValueError):
                return Response({
                    'status': 'error',
                    'message': f'Comment with ID {comment_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create reply data
            reply_data = request.data.copy()
            reply_data['post'] = parent_comment.post.id
            reply_data['parent'] = parent_comment.id
            
            # Handle admin_reply field properly as text
            # If admin_reply flag is provided and content exists, set admin_reply to the content text
            if request.data.get('admin_reply') and request.data.get('content'):
                # Fix: admin_reply should be text, not boolean
                reply_data['admin_reply'] = request.data.get('content')
                
                # Auto-approve admin replies
                reply_data['approved'] = True
            else:
                # For regular user replies, make sure they are NOT auto-approved
                # This ensures they go through moderation
                reply_data['approved'] = False
            
            # Create serializer for the reply
            reply_serializer = self.get_serializer(data=reply_data)
            
            # Validate and save if valid
            if reply_serializer.is_valid():
                reply_serializer.save()
                return Response({
                    'status': 'Reply added successfully',
                    'comment': reply_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Reply validation failed: {reply_serializer.errors}")
                return Response(reply_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.exception(f"Error adding reply: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Return all comments (approved and pending) for a post"""
        post_id = request.query_params.get('post')
        
        if not post_id:
            return Response({
                'error': 'Post ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            post_id = int(post_id)
        except ValueError:
            return Response({
                'error': 'Invalid post ID format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all non-trash top-level comments for this post (not replies)
        all_comments = Comment.objects.filter(post_id=post_id, is_trash=False, parent__isnull=True)
        
        # Split into approved and pending
        approved_comments = all_comments.filter(approved=True)
        pending_comments = all_comments.filter(approved=False)
        
        # Serialize comments
        approved_serialized = CommentSerializer(approved_comments, many=True).data
        pending_serialized = CommentSerializer(pending_comments, many=True).data
        
        return Response({
            'approved': approved_serialized,
            'pending': pending_serialized,
            'total': all_comments.count()
        })
        
    @action(detail=False, methods=['get'])
    def check_approved(self, request):
        """Check the status of approved comments for a post"""
        post_id = request.query_params.get('post')
        
        if not post_id:
            return Response({
                'error': 'Post ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            post_id = int(post_id)
            post = BlogPost.objects.get(id=post_id)
        except ValueError:
            return Response({
                'error': 'Invalid post ID format'
            }, status=status.HTTP_400_BAD_REQUEST)
        except BlogPost.DoesNotExist:
            return Response({
                'error': 'Post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get counts for top-level comments only
        comments = Comment.objects.filter(post=post, is_trash=False, parent__isnull=True)
        total_count = comments.count()
        approved_count = comments.filter(approved=True).count()
        unapproved_count = comments.filter(approved=False).count()
        
        # Get samples of top-level comments
        approved_samples = comments.filter(approved=True)[:3]
        unapproved_samples = comments.filter(approved=False)[:3]
        
        # Serialize samples
        approved_serialized = CommentSerializer(approved_samples, many=True).data
        unapproved_serialized = CommentSerializer(unapproved_samples, many=True).data
        
        return Response({
            'post_id': post.id,
            'post_title': post.title,
            'counts': {
                'total': total_count,
                'approved': approved_count,
                'unapproved': unapproved_count
            },
            'approved_samples': approved_serialized,
            'unapproved_samples': unapproved_serialized
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def comment_counts(request):
    """Get all comment counts categorized by status"""
    # Get counts for different comment categories (top-level comments only)
    top_level_comments = Comment.objects.filter(parent__isnull=True)
    total_count = top_level_comments.count()
    approved_count = top_level_comments.filter(approved=True, is_trash=False).count()
    pending_count = top_level_comments.filter(approved=False, is_trash=False).count()
    trashed_count = top_level_comments.filter(is_trash=True).count()
    
    # Calculate counts by post
    posts_with_comments = top_level_comments.values('post').distinct().count()
    posts_with_pending = top_level_comments.filter(approved=False, is_trash=False).values('post').distinct().count()
    
    # Return counts
    return Response({
        'total': total_count,
        'approved': approved_count,
        'pending': pending_count,
        'trashed': trashed_count,
        'posts': {
            'with_comments': posts_with_comments,
            'with_pending': posts_with_pending
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def comment_action(request, action, comment_id=None):
    """Perform actions on comments (approve, unapprove, trash, restore, delete)"""
    # Handle comment_id from URL or request body
    if comment_id is None:
        comment_id = request.data.get('comment_id')
        if comment_id is None:
            return Response({
                'status': 'error',
                'message': 'Comment ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the comment
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({
            'status': 'error',
            'message': f'Comment with ID {comment_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Perform the requested action
    if action == 'approve':
        comment.approved = True
        comment.is_trash = False
        comment.save()
        return Response({
            'status': 'success',
            'message': f'Comment {comment_id} approved successfully'
        })
    elif action == 'unapprove':
        comment.approved = False
        comment.save()
        return Response({
            'status': 'success',
            'message': f'Comment {comment_id} unapproved successfully'
        })
    elif action == 'trash':
        comment.is_trash = True
        comment.save()
        return Response({
            'status': 'success',
            'message': f'Comment {comment_id} moved to trash successfully'
        })
    elif action == 'restore':
        comment.is_trash = False
        comment.save()
        return Response({
            'status': 'success',
            'message': f'Comment {comment_id} restored from trash successfully'
        })
    elif action == 'delete':
        comment.delete()
        return Response({
            'status': 'success',
            'message': f'Comment {comment_id} deleted permanently'
        })
    else:
        return Response({
            'status': 'error',
            'message': f'Unknown action: {action}'
        }, status=status.HTTP_400_BAD_REQUEST)