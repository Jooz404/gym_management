from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from packages.models import Package
from memberships.models import Membership
from members.models import Member, sanitize_phone_number


class MemberModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='staff_member',
            password='password123',
            role=User.Role.STAFF
        )
        self.client.login(username='staff_member', password='password123')

        self.pkg = Package.objects.create(
            name='Paket Bulanan',
            duration_days=30,
            price=300000,
            is_active=True
        )

        # Buat 20 member untuk menguji kriteria berhasil (Definition of Done) Fase 2
        self.members = []
        for i in range(1, 21):
            m = Member.objects.create(
                member_code=f"FLX-{1000 + i}",
                full_name=f"Member Testing {i}",
                phone_wa=f"0812000000{i:02d}",
                notes=f"Catatan member {i}"
            )
            self.members.append(m)

    def test_phone_sanitization_d018(self):
        # Format 08xxx menjadi 628xxx
        self.assertEqual(sanitize_phone_number("081234567890"), "6281234567890")
        # Format dengan spasi dan strip
        self.assertEqual(sanitize_phone_number("+62 812-3456-7890"), "6281234567890")
        # Format 8xxx tanpa 0
        self.assertEqual(sanitize_phone_number("81234567890"), "6281234567890")

        # Cek saat disimpan di model
        member = Member.objects.create(
            full_name="Budi Sanitasi",
            phone_wa="0852-9988-7766"
        )
        self.assertEqual(member.phone_wa, "6285299887766")
        self.assertEqual(member.wa_url, "https://wa.me/6285299887766")

    def test_auto_generate_member_code_d011(self):
        member = Member.objects.create(full_name="Member Tanpa Kode")
        self.assertTrue(member.member_code.startswith("FLX-"))
        self.assertNotIn(" ", member.member_code)

    def test_member_list_and_search_by_name(self):
        # Cari nama "Member Testing 15"
        resp = self.client.get(reverse('member_list') + '?q=Testing 15')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Member Testing 15")
        self.assertNotContains(resp, "Member Testing 16")

    def test_member_search_by_code(self):
        # Cari kode "FLX-1007"
        resp = self.client.get(reverse('member_list') + '?q=FLX-1007')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "FLX-1007")
        self.assertContains(resp, "Member Testing 7")

    def test_member_create_view(self):
        resp = self.client.post(reverse('member_create'), {
            'full_name': 'Member Baru Kasir',
            'phone_wa': '089911223344',
            'join_date': '2026-11-04',
            'notes': 'Daftar di meja kasir',
            'is_active': True,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        new_m = Member.objects.get(full_name='Member Baru Kasir')
        self.assertEqual(new_m.phone_wa, '6289911223344')
        self.assertTrue(new_m.member_code.startswith('FLX-'))

    def test_member_detail_view(self):
        target = self.members[0]
        resp = self.client.get(reverse('member_detail', args=[target.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, target.full_name)
        self.assertContains(resp, target.member_code)

    def test_download_import_template(self):
        resp = self.client.get(reverse('download_import_template'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.has_header('Content-Disposition'))
        self.assertIn('.csv', resp['Content-Disposition'])

    def test_member_import_csv_valid(self):
        csv_content = (
            "nama_lengkap,nomor_whatsapp,tanggal_bergabung,nama_paket,tanggal_mulai,tanggal_berakhir,catatan\n"
            "Member Migrasi Satu,081233445566,2026-11-01,Paket Bulanan,2026-11-01,2026-12-01,Buku kertas lama\n"
            "Member Migrasi Dua,082299887711,2026-10-15,Paket Bulanan,2026-10-15,2026-11-15,Member tetap\n"
        ).encode('utf-8')

        uploaded = SimpleUploadedFile("data_lama.csv", csv_content, content_type="text/csv")
        resp = self.client.post(reverse('member_import_csv'), {'csv_file': uploaded}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Sebanyak 2 data member berhasil dimasukkan")

        m1 = Member.objects.filter(full_name='Member Migrasi Satu').first()
        self.assertIsNotNone(m1)
        self.assertEqual(m1.phone_wa, '6281233445566')
        self.assertTrue(m1.memberships.exists())

    def test_member_import_csv_invalid_file(self):
        uploaded = SimpleUploadedFile("file_salah.txt", b"Bukan csv", content_type="text/plain")
        resp = self.client.post(reverse('member_import_csv'), {'csv_file': uploaded}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Format berkas harus berekstensi .csv")
