import os, predictionio, random

from django.conf import settings
from django.contrib.auth.models import User
from item.models import Item, Category, Subcategory
from user_profile.models import UserProfile, Preference


def train_system():
    os.environ["PATH"] += "PATH=$PATH:{}".format(settings.PIO_PATH)
    os.system("export PATH")
    os.system("cd ../../pio_files/swapp-recommendation; pio build; pio train")
    os.system("cd ../../pio_files/swapp-similar-product; pio build; pio train")

def initialize_data_on_pio():
    users = User.objects.filter(is_active=True)
    items = Item.objects.filter(is_available=True)
    categories = Subcategory.objects.all()
    pio = PIOEvent()

    for user in users:
        pio.create_user(user)

    for item in items:
        pio.create_item(item)

def random_initial_data():
    # For sample presentation only
    users = User.objects.all()
    items = Item.objects.all()
    categories = Category.objects.all().values_list('id', flat=True)

    # random viewing of items
    for event in range(10):
        user = users[random.randint(0,users.count()-1)]
        item = items[random.randint(0,items.count()-1)]
        PIOEvent().view_item(user,item)

    # random preferences
    from user_profile.tasks import set_user_preference
    for user in users:
        set_user_preference(user, [categories[random.randint(0,categories.count()-1)]])

def retrain_pio():
    pass

def lebesgue_measure(A1, A2, B1, B2):
    RD1 = 0
    RD2 = 0

    if B1 < A2 and B2 > A1:
        distance = A2 - A1
        if B1 > A1:
            distance = distance - (B1-A1)
        if B2 < A2:
            distance = distance - (A2-B2)

        RD1 = (float(distance) / (A2 - A1))*100
        RD2 = (float(distance) / (B2 - B1))*100

    if RD1 >= 15  and RD2 >= 15:
        return True
    else:
        return False


class PIOEvent(object):
    client_recommendation = predictionio.EventClient(
        access_key=settings.PIO_ACCESS_KEY_RECOMMENDATION,
        url=settings.PIO_EVENT_URL,
        threads=5,
        qsize=500
    )

    client_similar = predictionio.EventClient(
        access_key=settings.PIO_ACCESS_KEY_SIMILAR,
        url=settings.PIO_EVENT_URL,
        threads=5,
        qsize=500
    )

    def create_user(self, user):
        self.client_recommendation.create_event(
            event="$set",
            entity_type="user",
            entity_id="u{}".format(user.id),
        )
        self.client_similar.create_event(
            event="$set",
            entity_type="user",
            entity_id="u{}".format(user.id),
        )

    def create_item(self, item):
        self.client_recommendation.create_event(
            event="$set",
            entity_type="item",
            entity_id="i{}".format(item.id),
            properties={
                "categories" : ["cat{}".format(item.subcategory.id)]
            }
        )
        self.client_similar.create_event(
            event="$set",
            entity_type="item",
            entity_id="i{}".format(item.id),
            properties={
                "categories" : ["cat{}".format(item.subcategory.id)]
            }
        )

    def view_item(self, user, item):
        self.client_similar.create_event(
            event="view",
            entity_type="user",
            entity_id="u{}".format(user.id),
            target_entity_type="item",
            target_entity_id="i{}".format(item.id)
        )

    def buy_item(self, user, item):
        self.client_recommendation.create_event(
            event="buy",
            entity_type="user",
            entity_id="u{}".format(user.id),
            target_entity_type="item",
            target_entity_id="i{}".format(item.id)
        )

    def item_on_category(self, user, item):
        self.client_recommendation.create_event(
            event="rate",
            entity_type="user",
            entity_id="u{}".format(user.id),
            target_entity_type="item",
            target_entity_id="i{}".format(item.id),
            properties= { "rating" : float(4) }
        )


class PIOExport(object):
    engine_client_recommended = predictionio.EngineClient(url=settings.PIO_ACCESS_URL)
    engine_client_similar= predictionio.EngineClient(url=settings.PIO_SIMILAR_URL)

    def list_of_recommended_items(self, user):
        try:
            preference = Preference.objects.get(user=user)
            queryset = self.engine_client_recommended.send_query({"user": "u{}".format(int(user.id)), "num": 10})
            item_ids = [x.get('item')[1:] for x in queryset.get('itemScores') if x.get('score') > 3.5]

            if not set(map(int,item_ids)).issubset(Item.objects.all().values_list('id', flat=True)):
                return []

            items = [Item.objects.get(id=int(x)) for x in item_ids]
            sample_item = Item.objects.filter(owner=user)[0]
            items_filtered = [item for item in items if item.owner != user]
        except Exception as e:
            items_filtered = [item for item in Item.objects.exclude(owner=user)]
        return items_filtered

    def list_of_matching_items_by_price_range(self, current_item, recommended_items):
        matching_items = [item for item in recommended_items if lebesgue_measure(
            current_item.price_range_minimum,
            current_item.price_range_maximum,
            item.price_range_minimum,
            item.price_range_maximum)]

        return matching_items
