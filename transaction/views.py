from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q

from oauth2_provider.models import AccessToken
from push_notifications.models import APNSDevice
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import Item
from message.models import Thread
from swapp_api.authentication import BasicAuthentication
from swapp_api.permissions import IsAuthenticated
from swapp_api.predictionio_api import PIOEvent, train_system
from swapp_api.utils import send_push_notification
from transaction.models import Notification, Transaction
from transaction.serializers import TransactionSerializer


# Notification
class NotificationList(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            token = AccessToken.objects.get(token=kwargs.get('identifier'))
            user = token.user

            sorted_notifications = sorted(
                [notif.to_dict() for notif in user.notifications_received.all()],
                key=lambda n: n['date'],
                reverse=True
            )
            notifications_data = {'notifications': sorted_notifications}

            return Response(notifications_data, status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


class NotificationView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            notif = Notification.objects.get(id=kwargs.get('pk'))
            notif.is_read = True
            notif.save()

            return Response(None, status.HTTP_200_OK)
        except Exception as e:
            return Response("Error: {}".format(e), status.HTTP_400_BAD_REQUEST)


class NotificationDetail(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = identifier.split(' ')[1] if identifier else request.GET.get('identifier')
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            try:
                notification = Notification.objects.get(id=int(kwargs.get('pk')))
                notification_data = {
                    'notification': notification.to_dict(),
                    'item': notification.transaction.item1.to_dict()
                }

                return Response(notification_data, status=status.HTTP_200_OK)
            except Notification.DoesNotExist:
                return Response("Notification does not exist", status=status.HTTP_400_BAD_REQUEST)
        except AccessToken.DoesNotExist:
            return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)


class NotificationAction(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        POST request to create a new Notification instances relative to user action with regards to
        the Swap offer, and deletes the previous Transaction notification
        """

        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = identifier.split(' ')[1] if identifier else request.GET.get('identifier')
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            data = request.DATA
            action = data.get('action')
            thread_id = data.get('thread_id')
            notification_id = data.get('notification_id')

            thread = None
            offer_accepted = action == "accept"

            if not notification_id and not thread_id:
                return Response("There is an error in your request", status=status.HTTP_400_BAD_REQUEST)
            else:
                # Check if transaction was responded through the Notifications page or the Thread page
                if notification_id:
                    notification = Notification.objects.get(id=int(notification_id))
                else:
                    thread = Thread.objects.get(id=int(thread_id))
                    notification = thread.transaction.notification.filter(type="offer")[0]

                # Check if one or both two items are already subject to a pending transaction,
                # or under a transaction that is already approved
                if (notification.transaction.is_valid and offer_accepted):
                    return Response({"items_not_available": True}, status=status.HTTP_400_BAD_REQUEST)

                # Create new notification regarding the action selected
                new_notification = Notification.objects.create(
                    action_from=user,
                    recipient=notification.action_from,
                    type=action,
                    transaction=notification.transaction,
                    notification="{} your offer".format("accepted" if offer_accepted else "rejected")
                )

                # Approve/Reject transaction
                notification.transaction.is_approved = True if offer_accepted else False
                notification.transaction.date_approved = datetime.now()
                notification.transaction.save()

                # Sets availability of the two items to false
                if offer_accepted:
                    notification.transaction.item1.is_available = False
                    notification.transaction.item2.is_available = False
                    notification.transaction.item1.save()
                    notification.transaction.item2.save()

                # Get thread of current transaction
                thread = thread if thread else notification.transaction.thread

                # Send push notification regarding user action
                send_push_notification(
                    user=new_notification.recipient,
                    notification=new_notification.__unicode__(),
                    type="offer_{}".format(action),
                    obj_id=(thread.id if thread else None) if offer_accepted else None,
                    badge_count=(Transaction.get_pending_user_transactions(new_notification.recipient)
                                            .count())
                )

                # Delete current notification associated to action
                notification.delete()

                # If offer is rejected, deletes the associated thread
                if not offer_accepted:
                    notification.transaction.thread.delete()

                return Response("Success", status=status.HTTP_200_OK)
        except AccessToken.DoesNotExist:
            return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)


# Transaction
class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionDetail(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        POST request to create a Transaction object
        """

        try:
            identifier = kwargs.get('identifier')
            token = AccessToken.objects.get(token=identifier)
            user = token.user
            pio = PIOEvent()
            is_new_transaction = False

            # Retrieve Item instances
            transaction_data = request.DATA

            user_item = Item.objects.get(id=int(transaction_data.get('user_item_id')))
            to_swapp_item = Item.objects.get(id=int(transaction_data.get('other_item_id')))

            # Checks first if two items are already in a pending transaction
            try:
                existing_transaction = Transaction.objects.get(item1=user_item, item2=to_swapp_item)
            except Transaction.DoesNotExist:
                try:
                    existing_transaction = Transaction.objects.get(item1=to_swapp_item, item2=user_item)
                except Transaction.DoesNotExist:
                    is_new_transaction = True

            if is_new_transaction:
                transaction = Transaction.objects.create(item1=user_item, item2=to_swapp_item)

                pio.buy_item(user, to_swapp_item)

                if transaction:
                    recipient = User.objects.get(id=int(transaction_data.get('action_from_id')))
                    action_from = user

                    # Create corresponding Notification for the Transaction
                    notification = Notification.objects.create(
                        recipient=recipient,
                        action_from=action_from,
                        transaction=transaction
                    )

                    # Create corresponding Thread for the Transaction
                    thread = Thread.objects.create(
                        sender=transaction.item1.owner,
                        receiver=transaction.item2.owner,
                        transaction=transaction
                    )

                    # Send notification to APNS
                    send_push_notification(
                        user=recipient,
                        notification="{} was offered to be swapped for your {}.".format(user_item, to_swapp_item.name),
                        type="notification",
                        obj_id=notification.id
                    )

                    train_system()

                    return Response({'pending_transactions': Transaction.get_pending_user_transactions(user, detailed=True)},
                                    status=status.HTTP_200_OK)
                else:
                    return Response("Transaction failed", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'is_new_transaction': is_new_transaction}, status=status.HTTP_400_BAD_REQUEST)
        except AccessToken.DoesNotExist:
            return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)


class SwappingHistory(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Returns the list of all transactions of current user
        """

        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = identifier.split(' ')[1] if identifier else request.GET.get('identifier')
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            # Retrieve associated transactions to user
            user_transactions = Transaction.get_approved_user_transactions(user)
            swapping_history = {'history': [transaction.to_dict() for transaction in user_transactions]}

            return Response(swapping_history, status=status.HTTP_200_OK)
        except AccessToken.DoesNotExist:
            return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)
