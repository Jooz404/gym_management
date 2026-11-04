from django.test import TestCase, Client, override_settings
from django.urls import reverse
from accounts.models import User


class CoreViewsAndFeatureFlagsTest(TestCase):
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

    def test_context_processors_present_on_dashboard(self):
        self.client.login(username='ownertest', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('gym_name', response.context)
        self.assertEqual(response.context['gym_name'], 'Flex Gym Bitung')
        self.assertIn('feature_checkin', response.context)
        self.assertIn('feature_reports', response.context)
        self.assertIn('feature_wa_reminder', response.context)

    @override_settings(FEATURE_CHECKIN=True)
    def test_feature_checkin_allowed_when_flag_enabled(self):
        self.client.login(username='stafftest', password='password123')
        response = self.client.get(reverse('feature_checkin_test'))
        self.assertEqual(response.status_code, 200)

    @override_settings(FEATURE_CHECKIN=False)
    def test_feature_checkin_forbidden_when_flag_disabled(self):
        self.client.login(username='stafftest', password='password123')
        response = self.client.get(reverse('feature_checkin_test'))
        self.assertEqual(response.status_code, 403)

    @override_settings(FEATURE_REPORTS=True)
    def test_owner_can_access_reports_but_staff_forbidden(self):
        # Owner bisa akses
        self.client.login(username='ownertest', password='password123')
        resp_owner = self.client.get(reverse('feature_reports_test'))
        self.assertEqual(resp_owner.status_code, 200)
        self.client.logout()

        # Staff ditolak (403)
        self.client.login(username='stafftest', password='password123')
        resp_staff = self.client.get(reverse('feature_reports_test'))
        self.assertEqual(resp_staff.status_code, 403)
