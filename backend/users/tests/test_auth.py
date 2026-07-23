from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import DeletedUserEmail, User


class TestAuth(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "alanturing@aol.com",
            "username": "alan",
            "password": "youcan'thackme!123",
            "user_type": "Costumer",
        }
        self.client.post(reverse("users:signup"), data=self.user_data)
        self.client.logout()

    def test_login_success(self):
        """This test checks the /login and /me endpoints"""
        response_login = self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        })
        response_me = self.client.get(reverse("users:me"))
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertEqual(response_me.status_code, status.HTTP_200_OK)

    def test_login_wrong_password_fail(self):
        """In this test the login should fail, because of password"""
        response_login = self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": "wrongpassword1234!",
        })
        response_me = self.client.get(reverse("users:me"))
        self.assertEqual(response_login.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_me.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_returns_tokens(self):
        """Login should return access and refresh tokens"""
        response = self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh_success(self):
        """Refresh an access token using a valid refresh token"""
        login_response = self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        })
        refresh = login_response.data["refresh"]

        response = self.client.post(
            reverse("users:token_refresh"), {"refresh": refresh}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_bad_token_fail(self):
        """Refreshing with an invalid token should return 401"""
        response = self.client.post(
            reverse("users:token_refresh"), {"refresh": "not-a-real-token"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh(self):
        """After logout, the refresh token should be blacklisted"""
        login_response = self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        })
        refresh = login_response.data["refresh"]

        self.client.post(
            reverse("users:logout"), {"refresh": refresh}
        )

        # Trying to refresh with the blacklisted token should fail
        response = self.client.post(
            reverse("users:token_refresh"), {"refresh": refresh}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_fail(self):
        """Trying to access /me endpoint without authorizing"""
        response = self.client.get(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_account_delete_fail(self):
        """Trying to delete the account with wrong password"""
        self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        })
        response = self.client.delete(reverse("users:me"), {
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_delete_success(self):
        """Trying to delete the account with right password"""
        self.client.post(reverse("users:login"), {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        })
        # Mark as verified so the signal creates a DeletedUserEmail record
        User.objects.filter(email=self.user_data["email"]).update(is_verified=True)
        response = self.client.delete(reverse("users:me"), {
            "password": self.user_data["password"],
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(DeletedUserEmail.objects.filter(email=self.user_data["email"]).exists())
