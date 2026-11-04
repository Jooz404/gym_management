from django import forms
from django.utils import timezone
from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['full_name', 'phone_wa', 'member_code', 'join_date', 'notes', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama lengkap member',
                'autofocus': True,
            }),
            'phone_wa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 081234567890 atau 62812...',
            }),
            'member_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kosongkan untuk dibuat otomatis (misal: FLX-1001)',
            }),
            'join_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Catatan khusus kesehatan, kontak darurat, dsb. (opsional)',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'full_name': 'Nama Lengkap Member',
            'phone_wa': 'Nomor WhatsApp / HP',
            'member_code': 'Kode Member (Opsional)',
            'join_date': 'Tanggal Bergabung',
            'notes': 'Catatan Tambahan',
            'is_active': 'Status Akun Aktif',
        }
        help_texts = {
            'member_code': 'Bisa diisi manual sesuai nomor kartu fisik, atau biarkan kosong agar sistem membuatkannya secara otomatis.',
            'phone_wa': 'Format nomor akan otomatis dibersihkan menjadi format standar 628xxx.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('join_date'):
            self.initial['join_date'] = timezone.localdate()
        self.fields['member_code'].required = False

