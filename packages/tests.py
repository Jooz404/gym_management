from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from packages.models import Package


class PackageModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='owner_pkg',
            password='password123',
            role=User.Role.OWNER
        )
        self.staff = User.objects.create_user(
            username='staff_pkg',
            password='password123',
            role=User.Role.STAFF
        )
        self.package = Package.objects.create(
            name='Paket Uji Coba',
            duration_days=30,
            price=300000,
            is_active=True
        )

    def test_package_formatted_price(self):
        self.assertEqual(self.package.formatted_price, "Rp300.000")
        self.assertIn("30 hari", str(self.package))

    def test_package_list_view_accessible_by_staff_and_owner(self):
        # Staf bisa melihat daftar paket
        self.client.login(username='staff_pkg', password='password123')
        resp = self.client.get(reverse('package_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Paket Uji Coba')
        self.client.logout()

        # Owner bisa melihat daftar paket
        self.client.login(username='owner_pkg', password='password123')
        resp = self.client.get(reverse('package_list'))
        self.assertEqual(resp.status_code, 200)

    def test_package_create_restricted_to_owner(self):
        # Staf dilarang menambah paket
        self.client.login(username='staff_pkg', password='password123')
        resp = self.client.post(reverse('package_create'), {
            'name': 'Paket Ilegal Staf',
            'duration_days': 10,
            'price': 50000,
            'is_active': True,
        })
        self.assertEqual(resp.status_code, 403)
        self.client.logout()

        # Owner berhasil menambah paket
        self.client.login(username='owner_pkg', password='password123')
        resp = self.client.post(reverse('package_create'), {
            'name': 'Paket Baru Owner',
            'duration_days': 60,
            'price': 550000,
            'is_active': True,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Package.objects.filter(name='Paket Baru Owner').exists())

    def test_package_toggle_active(self):
        self.client.login(username='owner_pkg', password='password123')
        resp = self.client.post(reverse('package_toggle_active', args=[self.package.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.package.refresh_from_db()
        self.assertFalse(self.package.is_active)
