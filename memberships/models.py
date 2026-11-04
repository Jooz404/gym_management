from django.db import models
from django.conf import settings
from django.utils import timezone


class Membership(models.Model):
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name="Member"
    )
    package = models.ForeignKey(
        'packages.Package',
        on_delete=models.PROTECT,
        related_name='memberships',
        verbose_name="Paket"
    )
    start_date = models.DateField(verbose_name="Tanggal Mulai")
    end_date = models.DateField(verbose_name="Tanggal Berakhir")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_memberships',
        verbose_name="Dicatat Oleh"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")

    class Meta:
        verbose_name = "Keanggotaan"
        verbose_name_plural = "Daftar Keanggotaan"
        ordering = ['-end_date', '-created_at']

    def __str__(self):
        return f"{self.member.full_name} — {self.package.name} ({self.start_date} s/d {self.end_date})"

    @property
    def is_active_now(self) -> bool:
        """Status aktif jika hari ini berada dalam rentang start_date dan end_date (D-003)."""
        today = timezone.localdate()
        return self.start_date <= today <= self.end_date

    @property
    def days_remaining(self) -> int:
        """Jumlah hari tersisa sebelum masa aktif habis."""
        today = timezone.localdate()
        if self.end_date >= today:
            return (self.end_date - today).days
        return 0

    @property
    def is_expiring_soon(self) -> bool:
        """Akan habis dalam 7 hari ke depan."""
        today = timezone.localdate()
        return 0 <= (self.end_date - today).days <= 7

    @property
    def status_label(self) -> str:
        today = timezone.localdate()
        if today < self.start_date:
            return "Mendatang"
        elif today <= self.end_date:
            if self.is_expiring_soon:
                return "Akan Habis"
            return "Aktif"
        else:
            return "Kedaluwarsa"


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Tunai (Cash)'
        TRANSFER = 'transfer', 'Transfer Bank'
        QRIS = 'qris', 'QRIS Kasir'

    class Status(models.TextChoices):
        VERIFIED = 'verified', 'Terverifikasi'
        PENDING = 'pending', 'Menunggu Verifikasi'

    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Keanggotaan"
    )
    amount = models.IntegerField(verbose_name="Nominal (Rp)")
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.CASH,
        verbose_name="Metode Pembayaran"
    )
    paid_at = models.DateTimeField(default=timezone.now, verbose_name="Waktu Pembayaran")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.VERIFIED,
        verbose_name="Status Verifikasi"
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Diverifikasi Oleh"
    )
    note = models.TextField(blank=True, verbose_name="Catatan Pembayaran")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_payments',
        verbose_name="Dicatat Oleh"
    )

    class Meta:
        verbose_name = "Pembayaran"
        verbose_name_plural = "Daftar Pembayaran"
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.membership.member.full_name} — {self.formatted_amount} ({self.get_method_display()})"

    @property
    def formatted_amount(self) -> str:
        """Format nominal rupiah (misal: Rp300.000)."""
        formatted = f"{self.amount:,}".replace(',', '.')
        return f"Rp{formatted}"
