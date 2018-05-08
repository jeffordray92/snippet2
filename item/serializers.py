from rest_framework import serializers

from item.models import (
    Category,
    Item,
    Subcategory,
    Tag
)
from item.serializer_fields import Base64ImageField


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

class ItemSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Item

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
