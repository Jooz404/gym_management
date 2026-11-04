from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class AccountsModelAndAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='ownertest',
            password='password123',
            name='Test Owner',
            role=User.Role.OWNER
        )
        self.staff = User.objects.create_user(
            username='stafftest',
            password='password123',
            name='Test Staff',
            role=User.Role.STAFF
        )

    def test_user_roles(self):
        self.assertTrue(self.owner.is_owner)
        self.assertFalse(self.owner.is_staff_role)
        self.assertFalse(self.staff.is_owner)
        self.assertTrue(self.staff.is_staff_role)
        self.assertEqual(str(self.owner), "Test Owner (Pemilik (Owner))")

    def test_login_redirect_for_anonymous_user(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_login_success_and_logout(self):
        # Login dengan staff
        login_resp = self.client.post(reverse('login'), {
            'username': 'stafftest',
            'password': 'password123',
        }, follow=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertTrue(login_resp.context['user'].is_authenticated)
        self.assertEqual(login_resp.context['user'].username, 'stafftest')

        # Logout
        logout_resp = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertFalse(logout_resp.context['user'].is_authenticated)
