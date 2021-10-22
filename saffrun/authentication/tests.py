import json

from django.contrib.auth.models import User
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse


class AuthenticationTest(TestCase):
    fixtures = ['authentication_fixture', ]

    def setUp(self) -> None:
        self.client = Client()

    def test_get_method(self) -> None:
        response = self.client.get(path=reverse('auth:login', kwargs={}))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json.loads(response.content), {'detail': 'Method "GET" not allowed.'})

    def test_login_wrong_user(self) -> None:
        response = self.client.post(path=reverse('auth:login'), data={'username': 'username', 'password': 00000000})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), {'detail': 'No active account found with the given credentials'})

    def test_login_user(self) -> None:
        response = self.client.post(path=reverse('auth:login'), data={'username': 'ali', 'password': 'TEST!@#$'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(json.loads(response.content).keys()), ['refresh', 'access'])

    def test_register_user(self) -> None:
        user_count = User.objects.count()
        response = self.client.post(path=reverse('auth:register'), data={'username': 'user1', 'password': 'TEST!@#$'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(json.loads(response.content).keys()), ['username', 'password'])
        self.assertEqual(user_count+1, User.objects.count())
