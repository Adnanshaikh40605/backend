from rest_framework import serializers
from .models import BlogPost, BlogImage, Comment, Category
from django.contrib.auth.models import User
from django.conf import settings

def ensure_https_url(url):
    """
    Ensure URL uses HTTPS in production to avoid mixed content issues
    """
    if not settings.DEBUG and url and url.startswith('http://'):
        return url.replace('http://', 'https://')
    return url

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color', 'post_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_post_count(self, obj):
        """Get the post count from annotation or calculate it"""
        # If the queryset has annotation, use it
        if hasattr(obj, 'post_count'):
            return obj.post_count
        # Otherwise calculate it
        return obj.get_post_count()
        
    def to_representation(self, instance):
        """Ensure we return a proper representation even if instance is None"""
        if instance is None:
            return None
        return super().to_representation(instance)

class BlogImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogImage
        fields = ['id', 'image', 'image_url', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            # For S3 storage, obj.image.url already returns the full S3 URL
            # For local storage, we need to build the absolute URI
            url = obj.image.url
            
            # If it's already a full URL (S3), return it as is
            if url.startswith('http'):
                return ensure_https_url(url)
            
            # If it's a relative URL (local storage), build absolute URI
            request = self.context.get('request')
            if request:
                url = request.build_absolute_uri(url)
                return ensure_https_url(url)
            return ensure_https_url(url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    post_title = serializers.SerializerMethodField(
        help_text="Post title information including id, title, and slug",
        read_only=True
    )
    replies = serializers.SerializerMethodField(read_only=True)
    reply_count = serializers.SerializerMethodField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    has_more_replies = serializers.SerializerMethodField(read_only=True)
    like_count = serializers.SerializerMethodField(read_only=True)
    liked_by = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'post_title', 'parent', 'author_name', 'author_email', 
                 'author_website', 'content', 'approved', 'is_trash',
                 'created_at', 'admin_reply', 'replies', 'reply_count', 
                 'level', 'path', 'has_more_replies', 'like_count', 'liked_by']
        read_only_fields = ['is_trash', 'level', 'path']
    
    def validate_post(self, value):
        """Ensure the post exists"""
        try:
            # If a string ID is passed, convert it to an integer
            if isinstance(value, str) and value.isdigit():
                post_id = int(value)
                return BlogPost.objects.get(id=post_id)
            return value
        except BlogPost.DoesNotExist:
            raise serializers.ValidationError("The specified blog post does not exist.")
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError(f"Invalid post ID format: {str(e)}")
    
    def get_post_title(self, obj):
        if obj.post is None:
            return {
                'id': None,
                'title': 'Unknown Post',
                'slug': ''
            }
        return {
            'id': obj.post.id,
            'title': obj.post.title,
            'slug': obj.post.slug
        }
    
    def get_replies(self, obj):
        """Get approved replies to this comment with proper recursion control"""
        # Control recursion depth with context
        max_depth = self.context.get('max_depth', 3)
        current_depth = self.context.get('current_depth', 0)
        
        # If we've reached max depth or no_replies flag is set, return empty list
        if current_depth >= max_depth or self.context.get('no_replies', False):
            return []
            
        # Create new context with increased depth
        nested_context = self.context.copy()
        nested_context['current_depth'] = current_depth + 1
        
        # Get approved replies and serialize them
        replies = obj.replies.filter(approved=True, is_trash=False).order_by('created_at')
        
        # Apply pagination if needed
        limit = self.context.get('replies_limit', 5)
        if limit and replies.count() > limit:
            replies = replies[:limit]
        
        serializer = CommentSerializer(replies, many=True, context=nested_context)
        return serializer.data
    
    def get_reply_count(self, obj):
        """Get count of approved replies"""
        return obj.replies.filter(approved=True, is_trash=False).count()
    
    def get_has_more_replies(self, obj):
        """Check if there are more replies than what was returned"""
        # If we're not including replies, this is irrelevant
        if self.context.get('no_replies', False):
            return False
            
        limit = self.context.get('replies_limit', 5)
        if not limit:
            return False
            
        return obj.replies.filter(approved=True, is_trash=False).count() > limit
    
    def get_like_count(self, obj):
        """Get the number of likes for this comment"""
        return obj.likes.count()
    
    def get_liked_by(self, obj):
        """Get the names of users who liked this comment"""
        return list(obj.likes.values_list('user_name', flat=True))

class BlogPostListSerializer(serializers.ModelSerializer):
    featured_image_url = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', required=False, allow_null=True)
    category_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure category is properly included even if it's None
        if instance.category is None:
            representation['category'] = None
        return representation
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'excerpt', 'read_time', 'featured_image', 'featured_image_url', 
                 'category', 'category_id', 'category_name', 'published', 'position', 'created_at', 'comment_count',
                 'meta_title', 'meta_description', 'schema_headline', 'schema_description', 'schema_image_alt']
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            # For S3 storage, obj.featured_image.url already returns the full S3 URL
            # For local storage, we need to build the absolute URI
            url = obj.featured_image.url
            
            # If it's already a full URL (S3), return it as is
            if url.startswith('http'):
                return ensure_https_url(url)
            
            # If it's a relative URL (local storage), build absolute URI
            request = self.context.get('request')
            if request:
                url = request.build_absolute_uri(url)
                return ensure_https_url(url)
            return ensure_https_url(url)
        return None
        
    def validate_category_name(self, value):
        if value:
            try:
                return Category.objects.get(name__iexact=value)
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Category with name '{value}' does not exist.")
        return None
    
    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()
        
    def to_internal_value(self, data):
        # Debug print
        import logging
        logger = logging.getLogger('django')
        logger.info(f"BlogPostListSerializer.to_internal_value received data: {data}")
        
        # Create a mutable copy of the data to avoid QueryDict immutable errors
        # But avoid deep copying file objects which can't be pickled
        if hasattr(data, '_mutable'):
            # It's a QueryDict, make it mutable without deep copying
            if not data._mutable:
                data._mutable = True
        else:
            # It's a regular dict, create a shallow copy to be safe
            data = data.copy()
        
        # Handle category_name if provided
        if 'category_name' in data and data['category_name']:
            try:
                category = Category.objects.get(name__iexact=data['category_name'])
                # Set category_id to use the found category
                data['category_id'] = category.id
                logger.info(f"Found category by name: {category.name} (ID: {category.id})")
            except Category.DoesNotExist:
                logger.warning(f"Category with name '{data['category_name']}' not found")
                # Let the validation handle this error
                pass
        # Handle category field if it's an integer (direct ID)
        elif 'category' in data and data['category'] and isinstance(data['category'], (int, str)) and str(data['category']).isdigit():
            data['category_id'] = int(data['category'])
            logger.info(f"Using category ID directly: {data['category_id']}")
            
        return super().to_internal_value(data)

class BlogPostSerializer(serializers.ModelSerializer):
    images = BlogImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', required=False, allow_null=True)
    category_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    
    # SEO Meta Fields with validation
    meta_title = serializers.CharField(
        max_length=60,
        required=False,
        allow_blank=True,
        help_text="Max 60 characters for optimal SEO"
    )
    meta_description = serializers.CharField(
        max_length=160,
        required=False,
        allow_blank=True,
        help_text="Max 160 characters for optimal SEO"
    )
    
    # Schema.org JSON-LD Fields
    schema_headline = serializers.CharField(
        max_length=110,
        required=False,
        allow_blank=True,
        help_text="Schema headline (max 110 characters)"
    )
    schema_description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Schema description"
    )
    schema_image_alt = serializers.CharField(
        max_length=125,
        required=False,
        allow_blank=True,
        help_text="Alt text for schema image"
    )
    
    # JSON-LD Schema output
    json_ld_schema = serializers.SerializerMethodField(read_only=True)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure category is properly included even if it's None
        if instance.category is None:
            representation['category'] = None
        
        # Use model methods for consistency (DRY principle)
        representation['meta_title'] = representation['meta_title'] or instance.get_meta_title()
        representation['meta_description'] = representation['meta_description'] or instance.get_meta_description()
        
        return representation
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'excerpt', 'read_time', 'featured_image', 'featured_image_url', 'images', 'comments',
                 'category', 'category_id', 'category_name', 'published', 'featured', 'position', 'created_at', 'updated_at',
                 'meta_title', 'meta_description', 'schema_headline', 'schema_description', 'schema_image_alt', 'json_ld_schema']
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            # For S3 storage, obj.featured_image.url already returns the full S3 URL
            # For local storage, we need to build the absolute URI
            url = obj.featured_image.url
            
            # If it's already a full URL (S3), return it as is
            if url.startswith('http'):
                return ensure_https_url(url)
            
            # If it's a relative URL (local storage), build absolute URI
            request = self.context.get('request')
            if request:
                url = request.build_absolute_uri(url)
                return ensure_https_url(url)
            return ensure_https_url(url)
        return None
    
    def get_comments(self, obj):
        # Get only approved root comments (no parent)
        approved_comments = obj.comments.filter(approved=True, parent__isnull=True)
        
        # Set up context for nested serialization
        context = self.context.copy()
        context.update({
            'max_depth': 3,  # Show up to 3 levels of nested comments
            'current_depth': 0,
            'replies_limit': 5  # Limit to 5 replies per comment
        })
        
        return CommentSerializer(approved_comments, many=True, context=context).data
    
    def get_json_ld_schema(self, obj):
        """Get JSON-LD schema for this blog post"""
        request = self.context.get('request')
        return obj.generate_json_ld_schema(request)
        
    def to_internal_value(self, data):
        # Debug print
        import logging
        logger = logging.getLogger('django')
        logger.info(f"BlogPostSerializer.to_internal_value received data: {data}")
        
        # Create a mutable copy of the data to avoid QueryDict immutable errors
        # But avoid deep copying file objects which can't be pickled
        if hasattr(data, '_mutable'):
            # It's a QueryDict, make it mutable without deep copying
            if not data._mutable:
                data._mutable = True
        else:
            # It's a regular dict, create a shallow copy to be safe
            data = data.copy()
        
        # Handle category_name if provided
        if 'category_name' in data and data['category_name']:
            try:
                category = Category.objects.get(name__iexact=data['category_name'])
                # Set category_id to use the found category
                data['category_id'] = category.id
                logger.info(f"Found category by name: {category.name} (ID: {category.id})")
            except Category.DoesNotExist:
                logger.warning(f"Category with name '{data['category_name']}' not found")
                # Let the validation handle this error
                pass
        # Handle category field if it's an integer (direct ID)
        elif 'category' in data and data['category'] and isinstance(data['category'], (int, str)) and str(data['category']).isdigit():
            data['category_id'] = int(data['category'])
            logger.info(f"Using category ID directly: {data['category_id']}")
            
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        # Extract additional images if present
        additional_images = []
        if 'additional_images' in validated_data:
            additional_images = validated_data.pop('additional_images', [])
        
        # Create the blog post
        blog_post = BlogPost.objects.create(**validated_data)
        
        # Create image entries for each additional image
        for image_data in additional_images:
            BlogImage.objects.create(post=blog_post, image=image_data)
            
        return blog_post
    
    def update(self, instance, validated_data):
        # Extract additional images if present
        additional_images = []
        if 'additional_images' in validated_data:
            additional_images = validated_data.pop('additional_images', [])
        
        # Update the blog post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Ensure category is properly saved
        if 'category' in validated_data:
            instance.category = validated_data.get('category')
            
        instance.save()
        
        # Create image entries for each additional image
        for image_data in additional_images:
            BlogImage.objects.create(post=instance, image=image_data)
            
        return instance