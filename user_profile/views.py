from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import Http404

from push_notifications.models import APNSDevice
from oauth2_provider.models import AccessToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import Category, Subcategory
from user_profile.models import (
    Preference,
    UserProfile
)
from user_profile.serializers import (
    PreferenceSerializer,
    UserSerializer,
    UserProfileSerializer
)
from swapp_api.authentication import BasicAuthentication
from swapp_api.permissions import IsAuthenticated
from swapp_api.predictionio_api import PIOEvent, train_system


# User
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# UserProfile
class UserProfileDetail(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        GET request to retrieve a User based on username or access token
        """

        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user
            profile = UserProfile.objects.get(user=user)

            preferences = user.preferences.first()
            preference_list = []

            if preferences:
                categories = [category.name for category in Category.objects.all().order_by('name')]

                for i in range(len(categories)):
                    if preferences.categories.filter(name=categories[i]).exists():
                        preference_list.append(i)
                        
            user_info = {
                'id': user.id,
                'name': user.get_full_name(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': "" if not profile.phone else profile.phone,
                'address': "" if not user.profile else str(user.profile.location),
                'items': [item.to_dict() for item in user.items.filter(is_available=True)],
                'image': "" if not user.profile.photo else user.profile.photo.url,
                'subcategories': [subcategory.name for subcategory in Subcategory.objects.all()],
                'range': profile.distance_range,
                'preferences': preference_list,
            }

            return Response(user_info, status.HTTP_200_OK)
        except Exception, e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


class EditUserProfileView(APIView):
    """
    View to Edit Current User Profile
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        POST request to change user profile fields
        """
        try:
            data = request.DATA
            user = User.objects.get(id=int(data.get('id')))
            profile = UserProfile.objects.get(user=user)

            profile_data = {
                'phone': data.get('phone'),
                'user': user.id,
                'location': profile.location,
            }

            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')

            if data.get('photo'):
                profile_data['photo'] = data.get('photo')
                profile_serializer = UserProfileSerializer(profile, data=profile_data)

                if profile_serializer.is_valid():
                    # Deletes first its previous image to save server storage space
                    if profile.photo:
                        profile.photo.delete(False)

                    user.save()
                    profile_serializer.save()
                else:
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.save()

                profile.phone = data.get('phone')
                profile.save()

            return Response("Success", status=status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status=status.HTTP_400_BAD_REQUEST)


# Signup
class SignupView(APIView):
    """
    View to allow new users to sign up to the app
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, format=None):
        """
        POST request to create a new User and UserProfile
        """

        data = request.DATA
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()

            # Create APNSDevice instance for current user
            device_token = data.get('device_token')

            profile = UserProfile.objects.get(user=user)
            

            if device_token != "none":
                apns_device, created = APNSDevice.objects.get_or_create(registration_id=device_token)
                apns_device.user = user

                apns_device.save()

            if data.get('photo'):
                profile_data = {
                    'user': user.id,
                    'location': "",
                    'photo': data.get('photo')
                }
                profile_serializer = UserProfileSerializer(profile, data=profile_data)

                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(None, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    View to allow users to change their passwords
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        POST request to change password
        """

        identifier = kwargs.get('identifier')
        old_password = request.DATA.get('old_password')
        new_password = request.DATA.get('new_password')

        if identifier:
            try:
                # Query identifier as username first
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                try:
                    # If it fails, query identifier as access token
                    token = AccessToken.objects.get(token=identifier)
                    user = token.user
                except AccessToken.DoesNotExist:
                    return Response("No users matched", status.HTTP_404_NOT_FOUND)

            try:
                if not authenticate(username=user.username, password=old_password):
                    return Response("Wrong password", status.HTTP_406_NOT_REQUIRED)
                else:
                    user.set_password(new_password)
            except Exception as e:
                return Response(e, status.HTTP_400_BAD_REQUEST)

            return Response("Password successfully changed", status.HTTP_200_OK)
        else:
            return Response("No identifier is provided", status.HTTP_400_BAD_REQUEST)


class ChangeUserLocation(APIView):
    """
    View to change the location of the user on different occassions
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        POST request to change user location
        """

        try:
            data = request.DATA
            token = AccessToken.objects.get(token=kwargs.get('identifier'))
            user = UserProfile.objects.get(user=token.user)

            user.current_latitude = data.get('latitude')
            user.current_longitude = data.get('longitude')
            user.location = data.get('location')
            user.save()

            return Response("Test", status=status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status=status.HTTP_400_BAD_REQUEST)


class StoreDeviceTokenView(APIView):
    """
    Endpoint to handle storing of device token to its corresponding user
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            # Update APNS device token of currently logged-in user (For cases that user has logged in to another device)
            device_token = request.DATA.get('device_token')

            try:
                # Checks first if user is already registered for notifications.
                apns_device = APNSDevice.objects.get(user=user, registration_id=device_token)
            except APNSDevice.DoesNotExist:
                try:
                    # Checks if device token has already been registered
                    apns_device, created = APNSDevice.objects.get_or_create(registration_id=device_token)

                    if created or apns_device.user != user:
                        apns_device.user = user
                        apns_device.save()
                except:
                    pass

            return Response(None, status=status.HTTP_200_OK)
        except Exception, e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


# Preference
class PreferenceList(generics.ListCreateAPIView):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer


class PreferenceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer


class ChangePreferencesView(APIView):
    """
    Endpoint for Changing User Preferences
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post (self, request, **kwargs):
        try:
            data = request.DATA
            user = User.objects.get(id=int(data.get('id')))
            profile = UserProfile.objects.get(user=user)

            profile.distance_range = int(data.get('range'))
            profile.save()

            preference_list = data.get('preferences')
            preferences, created = Preference.objects.get_or_create(user=user)
            categories = [category for category in Category.objects.all().order_by('name')]

            try:
                preferences.categories.clear()

                for preference in preference_list:
                    preferences.categories.add(categories[int(preference)])
            except Exception as e:
                pass

            train_system()

            return Response("Success", status=status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


class PreferenceList(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            preferences = Preference.objects.get_or_create(user=user)
            categories = [category.name for category in Category.objects.all().order_by('name')]

            preference_list = []

            for i in range(len(categories)):
                if preferences.categories.filter(name=categories[i]).exists():
                    preference_list.append(i)

            result_text = {'preference_list': preference_list}

            return Response(result_text, status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)
