# Blog API Pagination & Search Guide

## Overview

The Blog API now supports both pagination with 9 blog cards displayed per page by default and universal search functionality. This guide explains how to use both features together.

## API Endpoint

```
GET /api/posts/
```

## API Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | - | Universal search across title, content, and slug |
| `page` | integer | 1 | Page number to retrieve |
| `limit` | integer | 9 | Number of posts per page (max: 50) |
| `published` | boolean | - | Filter by published status |
| `title` | string | - | Filter by title (legacy - use search instead) |
| `slug` | string | - | Filter by slug (legacy - use search instead) |

## Example API Calls

### 1. Get first page with default settings (9 posts)
```
GET /api/posts/?published=true
```

### 2. Get specific page
```
GET /api/posts/?published=true&page=2
```

### 3. Custom page size
```
GET /api/posts/?published=true&limit=5
```

### 4. Combine parameters
```
GET /api/posts/?published=true&page=2&limit=9
```

## Universal Search Examples

### 1. Search by title
```
GET /api/posts/?published=true&search=Django
```

### 2. Search by content
```
GET /api/posts/?published=true&search=React
```

### 3. Multi-term search (all terms must be found)
```
GET /api/posts/?published=true&search=web development
```

### 4. Search with pagination
```
GET /api/posts/?published=true&search=JavaScript&page=1&limit=5
```

### 5. Complex search with special characters
```
GET /api/posts/?published=true&search=API REST framework
```

## Response Format

```json
{
  "count": 15,
  "next": "http://example.com/api/posts/?page=2&published=true",
  "previous": null,
  "total_pages": 2,
  "current_page": 1,
  "page_size": 9,
  "results": [
    {
      "id": 1,
      "title": "Blog Post Title",
      "slug": "blog-post-title",
      "content": "Blog post content...",
      "featured_image": "/media/images/post.jpg",
      "published": true,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "comment_count": 5
    }
    // ... more posts
  ]
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Total number of posts |
| `next` | string/null | URL to next page (null if last page) |
| `previous` | string/null | URL to previous page (null if first page) |
| `total_pages` | integer | Total number of pages |
| `current_page` | integer | Current page number |
| `page_size` | integer | Number of posts per page |
| `results` | array | Array of blog post objects |

## Search Functionality

### How Search Works

The universal search feature searches across multiple fields:

1. **Title**: Searches in blog post titles
2. **Content**: Searches in blog post content (including HTML)
3. **Slug**: Searches in URL-friendly slugs

### Search Features

- **Multi-term Search**: All search terms must be found (AND logic)
- **Case Insensitive**: Search is not case sensitive
- **Partial Matching**: Finds partial matches within words
- **Relevance Ordering**: Title matches are prioritized over content matches
- **Special Character Handling**: Automatically cleans special characters
- **HTML Content Search**: Searches within rich text content

### Search Term Processing

The search functionality automatically:
- Removes HTML tags from search queries
- Splits search terms on whitespace
- Filters out terms shorter than 2 characters
- Limits to 10 search terms for performance
- Cleans special characters

### Search Examples

```javascript
// Search for posts containing "Django"
const searchResults = await postsApi.getAllPosts({
  search: "Django",
  published: true
});

// Multi-term search
const webDevPosts = await postsApi.getAllPosts({
  search: "web development",
  published: true
});

// Search with pagination
const paginatedSearch = await postsApi.getAllPosts({
  search: "JavaScript React",
  page: 1,
  limit: 5,
  published: true
});
```

## Frontend Implementation

The frontend automatically handles both pagination and search:

1. **Default Display**: Shows 9 blog cards per page
2. **Search Integration**: Real-time search with debouncing
3. **Navigation**: Provides Previous/Next buttons
4. **Page Indicator**: Shows current page number
5. **Responsive**: Adapts to different screen sizes

### Frontend Code Example

```javascript
// Fetch posts with pagination and search
const fetchBlogs = async (page = 1, searchTerm = '') => {
  const filters = {
    page: page,
    limit: 9,
    published: true
  };
  
  // Add search if provided
  if (searchTerm) {
    filters.search = searchTerm;
  }
  
  const response = await postsApi.getAllPosts(filters);
  
  if (response.data) {
    setBlogs(response.data.results || []);
    setTotalPages(response.data.total_pages || 1);
  }
};

// Search with debouncing
useEffect(() => {
  const timeoutId = setTimeout(() => {
    fetchBlogs(1, searchTerm); // Reset to page 1 on new search
  }, 500);

  return () => clearTimeout(timeoutId);
}, [searchTerm]);
```

## Configuration

### Backend Configuration

The pagination is configured in `backend/blog/pagination.py`:

```python
class BlogPostPagination(PageNumberPagination):
    page_size = 9  # Default posts per page
    page_size_query_param = 'limit'  # Allow custom page size
    max_page_size = 50  # Maximum allowed page size
```

### Frontend Configuration

The frontend pagination is configured in `Blog-Website/src/pages/BlogListPage.jsx`:

```javascript
const filters = {
  page: page,
  limit: 9,  // Posts per page
  published: true
};
```

## Testing

Run the test scripts to verify pagination:

```bash
# Test pagination logic
python backend/test_pagination.py

# Test API endpoints
python backend/test_api_endpoint.py
```

## Error Handling

The API handles various edge cases:

- **Invalid page numbers**: Returns first page
- **Limit too large**: Caps at `max_page_size` (50)
- **Invalid limit values**: Uses default page size
- **Empty results**: Returns empty results array

## Performance Considerations

- **Database Optimization**: Uses `LIMIT` and `OFFSET` for efficient querying
- **Prefetch Related**: Optimizes related data loading (images, comments)
- **Caching**: Consider implementing caching for frequently accessed pages

## Migration Notes

If upgrading from the previous 6-posts-per-page system:

1. **Backend**: The pagination class automatically handles the new page size
2. **Frontend**: Update any hardcoded references from 6 to 9
3. **Testing**: Verify pagination works with existing data

## Troubleshooting

### Common Issues

1. **Wrong page size**: Check `limit` parameter in API calls
2. **Missing pagination**: Ensure `BlogPostPagination` is set in ViewSet
3. **Frontend not updating**: Verify `total_pages` calculation uses correct page size

### Debug Commands

```bash
# Check Django configuration
python manage.py check

# Test API directly
curl "http://localhost:8000/api/posts/?published=true&limit=9"
```

## Future Enhancements

Potential improvements:

1. **Cursor-based pagination** for better performance with large datasets
2. **Search pagination** with preserved search terms
3. **Infinite scroll** option for mobile interfaces
4. **Page size preferences** stored in user settings