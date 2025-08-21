from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class ApiKeyUser(AnonymousUser):
    """Custom user class for API key authentication"""
    @property
    def is_authenticated(self):
        return True


class ApiKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key based authentication
    """
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            # Check if it's a frontend request (no API key required for GET requests to certain endpoints)
            if request.method == 'GET' and '/api/processes/' in request.path:
                return (ApiKeyUser(), None)
            return None
        
        if api_key != settings.API_KEY:
            raise AuthenticationFailed('Invalid API key')
        
        return (ApiKeyUser(), None)
    
    def authenticate_header(self, request):
        return 'X-API-Key' 