#!/usr/bin/env python3
"""
Add 15 test blog posts via API calls to the production Railway backend
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta

# Production API base URL
API_BASE_URL = "https://backend-production-92ae.up.railway.app/api"

def create_categories_via_api():
    """Create categories via API"""
    categories_data = [
        {
            'name': 'Technology Trends',
            'description': 'Latest trends in technology and innovation',
            'color': '#007bff'
        },
        {
            'name': 'Software Engineering',
            'description': 'Software development best practices and methodologies',
            'color': '#28a745'
        },
        {
            'name': 'Frontend Development',
            'description': 'Modern frontend frameworks and techniques',
            'color': '#dc3545'
        },
        {
            'name': 'Backend Development',
            'description': 'Server-side development and architecture',
            'color': '#ffc107'
        },
        {
            'name': 'Cloud Computing',
            'description': 'Cloud platforms and distributed systems',
            'color': '#6f42c1'
        },
        {
            'name': 'AI & Machine Learning',
            'description': 'Artificial intelligence and machine learning topics',
            'color': '#fd7e14'
        }
    ]
    
    created_categories = []
    
    for cat_data in categories_data:
        try:
            response = requests.post(
                f"{API_BASE_URL}/categories/",
                json=cat_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 201:
                category = response.json()
                created_categories.append(category)
                print(f"✅ Created category: {category['name']}")
            elif response.status_code == 400:
                # Category might already exist, try to get it
                try:
                    get_response = requests.get(f"{API_BASE_URL}/categories/", timeout=30)
                    if get_response.status_code == 200:
                        categories = get_response.json().get('results', [])
                        existing_cat = next((c for c in categories if c['name'] == cat_data['name']), None)
                        if existing_cat:
                            created_categories.append(existing_cat)
                            print(f"📝 Category already exists: {existing_cat['name']}")
                except:
                    pass
            else:
                print(f"❌ Failed to create category {cat_data['name']}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating category {cat_data['name']}: {e}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    return created_categories

def generate_dynamic_blog_posts():
    """Generate 15 dynamic blog posts with varied content"""
    
    # Dynamic content templates
    tech_topics = [
        "Quantum Computing", "Blockchain Technology", "Edge Computing", "5G Networks",
        "Internet of Things", "Augmented Reality", "Virtual Reality", "Cybersecurity",
        "Cloud Native", "Microservices", "Serverless Computing", "DevSecOps",
        "Low-Code Platforms", "API-First Development", "Headless Architecture"
    ]
    
    programming_concepts = [
        "Design Patterns", "Clean Code", "Test-Driven Development", "Continuous Integration",
        "Code Review", "Refactoring", "Performance Optimization", "Memory Management",
        "Concurrency", "Functional Programming", "Object-Oriented Programming", "SOLID Principles",
        "Domain-Driven Design", "Event-Driven Architecture", "Reactive Programming"
    ]
    
    frameworks_tools = [
        "React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "Spring Boot",
        "Docker", "Kubernetes", "Jenkins", "Git", "MongoDB", "PostgreSQL", "Redis",
        "Elasticsearch"
    ]
    
    categories = [
        "Technology Trends", "Software Engineering", "Frontend Development", 
        "Backend Development", "Cloud Computing", "AI & Machine Learning"
    ]
    
    blog_posts = []
    
    for i in range(15):
        # Randomly select topic elements
        topic = random.choice(tech_topics)
        concept = random.choice(programming_concepts)
        tool = random.choice(frameworks_tools)
        category = random.choice(categories)
        
        # Generate dynamic title
        title_templates = [
            f"Mastering {topic}: A Complete Guide",
            f"Building Modern Applications with {tool}",
            f"Understanding {concept} in {topic}",
            f"The Future of {topic} Development",
            f"Best Practices for {concept} with {tool}",
            f"Getting Started with {topic} and {tool}",
            f"Advanced {concept} Techniques",
            f"Implementing {topic} Solutions",
            f"Deep Dive into {tool} Architecture",
            f"Optimizing {concept} for Production"
        ]
        
        title = random.choice(title_templates)
        
        # Generate dynamic content
        content = f"""
        <h2>Introduction to {topic}</h2>
        <p>In today's rapidly evolving tech landscape, {topic.lower()} has become increasingly important for developers and organizations alike. This comprehensive guide will walk you through the essential concepts and practical applications.</p>
        
        <h3>Why {topic} Matters</h3>
        <p>{topic} represents a significant shift in how we approach modern software development. By understanding and implementing {concept.lower()}, developers can:</p>
        <ul>
            <li>Improve application performance and scalability</li>
            <li>Enhance code maintainability and readability</li>
            <li>Reduce development time and costs</li>
            <li>Build more robust and reliable systems</li>
        </ul>
        
        <h3>Getting Started with {tool}</h3>
        <p>To effectively work with {topic.lower()}, we'll be using {tool}, which provides excellent support for implementing {concept.lower()}. Here's a basic example:</p>
        
        <pre><code>
// Example implementation
const {tool.lower()}Config = {{
    environment: 'production',
    enableOptimization: true,
    features: ['{concept.lower()}', 'performance-monitoring'],
    version: '2.0.0'
}};

function initialize{tool.replace(' ', '').replace('.', '').replace('-', '')}() {{
    console.log('Initializing {tool} for {topic}...');
    return new Promise((resolve) => {{
        setTimeout(() => {{
            console.log('✅ {tool} initialized successfully!');
            resolve(true);
        }}, 1000);
    }});
}}

// Usage
initialize{tool.replace(' ', '').replace('.', '').replace('-', '')}()
    .then(() => {{
        console.log('Ready to implement {concept}!');
    }});
        </code></pre>
        
        <h3>Key Concepts and Best Practices</h3>
        <p>When working with {topic.lower()}, it's crucial to understand these fundamental concepts:</p>
        
        <h4>1. Architecture Considerations</h4>
        <p>Designing systems with {concept.lower()} requires careful planning and consideration of various factors including scalability, maintainability, and performance.</p>
        
        <h4>2. Implementation Strategies</h4>
        <p>There are several approaches to implementing {topic.lower()} solutions:</p>
        <ul>
            <li><strong>Incremental Approach</strong>: Gradually introduce {concept.lower()} concepts</li>
            <li><strong>Full Migration</strong>: Complete system overhaul using {tool}</li>
            <li><strong>Hybrid Solution</strong>: Combine traditional methods with modern {topic.lower()} practices</li>
        </ul>
        
        <h3>Real-World Applications</h3>
        <p>Many successful companies have implemented {topic.lower()} solutions to solve complex business problems:</p>
        
        <blockquote>
        <p>"By adopting {concept.lower()} with {tool}, we reduced our deployment time by 60% and improved system reliability significantly." - Tech Lead at Fortune 500 Company</p>
        </blockquote>
        
        <h3>Common Challenges and Solutions</h3>
        <p>While implementing {topic.lower()}, developers often face several challenges:</p>
        
        <h4>Challenge 1: Learning Curve</h4>
        <p><strong>Solution:</strong> Start with small projects and gradually build expertise. Utilize online resources and community support.</p>
        
        <h4>Challenge 2: Integration Complexity</h4>
        <p><strong>Solution:</strong> Use well-documented APIs and follow established patterns. Consider using {tool} for smoother integration.</p>
        
        <h4>Challenge 3: Performance Optimization</h4>
        <p><strong>Solution:</strong> Implement proper monitoring and profiling tools. Apply {concept.lower()} principles consistently.</p>
        
        <h3>Future Trends and Developments</h3>
        <p>The field of {topic.lower()} is constantly evolving. Here are some trends to watch:</p>
        <ul>
            <li>Enhanced automation and AI integration</li>
            <li>Improved developer experience and tooling</li>
            <li>Better performance optimization techniques</li>
            <li>Stronger security and compliance features</li>
        </ul>
        
        <h3>Getting Started Today</h3>
        <p>Ready to dive into {topic.lower()}? Here's your action plan:</p>
        <ol>
            <li>Set up your development environment with {tool}</li>
            <li>Practice basic {concept.lower()} concepts</li>
            <li>Build a small prototype project</li>
            <li>Join the community and contribute to open source</li>
            <li>Stay updated with the latest developments</li>
        </ol>
        
        <h3>Conclusion</h3>
        <p>{topic} combined with {concept.lower()} represents the future of software development. By mastering these concepts and tools like {tool}, developers can build more efficient, scalable, and maintainable applications.</p>
        
        <p>The journey to mastering {topic.lower()} may seem challenging, but with consistent practice and the right approach, you'll be building amazing applications in no time!</p>
        
        <hr>
        <p><em>This post was generated on {datetime.now().strftime('%B %d, %Y')} as part of our comprehensive technology blog series.</em></p>
        """
        
        blog_post = {
            'title': title,
            'content': content.strip(),
            'category_name': category,
            'published': True,
            'featured': random.choice([True, False, False, False]),  # 25% chance of being featured
            'position': i + 1
        }
        
        blog_posts.append(blog_post)
    
    return blog_posts

def create_blog_post_via_api(post_data, categories):
    """Create a single blog post via API"""
    try:
        # Find category ID
        category_id = None
        if post_data.get('category_name'):
            category = next((c for c in categories if c['name'] == post_data['category_name']), None)
            if category:
                category_id = category['id']
        
        # Prepare API payload
        api_payload = {
            'title': post_data['title'],
            'content': post_data['content'],
            'published': post_data['published'],
            'featured': post_data['featured'],
            'position': post_data['position']
        }
        
        if category_id:
            api_payload['category'] = category_id
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/posts/",
            json=api_payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Longer timeout for content creation
        )
        
        if response.status_code == 201:
            blog_post = response.json()
            print(f"✅ Created blog post: {blog_post['title']}")
            return blog_post
        else:
            print(f"❌ Failed to create blog post '{post_data['title']}': {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating blog post '{post_data['title']}': {e}")
        return None

def test_api_connection():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/posts/", timeout=10)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to API: {e}")
        return False

def main():
    """Main function to create test blogs via API"""
    print("🚀 Adding 15 Dynamic Test Blogs via Production API")
    print("=" * 60)
    
    # Test API connection first
    if not test_api_connection():
        print("💥 Cannot connect to API. Please check the URL and try again.")
        return
    
    print("\n📂 Step 1: Creating categories...")
    categories = create_categories_via_api()
    
    if not categories:
        print("⚠️  No categories available. Posts will be created without categories.")
        categories = []
    
    print(f"\n📝 Step 2: Generating {15} dynamic blog posts...")
    blog_posts_data = generate_dynamic_blog_posts()
    
    print(f"\n🌐 Step 3: Creating blog posts via API...")
    created_posts = []
    
    for i, post_data in enumerate(blog_posts_data, 1):
        print(f"\n[{i}/15] Creating: {post_data['title'][:50]}...")
        
        created_post = create_blog_post_via_api(post_data, categories)
        if created_post:
            created_posts.append(created_post)
        
        # Add delay between requests to avoid overwhelming the server
        time.sleep(1)
    
    # Summary
    print(f"\n🎉 Blog Creation Complete!")
    print("=" * 60)
    print(f"✅ Successfully created: {len(created_posts)} blog posts")
    print(f"❌ Failed to create: {len(blog_posts_data) - len(created_posts)} blog posts")
    
    if created_posts:
        print(f"\n📊 Created Posts:")
        for post in created_posts[:5]:  # Show first 5
            print(f"   - {post['title']}")
        if len(created_posts) > 5:
            print(f"   ... and {len(created_posts) - 5} more")
    
    print(f"\n🌐 You can view all posts at:")
    print(f"   {API_BASE_URL}/posts/?published=true")
    
    # Test the final result
    print(f"\n🧪 Testing final API response...")
    try:
        response = requests.get(f"{API_BASE_URL}/posts/?page=1&limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_posts = data.get('count', 0)
            print(f"✅ API working! Total posts in database: {total_posts}")
        else:
            print(f"⚠️  API returned status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error testing final API: {e}")

if __name__ == "__main__":
    main()