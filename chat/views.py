from datetime import datetime, timedelta
import pytz

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt import authentication
from django.contrib.auth.admin import User

from .models import Message, Chat
from .serializers import MessageSerializer, ChatSerializer
from .pagination import StandardPagination


class ChatView(ModelViewSet):
    authentication_classes = (authentication.JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer
    pagination_class = StandardPagination
    queryset = Chat.objects.all()

    def create(self, request, *args, **kwargs):
        participants_name = request.data.getlist('participants')

        if participants_name is None:
            return Response({'error': 'participants is required to create new chat'},
                            status.HTTP_400_BAD_REQUEST)

        if request.data.get('is_private') is None:
            return Response({'error': 'is_private is required'}, status.HTTP_400_BAD_REQUEST)

        if len(participants_name) == 0:
            return Response({'error': 'at least one participant except you is required'},
                            status.HTTP_400_BAD_REQUEST)

        if request.user.username in participants_name:
            return Response({'error': "you cant't add yourself to the chat"},
                            status.HTTP_400_BAD_REQUEST)

        participants_name.append(request.user.username)
        is_private = request.data.get('is_private') == 'True'

        if len(participants_name) > 2 and is_private:
            return Response({'error': "you can't add more that 1 user to the private chat"},
                            status.HTTP_400_BAD_REQUEST)

        participants = User.objects.filter(username__in=participants_name)

        chat = Chat.objects.create(
            is_private=request.data.get('is_private')
        )
        chat.participants.set(participants)
        chat.save()

        return Response({'result': 'chat successfully created'}, status.HTTP_201_CREATED)


class MessageView(ModelViewSet):
    authentication_classes = (authentication.JSONWebTokenAuthentication, )
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def list(self, request, *args, **kwargs):
        chat = Chat.objects.get(id=kwargs['pk'])
        messages = chat.messages

        if not chat.participants.filter(id=request.user.id).exists():
            return Response({'error': "you can't see messages in chat if you are not participants"},
                            status.HTTP_403_FORBIDDEN)

        serialized = MessageSerializer(messages, many=True)
        return Response(serialized.data)

    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        chat_id = request.data.get('chat_id')

        if text is None or chat_id is None:
            return Response({'error': 'chat_id and text are required'},
                            status.HTTP_400_BAD_REQUEST)

        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'chat with such id does not exist'},
                            status.HTTP_400_BAD_REQUEST)

        if not chat.participants.filter(id=request.user.id).exists():
            Response({'error': "You can't send messages to chats where are you not participate"},
                     status.HTTP_403_FORBIDDEN)

        Message(
            text=text,
            sender=request.user,
            chat_id=chat_id
        ).save()

        return Response({'status': 'messages has been sent'}, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        message = Message.objects.get(id=pk)

        if request.data.get('text') is None:
            return Response({'error': 'text is required'},
                            status.HTTP_400_BAD_REQUEST)

        # user can edit only own messages
        if request.user.id != message.sender.id:
            return Response({'error': "You can edit only own messages"},
                            status.HTTP_403_FORBIDDEN)

        # can't edit messages older than 30 minutes
        if (datetime.now().astimezone(pytz.utc)) \
                - message.time > timedelta(minutes=30):
            return Response({'error': "You can't edit messages older than 30 minutes"},
                            status.HTTP_403_FORBIDDEN)

        message.is_edited = True
        message.text = request.data.get('text')
        serializer = self.serializer_class(message,
                                           data=request.data,
                                           partial=True)
        serializer.is_valid()
        serializer.save()

        return Response(serializer.data, status.HTTP_202_ACCEPTED)


class ChatParticipantsView(APIView):
    authentication_classes = (authentication.JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        chat_id = kwargs['pk']
        chat = Chat.objects.get(id=chat_id)

        if chat.is_private:
            return Response({'error': "This chat is private"},
                            status.HTTP_403_FORBIDDEN)

        if not chat.participants.filter(id=request.user.id).exists():
            return Response({'error': "You can't add user to chat if "
                                      "you are not in this chat"},
                            status.HTTP_403_FORBIDDEN)

        try:
            new_participant = User.objects.get(id=request.data.get('user_id'))
        except User.DoesNotExist:
            return Response({'error': 'user with such id does not exist'}, status.HTTP_400_BAD_REQUEST)

        if chat.participants.filter(id=new_participant.id).exists():
            return Response({'error': 'user is already in this chat'},
                            status.HTTP_400_BAD_REQUEST)

        chat.participants.add(new_participant)

        return Response({'result': 'user was added to this chat'}, status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        chat_id = kwargs['pk']
        chat = Chat.objects.get(id=chat_id)

        if request.data.get('user_id') is None:
            return Response({'error': 'user_id is required'}, status.HTTP_400_BAD_REQUEST)

        if not chat.participants.filter(id=request.user.id).exists():
            return Response({'error': "You can't remove user from chat"
                                      " if you are not in this chat"},
                            status.HTTP_403_FORBIDDEN)

        try:
            new_participant = User.objects.get(id=request.data.get('user_id'))
        except User.DoesNotExist:
            return Response({'error': 'user with such id does not exist'}, status.HTTP_400_BAD_REQUEST)

        if not chat.participants.filter(id=request.data.get('user_id')).exists():
            return Response({'error': 'user is not in this chat'},
                            status.HTTP_400_BAD_REQUEST)

        chat.participants.remove(new_participant)

        return Response({'result': 'user was deleted from this chat'}, status.HTTP_200_OK)

