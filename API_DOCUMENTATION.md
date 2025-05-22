# Blog CMS API Documentation

This document explains how to access and use the interactive API documentation for the Blog CMS platform.

## API Documentation URL

The following URL provides access to the API documentation:

- **Swagger UI**: [https://web-production-f03ff.up.railway.app/api/docs/](https://web-production-f03ff.up.railway.app/api/docs/)
  - Interactive documentation with a user-friendly interface
  - Allows testing API endpoints directly from the browser

## API Sections

The API is organized into the following sections:

1. **Posts** - Endpoints for managing blog posts
   - Create, retrieve, update, and delete blog posts
   - Special operations like slug validation and image uploads

2. **Comments** - Endpoints for managing blog comments
   - Create, retrieve, update, and delete comments
   - Moderation endpoints for approving/rejecting comments
   - Comment counts and status information

3. **Images** - Endpoints for managing blog images
   - Upload and manage images associated with blog posts

## How to Use the Documentation

### Using Swagger UI

1. Navigate to the Swagger UI URL: [https://web-production-f03ff.up.railway.app/api/docs/](https://web-production-f03ff.up.railway.app/api/docs/)

2. Explore available endpoints organized by tags (Posts, Comments, Images)

3. Click on an endpoint to expand it and see:
   - Required parameters
   - Request body schema
   - Response schemas
   - Example values

4. To test an endpoint:
   - Fill in the required parameters and request body
   - Click the "Execute" button
   - View the response

### Authentication

For endpoints that require authentication:

1. Click the "Authorize" button at the top of the Swagger UI
2. Enter your API token in the format: `Bearer YOUR_TOKEN`
3. Click "Authorize" to save

## API Endpoints Overview

### Posts

- `GET /api/posts/` - List all blog posts
- `POST /api/posts/` - Create a new blog post
- `GET /api/posts/{id}/` - Retrieve a specific blog post
- `PUT /api/posts/{id}/` - Update a blog post
- `DELETE /api/posts/{id}/` - Delete a blog post
- `GET /api/posts/by-slug/{slug}/` - Retrieve a post by its slug
- `POST /api/posts/validate-slug/` - Validate a slug for uniqueness

### Comments

- `GET /api/comments/` - List all comments
- `POST /api/comments/` - Create a new comment
- `GET /api/comments/{id}/` - Retrieve a specific comment
- `PUT /api/comments/{id}/` - Update a comment
- `DELETE /api/comments/{id}/` - Delete a comment
- `GET /api/comments/pending-count/` - Get count of pending comments
- `GET /api/comments/all/` - Get all comments (including unapproved)
- `POST /api/comments/{id}/approve/` - Approve a specific comment
- `POST /api/comments/{id}/reject/` - Reject a specific comment
- `POST /api/comments/bulk_approve/` - Approve multiple comments
- `POST /api/comments/bulk_reject/` - Reject multiple comments

### Images

- `GET /api/images/` - List all images
- `POST /api/images/` - Upload a new image
- `GET /api/images/{id}/` - Retrieve a specific image
- `DELETE /api/images/{id}/` - Delete an image

## Contact

For any questions or support regarding the API:
- Email: skadnan40605@gmail.com
- Backend URL: https://web-production-f03ff.up.railway.app/
- Frontend URL: https://blog-cms-frontend-ten.vercel.app/ 