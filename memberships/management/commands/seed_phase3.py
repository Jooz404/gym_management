from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from members.models import Member
from packages.models import Package
from memberships.models import Membership, Payment


class Command(BaseCommand):
    help = "Membuat data contoh Fase 3: Membership aktif, akan habis, dan kedaluwarsa beserta pembayarannya"

    def handle(self, *args, **options):
        staff = User.objects.filter(role=User.Role.STAFF).first() or User.objects.first()
        pkg_monthly = Package.objects.filter(duration_days=30).first() or Package.objects.first()
        pkg_daily = Package.objects.filter(duration_days=1).first() or pkg_monthly

        if not pkg_monthly:
            self.stdout.write(self.style.ERROR('Paket belum ada, jalankan seed_phase2 terlebih dahulu.'))
            return

        today = timezone.localdate()

        # Ambil 10 member contoh pertama untuk diberi membership dengan skenario berbeda
        members = list(Member.objects.all()[:12])
        if len(members) < 6:
            self.stdout.write(self.style.WARNING('Data member belum cukup untuk simulasi.'))
            return

        # Skenario 1: Member Aktif Aman (habis 20 hari lagi)
        for m in members[0:4]:
            if not m.memberships.exists():
                ms = Membership.objects.create(
                    member=m,
                    package=pkg_monthly,
                    start_date=today - timedelta(days=10),
                    end_date=today + timedelta(days=20),
                    created_by=staff
                )
                Payment.objects.create(
                    membership=ms,
                    amount=pkg_monthly.price,
                    method=Payment.Method.CASH,
                    status=Payment.Status.VERIFIED,
                    verified_by=staff,
                    created_by=staff,
                    note='Pembayaran tunai kasir'
                )

        # Skenario 2: Member Akan Habis (Expiring Soon - 3 s/d 5 hari lagi)
        for i, m in enumerate(members[4:7]):
            if not m.memberships.exists():
                remaining = 2 + i
                ms = Membership.objects.create(
                    member=m,
                    package=pkg_monthly,
                    start_date=today - timedelta(days=30 - remaining),
                    end_date=today + timedelta(days=remaining),
                    created_by=staff
                )
                Payment.objects.create(
                    membership=ms,
                    amount=pkg_monthly.price,
                    method=Payment.Method.TRANSFER,
                    status=Payment.Status.VERIFIED,
                    verified_by=staff,
                    created_by=staff,
                    note='Transfer Bank BCA'
                )

        # Skenario 3: Member Kedaluwarsa (Expired - habis 5 hari yang lalu)
        for m in members[7:10]:
            if not m.memberships.exists():
                ms = Membership.objects.create(
                    member=m,
                    package=pkg_monthly,
                    start_date=today - timedelta(days=35),
                    end_date=today - timedelta(days=5),
                    created_by=staff
                )
                Payment.objects.create(
                    membership=ms,
                    amount=pkg_monthly.price,
                    method=Payment.Method.QRIS,
                    status=Payment.Status.VERIFIED,
                    verified_by=staff,
                    created_by=staff,
                    note='QRIS statis kasir'
                )

        # Skenario 4: members[10:] dibiarkan belum ada paket untuk menguji 'no_membership'

        self.stdout.write(self.style.SUCCESS('Data contoh membership Fase 3 (Aktif, Akan Habis, Kedaluwarsa) berhasil dibuat.'))

