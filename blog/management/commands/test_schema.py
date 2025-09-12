from django.core.management.base import BaseCommand
from blog.models import BlogPost, Category
import json


class Command(BaseCommand):
    help = 'Test JSON-LD schema generation for blog posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Test schema for a specific post slug',
        )
        parser.add_argument(
            '--create-test-post',
            action='store_true',
            help='Create a test post with schema data',
        )

    def handle(self, *args, **options):
        if options['create_test_post']:
            self.create_test_post()
        
        if options['slug']:
            self.test_post_schema(options['slug'])
        else:
            # Test all published posts
            posts = BlogPost.objects.filter(published=True)
            if not posts.exists():
                self.stdout.write(
                    self.style.WARNING('No published posts found. Use --create-test-post to create one.')
                )
                return
            
            for post in posts:
                self.test_post_schema(post.slug)

    def create_test_post(self):
        """Create a test blog post with schema data"""
        self.stdout.write('Creating test blog post...')
        
        # Create or get a test category
        category, created = Category.objects.get_or_create(
            name='Technology',
            defaults={
                'description': 'Technology related posts',
                'color': '#007bff'
            }
        )
        
        # Create test post
        post, created = BlogPost.objects.get_or_create(
            slug='test-schema-post',
            defaults={
                'title': 'Test Schema Post: Advanced SEO Implementation',
                'content': '''
                <h2>Introduction</h2>
                <p>This is a comprehensive test post to demonstrate our advanced JSON-LD schema implementation for SEO optimization.</p>
                
                <h2>Key Features</h2>
                <p>Our schema implementation includes:</p>
                <ul>
                    <li>Automatic schema generation</li>
                    <li>SEO-optimized structured data</li>
                    <li>Rich snippets support</li>
                    <li>Google Search Console compatibility</li>
                </ul>
                
                <h2>Benefits</h2>
                <p>By implementing proper structured data, we can improve search engine visibility and click-through rates.</p>
                ''',
                'excerpt': 'A comprehensive test post demonstrating advanced JSON-LD schema implementation for optimal SEO performance.',
                'meta_title': 'Test Schema Post: Advanced SEO Implementation Guide',
                'meta_description': 'Learn how our advanced JSON-LD schema implementation improves SEO performance and search engine visibility for blog posts.',
                'schema_headline': 'Advanced SEO Schema Implementation Test',
                'schema_description': 'Comprehensive demonstration of JSON-LD structured data implementation for enhanced search engine optimization and rich snippets.',
                'schema_image_alt': 'Advanced SEO schema implementation diagram',
                'published': True,
                'featured': True,
                'category': category,
                'read_time': 5
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created test post: {post.title}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Test post already exists: {post.title}')
            )
        
        return post

    def test_post_schema(self, slug):
        """Test schema generation for a specific post"""
        try:
            post = BlogPost.objects.get(slug=slug, published=True)
            
            self.stdout.write(f'\n🔍 Testing schema for post: {post.title}')
            self.stdout.write(f'📝 Slug: {post.slug}')
            self.stdout.write(f'📅 Created: {post.created_at}')
            self.stdout.write(f'📅 Updated: {post.updated_at}')
            
            # Generate schema
            schema_json = post.generate_json_ld_schema()
            
            # Parse to verify it's valid JSON
            try:
                schema_data = json.loads(schema_json)
                self.stdout.write(self.style.SUCCESS('✅ Schema JSON is valid'))
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'❌ Invalid JSON: {e}'))
                return
            
            # Validate required schema fields
            required_fields = ['@context', '@type', '@id', 'mainEntityOfPage', 'headline', 'description']
            missing_fields = []
            
            for field in required_fields:
                if field not in schema_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.stdout.write(
                    self.style.ERROR(f'❌ Missing required fields: {", ".join(missing_fields)}')
                )
            else:
                self.stdout.write(self.style.SUCCESS('✅ All required schema fields present'))
            
            # Display schema summary
            self.stdout.write('\n📋 Schema Summary:')
            self.stdout.write(f'   Context: {schema_data.get("@context")}')
            self.stdout.write(f'   Type: {schema_data.get("@type")}')
            self.stdout.write(f'   Headline: {schema_data.get("headline")}')
            self.stdout.write(f'   Description: {schema_data.get("description")[:100]}...')
            
            if 'image' in schema_data:
                self.stdout.write(f'   Image: {schema_data["image"].get("url", "No URL")}')
            else:
                self.stdout.write('   Image: Not set')
            
            if 'datePublished' in schema_data:
                self.stdout.write(f'   Published: {schema_data["datePublished"]}')
            
            if 'dateModified' in schema_data:
                self.stdout.write(f'   Modified: {schema_data["dateModified"]}')
            
            # Display full schema (formatted)
            self.stdout.write('\n📄 Full JSON-LD Schema:')
            self.stdout.write('=' * 80)
            formatted_schema = json.dumps(schema_data, indent=2, ensure_ascii=False)
            self.stdout.write(formatted_schema)
            self.stdout.write('=' * 80)
            
            # Display script tag
            script_tag = post.get_json_ld_script_tag()
            self.stdout.write('\n🏷️  HTML Script Tag:')
            self.stdout.write('-' * 80)
            self.stdout.write(script_tag)
            self.stdout.write('-' * 80)
            
            # Test API endpoint
            self.stdout.write('\n🌐 API Endpoint Test:')
            self.stdout.write(f'   URL: /api/posts/{slug}/schema/')
            self.stdout.write('   Status: Available for testing')
            
        except BlogPost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Post with slug "{slug}" not found or not published')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error testing schema: {str(e)}')
            )