import os, predictionio, random

from django.conf import settings

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