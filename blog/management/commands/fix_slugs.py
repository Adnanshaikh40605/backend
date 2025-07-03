from django.core.management.base import BaseCommand
from blog.models import BlogPost
from django.utils.text import slugify
from django.db.models import Q

class Command(BaseCommand):
    help = 'Fix or populate slugs for blog posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='all',
            choices=['null', 'empty', 'all'],
            help='Mode: fix only NULL slugs (null), only empty slugs (empty), or both (all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        dry_run = options['dry_run']
        
        # Build query based on mode
        if mode == 'null':
            query = Q(slug__isnull=True)
            self.stdout.write(f"Searching for posts with NULL slugs...")
        elif mode == 'empty':
            query = Q(slug='')
            self.stdout.write(f"Searching for posts with empty slugs...")
        else:  # all
            query = Q(slug__isnull=True) | Q(slug='')
            self.stdout.write(f"Searching for posts with NULL or empty slugs...")
        
        # Get posts that need fixing
        posts_to_fix = BlogPost.objects.filter(query)
        
        self.stdout.write(self.style.SUCCESS(f'Found {posts_to_fix.count()} posts that need slug fixes'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No changes will be made'))
        
        # Counter for fixed posts
        fixed_count = 0
        
        for post in posts_to_fix:
            # Generate slug from title
            original_slug = slugify(post.title)
            
            # Handle empty titles
            if not original_slug:
                original_slug = f"post-{post.id}"
            
            slug = original_slug
            counter = 1
            
            # Ensure uniqueness
            while BlogPost.objects.filter(slug=slug).exclude(id=post.id).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            old_slug = post.slug if post.slug else "NULL"
            
            if not dry_run:
                post.slug = slug
                post.save()
                fixed_count += 1
                
            status = "[WOULD FIX]" if dry_run else "[FIXED]"
            self.stdout.write(f"{status} Post ID {post.id}: '{post.title}' - Slug changed from '{old_slug}' to '{slug}'")
        
        action = "Would fix" if dry_run else "Fixed"
        self.stdout.write(self.style.SUCCESS(f'{action} {fixed_count} posts')) 