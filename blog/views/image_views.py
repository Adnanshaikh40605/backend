from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import BlogImage, BlogPost
from ..serializers import BlogImageSerializer

# Setup logger
logger = logging.getLogger(__name__)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    """Upload an image and optionally associate with a post"""
    try:
        # Check if image file exists in request
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get post ID if provided
        post_id = request.data.get('post')
        post = None
        
        if post_id:
            try:
                post = BlogPost.objects.get(pk=post_id)
            except BlogPost.DoesNotExist:
                return Response(
                    {'error': f'Post with ID {post_id} does not exist'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create and save the image
        image_file = request.FILES['image']
        blog_image = BlogImage(image=image_file)
        
        if post:
            blog_image.post = post
            
        blog_image.save()
        
        # Serialize and return
        serializer = BlogImageSerializer(blog_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error in upload_image: {str(e)}")
        return Response(
            {'error': f'Failed to upload image: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    tags=['Images'],
    operation_id='list_images',
    operation_description='Get a list of all blog images',
    responses={
        200: openapi.Response('Successful response', BlogImageSerializer(many=True))
    }
)
class BlogImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog images.
    
    list:
    Return a list of all images.
    
    retrieve:
    Return a specific image by ID.
    
    create:
    Create a new image.
    
    update:
    Update an existing image.
    
    destroy:
    Delete an image.
    """
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_id='retrieve_image',
        operation_description='Get a specific blog image by ID',
        responses={
            200: openapi.Response('Successful response', BlogImageSerializer),
            404: openapi.Response('Image not found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_id='create_image',
        operation_description='Create a new blog image',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['post', 'image'],
            properties={
                'post': openapi.Schema(type=openapi.TYPE_INTEGER, description='Post ID'),
                'image': openapi.Schema(type=openapi.TYPE_FILE, description='Image file')
            }
        ),
        responses={
            201: openapi.Response('Image created successfully', BlogImageSerializer),
            400: openapi.Response('Bad request')
        },
        consumes=['multipart/form-data']
    )
    def create(self, request, *args, **kwargs):
        """Create a new image with proper error handling"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating image: {str(e)}")
            return Response(
                {'error': f"Failed to create image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_id='update_image',
        operation_description='Update an existing blog image',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post': openapi.Schema(type=openapi.TYPE_INTEGER, description='Post ID'),
                'image': openapi.Schema(type=openapi.TYPE_FILE, description='Image file')
            }
        ),
        responses={
            200: openapi.Response('Image updated successfully', BlogImageSerializer),
            400: openapi.Response('Bad request'),
            404: openapi.Response('Image not found')
        }
    )
    def update(self, request, *args, **kwargs):
        """Update an existing image with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating image: {str(e)}")
            return Response(
                {'error': f"Failed to update image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_id='delete_image',
        operation_description='Delete a blog image',
        responses={
            204: openapi.Response('Image deleted successfully'),
            404: openapi.Response('Image not found')
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs) 