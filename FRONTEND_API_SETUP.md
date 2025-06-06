# Frontend API Connection Guide

This guide explains how to connect your frontend application to the Django API backend.

## API Base URL

Your Django API is deployed at:

```
https://web-production-f03ff.up.railway.app
```

## API Endpoints

All API endpoints are prefixed with `/api/`, for example:

- Blog Posts: `https://web-production-f03ff.up.railway.app/api/posts/`
- Comments: `https://web-production-f03ff.up.railway.app/api/comments/`
- Images: `https://web-production-f03ff.up.railway.app/api/images/`

## Media Files

Media files (uploads, images) are available at:

```
https://web-production-f03ff.up.railway.app/media/
```

## React/Vite Frontend Setup

### 1. Create a `.env` file in your React project root:

```
VITE_API_URL=https://web-production-f03ff.up.railway.app
VITE_MEDIA_URL=https://web-production-f03ff.up.railway.app/media/
```

### 2. API Service Structure

The API services are organized in the following files:

- `src/api/FRONTEND_API_SERVICE.js` - Main API service with core functionality
- `src/api/apiEndpoints.js` - Centralized endpoint URLs
- `src/api/apiService.js` - API service functions by resource type
- `src/api/apiMocks.js` - Mock data for development

### 3. Using the API Services

```javascript
// Import the API services
import { postAPI, commentAPI, mediaAPI } from './api/apiService';

// Fetch posts
const fetchPosts = async () => {
  const posts = await postAPI.getAll();
  return posts;
};

// Get a single post
const getPost = async (id) => {
  const post = await postAPI.getById(id);
  return post;
};

// Create a new post
const createPost = async (postData) => {
  const newPost = await postAPI.create(postData);
  return newPost;
};

// Get image URL
const getImageUrl = (path) => {
  return mediaAPI.getImageUrl(path);
};
```

### 4. CORS and CSRF Configuration

The backend has been configured to accept requests from your frontend. For authenticated requests that modify data:

```javascript
// Example of creating a comment with CSRF token
const createComment = async (commentData) => {
  const newComment = await commentAPI.create(commentData);
  return newComment;
};
```

The API service automatically handles:
- CSRF token extraction from cookies
- Proper headers for different request types
- Credentials inclusion for authenticated requests

## Deploying Your Frontend

You can deploy your frontend to services like:

1. **Vercel**: Excellent for React apps
2. **Netlify**: Good alternative with easy deployment
3. **Firebase Hosting**: Google's hosting service

After deploying your frontend, make sure to:

1. Add your frontend URL to the backend settings by setting the `FRONTEND_URL` environment variable
2. Update any hardcoded URLs in your frontend code to use environment variables

## Testing the Connection

To verify the API connection is working:

1. Open your browser console
2. Try a simple fetch request to the API
3. Check that the response contains your blog post data 

```javascript
// Test API connection
fetch('https://web-production-f03ff.up.railway.app/api/posts/')
  .then(response => response.json())
  .then(data => console.log('Posts:', data))
  .catch(error => console.error('Error:', error));
``` 