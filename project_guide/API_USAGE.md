# Frontend API Usage Guide

## API Configuration

The frontend is configured to connect to the backend API in two ways:

1. **Development Mode**: Using Vite's proxy feature to forward requests from `http://localhost:5173/api/*` to `http://localhost:8000/api/*`
2. **Production Mode**: Using environment variables to specify the API URL

## API Service Architecture

The API service is organized into four main files:

1. **FRONTEND_API_SERVICE.js** - Main API service with core functionality and utilities
   ```javascript
   // Example from FRONTEND_API_SERVICE.js
   export const mediaAPI = {
     getImageUrl: (path) => { /* ... */ },
     getOptimizedImageUrl: (path, { width, height, format } = {}) => { /* ... */ }
   };
   ```

2. **apiEndpoints.js** - Contains all API endpoint URLs
   ```javascript
   // Example from apiEndpoints.js
   export const POST_ENDPOINTS = {
     LIST: `${API_URL}/api/posts/`,
     DETAIL: (id) => `${API_URL}/api/posts/${id}/`,
     UPLOAD_IMAGES: (id) => `${API_URL}/api/posts/${id}/upload_images/`,
   };
   ```

3. **apiService.js** - Contains API service functions organized by resource type
   ```javascript
   // Example from apiService.js
   const postAPI = {
     getAll: async (params = {}) => { /* ... */ },
     getById: async (id) => { /* ... */ },
     create: async (postData) => { /* ... */ },
     // ...
   };
   ```

4. **apiMocks.js** - Contains mock data for development fallback

## Local Development

When running locally:

1. Start the Django backend server: `python manage.py runserver`
2. Start the frontend dev server: `cd frontend && npm run dev`
3. The frontend will access APIs via relative URLs like `/api/posts/`
4. Vite's proxy configuration will automatically forward these requests to your Django backend

## Using the API Services

```jsx
import { useEffect, useState } from 'react';
import { postAPI, mediaAPI } from '../api/apiService';

function PostList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPosts() {
      try {
        const data = await postAPI.getAll({ published: true });
        setPosts(data);
      } catch (error) {
        console.error('Failed to fetch posts:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchPosts();
  }, []);

  // Example of using mediaAPI to get image URLs
  const getImageUrl = (path) => {
    return mediaAPI.getImageUrl(path);
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Posts</h1>
      {posts.map(post => (
        <div key={post.id}>
          <h2>{post.title}</h2>
          {post.featured_image && (
            <img 
              src={getImageUrl(post.featured_image)} 
              alt={post.title} 
              style={{ maxWidth: '100%' }} 
            />
          )}
          <p>{post.excerpt}</p>
        </div>
      ))}
    </div>
  );
}
```

## Environment Variables

For production or custom setups, you can set these environment variables:

- `VITE_API_URL`: Base URL for API calls (e.g., `https://api.example.com`)
- `VITE_MEDIA_URL`: Base URL for media files (e.g., `https://api.example.com/media/`)

## Error Handling

The API service includes built-in error handling:

```jsx
import { useState } from 'react';
import { commentAPI } from '../api/apiService';

function CommentForm({ postId }) {
  const [comment, setComment] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    
    try {
      await commentAPI.create({
        post: postId,
        content: comment,
        name,
        email
      });
      
      setSuccess(true);
      setComment('');
      setName('');
      setEmail('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Comment submitted for approval!</div>}
      {/* Form fields */}
    </form>
  );
}
```

## Available API Endpoints

### Blog Posts

- **Get all posts**: `GET /api/posts/`
  - Query parameters:
    - `published=true` or `published=false` to filter by publication status

- **Get a specific post**: `GET /api/posts/{post_id}/`
- **Create a new post**: `POST /api/posts/`
- **Update a post**: `PUT /api/posts/{post_id}/`
- **Partially update a post**: `PATCH /api/posts/{post_id}/`
- **Delete a post**: `DELETE /api/posts/{post_id}/`
- **Upload images to a post**: `POST /api/posts/{post_id}/upload_images/`

### Blog Images

- **Get all images**: `GET /api/images/`
- **Get an image**: `GET /api/images/{image_id}/`
- **Upload an image**: `POST /api/images/`
- **Update an image**: `PUT /api/images/{image_id}/`
- **Partially update an image**: `PATCH /api/images/{image_id}/`
- **Delete an image**: `DELETE /api/images/{image_id}/`

### Comments

- **Get all comments**: `GET /api/comments/`
  - Query parameters:
    - `post={post_id}` to filter by post
    - `approved=true` or `approved=false` to filter by approval status

- **Get a comment**: `GET /api/comments/{comment_id}/`
- **Create a comment**: `POST /api/comments/`
- **Update a comment**: `PUT /api/comments/{comment_id}/`
- **Partially update a comment**: `PATCH /api/comments/{comment_id}/`
- **Delete a comment**: `DELETE /api/comments/{comment_id}/`
- **Get pending comments count**: `GET /api/comments/pending-count/`
- **Approve a comment**: `POST /api/comments/{comment_id}/approve/`
- **Reject a comment**: `POST /api/comments/{comment_id}/reject/`
- **Bulk approve comments**: `POST /api/comments/bulk_approve/`
- **Bulk reject comments**: `POST /api/comments/bulk_reject/`
- **Get all comments for a post**: `GET /api/comments/all/?post={post_id}`

``` 