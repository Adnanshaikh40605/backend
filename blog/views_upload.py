"""
Image upload views for Quill editor
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from .utils.image_utils import validate_blog_image, optimize_blog_image
import os
import uuid

logger = logging.getLogger(__name__)

class QuillImageUploadView(APIView):
    """
    Handle image uploads for Quill editor
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Upload an image for Quill editor
        """
        try:
            # Check if image file is provided
            if 'image' not in request.FILES:
                return Response({
                    'error': 'No image file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validate the image
            validation_result = validate_blog_image(image_file)
            if not validation_result['valid']:
                return Response({
                    'error': 'Invalid image file',
                    'details': validation_result['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate unique filename
            file_extension = os.path.splitext(image_file.name)[1].lower()
            if not file_extension:
                file_extension = '.jpg'  # Default extension
            
            unique_filename = f"quill_uploads/{uuid.uuid4().hex}{file_extension}"
            
            # Optimize the image
            try:
                optimized_image = optimize_blog_image(image_file)
                if optimized_image:
                    image_file = optimized_image
                    # Update filename for WebP if converted
                    if optimized_image.name.endswith('.webp'):
                        unique_filename = f"quill_uploads/{uuid.uuid4().hex}.webp"
            except Exception as e:
                logger.warning(f"Image optimization failed, using original: {str(e)}")
            
            # Save the file
            if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') and settings.AWS_STORAGE_BUCKET_NAME:
                # Using S3 storage
                file_path = default_storage.save(unique_filename, image_file)
                file_url = default_storage.url(file_path)
            else:
                # Using local storage
                file_path = default_storage.save(unique_filename, image_file)
                file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
            
            logger.info(f"Image uploaded successfully: {file_url}")
            
            return Response({
                'url': file_url,
                'filename': os.path.basename(file_path),
                'size': image_file.size
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return Response({
                'error': 'Failed to upload image',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CKEditorImageUploadView(APIView):
    """
    Handle image uploads for CKEditor (backward compatibility)
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Upload an image for CKEditor
        """
        try:
            # Check if image file is provided
            if 'upload' not in request.FILES:
                return Response({
                    'error': {
                        'message': 'No image file provided'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['upload']
            
            # Validate the image
            validation_result = validate_blog_image(image_file)
            if not validation_result['valid']:
                return Response({
                    'error': {
                        'message': 'Invalid image file: ' + ', '.join(validation_result['errors'])
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate unique filename
            file_extension = os.path.splitext(image_file.name)[1].lower()
            if not file_extension:
                file_extension = '.jpg'  # Default extension
            
            unique_filename = f"ckeditor_uploads/{uuid.uuid4().hex}{file_extension}"
            
            # Optimize the image
            try:
                optimized_image = optimize_blog_image(image_file)
                if optimized_image:
                    image_file = optimized_image
                    # Update filename for WebP if converted
                    if optimized_image.name.endswith('.webp'):
                        unique_filename = f"ckeditor_uploads/{uuid.uuid4().hex}.webp"
            except Exception as e:
                logger.warning(f"Image optimization failed, using original: {str(e)}")
            
            # Save the file
            if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') and settings.AWS_STORAGE_BUCKET_NAME:
                # Using S3 storage
                file_path = default_storage.save(unique_filename, image_file)
                file_url = default_storage.url(file_path)
            else:
                # Using local storage
                file_path = default_storage.save(unique_filename, image_file)
                file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
            
            logger.info(f"CKEditor image uploaded successfully: {file_url}")
            
            # CKEditor expects this specific response format
            return Response({
                'url': file_url,
                'uploaded': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error uploading CKEditor image: {str(e)}")
            return Response({
                'error': {
                    'message': f'Failed to upload image: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)