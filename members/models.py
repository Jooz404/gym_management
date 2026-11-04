import re
from django.db import models
from django.utils import timezone


def sanitize_phone_number(phone_raw: str) -> str:
    """
    Sanitasi nomor WhatsApp (D-018):
    Menghilangkan spasi, tanda hubung, dan tanda plus.
    Mengubah awalan 08xxx atau 8xxx menjadi standar Indonesia 628xxx.
    """
    if not phone_raw:
        return ""
    # Hapus semua karakter selain angka
    digits = re.sub(r'\D', '', str(phone_raw))
    if not digits:
        return ""
    if digits.startswith('08'):
        return '628' + digits[2:]
    if digits.startswith('8'):
        return '628' + digits[1:]
    if digits.startswith('628'):
        return digits
    return digits


class Member(models.Model):
    member_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Kode Member (ID/QR)"
    )
    full_name = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    phone_wa = models.CharField(max_length=20, blank=True, verbose_name="Nomor WhatsApp")
    join_date = models.DateField(default=timezone.now, verbose_name="Tanggal Bergabung")
    notes = models.TextField(blank=True, verbose_name="Catatan")
    is_active = models.BooleanField(default=True, verbose_name="Akun Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")

    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Daftar Member"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.member_code} — {self.full_name}"

    @classmethod
    def generate_unique_code(cls) -> str:
        """
        Menghasilkan kode unik member dengan format FLX-XXXX (D-011).
        String pendek, huruf kapital, tanpa spasi, ramah QR & barcode scanner fisik.
        """
        last_member = cls.objects.order_by('-id').first()
        next_num = 1001 if not last_member else last_member.id + 1001
        candidate = f"FLX-{next_num}"
        # Pastikan benar-benar unik
        while cls.objects.filter(member_code=candidate).exists():
            next_num += 1
            candidate = f"FLX-{next_num}"
        return candidate

    def save(self, *args, **kwargs):
        # Auto-generate member_code jika belum ada
        if not self.member_code:
            self.member_code = self.generate_unique_code()
        else:
            self.member_code = self.member_code.strip().upper()

        # Sanitasi nomor WhatsApp otomatis (D-018)
        if self.phone_wa:
            self.phone_wa = sanitize_phone_number(self.phone_wa)

        super().save(*args, **kwargs)

    @property
    def wa_url(self) -> str:
        """Tautan langsung ke chat WhatsApp."""
        if not self.phone_wa:
            return ""
        return f"https://wa.me/{self.phone_wa}"
