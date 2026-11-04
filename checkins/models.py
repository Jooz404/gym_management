from django.db import models
from django.conf import settings
from django.utils import timezone


class Checkin(models.Model):
    class Method(models.TextChoices):
        CODE = 'code', 'Ketik Kode'
        QR = 'qr', 'Scan Barcode / QR'
        MANUAL = 'manual', 'Manual Kasir'

    class Result(models.TextChoices):
        ALLOWED = 'allowed', 'Diizinkan (Aktif)'
        EXPIRED_WARNING = 'expired_warning', 'Peringatan Kedaluwarsa'

    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='checkins',
        verbose_name="Member"
    )
    checked_in_at = models.DateTimeField(default=timezone.now, verbose_name="Waktu Check-in")
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.CODE,
        verbose_name="Metode Check-in"
    )
    result = models.CharField(
        max_length=20,
        choices=Result.choices,
        default=Result.ALLOWED,
        verbose_name="Hasil Check-in"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_checkins',
        verbose_name="Dicatat Oleh"
    )
    notes = models.CharField(max_length=255, blank=True, verbose_name="Catatan")

    class Meta:
        verbose_name = "Kehadiran (Check-in)"
        verbose_name_plural = "Daftar Kehadiran"
        ordering = ['-checked_in_at']

    def __str__(self):
        return f"{self.member.member_code} — {self.member.full_name} ({self.checked_in_at.strftime('%d/%m/%Y %H:%M')})"

    @property
    def is_allowed(self) -> bool:
        return self.result == self.Result.ALLOWED

    @property
    def is_warning(self) -> bool:
        return self.result == self.Result.EXPIRED_WARNING
