from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext as _

from item.models import Item


optional = {
    'blank': True,
    'null' : True,
}

class Transaction(models.Model):
    """
    The Transaction model displays the information for each item transaction
    """
    item1 = models.ForeignKey(Item, related_name='item1') # item from the initiator
    item2 = models.ForeignKey(Item, related_name='item2') # item the initiator wanted in exchange of his item
    date_created = models.DateTimeField(default=timezone.now)
    is_approved = models.NullBooleanField()
    date_approved = models.DateTimeField(**optional)

    def __unicode__(self):
        return "{} in exchange of {}".format(self.item1, self.item2)

    class Meta(object):
        ordering = ['date_created']
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    def to_dict(self):
        return {
            "item_1": self.item1.name,
            "item_1_owner_id": self.item1.owner.id,
            "item_1_photo": "" if not self.item1.photo else  self.item1.photo.url,
            "item_2": self.item2.name,
            "item_2_owner_id": self.item2.owner.id,
            "item_2_photo": "" if not self.item2.photo else  self.item2.photo.url,
            "date_approved": self.date_approved
        }

    @property
    def is_valid(self):
        """
        Property to determine if a transaction has one or both items currently unavailable.
        """

        return (self.item1.is_available == True and self.item2.is_available == True)

    @classmethod
    def get_approved_user_transactions(cls, user, detailed=False):
        """
        Class method to retrieve all approved transactions associated to a user.

        Returns a list of id's corresponding to the two items per matching transaction if `detailed`
        is set to `True`, else returns the resulting Queryset.
        """

        transaction_details_list = []
        user_transactions = cls.objects.filter((Q(item1__owner=user) | Q(item2__owner=user)), is_approved=True)

        for transaction in user_transactions:
            transaction_dict = {
                "user_item_id": transaction.item1.id,
                "other_item_id": transaction.item2.id,
                "action_from_id": user.id,
            }

            transaction_details_list.append(transaction_dict)

        return transaction_details_list if detailed else user_transactions

    @classmethod
    def get_pending_user_transactions(cls, user, detailed=False):
        """
        Class method to retrieve all pending transactions associated to a user.

        Returns a list of id's corresponding to the two items per matching transaction if `detailed`
        is set to `True`, else returns the resulting Queryset.
        """

        transaction_details_list = []
        user_transactions = cls.objects.filter((Q(item1__owner=user) | Q(item2__owner=user)), is_approved=None)

        for transaction in user_transactions:
            transaction_dict = {
                "user_item_id": transaction.item1.id,
                "other_item_id": transaction.item2.id,
                "action_from_id": user.id,
                "transaction_id": transaction.id
            }

            transaction_details_list.append(transaction_dict)

        return transaction_details_list if detailed else user_transactions


class Notification(models.Model):
    """
    Model to encapsulate various notification details
    """

    TYPE_CHOICES = (
        ('offer', 'Offer'),
        ('accept', 'Accept'),
        ('reject', 'Reject')
    )

    # Notification information
    notification = models.CharField(max_length=100)
    date_created = models.DateTimeField(default=timezone.now)
    type = models.CharField(choices=TYPE_CHOICES, default='offer', max_length=10)
    is_read = models.BooleanField(default=False)

    # Target users
    recipient = models.ForeignKey(User, related_name='notifications_received')
    action_from = models.ForeignKey(User, related_name='notifications_sent')

    # Transaction
    transaction = models.ForeignKey(Transaction, related_name='notification', **optional)

    def __unicode__(self):
        full_name = self.action_from.get_full_name()

        return "{} {}".format(self.action_from.username if not full_name else full_name, self.notification)

    class Meta(object):
        ordering = ['date_created']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def to_dict(self):
        return {
            "notif_id": self.id,
            "notif_type": self.type,
            "notification": self.__unicode__(),
            "date": self.date_created,
            "is_read": self.is_read,
            "item_id": self.transaction.item1.id,
            "other_item_id": self.transaction.item2.id,
            "item_photo": "" if not self.transaction.item1.photo else self.transaction.item1.photo.url,
            "other_item_photo": "" if not self.transaction.item2.photo else self.transaction.item2.photo.url,
            "is_valid_transaction": self.transaction.is_valid
        }

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.notification:
            self.notification = "offered a Swapp with you."

        return super(Notification, self).save()
