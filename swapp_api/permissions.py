from oauth2_provider.models import AccessToken
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response


class IsAuthenticated(BasePermission):
    """
    A subclass of Django REST frameworks's `BasePermission`

    Custom permissions class to allow access only to authenticated users.
    """

    def check_permission(self, user):
        """
        Checks if given token in the request is associated to an authenticated user.
        """

        if not self.view.request.GET.get('identifier'):
            raise Response("Access Token needs to be provided.", status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                token = AccessToken.objects.get(token=self.view.request.GET.get('identifier'))
                user = token.user
            except AccessToken.DoesNotExist:
                raise Response("User is not autheticated.", status=status.HTTP_401_UNAUTHORIZED)
