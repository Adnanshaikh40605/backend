import os
import json
import yaml
from django.core.management.base import BaseCommand, CommandError
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.codecs import OpenAPICodecJson, OpenAPICodecYaml
from django.core.management import call_command
from django.urls import get_resolver


class Command(BaseCommand):
    help = 'Generate Swagger API documentation in JSON or YAML format'

    def add_arguments(self, parser):
        parser.add_argument('--format', type=str, choices=['json', 'yaml'], default='json',
                           help='Output format (json or yaml)')
        parser.add_argument('--file', type=str, default='api-docs',
                           help='Output filename without extension')
        parser.add_argument('--url', type=str, default='https://web-production-f03ff.up.railway.app/',
                           help='Base URL for API server')

    def handle(self, *args, **options):
        # Import here to avoid circular imports
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi
        from rest_framework import permissions
        
        # Get the format
        format_name = options['format']
        file_name = options['file']
        url = options['url']
        
        # Add extension if not provided
        if not file_name.endswith(f'.{format_name}'):
            file_name = f"{file_name}.{format_name}"
        
        # Create the schema generator
        generator = OpenAPISchemaGenerator(
            info=openapi.Info(
                title="Blog CMS API",
                default_version='v1',
                description="API documentation for the Blog CMS platform",
                terms_of_service="https://www.example.com/terms/",
                contact=openapi.Contact(email="skadnan40605@gmail.com"),
                license=openapi.License(name="BSD License"),
            ),
            url=url
        )
        
        # Generate the schema
        schema = generator.get_schema(request=None, public=True)
        
        # Use the appropriate codec
        if format_name == 'json':
            codec = OpenAPICodecJson()
        else:  # yaml
            codec = OpenAPICodecYaml()
        
        # Serialize the schema
        content = codec.encode(schema)
        
        # Write to file
        with open(file_name, 'w') as f:
            f.write(content)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated API documentation: {file_name}')) 