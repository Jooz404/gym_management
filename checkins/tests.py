from datetime import timedelta
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from members.models import Member
from packages.models import Package
from memberships.models import Membership, Payment
from checkins.models import Checkin


class CheckinViewsAndLogicTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='staff_checkin',
            password='password123',
            name='Kasir Frontdesk',
            role=User.Role.STAFF
        )
        self.client.login(username='staff_checkin', password='password123')

        self.pkg = Package.objects.create(
            name='Paket Bulanan 30 Hari',
            duration_days=30,
            price=300000,
            is_active=True
        )

        today = timezone.localdate()

        # 1. Member Aktif
        self.active_member = Member.objects.create(
            member_code='FLX-AKTIF1',
            full_name='Member Aktif Budi',
            phone_wa='081234567801'
        )
        Membership.objects.create(
            member=self.active_member,
            package=self.pkg,
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=25),
            created_by=self.staff
        )

        # 2. Member Kedaluwarsa (Expired)
        self.expired_member = Member.objects.create(
            member_code='FLX-HABIS1',
            full_name='Member Habis Siti',
            phone_wa='081234567802'
        )
        Membership.objects.create(
            member=self.expired_member,
            package=self.pkg,
            start_date=today - timedelta(days=40),
            end_date=today - timedelta(days=10),
            created_by=self.staff
        )

        # 3. Member Belum Ada Paket
        self.nopkg_member = Member.objects.create(
            member_code='FLX-BARU1',
            full_name='Member Baru Tanpa Paket',
            phone_wa='081234567803'
        )

        # 4. Member Dinonaktifkan / Diblokir (walau punya paket aktif)
        self.blocked_member = Member.objects.create(
            member_code='FLX-BLOKIR1',
            full_name='Member Diblokir Anton',
            phone_wa='081234567804',
            is_active=False
        )
        Membership.objects.create(
            member=self.blocked_member,
            package=self.pkg,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=28),
            created_by=self.staff
        )

    def test_checkin_page_get(self):
        resp = self.client.get(reverse('checkin_page'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Check-in Kehadiran Member')

    def test_checkin_active_member_allowed(self):
        resp = self.client.post(reverse('checkin_page'), {
            'member_code': 'FLX-AKTIF1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'CHECK-IN BERHASIL (MEMBER AKTIF)')
        self.assertContains(resp, 'Member Aktif Budi')

        # Cek database
        checkin = Checkin.objects.filter(member=self.active_member).first()
        self.assertIsNotNone(checkin)
        self.assertEqual(checkin.result, Checkin.Result.ALLOWED)
        self.assertTrue(checkin.is_allowed)
        self.assertEqual(checkin.recorded_by, self.staff)

    def test_checkin_expired_member_warning_d008(self):
        resp = self.client.post(reverse('checkin_page'), {
            'member_code': 'flx-habis1', # uji case insensitive
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PERINGATAN: MASA AKTIF KEDALUWARSA')
        self.assertContains(resp, 'Member Habis Siti')
        self.assertContains(resp, reverse('membership_create', args=[self.expired_member.pk]))

        # Cek database
        checkin = Checkin.objects.filter(member=self.expired_member).first()
        self.assertIsNotNone(checkin)
        self.assertEqual(checkin.result, Checkin.Result.EXPIRED_WARNING)
        self.assertTrue(checkin.is_warning)

    def test_checkin_nopkg_member_warning(self):
        resp = self.client.post(reverse('checkin_page'), {
            'member_code': 'FLX-BARU1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PERINGATAN: MASA AKTIF KEDALUWARSA')

        checkin = Checkin.objects.filter(member=self.nopkg_member).first()
        self.assertIsNotNone(checkin)
        self.assertEqual(checkin.result, Checkin.Result.EXPIRED_WARNING)

    def test_checkin_inactive_member_blocked(self):
        # Member nonaktif/diblokir harus DITOLAK walau masa berlaku paket masih panjang
        resp = self.client.post(reverse('checkin_page'), {
            'member_code': 'FLX-BLOKIR1',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'AKSES DITOLAK: AKUN NONAKTIF / DIBLOKIR')
        self.assertContains(resp, 'Member Diblokir Anton')

        # Cek database
        checkin = Checkin.objects.filter(member=self.blocked_member).first()
        self.assertIsNotNone(checkin)
        self.assertEqual(checkin.result, Checkin.Result.BLOCKED)
        self.assertTrue(checkin.is_blocked)
        self.assertFalse(checkin.is_allowed)

    def test_checkin_unknown_code(self):
        resp = self.client.post(reverse('checkin_page'), {
            'member_code': 'KODE-PALSU-999',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'KODE TIDAK DITEMUKAN')
        self.assertEqual(Checkin.objects.count(), 0)

    @override_settings(FEATURE_CHECKIN=False)
    def test_checkin_forbidden_when_flag_disabled_d012(self):
        resp = self.client.get(reverse('checkin_page'))
        self.assertEqual(resp.status_code, 403)
