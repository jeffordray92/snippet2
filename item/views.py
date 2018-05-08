import json

from django.contrib.auth.models import User
from django.http import Http404

from oauth2_provider.models import AccessToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import (
    Category,
    Item,
    Subcategory,
    Tag,
)
from item.serializers import (
    CategorySerializer,
    ItemSerializer,
    SubcategorySerializer,
    TagSerializer,
)
from item.utils import distance_on_unit_sphere, recommended_items_based_on_location
from swapp_api.authentication import BasicAuthentication
from swapp_api.permissions import IsAuthenticated
from swapp_api.predictionio_api import PIOEvent, PIOExport, train_system
from transaction.models import Transaction
from user_profile.models import UserProfile


# Category
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Subcategory
class SubcategoryList(generics.ListCreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class SubcategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


# Tag
class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# Item
class ItemList(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            token = AccessToken.objects.get(token=kwargs.get('identifier'))
            user = token.user
            profile = UserProfile.objects.get(user=user)

            # Retrieve and filter out user's recommended items by availability, location, and price ranges
            user_items = user.items.filter(is_available=True)

            if not user_items:
                msg = "You have yet to add your very first item.\nClick the 'Plus' icon in you Profile page to do so."

                return Response(msg, status.HTTP_404_NOT_FOUND)

            recommended_items = PIOExport().list_of_recommended_items(user)
            recommended_items = [item for item in recommended_items if item.is_available]
            recommended_items_by_location = recommended_items_based_on_location(
                                                profile,
                                                recommended_items)
            matching_items = PIOExport().list_of_matching_items_by_price_range(
                                    user_items[0],
                                    recommended_items_by_location)

            return_data = {
                'owned_items': [item.to_dict() for item in user_items],
                'other_users_items': [item.to_dict() for item in matching_items],
                'pending_transactions': Transaction.get_pending_user_transactions(user, detailed=True)
                # TODO: Filter items with existing transaction
            }

            return Response(return_data, status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


class ItemDetail(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        id = kwargs.get('pk')

        try:
            item = Item.objects.get(id=id);

            return Response(item.to_dict(), status.HTTP_200_OK)
        except Item.DoesNotExist:
            raise Http404

        return Response("Error", status.HTTP_400_BAD_REQUEST)


class ItemView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        data = request.DATA
        id = kwargs.get('pk')
        pio = PIOEvent()

        try:
            item = Item.objects.get(id=id)
            user = User.objects.get(id=int(data.get('user')))

            pio.view_item(user,item)

            return Response("Success", status.HTTP_200_OK)
        except Exception as e:
            # Handles all errors that may be caused by errors on PredictionIO
            raise Http404

        return Response("Error", status.HTTP_400_BAD_REQUEST)


class ItemEdit(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        data = request.DATA
        item = Item.objects.get(id=data.get('id'))

        data['owner'] = item.owner.id
        data['condition'] = True if data['condition'] == "brand_new" else False
        data['subcategory'] = Subcategory.objects.get(name=data.get('subcategory')).id

        if not data.get('photo'):
            item.name = data.get('name')
            item.description = data.get('description')
            item.condition = data.get('condition')
            item.subcategory = Subcategory.objects.get(id=data.get('subcategory'))
            item.latitude = data.get('latitude')
            item.longitude = data.get('longitude')
            item.price_range_minimum = data.get('price_range_minimum')
            item.price_range_maximum = data.get('price_range_maximum')
            item.save()

            return Response(item.to_dict(), status=status.HTTP_201_CREATED)
        else:
            serializer = ItemSerializer(item, data=data)

            if serializer.is_valid():
                # Deletes first its previous image to save server storage space
                if item.photo:
                    item.photo.delete(False)

                serializer.save()

                return Response(item.to_dict(), status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemAdd(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        identifier = request.META.get('HTTP_AUTHORIZATION')
        identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
        token = AccessToken.objects.get(token=identifier)
        user = token.user

        data = request.DATA
        data['owner'] = user.id
        data['condition'] = True if data['condition'] == "brand_new" else False
        data['subcategory'] = Subcategory.objects.get(name=data.get('subcategory')).id

        serializer = ItemSerializer(data=data)

        if serializer.is_valid():
            item = serializer.save()

            profile = UserProfile.objects.get(user__id=int(user.id))
            profile.current_latitude = data.get('latitude')
            profile.current_longitude = data.get('longitude')
            profile.save()

            train_system()

            return Response(item.to_dict(), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDelete(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        try:
            item = Item.objects.get(id=int(kwargs.get('pk')))

            item.delete()
        except Item.DoesNotExist:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        return Response("Successfully deleted", status=status.HTTP_200_OK)


class ItemConflictCheck(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user
            profile = UserProfile.objects.get(user=user)

            conflict_items = Item.objects.filter(owner=user, is_available=True)
            result = "False"

            for item in conflict_items:
                # Checks if the distance of an item is greater than 50Km with the current location of the user
                if item.latitude == None or item.longitude == None:
                    result = "True"
                elif distance_on_unit_sphere(item.latitude, item.longitude, profile.current_latitude, profile.current_longitude)[1] > 50.0:
                    result = "True"

            result_text = {'result': result}

            return Response(result_text, status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


class ItemConflictResolve(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user
            profile = UserProfile.objects.get(user=user)

            items = Item.objects.filter(owner=user, is_available=True)

            for item in items:
                item.latitude = profile.current_latitude
                item.longitude = profile.current_longitude
                item.save()

            return Response("Conflict successfully resolved", status=status.HTTP_200_OK)

        except Exception as e:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)


class MatchingItems(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        GET request to retrieve all matching items for a given item
        """

        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user
            profile = UserProfile.objects.get(user=user)

            try:
                item_id = kwargs.get('pk')

                if not item_id:
                    return Response("No Item ID was provided", status=status.HTTP_400_BAD_REQUEST)

                current_item = Item.objects.get(id=int(item_id))

                recommended_items = PIOExport().list_of_recommended_items(user)
                recommended_items = [item for item in recommended_items if item.is_available]
                recommended_items_by_location = recommended_items_based_on_location(
                                                    profile,
                                                    recommended_items)
                matching_items = PIOExport().list_of_matching_items_by_price_range(
                                    current_item,
                                    recommended_items_by_location)

                return_data = {
                    'matching_items': [item.to_dict() for item in matching_items],
                    'pending_transactions': Transaction.get_pending_user_transactions(user, detailed=True)
                }

                return Response(return_data, status=status.HTTP_200_OK)
            except Item.DoesNotExist:
                return Response("Item does not exist", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)
