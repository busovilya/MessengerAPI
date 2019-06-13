from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.admin import User


class GetUsersTest(APITestCase):
    def setUp(self) -> None:
        User.objects.create_user(username='User1', password='testpass1234')
        User.objects.create_user(username='User2', email='test@email.com')
        User.objects.create_user(username='User3')

        response = self.client.post(reverse('obtain-token'),
                                    data={'username': 'User1',
                                          'password': 'testpass1234'},
                                    headers={'Content-Type': 'application/json'})
        jwt_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(jwt_token))

    def test_get_users(self):
        url = reverse('users')
        response = self.client.get(url)
        json_response_expected = [
            {
                'username': 'User1',
                'email': ''
            },
            {
                'username': 'User2',
                'email': 'test@email.com'
            },
            {
                'username': 'User3',
                'email': ''
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, json_response_expected)


class UserRegistrationTest(APITestCase):
    def test_create_user(self):
        url = reverse('registration')
        data = {
            'username': 'TestUser',
            'password': 'iamtest1234',
            'email': 'test@gmail.com'
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username='TestUser')
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'TestUser')
        self.assertEqual(user.email, 'test@gmail.com')

    def test_create_user_without_username(self):
        url = reverse('registration')
        data = {
            'password': 'iamtest1234'
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password(self):
        url = reverse('registration')
        data = {
            'username': 'IamTestUser'
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_existed_user(self):
        User.objects.create_user(username='TestUser', password='testpassword1234')

        url = reverse('registration')
        data = {
            'username': 'TestUser',
            'password': 'testtest12341234'
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
