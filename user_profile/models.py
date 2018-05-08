import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.translation import ugettext as _

from cities_light.models import City

from swapp_api.fields import AutoResizeImageField
from swapp_api.pio_event import PIOEvent

logger = logging.getLogger(__name__)

optional = {
    'blank': True,
    'null' : True,
}


class UserProfile(models.Model):
    """
    The UserProfile model includes the information of the registered user.
    """

    user = models.OneToOneField(User, related_name='profile')
    location = models.CharField(max_length=50, **optional)
    phone = models.CharField(max_length=50, **optional)
    photo = AutoResizeImageField(upload_to = "profile/", max_length = 500, **optional)
    date_registered = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)
    current_latitude = models.DecimalField(max_digits=11, decimal_places=8, **optional)
    current_longitude = models.DecimalField(max_digits=11, decimal_places=8, **optional)
    distance_range = models.IntegerField(default=100)

    def __unicode__(self):
        return "{}".format(self.user)

    class Meta(object):
        ordering = ['user']
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def save(self, *args, **kwargs):
        new = False if self.pk else True

        super(UserProfile, self).save(*args, **kwargs)

        if new:
            try:
                pio = PIOEvent()

                pio.create_user(self.user)
            except Exception as e:
                logger.error(e)


class Preference(models.Model):
    """
    The Preference model includes information regarding the categories and tags the user prefers when searching for products.
    """
    user = models.ForeignKey(User, related_name='preferences')
    categories = models.ManyToManyField("item.Category", **optional)
    tags = models.ManyToManyField("item.Tag", **optional)

    def __unicode__(self):
        return "{}".format(self.user)

    class Meta(object):
        ordering = ['user']
        verbose_name = _('User Preference')
        verbose_name_plural = _('User Preferences')


# Signal Method(s)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Upon creation of a new User instance, its corresponding UserProfile instance is also created, linking it to the
    current user.
    """

    if created:

        UserProfile.objects.create(user=instance, location="No Location Set")


def create_user_preference(sender, instance, created, **kwargs):
    """
    Upon creation of a new User instance, its corresponding Preference instance is also created, linking it to the
    current user.
    """

    if created:
        Preference.objects.create(user=instance)


def set_user_password(sender, instance, **kwargs):
    """
    Before saving a User instance, User instance's `set_password` method is called to properly save user's password.
    """

    if instance and not instance.id:
        instance.set_password(instance.password)


# Register the signal
post_save.connect(create_user_profile, sender=User)
post_save.connect(create_user_preference, sender=User)
pre_save.connect(set_user_password, sender=User)
