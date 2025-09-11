from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .models import BlogImage
from .serializers import BlogImageSerializer

# Setup logger
logger = logging.getLogger(__name__)

class BlogImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing blog images.
    """
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Require authentication for ALL actions
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        operation_description="List all blog images",
        responses={
            200: BlogImageSerializer(many=True)
        },
        tags=['Images']
    )
    def list(self, request, *args, **kwargs):
        """List all blog images"""
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
        """Retrieve a specific blog image"""
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
        """Create a new blog image"""
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
        """Update a blog image"""
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
        """Partially update a blog image"""
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
        """Delete a blog image"""
        return super().destroy(request, *args, **kwargs) 