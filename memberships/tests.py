from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from members.models import Member
from packages.models import Package
from memberships.models import Membership, Payment


class MembershipAndPaymentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='staff_ms',
            password='password123',
            name='Staf Kasir',
            role=User.Role.STAFF
        )
        self.client.login(username='staff_ms', password='password123')

        self.pkg_monthly = Package.objects.create(
            name='Paket Bulanan 30 Hari',
            duration_days=30,
            price=300000,
            is_active=True
        )
        self.member = Member.objects.create(
            member_code='FLX-9999',
            full_name='Member Uji Perpanjangan',
            phone_wa='081234567899'
        )

    def test_new_member_membership_creation(self):
        today = timezone.localdate()
        resp = self.client.post(reverse('membership_create', args=[self.member.pk]), {
            'package': self.pkg_monthly.pk,
            'method': Payment.Method.CASH,
            'amount': 300000,
            'note': 'Pendaftaran pertama',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Cek membership terbuat
        membership = Membership.objects.filter(member=self.member).first()
        self.assertIsNotNone(membership)
        self.assertEqual(membership.start_date, today)
        self.assertEqual(membership.end_date, today + timedelta(days=29))
        self.assertTrue(membership.is_active_now)

        # Cek payment terbuat dan terverifikasi otomatis (D-016)
        payment = Payment.objects.filter(membership=membership).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, 300000)
        self.assertEqual(payment.status, Payment.Status.VERIFIED)
        self.assertEqual(payment.verified_by, self.staff)

    def test_renewal_for_active_member_accumulates_days(self):
        today = timezone.localdate()
        # Buat membership awal yang masih aktif (sisa 10 hari ke depan)
        old_end = today + timedelta(days=10)
        Membership.objects.create(
            member=self.member,
            package=self.pkg_monthly,
            start_date=today - timedelta(days=20),
            end_date=old_end,
            created_by=self.staff
        )
        self.assertTrue(self.member.is_membership_active)

        # Lakukan perpanjangan saat masih aktif
        resp = self.client.post(reverse('membership_create', args=[self.member.pk]), {
            'package': self.pkg_monthly.pk,
            'method': Payment.Method.TRANSFER,
            'amount': 300000,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Membership baru harus dimulai dari old_end + 1 hari (sisa hari tidak hilang)
        new_ms = Membership.objects.filter(member=self.member).order_by('-end_date').first()
        expected_start = old_end + timedelta(days=1)
        expected_end = expected_start + timedelta(days=29)
        self.assertEqual(new_ms.start_date, expected_start)
        self.assertEqual(new_ms.end_date, expected_end)
        self.assertEqual(self.member.days_remaining, (expected_end - today).days)

    def test_renewal_for_expired_member_starts_today(self):
        today = timezone.localdate()
        # Buat membership lama yang sudah kedaluwarsa 5 hari lalu
        Membership.objects.create(
            member=self.member,
            package=self.pkg_monthly,
            start_date=today - timedelta(days=35),
            end_date=today - timedelta(days=5),
            created_by=self.staff
        )
        self.assertFalse(self.member.is_membership_active)

        # Lakukan perpanjangan
        resp = self.client.post(reverse('membership_create', args=[self.member.pk]), {
            'package': self.pkg_monthly.pk,
            'method': Payment.Method.QRIS,
            'amount': 300000,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Membership baru harus dimulai hari ini
        new_ms = Membership.objects.filter(member=self.member).order_by('-end_date').first()
        self.assertEqual(new_ms.start_date, today)
        self.assertEqual(new_ms.end_date, today + timedelta(days=29))
        self.assertTrue(self.member.is_membership_active)

    def test_payment_receipt_view(self):
        today = timezone.localdate()
        ms = Membership.objects.create(
            member=self.member,
            package=self.pkg_monthly,
            start_date=today,
            end_date=today + timedelta(days=29),
            created_by=self.staff
        )
        pay = Payment.objects.create(
            membership=ms,
            amount=300000,
            method=Payment.Method.CASH,
            status=Payment.Status.VERIFIED,
            verified_by=self.staff
        )
        resp = self.client.get(reverse('payment_receipt', args=[pay.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Rp300.000")
        self.assertContains(resp, self.member.full_name)
        self.assertContains(resp, self.member.member_code)
