from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BlogPostPagination(PageNumberPagination):
    """
    Custom pagination class for blog posts that supports dynamic page size
    """
    page_size = 9  # Default to 9 posts per page
    page_size_query_param = 'limit'  # Allow client to set page size with ?limit=X
    max_page_size = 50  # Maximum allowed page size
    
    def get_page_size(self, request):
        """
        Return the page size for this pagination instance.
        """
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size > 0:
                    return min(page_size, self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response object for the given output data.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page
        })