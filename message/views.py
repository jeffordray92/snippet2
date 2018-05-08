from oauth2_provider.models import AccessToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from message.models import Message, Thread
from message.serializers import MessageSerializer, ThreadSerializer
from swapp_api.authentication import BasicAuthentication
from swapp_api.permissions import IsAuthenticated
from swapp_api.utils import send_push_notification
from transaction.models import Transaction
from user_profile.models import UserProfile


# Message
class MessageList(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# Thread
class ThreadList(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            identifier = kwargs.get('identifier')
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            try:
                profile = user.profile
                user_photo = "" if not profile.photo else profile.photo.url
            except UserProfile.DoesNotExist:
                user_photo = ""

            threads_received = user.thread_receiver.all()
            threads_initiated = user.thread_sender.all()

            all_threads = threads_received | threads_initiated
            sorted_threads = sorted(
                [thread.to_dict() for thread in all_threads],
                key=lambda t: t['date_modified'],
                reverse=True
            )

            threads_data = {
                'threads': [thread for thread in sorted_threads],
                'current_user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'photo': user_photo
                }
            }

            return Response(threads_data, status=status.HTTP_200_OK)
        except AccessToken.DoesNotExist:
            return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)


class ThreadDetail(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        try:
            thread = Thread.objects.get(id=int(kwargs.get('pk')))

            try:
                identifier = request.META.get('HTTP_AUTHORIZATION')
                identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
                token = AccessToken.objects.get(token=identifier)
                user = token.user

                # Set all Thread message's `is_read` attribute to True
                for message in thread.messages.all():
                    message.is_read = True if user == message.receiver else False
                    message.save()

                try:
                    profile = user.profile
                    user_photo = "" if not profile.photo else profile.photo.url
                except UserProfile.DoesNotExist:
                    user_photo = ""

                thread_data = {
                    'transaction_is_valid': thread.transaction.is_valid,
                    'thread': thread.to_dict(detailed=True),
                    'current_user': {
                        'id': user.id,
                        'name': user.get_full_name(),
                        'photo': user_photo
                    }
                }

                return Response(thread_data, status=status.HTTP_200_OK)
            except AccessToken.DoesNotExist:
                return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)
        except Thread.DoesNotExist:
            return Response("Thread does not exist", status=status.HTTP_400_BAD_REQUEST)


class ThreadCreate(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        data = request.DATA

        try:
            identifier = request.META.get('HTTP_AUTHORIZATION')
            identifier = request.GET.get('identifier') if not identifier else identifier.split(' ')[1]
            token = AccessToken.objects.get(token=identifier)
            user = token.user

            transaction = Transaction.objects.get(id=int(data.get('transaction_id')))

            try:
                profile = user.profile
                user_photo = "" if not profile.photo else profile.photo.url
            except UserProfile.DoesNotExist:
                user_photo = ""

            thread, created = Thread.objects.get_or_create(
                sender=transaction.item1.owner,
                receiver=transaction.item2.owner,
                transaction=transaction
            )

            if thread:
                thread_data = {
                    'thread': thread.to_dict(),
                    'current_user': {
                        'id': user.id,
                        'name': user.get_full_name(),
                        'photo': user_photo
                    }
                }

                return Response(thread_data, status=status.HTTP_201_CREATED)
            else:
                return Response("There is an error in your request", status=status.HTTP_400_BAD_REQUEST)
        except AccessToken.DoesNotExist:
            return Response("Access Token is invalid", status=status.HTTP_400_BAD_REQUEST)


class SendMessage(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        data = request.DATA

        serializer = MessageSerializer(data=data)

        if serializer.is_valid():
            message = serializer.save()
            sender = message.sender.first_name if message.sender.first_name else message.sender.username

            # Send notification to APNS
            send_push_notification(
                user=message.receiver,
                notification="From {}: {}".format(sender, message.text),
                type="message",
                obj_id=message.thread.id
            )

            return Response(message.to_dict(), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
