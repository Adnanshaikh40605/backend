from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class FileUploadAutoSchema(SwaggerAutoSchema):
    """Custom schema generator for file upload endpoints"""
    
    def get_request_serializer(self):
        try:
            serializer = super().get_request_serializer()
            if serializer is not None:
                # Check if any serializer field is a FileField or ImageField
                has_file_field = any(
                    isinstance(field, (serializers.FileField, serializers.ImageField))
                    for field in serializer.fields.values()
                )
                
                if has_file_field and self.get_consumes() != ['multipart/form-data']:
                    # If it has file fields, ensure 'multipart/form-data' is in consumes
                    self.overrides.setdefault('consumes', ['multipart/form-data'])
            return serializer
        except Exception as e:
            logger.error(f"Error in FileUploadAutoSchema.get_request_serializer: {str(e)}")
            return None

class CustomSchemaGenerator(OpenAPISchemaGenerator):
    """Custom schema generator that handles file uploads"""
    
    def get_schema(self, request=None, public=False):
        """Generate a schema"""
        try:
            schema = super().get_schema(request, public)
            
            # Add global 'consumes' for file upload endpoints if not present
            if 'consumes' not in schema:
                schema['consumes'] = ['application/json', 'multipart/form-data']
                
            return schema
        except Exception as e:
            logger.error(f"Error generating schema: {str(e)}")
            # Return a minimal valid schema to avoid breaking the UI
            return {
                "swagger": "2.0", 
                "info": {"title": "API Documentation", "version": "v1"},
                "paths": {},
                "consumes": ['application/json', 'multipart/form-data']
            } 