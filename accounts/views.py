from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from .forms import LoginForm


class CustomLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Selamat datang kembali, {form.get_user().name or form.get_user().username}!")
        return super().form_valid(form)


def user_logout(request):
    logout(request)
    messages.info(request, "Anda telah berhasil keluar dari sistem.")
    return redirect('login')
