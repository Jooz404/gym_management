from django.db import models


class Package(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Paket")
    duration_days = models.PositiveIntegerField(verbose_name="Durasi (Hari)")
    price = models.IntegerField(verbose_name="Harga (Rp)")
    is_active = models.BooleanField(default=True, verbose_name="Status Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")

    class Meta:
        verbose_name = "Paket Keanggotaan"
        verbose_name_plural = "Daftar Paket Keanggotaan"
        ordering = ['price', 'duration_days']

    def __str__(self):
        status = "Aktif" if self.is_active else "Nonaktif"
        return f"{self.name} ({self.duration_days} hari) — {self.formatted_price} [{status}]"

    @property
    def formatted_price(self):
        """Format harga rupiah (misal: Rp300.000)."""
        formatted = f"{self.price:,}".replace(',', '.')
        return f"Rp{formatted}"
