from datetime import timedelta
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from members.models import Member
from packages.models import Package
from memberships.models import Membership, Payment
from checkins.models import Checkin


class CoreViewsAndDashboardTest(TestCase):
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

        self.pkg = Package.objects.create(
            name='Paket Bulanan 30 Hari',
            duration_days=30,
            price=300000,
            is_active=True
        )

        today = timezone.localdate()

        # 1. Member Aktif Aman (sisa 20 hari)
        self.m_active = Member.objects.create(
            member_code='FLX-DASH1',
            full_name='Member Aktif',
            phone_wa='081200000001'
        )
        self.ms_active = Membership.objects.create(
            member=self.m_active,
            package=self.pkg,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=20),
            created_by=self.staff
        )
        Payment.objects.create(
            membership=self.ms_active,
            amount=300000,
            method=Payment.Method.CASH,
            status=Payment.Status.VERIFIED,
            verified_by=self.staff,
            paid_at=timezone.now()
        )

        # 2. Member Akan Habis (sisa 3 hari)
        self.m_expiring = Member.objects.create(
            member_code='FLX-DASH2',
            full_name='Member Mau Habis',
            phone_wa='081200000002'
        )
        self.ms_expiring = Membership.objects.create(
            member=self.m_expiring,
            package=self.pkg,
            start_date=today - timedelta(days=27),
            end_date=today + timedelta(days=3),
            created_by=self.staff
        )
        Payment.objects.create(
            membership=self.ms_expiring,
            amount=300000,
            method=Payment.Method.TRANSFER,
            status=Payment.Status.VERIFIED,
            verified_by=self.staff,
            paid_at=timezone.now()
        )

        # 3. Member Kedaluwarsa (habis 5 hari lalu)
        self.m_expired = Member.objects.create(
            member_code='FLX-DASH3',
            full_name='Member Sudah Habis',
            phone_wa='081200000003'
        )
        Membership.objects.create(
            member=self.m_expired,
            package=self.pkg,
            start_date=today - timedelta(days=35),
            end_date=today - timedelta(days=5),
            created_by=self.staff
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

    def test_dashboard_metrics_calculation(self):
        self.client.login(username='ownertest', password='password123')
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['total_members'], 3)
        self.assertEqual(resp.context['active_count'], 2) # m_active dan m_expiring
        self.assertEqual(resp.context['expiring_count'], 1) # m_expiring
        self.assertEqual(resp.context['expired_count'], 1) # m_expired
        self.assertEqual(resp.context['today_income'], 600000)

    def test_wa_reminders_page(self):
        self.client.login(username='stafftest', password='password123')
        resp = self.client.get(reverse('wa_reminders'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Member Mau Habis')
        self.assertContains(resp, 'Member Sudah Habis')
        self.assertContains(resp, 'https://wa.me/6281200000002')

    @override_settings(FEATURE_WA_REMINDER=False)
    def test_wa_reminders_forbidden_when_flag_disabled(self):
        self.client.login(username='stafftest', password='password123')
        resp = self.client.get(reverse('wa_reminders'))
        self.assertEqual(resp.status_code, 403)

    def test_reports_view_accessible_by_owner_forbidden_to_staff(self):
        # Staf dilarang mengakses laporan
        self.client.login(username='stafftest', password='password123')
        resp_staff = self.client.get(reverse('reports_view'))
        self.assertEqual(resp_staff.status_code, 403)
        self.client.logout()

        # Owner berhasil mengakses laporan
        self.client.login(username='ownertest', password='password123')
        resp_owner = self.client.get(reverse('reports_view'))
        self.assertEqual(resp_owner.status_code, 200)
        self.assertContains(resp_owner, 'Laporan Keuangan & Omzet')
        self.assertContains(resp_owner, 'Rp600.000')

    @override_settings(FEATURE_REPORTS=False)
    def test_reports_forbidden_when_flag_disabled(self):
        self.client.login(username='ownertest', password='password123')
        resp = self.client.get(reverse('reports_view'))
        self.assertEqual(resp.status_code, 403)

    def test_backup_database_accessible_by_owner_forbidden_to_staff(self):
        # Staf dilarang backup db
        self.client.login(username='stafftest', password='password123')
        resp_staff = self.client.get(reverse('backup_database'))
        self.assertEqual(resp_staff.status_code, 403)
        self.client.logout()

        # Owner berhasil mengunduh file sqlite
        self.client.login(username='ownertest', password='password123')
        resp_owner = self.client.get(reverse('backup_database'))
        self.assertEqual(resp_owner.status_code, 200)
        self.assertTrue(resp_owner.has_header('Content-Disposition'))
        self.assertIn('.sqlite3', resp_owner['Content-Disposition'])
