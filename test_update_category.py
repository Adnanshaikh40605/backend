import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoint
BASE_URL = 'http://localhost:8000/api'

def test_update_category():
    # Get a list of categories to use for testing
    categories_response = requests.get(f'{BASE_URL}/categories/')
    if categories_response.status_code != 200:
        logger.error(f"Failed to get categories: {categories_response.text}")
        return
    
    categories_data = categories_response.json()
    logger.info(f"Categories response: {categories_data}")
    
    # Check if categories is a list or has a 'results' key
    if isinstance(categories_data, dict) and 'results' in categories_data:
        categories = categories_data['results']
    else:
        categories = categories_data
    
    if not categories:
        logger.error("No categories found for testing")
        return
    
    # Get a list of blog posts to update
    posts_response = requests.get(f'{BASE_URL}/posts/')
    if posts_response.status_code != 200:
        logger.error(f"Failed to get posts: {posts_response.text}")
        return
    
    posts_data = posts_response.json()
    logger.info(f"Posts response structure: {list(posts_data.keys()) if isinstance(posts_data, dict) else 'Not a dict'}")
    
    if isinstance(posts_data, dict) and 'results' in posts_data:
        posts = posts_data['results']
    else:
        posts = posts_data
    
    if not posts:
        logger.error("No posts found for testing")
        return
    
    # Get the first post for testing
    post = posts[0]
    post_id = post['id']
    post_slug = post['slug']
    current_category = post.get('category')
    
    logger.info(f"Testing with post ID: {post_id}, slug: {post_slug}, current category: {current_category}")
    
    # Find a different category to update to
    new_category = None
    for category in categories:
        if current_category is None or (isinstance(current_category, dict) and category['id'] != current_category.get('id')):
            new_category = category
            break
    
    if not new_category:
        logger.error("Could not find a different category for testing")
        return
    
    logger.info(f"Will update to category: {new_category['name']} (ID: {new_category['id']})")
    
    # Test updating with category_id
    update_data = {
        'category_id': new_category['id']
    }
    
    logger.info(f"Updating post with data: {update_data}")
    
    # Try updating using the slug first
    update_response = requests.patch(
        f'{BASE_URL}/posts/{post_slug}/',
        data=json.dumps(update_data),
        headers={'Content-Type': 'application/json'}
    )
    
    if update_response.status_code == 200:
        updated_post = update_response.json()
        logger.info(f"Successfully updated post using slug. New category: {updated_post.get('category')}")
    else:
        logger.error(f"Failed to update post using slug: {update_response.status_code} - {update_response.text}")
        
        # Try updating using the ID as fallback
        logger.info(f"Trying to update using ID instead of slug")
        update_response = requests.patch(
            f'{BASE_URL}/posts/{post_id}/',
            data=json.dumps(update_data),
            headers={'Content-Type': 'application/json'}
        )
        
        if update_response.status_code == 200:
            updated_post = update_response.json()
            logger.info(f"Successfully updated post using ID. New category: {updated_post.get('category')}")
        else:
            logger.error(f"Failed to update post using ID: {update_response.status_code} - {update_response.text}")
    
    # Test updating with category_name
    update_data = {
        'category_name': new_category['name']
    }
    
    logger.info(f"Updating post with data: {update_data}")
    
    # Try updating using the slug
    update_response = requests.patch(
        f'{BASE_URL}/posts/{post_slug}/',
        data=json.dumps(update_data),
        headers={'Content-Type': 'application/json'}
    )
    
    if update_response.status_code == 200:
        updated_post = update_response.json()
        logger.info(f"Successfully updated post using slug and category_name. New category: {updated_post.get('category')}")
    else:
        logger.error(f"Failed to update post using slug and category_name: {update_response.status_code} - {update_response.text}")
        
        # Try updating using the ID as fallback
        logger.info(f"Trying to update using ID instead of slug with category_name")
        update_response = requests.patch(
            f'{BASE_URL}/posts/{post_id}/',
            data=json.dumps(update_data),
            headers={'Content-Type': 'application/json'}
        )
        
        if update_response.status_code == 200:
            updated_post = update_response.json()
            logger.info(f"Successfully updated post using ID and category_name. New category: {updated_post.get('category')}")
        else:
            logger.error(f"Failed to update post using ID and category_name: {update_response.status_code} - {update_response.text}")

if __name__ == "__main__":
    logger.info("Starting test for updating blog post category")
    test_update_category()
    logger.info("Test completed")