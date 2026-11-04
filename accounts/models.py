from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Pemilik (Owner)'
        STAFF = 'staff', 'Staf (Kasir)'

    name = models.CharField(max_length=150, blank=True, verbose_name="Nama Lengkap")
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
        verbose_name="Peran"
    )

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Daftar Pengguna"

    def __str__(self):
        display_name = self.name or self.username
        return f"{display_name} ({self.get_role_display()})"

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER or self.is_superuser

    @property
    def is_staff_role(self):
        return self.role == self.Role.STAFF
