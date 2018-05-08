from django.shortcuts import get_object_or_404

from item.models import Category, Subcategory, Item
from swapp_api.predictionio_api import PIOEvent
from user_profile.models import Preference


def set_user_preference(user, categories=[]):
    """
    Function that sets the user preference of the user

    Args:
        user: the current user (object)
        categories: list of Category IDs of the user's preferences (list of integers)

    Returns:
        None
    """
    preference, created = Preference.objects.get_or_create(user=user)
    pio = PIOEvent()
    preference.categories.clear()
    for cat in categories:
        category = get_object_or_404(Category, id=int(cat))
        preference.categories.add(category)
        for subcategory in Subcategory.objects.filter(parent_category=category):
            for item in Item.objects.filter(subcategory=subcategory).exclude(owner=user):
                pio.item_on_category(user, item)