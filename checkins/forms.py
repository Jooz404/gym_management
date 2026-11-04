from django import forms


class CheckinForm(forms.Form):
    member_code = forms.CharField(
        label="Kode Member (ID / Barcode / QR)",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-uppercase font-monospace text-center',
            'placeholder': 'Ketik atau Scan Kode Member (misal: FLX-1001)...',
            'autofocus': True,
            'autocomplete': 'off',
            'style': 'font-size: 1.5rem; letter-spacing: 2px;',
        }),
        help_text="Kursor otomatis aktif. Tekan Enter setelah mengetik atau memindai barcode/QR."
    )

    def clean_member_code(self):
        code = self.cleaned_data.get('member_code', '').strip().upper()
        if not code:
            raise forms.ValidationError("Kode member tidak boleh kosong.")
        return code

