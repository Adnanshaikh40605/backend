from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from .models import BlogPost, Comment, Category


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for authenticated users
    Returns counts for posts, comments, and categories
    """
    try:
        # Get all posts count
        total_posts = BlogPost.objects.count()
        
        # Get published posts count
        published_posts = BlogPost.objects.filter(published=True).count()
        
        # Get draft posts count
        draft_posts = BlogPost.objects.filter(published=False).count()
        
        # Get total comments count
        total_comments = Comment.objects.count()
        
        # Get pending (unapproved) comments count
        pending_comments = Comment.objects.filter(approved=False).count()
        
        # Get total categories count
        total_categories = Category.objects.count()
        
        # Prepare response data
        stats = {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'total_comments': total_comments,
            'pending_comments': pending_comments,
            'total_categories': total_categories,
        }
        
        return Response({
            'success': True,
            'data': stats,
            'message': 'Dashboard statistics retrieved successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve dashboard statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
