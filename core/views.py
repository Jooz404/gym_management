from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .decorators import feature_required, role_required, owner_required


@login_required
def dashboard(request):
    """
    Halaman dashboard utama untuk Staf dan Owner.
    Tampilan kartu dan aksi menyesuaikan dengan peran pengguna dan feature flag.
    """
    context = {
        'title': 'Dashboard Utama',
    }
    return render(request, 'core/dashboard.html', context)


# Endpoint pembuktian proteksi Feature Flag (D-012)
@login_required
@feature_required('FEATURE_CHECKIN')
def feature_checkin_test(request):
    return HttpResponse("Halaman fitur Check-in aktif dan dapat diakses.")


@login_required
@feature_required('FEATURE_REPORTS')
@owner_required
def feature_reports_test(request):
    return HttpResponse("Halaman fitur Laporan Keuangan aktif dan dapat diakses khusus Owner.")


@login_required
@feature_required('FEATURE_WA_REMINDER')
def feature_wa_test(request):
    return HttpResponse("Halaman fitur Pengingat WhatsApp aktif dan dapat diakses.")
