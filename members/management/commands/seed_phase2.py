from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from packages.models import Package
from members.models import Member


class Command(BaseCommand):
    help = "Membuat data contoh Fase 2: Paket Keanggotaan dan 20 Member Contoh untuk Pengujian Pencarian"

    def handle(self, *args, **options):
        # 1. Paket Keanggotaan Default
        packages_data = [
            {'name': 'Paket Bulanan Regular', 'duration_days': 30, 'price': 300000, 'is_active': True},
            {'name': 'Paket Harian (Insidental)', 'duration_days': 1, 'price': 35000, 'is_active': True},
            {'name': 'Paket 3 Bulan Diskon', 'duration_days': 90, 'price': 800000, 'is_active': True},
            {'name': 'Paket Pelajar/Mahasiswa', 'duration_days': 30, 'price': 250000, 'is_active': True},
        ]
        created_pkg_count = 0
        for pdata in packages_data:
            pkg, created = Package.objects.get_or_create(
                name=pdata['name'],
                defaults=pdata
            )
            if created:
                created_pkg_count += 1
        self.stdout.write(self.style.SUCCESS(f"{created_pkg_count} paket default berhasil dibuat."))

        # 2. 20 Member Contoh untuk Pengujian
        sample_members = [
            ("Rizky Pratama", "081234567801", "Catatan: Pemula gym"),
            ("Siti Nurhaliza", "081234567802", "Catatan: Fokus cardio"),
            ("Budi Santoso", "081234567803", ""),
            ("Dewi Lestari", "081234567804", ""),
            ("Agus Setiawan", "081234567805", "Catatan: Rekomendasi teman"),
            ("Mega Wijaya", "081234567806", ""),
            ("Fajar Nugraha", "081234567807", "Catatan: Suka sesi pagi"),
            ("Indah Permata", "081234567808", ""),
            ("Hendra Gunawan", "081234567809", ""),
            ("Eka Putri", "081234567810", "Catatan: Mahasiswi"),
            ("Joko Susilo", "081234567811", ""),
            ("Tri Handayani", "081234567812", ""),
            ("Doni Ramadhan", "081234567813", ""),
            ("Fitriani Azahra", "081234567814", ""),
            ("Gita Gutawa", "081234567815", "Catatan: Sesi malam"),
            ("Ilham Maulana", "081234567816", ""),
            ("Kartika Sari", "081234567817", ""),
            ("Lukman Hakim", "081234567818", ""),
            ("Nadya Hutagalung", "081234567819", ""),
            ("Rendy Pandugo", "081234567820", "Catatan: Atlet lokal"),
        ]

        created_member_count = 0
        base_date = timezone.localdate() - timedelta(days=60)
        for i, (name, phone, notes) in enumerate(sample_members, start=1):
            code = f"FLX-{1000 + i}"
            member, created = Member.objects.get_or_create(
                member_code=code,
                defaults={
                    'full_name': name,
                    'phone_wa': phone,
                    'join_date': base_date + timedelta(days=i * 2),
                    'notes': notes,
                    'is_active': True,
                }
            )
            if created:
                created_member_count += 1

        self.stdout.write(self.style.SUCCESS(f"{created_member_count} member contoh berhasil dibuat dengan kode unik FLX-1001 s/d FLX-1020."))

