from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Membuat akun awal default untuk Pengujian: Owner (Pemilik) dan Staff (Kasir)"

    def handle(self, *args, **options):
        # Akun Pemilik (Owner)
        owner, created = User.objects.get_or_create(
            username='owner',
            defaults={
                'name': 'Pemilik Flex Gym',
                'role': User.Role.OWNER,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            owner.set_password('owner123')
            owner.save()
            self.stdout.write(self.style.SUCCESS('Akun Owner berhasil dibuat (username: owner, password: owner123)'))
        else:
            self.stdout.write(self.style.WARNING('Akun Owner sudah ada.'))

        # Akun Kasir (Staff)
        staff, created = User.objects.get_or_create(
            username='staff',
            defaults={
                'name': 'Kasir Gym Bitung',
                'role': User.Role.STAFF,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            staff.set_password('staff123')
            staff.save()
            self.stdout.write(self.style.SUCCESS('Akun Staff berhasil dibuat (username: staff, password: staff123)'))
        else:
            self.stdout.write(self.style.WARNING('Akun Staff sudah ada.'))

