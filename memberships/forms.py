from django import forms
from packages.models import Package
from .models import Payment


class MembershipRenewForm(forms.Form):
    package = forms.ModelChoiceField(
        queryset=Package.objects.filter(is_active=True),
        label="Pilih Paket Keanggotaan",
        empty_label="-- Pilih Paket --",
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'package-select',
            'autofocus': True,
        })
    )
    method = forms.ChoiceField(
        choices=Payment.Method.choices,
        label="Metode Pembayaran",
        initial=Payment.Method.CASH,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    amount = forms.IntegerField(
        label="Nominal Pembayaran (Rp)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'amount-input',
            'placeholder': 'Nominal pembayaran',
            'min': '0',
            'step': '1000',
        }),
        help_text="Terisi otomatis sesuai harga paket yang dipilih."
    )
    custom_start_date = forms.DateField(
        required=False,
        label="Tanggal Mulai Khusus (Opsional)",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        help_text="Kosongkan agar sistem menghitung otomatis: jika masih aktif berlanjut dari sisa hari, jika habis mulai hari ini."
    )
    note = forms.CharField(
        required=False,
        label="Catatan Pembayaran",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contoh: Bayar lunas tunai di meja kasir',
        })
    )

