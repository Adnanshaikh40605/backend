# Setting Up Swagger UI for Django REST Framework API Documentation

This guide explains how to implement Swagger UI for API documentation in your Django REST Framework project.

## What is Swagger UI?

Swagger UI allows developers to visualize and interact with the API's resources without having any of the implementation logic in place. It's a great way to document your API and allow others to test it without writing any code.

## Installation Steps

### 1. Install Required Packages

First, install the `drf-yasg` package (Yet Another Swagger Generator):

```bash
pip install drf-yasg
```

Add it to your `requirements.txt` or `Pipfile` to ensure it's included in your project dependencies.

### 2. Configure Django Settings

Add `drf_yasg` to your `INSTALLED_APPS` in your project's `settings.py`:

```python
INSTALLED_APPS = [
    # ...existing apps
    'rest_framework',
    'drf_yasg',
    # ...other apps
]
```

### 3. Set Up URL Configuration

In your project's main `urls.py` file, add the following:

```python
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Blog CMS API",
        default_version='v1',
        description="API documentation for the Blog CMS platform",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ... your existing URL patterns
    
    # Swagger documentation URL
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
```

### 4. Improve Your API Documentation

For better documentation, add proper docstrings to your ViewSets, Views, and Serializers:

#### ViewSet Example:

```python
class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog post operations.
    
    retrieve:
    Return a single blog post instance.
    
    list:
    Return a list of all published blog posts.
    
    create:
    Create a new blog post.
    
    update:
    Update an existing blog post.
    
    partial_update:
    Update one or more fields of an existing blog post.
    
    destroy:
    Delete a blog post.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

#### Action Method Example:

```python
@action(detail=True, methods=['post'])
def publish(self, request, pk=None):
    """
    Publish a blog post.
    
    This endpoint changes the status of a blog post to published.
    """
    post = self.get_object()
    post.published = True
    post.save()
    return Response({'status': 'post published'})
```

### 5. Customize Swagger UI (Optional)

You can customize the appearance of Swagger UI by overriding the template. Create a `templates/drf-yasg/swagger-ui.html` file in your project:

```html
{% extends "drf-yasg/swagger-ui.html" %}

{% block extra_styles %}
<style>
  /* Custom CSS for swagger UI */
  .swagger-ui .topbar {
    background-color: #333333;
  }
  .swagger-ui .info .title {
    color: #0066cc;
  }
</style>
{% endblock %}
```

## Configure API Grouping

To organize your API endpoints into logical groups:

```python
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(tags=['Posts'])
class PostViewSet(viewsets.ModelViewSet):
    # ...

@swagger_auto_schema(tags=['Comments'])
class CommentViewSet(viewsets.ModelViewSet):
    # ...
```

## Securing Swagger UI for Production

For production environments, you might want to restrict access to the API documentation:

```python
schema_view = get_schema_view(
    # ... schema info
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
)
```

## Testing Your Swagger Documentation

After implementing Swagger, you can access the documentation at:

- Swagger UI: `http://localhost:8000/api/docs/`

## Troubleshooting

1. **Missing endpoints**: Ensure your views are properly registered in the URL patterns.

2. **Authentication issues**: If you're using token authentication, make sure to configure Swagger to accept tokens:

```python
schema_view = get_schema_view(
    # ... schema info
    security_definitions={
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
)
```

3. **Schema generation errors**: Make sure your serializers and viewsets are properly documented and follow REST Framework conventions.

## Advanced Usage

### Adding Request/Response Examples

```python
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class PostViewSet(viewsets.ModelViewSet):
    @swagger_auto_schema(
        operation_description="Create a new blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Post title'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Post content'),
                'published': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Publication status'),
            },
            required=['title', 'content']
        ),
        responses={
            201: PostSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

### Custom Response Schemas

For custom responses that don't match your serializer:

```python
@swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="Count of pending comments",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        )
    }
)
@api_view(['GET'])
def pending_comment_count(request):
    count = Comment.objects.filter(approved=False).count()
    return Response({'count': count})
```

## Exporting API Documentation

You can export your API documentation in various formats:

```bash
# Export as JSON
python manage.py generate_swagger --format json --file api-docs.json

# Export as YAML
python manage.py generate_swagger --format yaml --file api-docs.yaml
```

These documents can be shared with frontend developers or imported into other API tools.

## Conclusion

With Swagger UI implemented, your API now has interactive documentation that makes it easier for developers to understand and use. This not only serves as documentation but also as a testing tool for your API endpoints. 