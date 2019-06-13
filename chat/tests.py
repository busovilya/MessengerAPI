from datetime import datetime

import pytz
from django.urls import reverse
from django.contrib.auth.admin import User
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Chat, Message
from .serializers import MessageSerializer


class GetChatTest(APITestCase):
    def setUp(self):
        User.objects.create_user(username='User1', password='testpass1234')
        User.objects.create_user(username='User2', password='testpass1234')
        User.objects.create_user(username='User3', password='testpass1234')

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

        chat1 = Chat.objects.create(is_private=True)
        chat1.participants.set((User.objects.get(username='User1'),
                                User.objects.get(username='User2')))

        chat2 = Chat.objects.create(is_private=False)
        chat2.participants.set((User.objects.get(username='User1'),
                                User.objects.get(username='User2'),
                                User.objects.get(username='User3')))

    def test_get_all_chats_successful(self):
        expected = [{
            'participants': [{
                'username': user.username,
                'email': user.email
            } for user in chat.participants.all()],
            'is_private': chat.is_private
        } for chat in Chat.objects.all()]

        url = reverse('chats-view')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'], expected)

    def test_get_chat_successful(self):
        chat = Chat.objects.get(is_private=False)
        expected = {
            'participants': [{
                'username': user.username,
                'email': user.email
            } for user in chat.participants.all()],
            'is_private': chat.is_private
        }

        url = reverse('get-chat-view', kwargs={'pk': chat.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)


class CreateChatTest(APITestCase):
    def setUp(self):
        User.objects.create_user(username='User1', password='testpass1234')
        User.objects.create_user(username='User2', password='testpass1234')
        User.objects.create_user(username='User3', password='testpass1234')

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_create_non_private_chat_successful(self):
        url = reverse('chats-view')
        data = {
            'participants': [user.username for user in User.objects.all().exclude(username='User1')],
            'is_private': False
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEquals(list(Chat.objects.get(id=1).participants.all()),
                          list(User.objects.all()))

    def test_create_private_chat_multiple_users_fail(self):
        url = reverse('chats-view')
        data = {
            'participants': [user.username for user in User.objects.all().exclude(username='User1')],
            'is_private': True
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Chat.objects.count(), 0)

    def test_create_chat_with_yourself_fail(self):
        url = reverse('chats-view')
        data = {
            'participants': [user.username for user in User.objects.all()],
            'is_private': True
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Chat.objects.count(), 0)


class AddChatParticipantTest(APITestCase):
    def setUp(self):
        User.objects.create_user(username='User1', password='testpass1234')
        User.objects.create_user(username='User2', password='testpass1234')
        User.objects.create_user(username='User3', password='testpass1234')

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_add_participant_successful(self):
        chat = Chat.objects.create(is_private=False)
        chat.participants.add(User.objects.get(username='User1'))
        chat.participants.add(User.objects.get(username='User2'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 3
        }
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(chat.participants.count(), 3)
        self.assertEquals(list(chat.participants.all()), list(User.objects.all()))

    def test_add_existing_user_fail(self):
        chat = Chat.objects.create(is_private=False)
        chat.participants.add(User.objects.get(username='User1'))
        chat.participants.add(User.objects.get(username='User2'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 2
        }
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(chat.participants.count(), 2)

    def test_add_user_to_private_chat_fail(self):
        chat = Chat.objects.create(is_private=True)
        chat.participants.add(User.objects.get(username='User1'))
        chat.participants.add(User.objects.get(username='User2'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 3
        }
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(chat.participants.count(), 2)


class RemoveChatParticipantView(APITestCase):
    def setUp(self):
        User.objects.create_user(username='User1', password='testpass1234')
        User.objects.create_user(username='User2', password='testpass1234')
        User.objects.create_user(username='User3', password='testpass1234')

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_remove_participant_from_chat_successful(self):
        chat = Chat.objects.create(is_private=False)
        chat.participants.add(User.objects.get(username='User1'))
        chat.participants.add(User.objects.get(username='User2'))
        chat.participants.add(User.objects.get(username='User3'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 3
        }
        response = self.client.delete(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(chat.participants.count(), 2)

    def test_remove_non_existing_participant_from_chat_fail(self):
        chat = Chat.objects.create(is_private=False)
        chat.participants.add(User.objects.get(username='User1'))
        chat.participants.add(User.objects.get(username='User2'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 3
        }
        response = self.client.delete(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['error'], 'user is not in this chat')
        self.assertEquals(chat.participants.count(), 2)

    def test_remove_participant_you_are_not_in_chat_fail(self):
        chat = Chat.objects.create(is_private=False)
        chat.participants.add(User.objects.get(username='User2'))
        chat.participants.add(User.objects.get(username='User3'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 3
        }
        response = self.client.delete(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(response.data['error'], "You can't remove user from chat"
                                                  " if you are not in this chat")
        self.assertEquals(chat.participants.count(), 2)

    def test_remove_participant_user_does_not_exist_fail(self):
        chat = Chat.objects.create(is_private=True)
        chat.participants.add(User.objects.get(username='User1'))
        chat.participants.add(User.objects.get(username='User2'))
        chat.participants.add(User.objects.get(username='User3'))

        url = reverse('chat-participants-view', kwargs={'pk': 1})
        data = {
            'user_id': 4
        }
        response = self.client.delete(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['error'], "user with such id does not exist")
        self.assertEquals(chat.participants.count(), 3)


class GetMessageTest(APITestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='User1', password='testpass1234')
        user2 = User.objects.create_user(username='User2', password='testpass1234')
        user3 = User.objects.create_user(username='User3', password='testpass1234')

        chat = Chat.objects.create(is_private=False)
        chat.participants.add(user1, user2, user3)

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_get_one_message_from_chat_successful(self):
        msg = Message.objects.create(
            text='hello, world!',
            sender_id=1,
            chat_id=1
        )
        serialized = MessageSerializer(msg)

        url = reverse('messages-view', kwargs={'pk': 1})
        response = self.client.get(url)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, serialized.data)

    def test_get_one_message_not_found_fail(self):
        msg = Message.objects.create(
            text='hello, world!',
            sender_id=1,
            chat_id=1
        )

        url = reverse('messages-view', kwargs={'pk': 2})
        response = self.client.get(url)

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateMessageTest(APITestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='User1', password='testpass1234')
        user2 = User.objects.create_user(username='User2', password='testpass1234')
        user3 = User.objects.create_user(username='User3', password='testpass1234')

        chat = Chat.objects.create(is_private=False)
        chat.participants.add(user1, user2, user3)

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_update_message_successful(self):
        msg = Message.objects.create(
            text='hello, world!',
            sender_id=1,
            chat_id=1
        )

        url = reverse('messages-view', kwargs={'pk': 1})

        data = {'text': 'World, Hello!'}
        response = self.client.put(url, data=data)

        msg = Message.objects.get(id=1)
        self.assertEquals(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEquals(msg.text, 'World, Hello!')
        self.assertEquals(msg.chat_id, 1)
        self.assertEquals(msg.sender_id, 1)
        self.assertTrue(msg.is_edited)


class CreateMessageTest(APITestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='User1', password='testpass1234')
        user2 = User.objects.create_user(username='User2', password='testpass1234')
        user3 = User.objects.create_user(username='User3', password='testpass1234')

        chat = Chat.objects.create(is_private=False)
        chat.participants.add(user1, user2, user3)

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_send_message_successful(self):
        url = reverse('create-message-view')
        data = {
            'text': 'Hello, world!',
            'chat_id': 1
        }

        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Chat.objects.get(id=1).messages.count(), 1)
        msg = Message.objects.get(id=1)
        self.assertEquals(msg.text, 'Hello, world!')
        self.assertEquals(msg.sender.username, 'User1')