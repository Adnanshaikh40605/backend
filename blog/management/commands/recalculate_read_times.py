from django.core.management.base import BaseCommand
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Recalculate read times for all blog posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        posts = BlogPost.objects.all()
        updated_count = 0
        
        self.stdout.write(f"Found {posts.count()} blog posts to process...")
        
        for post in posts:
            old_read_time = post.read_time
            new_read_time = post.calculate_read_time()
            
            if old_read_time != new_read_time:
                if dry_run:
                    self.stdout.write(
                        f"Would update '{post.title}' (ID: {post.id}): "
                        f"{old_read_time} min → {new_read_time} min"
                    )
                else:
                    post.read_time = new_read_time
                    post.save(update_fields=['read_time'])
                    self.stdout.write(
                        f"Updated '{post.title}' (ID: {post.id}): "
                        f"{old_read_time} min → {new_read_time} min"
                    )
                updated_count += 1
            else:
                self.stdout.write(
                    f"No change needed for '{post.title}' (ID: {post.id}): {old_read_time} min"
                )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"Dry run complete. Would update {updated_count} posts.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated {updated_count} posts.")
            )
