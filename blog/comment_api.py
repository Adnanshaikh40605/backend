from django.http import JsonResponse
from rest_framework.decorators import api_view
import logging
from .models import Comment
from rest_framework.response import Response
from rest_framework import status
from .serializers import CommentSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

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
def comment_counts_direct(request):
    """Get counts for comments in different states (all, pending, approved, trash)"""
    try:
        # Log the request for debugging
        logger.info(f"Received request to comment_counts_direct endpoint: {request.path}")
        
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

# Adding this alias for the counts endpoint to make it available at /api/comments/counts/ as well
comment_counts = comment_counts_direct

@api_view(['POST'])
@csrf_exempt
def approve_comment(request):
    """Approve a comment - no authentication required"""
    try:
        comment_id = request.data.get('comment_id')
        if not comment_id:
            return JsonResponse({'error': 'Comment ID is required'}, status=400)
        
        # Log the request data for debugging
        logger.info(f"Comment approve request: comment_id={comment_id}")
        
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Approve the comment
        comment.approved = True
        comment.is_trash = False
        comment.save()
        
        # Log success
        logger.info(f"Comment {comment_id} approved successfully")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Comment approved',
            'comment_id': comment_id
        })
            
    except Exception as e:
        logger.error(f"Error approving comment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@csrf_exempt
def unapprove_comment(request):
    """Unapprove a comment - no authentication required"""
    try:
        comment_id = request.data.get('comment_id')
        if not comment_id:
            return JsonResponse({'error': 'Comment ID is required'}, status=400)
        
        # Log the request data for debugging
        logger.info(f"Comment unapprove request: comment_id={comment_id}")
        
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Unapprove the comment
        comment.approved = False
        comment.save()
        
        # Log success
        logger.info(f"Comment {comment_id} unapproved successfully")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Comment unapproved',
            'comment_id': comment_id
        })
            
    except Exception as e:
        logger.error(f"Error unapproving comment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500) 