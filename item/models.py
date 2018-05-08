import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.utils import timezone
from django.utils.translation import ugettext as _

from user_profile.models import UserProfile
from swapp_api.fields import AutoResizeImageField
from swapp_api.pio_event import PIOEvent

logger = logging.getLogger(__name__)

optional = {
    'blank': True,
    'null' : True,
}


class Item(models.Model):
    """
    The Item model includes the important information about the item as it is presented in its profile page.
    """
    name = models.CharField(max_length=250)
    owner = models.ForeignKey(User, related_name='items')
    photo = AutoResizeImageField(upload_to = "item/", max_length = 500, **optional)
    date_posted = models.DateTimeField(default=timezone.now)
    price_range_minimum = models.PositiveIntegerField()
    price_range_maximum = models.PositiveIntegerField()
    subcategory = models.ForeignKey('item.Subcategory')
    tags = models.ManyToManyField('item.Tag', **optional)
    description = models.TextField(**optional)
    is_available = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, **optional)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, **optional)
    condition = models.BooleanField(default=True)  # Brand new

    def __unicode__(self):
        return "{} (from: {})".format(self.name, self.owner)

    class Meta(object):
        ordering = ['date_posted']
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def to_dict(self):
        try:
            location = str(self.owner.profile.location)
            owner_photo_url = "" if not self.owner.profile.photo else self.owner.profile.photo.url
        except UserProfile.DoesNotExist:
            location = ""
            owner_photo_url = ""

        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner.id,
            'owner_photo': owner_photo_url,
            'owner_location': location,
            'price_range': "PHP {} - {}".format(self.price_range_minimum, self.price_range_maximum),
            'price_range_maximum': self.price_range_maximum,
            'price_range_minimum': self.price_range_minimum,
            'date_posted': self.date_posted,
            'date_posted_formatted': self.date_posted.strftime("%B %m, %Y"),
            'description': self.description,
            'condition': self.condition,
            'photo': "" if not self.photo else self.photo.url,
            'subcategory': self.subcategory.name,
            'is_available': self.is_available,
        }

    def save(self, *args, **kwargs):
        new = False if self.pk else True
        super(Item, self).save(*args, **kwargs)
        if new:
            try:
                pio = PIOEvent()
                pio.create_item(self)
            except Exception as e:
                logger.error(e)


class Tag(models.Model):
    """
    The Tag model provides keyword that would give more information about specific items.
    """
    tag_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, **optional)

    def __unicode__(self):
        return "{}".format(self.tag_name)

    class Meta(object):
        ordering = ['tag_name']
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Category(models.Model):
    """
    The Category model include the groups by which the items are divided.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, **optional)
    date_created = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "{}".format(self.name)

    class Meta(object):
        ordering = ['name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

class Subcategory(models.Model):
    """
    The Subcategory models shows which specifc group under a category are the items subdivided.
    """
    name = models.CharField(max_length=100, unique=True, default="")
    description = models.CharField(max_length=500, **optional)
    parent_category = models.ForeignKey('item.Category')
    date_created = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "{} (under {})".format(self.name, self.parent_category)

    class Meta(object):
        ordering = ['name']
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')


class SwapHistory(models.Model):
    """
    This saves the specific swaps made by each users
    """

    user1 = models.ForeignKey(User, related_name='swap_history_first_user')
    user2 = models.ForeignKey(User, related_name='swap_history_second_user')
    item1 = models.ForeignKey(Item, related_name='swap_history_first_item') # Item owned by the first user
    item2 = models.ForeignKey(Item, related_name='swap_history_second_item') # Item owned by the second user
    date = models.DateTimeField(default=timezone.now)
    transaction_trail = models.ForeignKey('transaction.Transaction')

    def __unicode__(self):
        return "{} and {} - ({})".format(self.user1, self.user2, self.date)

    class Meta(object):
        ordering = ['date']
        verbose_name = _('Swap History')
        verbose_name_plural = _('Swap History')


# Signal Method(s)
def delete_previous_item_image(sender, instance, **kwargs):
    """
    Before deleting the item instance, deletes first its associated image before it is replaced.
    """

    if instance and instance.photo:
        instance.photo.delete(False)


pre_delete.connect(delete_previous_item_image, sender=Item)
