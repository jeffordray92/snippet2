from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from transaction.models import Transaction
from user_profile.models import UserProfile


class Thread(models.Model):
    """
    The Thread model includes information about message threads from users
    """

    sender = models.ForeignKey(User, related_name='thread_sender')
    receiver = models.ForeignKey(User, related_name='thread_receiver')
    date_initiated = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    transaction = models.OneToOneField(Transaction, related_name='thread')

    def __unicode__(self):
        return "Thread for {}".format(self.transaction)

    class Meta(object):
        ordering = ['date_modified']
        verbose_name = _('Message Thread')
        verbose_name_plural = _('Message Threads')

    def to_dict(self, detailed=False):
        """
        Returns all necessary details for a certain Thread instance

        An additionaly parameter, `detailed`, checks if all thread messages and
        pending transaction information will also be included.
        """

        all_messages = self.messages.all()

        try:
            profile = self.sender.profile
            sender_photo = "" if not profile.photo else profile.photo.url
        except UserProfile.DoesNotExist:
            sender_photo = ""

        try:
            profile = self.receiver.profile
            receiver_photo = "" if not profile.photo else profile.photo.url
        except UserProfile.DoesNotExist:
            receiver_photo = ""

        thread_data = {
            'id': self.id,
            'sender': self.sender.get_full_name(),
            'sender_id': self.sender.id,
            'sender_photo': sender_photo,
            'receiver': self.receiver.get_full_name(),
            'receiver_id': self.receiver.id,
            'receiver_photo': receiver_photo,
            'item_photo': "" if not self.transaction.item1.photo else self.transaction.item1.photo.url,
            'latest_message': {} if not all_messages else all_messages.latest('date_sent').to_dict(),
            'date_modified': self.date_modified,
        }

        if detailed:
            """
            Additional key-value pair(s) specifically for the Message Thread (Conversation) page
            """

            is_approved = self.transaction.is_approved

            thread_data.update({'messages': [message.to_dict() for message in all_messages]})
            thread_data.update({'status': is_approved if is_approved != None else False})
            thread_data.update({'item_1': {
                'name': self.transaction.item1.name,
                'owner': self.transaction.item1.name,
                'photo': "" if not self.transaction.item1.photo else self.transaction.item1.photo.url,
                'is_available': self.transaction.item1.is_available}
            })
            thread_data.update({'item_2': {
                'name': self.transaction.item2.name,
                'owner': self.transaction.item2.name,
                'photo': "" if not self.transaction.item2.photo else self.transaction.item2.photo.url,
                'is_available': self.transaction.item2.is_available}
            })

        return thread_data


class Message(models.Model):
    """
    The Message model includes the specific message entry from each thread
    """

    thread = models.ForeignKey('message.Thread', related_name='messages')
    sender = models.ForeignKey(User, related_name='message_sender')
    receiver = models.ForeignKey(User, related_name='message_receiver')
    text = models.CharField(max_length=500)
    date_sent = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __unicode__(self):
        return "From {} to {} [{}]".format(self.sender, self.receiver, self.date_sent)

    class Meta(object):
        ordering = ['date_sent']
        verbose_name = _('Message Entry')
        verbose_name_plural = _('Message Entries')

    def to_dict(self):
        try:
            profile = self.sender.profile
            sender_photo = "" if not profile.photo else profile.photo.url
        except UserProfile.DoesNotExist:
            sender_photo = ""

        return {
            'text': self.text,
            'sender': self.sender.get_full_name(),
            'sender_id': self.sender.id,
            'sender_photo': sender_photo,
            'is_read': self.is_read,
            'date_sent': self.date_sent
        }
