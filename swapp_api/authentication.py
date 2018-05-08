import base64

from django.contrib.auth import authenticate

from oauth2_provider.models import AccessToken
from rest_framework import status
from rest_framework.authentication import BaseAuthentication

from rest_framework.response import Response


class BasicAuthentication(BaseAuthentication):
    """
    A subclass of Django REST frameworks's `BaseAuthentication`

    Custom authenticaton class that uses HTTP Basic authentication.
    Expects a Base 64 encoded API key. Requires HTTPS using `request.is_secure` method.
    """

    def authenticate(self, request):
        """
        Returns a User instance if a correct API key have been supplied
        using HTTP Basic authentication. Otherwise returns False.
        """

        access_token = request.META.get('HTTP_AUTHORIZATION')

        if not access_token:
            access_token = request.GET.get('identifier')

        if access_token:
            try:
                access_token_obj = AccessToken.objects.get(token=access_token)
                return access_token_obj.user
            except AccessToken.DoesNotExist:
                pass

        return None