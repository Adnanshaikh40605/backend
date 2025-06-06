from django.core.management.base import BaseCommand
from blog.models import BlogPost
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Fix blog posts with NULL slugs'

    def handle(self, *args, **options):
        posts_with_null_slug = BlogPost.objects.filter(slug__isnull=True)
        
        self.stdout.write(self.style.SUCCESS(f'Found {posts_with_null_slug.count()} posts with NULL slugs'))
        
        for post in posts_with_null_slug:
            # Generate slug from title
            original_slug = slugify(post.title)
            slug = original_slug
            counter = 1
            
            # Ensure uniqueness
            while BlogPost.objects.filter(slug=slug).exclude(id=post.id).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            post.slug = slug
            post.save()
            
            self.stdout.write(self.style.SUCCESS(f'Added slug "{slug}" to post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS('NULL slug fixing completed!')) 