from rest_framework import serializers
from .models import BlogPost, BlogImage, Comment
from django.contrib.auth.models import User

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

class BlogImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogImage
        fields = ['id', 'image', 'image_url', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
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
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'post_title', 'parent', 'author_name', 'author_email', 
                 'author_website', 'content', 'approved', 'is_trash',
                 'created_at', 'admin_reply', 'replies', 'reply_count', 
                 'level', 'path', 'has_more_replies']
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

class BlogPostListSerializer(serializers.ModelSerializer):
    featured_image_url = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'featured_image', 'featured_image_url', 
                 'published', 'position', 'created_at', 'comment_count']
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()

class BlogPostSerializer(serializers.ModelSerializer):
    images = BlogImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'featured_image', 'featured_image_url', 'images', 'comments',
                 'published', 'featured', 'position', 'created_at', 'updated_at']
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
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
        instance.save()
        
        # Create image entries for each additional image
        for image_data in additional_images:
            BlogImage.objects.create(post=instance, image=image_data)
            
        return instance 