from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
import logging

from .serializers import UserSerializer

# Setup logger
logger = logging.getLogger(__name__)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile"""
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve the user profile"""
        if not request.user.is_authenticated:
            return Response({
                "authenticated": False,
                "message": "User is not authenticated"
            })
        
        user = self.get_object()
        serializer = UserSerializer(user)
        
        # Add authentication status to response
        data = serializer.data
        data['authenticated'] = True
        
        # Add user permissions
        data['permissions'] = {
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        return Response(data) 