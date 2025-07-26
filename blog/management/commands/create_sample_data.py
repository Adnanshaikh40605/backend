from django.core.management.base import BaseCommand
from blog.models import BlogPost, Comment
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create sample blog posts and comments for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            BlogPost.objects.all().delete()
            Comment.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Sample blog posts
        posts_data = [
            {
                'title': 'Exploring the Nightlife of Your City with a Dedicated Night Driver from Driveronhire.com',
                'slug': 'exploring-nightlife',
                'content': '''
                <p>When the sun sets and the city lights begin to twinkle, a whole new world of entertainment and excitement comes alive. The nightlife scene offers endless possibilities - from trendy rooftop bars and pulsating nightclubs to intimate jazz lounges and late-night eateries.</p>
                
                <p>However, navigating the nightlife safely and responsibly requires careful planning, especially when it comes to transportation. This is where a dedicated night driver from Driveronhire.com becomes your perfect companion for an unforgettable evening out.</p>
                
                <h3>Why Choose a Professional Night Driver?</h3>
                <p>Having a professional driver eliminates the stress of finding parking, dealing with traffic, and most importantly, ensures you get home safely without compromising on the fun.</p>
                
                <h3>Popular Nightlife Destinations</h3>
                <ul>
                    <li>Downtown entertainment districts</li>
                    <li>Rooftop bars with city views</li>
                    <li>Live music venues</li>
                    <li>Late-night dining spots</li>
                </ul>
                ''',
                'published': True,
                'featured': True,
                'position': 1
            },
            {
                'title': 'The Ultimate Guide to Safe Night Transportation',
                'slug': 'safe-night-transportation-guide',
                'content': '''
                <p>Safety should always be your top priority when enjoying the nightlife. Whether you're planning a night out with friends or a romantic evening, having reliable transportation is crucial.</p>
                
                <p>Professional drivers are trained to handle various situations and know the city's roads like the back of their hand. They ensure you reach your destinations safely and on time.</p>
                
                <h3>Benefits of Professional Night Drivers</h3>
                <ul>
                    <li>Licensed and insured drivers</li>
                    <li>Knowledge of the best routes</li>
                    <li>Available 24/7</li>
                    <li>Clean and comfortable vehicles</li>
                </ul>
                ''',
                'published': True,
                'featured': False,
                'position': 2
            },
            {
                'title': 'Why Choose Professional Drivers for Your Night Out',
                'slug': 'professional-drivers-night-out',
                'content': '''
                <p>A night out should be about having fun, not worrying about logistics. Professional drivers from Driveronhire.com take care of all your transportation needs so you can focus on enjoying yourself.</p>
                
                <p>From picking you up at your doorstep to ensuring you get home safely, professional drivers provide a seamless experience that enhances your night out.</p>
                
                <h3>Convenience Features</h3>
                <p>Modern ride services offer features like real-time tracking, multiple stops, and flexible scheduling to accommodate your plans.</p>
                ''',
                'published': True,
                'featured': False,
                'position': 3
            },
            {
                'title': 'Top 10 Nightlife Destinations in the City',
                'slug': 'top-nightlife-destinations',
                'content': '''
                <p>Discover the hottest spots in the city for an amazing night out. From exclusive clubs to cozy pubs, we've compiled a list of must-visit destinations.</p>
                
                <h3>Featured Destinations</h3>
                <ol>
                    <li>The Rooftop Lounge - Stunning city views</li>
                    <li>Jazz Corner - Live music every night</li>
                    <li>Club Neon - Dance the night away</li>
                    <li>The Whiskey Bar - Premium spirits</li>
                    <li>Midnight Diner - Late-night comfort food</li>
                </ol>
                
                <p>Each of these venues offers a unique experience, and with a professional driver, you can visit multiple locations in one night without any hassle.</p>
                ''',
                'published': True,
                'featured': False,
                'position': 4
            },
            {
                'title': 'Planning the Perfect Night Out: A Step-by-Step Guide',
                'slug': 'planning-perfect-night-out',
                'content': '''
                <p>A great night out doesn't happen by accident - it requires some planning. Here's your comprehensive guide to organizing an unforgettable evening.</p>
                
                <h3>Step 1: Choose Your Destinations</h3>
                <p>Research venues that match your group's preferences and make reservations where necessary.</p>
                
                <h3>Step 2: Arrange Transportation</h3>
                <p>Book a professional driver to handle all your transportation needs throughout the night.</p>
                
                <h3>Step 3: Set a Budget</h3>
                <p>Plan your expenses including drinks, food, and transportation to avoid overspending.</p>
                ''',
                'published': True,
                'featured': False,
                'position': 5
            },
            {
                'title': 'Draft: Upcoming Events and Promotions',
                'slug': 'upcoming-events-promotions',
                'content': '<p>This is a draft post about upcoming events and special promotions. Content to be added soon.</p>',
                'published': False,
                'featured': False,
                'position': 6
            }
        ]

        created_posts = []
        for post_data in posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults=post_data
            )
            if created:
                created_posts.append(post)
                self.stdout.write(f'Created post: {post.title}')
            else:
                self.stdout.write(f'Post already exists: {post.title}')

        # Create sample comments for the first post
        if created_posts:
            first_post = BlogPost.objects.get(slug='exploring-nightlife')
            
            comments_data = [
                {
                    'post': first_post,
                    'author_name': 'Sarah Johnson',
                    'author_email': 'sarah@example.com',
                    'content': 'Great article! I always use professional drivers when going out. Safety first!',
                    'approved': True
                },
                {
                    'post': first_post,
                    'author_name': 'Mike Chen',
                    'author_email': 'mike@example.com',
                    'content': 'This is exactly what I needed to read. Planning a night out for my birthday next week.',
                    'approved': True
                },
                {
                    'post': first_post,
                    'author_name': 'Emma Wilson',
                    'author_email': 'emma@example.com',
                    'content': 'Love the tips about nightlife destinations. The rooftop bars sound amazing!',
                    'approved': True
                }
            ]

            for comment_data in comments_data:
                comment, created = Comment.objects.get_or_create(
                    post=comment_data['post'],
                    author_email=comment_data['author_email'],
                    defaults=comment_data
                )
                if created:
                    self.stdout.write(f'Created comment by: {comment.author_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data creation completed! '
                f'Total posts: {BlogPost.objects.count()}, '
                f'Published posts: {BlogPost.objects.filter(published=True).count()}'
            )
        )