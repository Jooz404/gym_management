from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Masukkan username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Kata Sandi",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Masukkan kata sandi',
        })
    )

    error_messages = {
        'invalid_login': "Username atau kata sandi yang Anda masukkan salah. Silakan coba lagi.",
        'inactive': "Akun ini telah dinonaktifkan. Hubungi pemilik gym.",
    }

