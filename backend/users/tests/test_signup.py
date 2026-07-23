from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestSignup(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "user_type": "Costumer",
        }

    def test_signup_success(self):
        """This test checks two things:
            1. If the signup returns the correct status code
            2. If the user is authenticated after signup, by checking the /me endpoint
        """
        response_signup = self.client.post(reverse("users:signup"), data=self.user_data)
        response_me = self.client.get(reverse("users:me"))
        self.assertEqual(response_signup.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_me.status_code, status.HTTP_200_OK)

    def test_singup_duplicate_email_fail(self):
        """This test checks if the signup fails and sends 400 HTTP status code
            after trying to signup with an email that already exists in the database."""
        self.client.post(reverse("users:signup"), data=self.user_data)
        self.client.logout()
        response = self.client.post(reverse("users:signup"), {
            "email": self.user_data["email"],
            "username": "anotheruser",
            "password": "anotherpassword123",
            "user_type": "Costumer",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_singup_duplicate_username_fail(self):
        """This test checks if the signup fails and sends 400 HTTP status code
            after trying to signup with a username that already exists in the database."""
        self.client.post(reverse("users:signup"), data=self.user_data)
        self.client.logout()
        response = self.client.post(reverse("users:signup"), {
            "email": "anotheremail@example.com",
            "username": self.user_data["username"],
            "password": "anotherpassword123",
            "user_type": "Costumer",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_forbidden_username_fail(self):
        """This test checks if the signup fails and sends 400 HTTP status code
            after trying to signup with a username that is forbidden."""
        response = self.client.post(
            reverse("users:signup"),
            data={**self.user_data, "username": "profile"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_invalid_username_fail(self):
        """This test tests username validation.
        In this project username can only contain lowercase letters and underscores"""
        response = self.client.post(
            reverse("users:signup"),
            data={**self.user_data, "username": "Alan1234"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
