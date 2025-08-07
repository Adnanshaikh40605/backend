# Blog CMS Frontend API Guide

## API Configuration

This frontend application is designed to connect to a Django REST API backend. There are two ways the frontend connects to the backend:

1. **Development Mode**: Using Vite's proxy feature
2. **Production Mode**: Using environment variables

## Setup Instructions

### 1. Development Mode Setup

In development mode, the frontend makes requests to relative URLs like `/api/posts/`, and Vite's development server proxies these requests to the Django backend.

1. Make sure your Django backend is running (typically on port 8000)
2. Create a `.env.development` file in the frontend root with:
   ```
   VITE_API_URL=""
   VITE_MEDIA_URL="/media/"
   ```
3. Run the frontend development server: `npm run dev`

The proxy is configured in `vite.config.js` to forward requests:
- `/api/*` → `http://localhost:8000/api/*`
- `/media/*` → `http://localhost:8000/media/*`
- `/ckeditor/*` → `http://localhost:8000/ckeditor/*`

### 2. Production Mode Setup

For production deployment:

1. Create a `.env.production` file with:
   ```
   VITE_API_URL="https://your-api-domain.com"
   VITE_MEDIA_URL="https://your-api-domain.com/media/"
   ```
2. Build the frontend: `npm run build`

## API Service Architecture

The API service has been restructured into a modular architecture with five main files:

1. **index.js** - Main entry point that re-exports everything for backward compatibility
2. **apiEndpoints.js** - Contains all API endpoint URLs and environment configuration
3. **apiService.js** - Contains API service functions organized by resource type (post, comment, media)
4. **apiUtils.js** - Shared utility functions for API operations (error handling, headers, etc.)
5. **apiMocks.js** - Contains mock data for development fallback when API is unavailable

This modular structure improves maintainability, error handling, and code organization.

### Using the API Services

```javascript
// Import the API services from the main index file
import { postAPI, commentAPI, mediaAPI } from '../api';

// Example usage in a component
function PostList() {
  const [posts, setPosts] = useState([]);
  
  useEffect(() => {
    // Fetch posts using the API service
    postAPI.getAll()
      .then(data => setPosts(data))
      .catch(error => console.error('Error fetching posts:', error));
  }, []);
  
  // Render posts...
}
```

## API Service Modules

### 1. apiEndpoints.js

Contains all API endpoint URLs and environment configuration:

```javascript
// Get environment variables with fallback to development values
const isDevelopment = window.location.hostname === 'localhost';
const DEFAULT_API_URL = isDevelopment ? 'http://localhost:8000' : 'https://production-url.com';
const API_URL = import.meta.env.VITE_API_URL || DEFAULT_API_URL;

export const ENDPOINTS = {
  POSTS: `${API_URL}/api/posts/`,
  COMMENTS: `${API_URL}/api/comments/`,
  // Additional endpoints...
};
```

### 2. apiService.js

Organized by resource type for better maintainability:

```javascript
// Post API functions
export const postAPI = {
  getAll: async (params = {}) => { /* implementation */ },
  getById: async (id) => { /* implementation */ },
  create: async (postData) => { /* implementation */ },
  update: async (id, postData) => { /* implementation */ },
  delete: async (id) => { /* implementation */ }
};

// Comment API functions 
export const commentAPI = {
  getAll: async (postId = null) => { /* implementation */ },
  create: async (commentData) => { /* implementation */ },
  // Additional methods...
};

// Media API helper
export const mediaAPI = {
  getImageUrl: (path) => { /* implementation */ },
  getOptimizedImageUrl: (path, options) => { /* implementation */ }
};
```

### 3. apiUtils.js

Shared utility functions for API operations:

```javascript
// Helper function to get cookies (for CSRF token)
export function getCookie(name) { /* implementation */ }

// Default request headers
export const getHeaders = (includeContentType = true) => { /* implementation */ };

// Helper to format API responses with appropriate error handling
export const handleResponse = async (response) => { /* implementation */ };

// Function to handle API calls with fallback to mock data
export const handleApiWithFallback = async (apiCall, mockData) => { /* implementation */ };
```

### 4. apiMocks.js

Mock data for development fallback:

```javascript
// Mock posts data
export const mockPosts = [
  {
    id: 1,
    title: "Sample Blog Post 1",
    // Additional fields...
  },
  // Additional mock posts...
];

// Mock comments data
export const mockComments = {
  approved: [ /* mock approved comments */ ],
  pending: [ /* mock pending comments */ ]
};
```

## Error Handling

The API service includes improved error handling that:

1. Properly formats error responses with detailed information
2. Handles different response types (JSON, text, etc.)
3. Provides fallback to mock data during development
4. Includes consistent error logging for debugging

Example error handling:

```javascript
// In apiUtils.js
export const handleResponse = async (response) => {
  // For DELETE operations that return 204 No Content
  if (response.status === 204) {
    return true;
  }
  
  // Check if response is OK
  if (!response.ok) {
    const errorText = await response.text();
    try {
      // Try to parse as JSON
      const errorData = JSON.parse(errorText);
      throw new Error(JSON.stringify(errorData));
    } catch (e) {
      // If not JSON, use text or status
      throw new Error(errorText || `API request failed with status: ${response.status}`);
    }
  }
  
  // Handle response based on content type
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }
  
  return response.text();
};
```

## Available API Endpoints

All API endpoints are defined in `src/api/apiEndpoints.js` for consistency.

### Blog Posts

- **Get all posts**: `GET /api/posts/`
  - Query parameters:
    - `published=true` or `published=false` to filter by publication status

- **Get specific post**: `GET /api/posts/{post_id}/`
- **Create post**: `POST /api/posts/`
- **Update post**: `PATCH /api/posts/{post_id}/`
- **Delete post**: `DELETE /api/posts/{post_id}/`
- **Upload images to post**: `POST /api/posts/{post_id}/upload_images/`

### Comments

- **Get all comments**: `GET /api/comments/`
  - Query parameters:
    - `post={post_id}` to filter by post
    - `approved=true` or `approved=false` to filter by approval status

- **Get a comment**: `GET /api/comments/{comment_id}/`
- **Create comment**: `POST /api/comments/`
- **Get pending comments count**: `GET /api/comments/pending-count/`
- **Approve comment**: `POST /api/comments/{comment_id}/approve/`
- **Bulk approve comments**: `POST /api/comments/bulk_approve/`
- **Bulk reject comments**: `POST /api/comments/bulk_reject/`

### Media

- **Get image URL**: Use the `mediaAPI.getImageUrl(path)` helper function
- **Get optimized image URL**: Use the `mediaAPI.getOptimizedImageUrl(path, options)` helper function

### CKEditor

- **Upload image for CKEditor**: `POST /ckeditor5/image_upload/`

## Troubleshooting API Connections

If your API requests are failing, check:

1. **Browser Console**: Look for any CORS or network errors
2. **Request URLs**: Make sure the URLs match the expected format
3. **Django Server**: Ensure it's running and accessible
4. **Environment Variables**: Check that they're properly set
5. **Vite Proxy Configuration**: Verify the proxy settings in vite.config.js 