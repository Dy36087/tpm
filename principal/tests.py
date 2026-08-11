from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginRedirectTests(TestCase):
    def test_login_redirects_to_home_when_no_next_is_given(self):
        user = get_user_model().objects.create_user(
            username="testuser", password="secret123"
        )

        response = self.client.post(
            reverse("login"),
            {"username": user.username, "password": "secret123"},
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
