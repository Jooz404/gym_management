from django import forms
from .models import Package


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'duration_days', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Paket Bulanan Regular',
                'autofocus': True,
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah hari (contoh: 30 untuk 1 bulan)',
                'min': '1',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nominal dalam rupiah (contoh: 300000)',
                'min': '0',
                'step': '1000',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'name': 'Nama Paket',
            'duration_days': 'Durasi Masa Aktif (Hari)',
            'price': 'Harga Iuran (Rp)',
            'is_active': 'Paket Aktif (Dapat dipilih member baru/perpanjangan)',
        }

