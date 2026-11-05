from django import forms
from django.utils import timezone
from .models import Member, sanitize_phone_number


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
            'is_active': 'Hapus centang untuk menonaktifkan atau memblokir akses member ini.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('join_date'):
            self.initial['join_date'] = timezone.localdate()
        self.fields['member_code'].required = False

    def clean_member_code(self):
        code = self.cleaned_data.get('member_code', '').strip().upper()
        if code:
            existing = Member.objects.filter(member_code__iexact=code)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                other = existing.first()
                raise forms.ValidationError(
                    f"Kode member '{code}' sudah digunakan oleh '{other.full_name}'. "
                    f"Gunakan kode lain atau kosongkan kolom ini agar sistem membuat kode baru otomatis."
                )
        return code

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise forms.ValidationError("Nama lengkap member tidak boleh kosong.")

        # Cek jika ada member lama yang diblokir/nonaktif dengan nama yang sama persis
        query = Member.objects.filter(full_name__iexact=name)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        blocked_member = query.filter(is_active=False).first()
        if blocked_member:
            raise forms.ValidationError(
                f"Member dengan nama '{blocked_member.full_name}' sudah terdaftar dan saat ini berstatus "
                f"NONAKTIF / DIBLOKIR ({blocked_member.member_code}). "
                f"Dilarang membuat akun baru. Silakan buka data member lama dan aktifkan kembali akunnya jika diizinkan."
            )

        return name

    def clean_phone_wa(self):
        phone = self.cleaned_data.get('phone_wa', '').strip()
        if phone:
            return sanitize_phone_number(phone)
        return ""
