from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.decorators import feature_required
from members.models import Member
from .models import Checkin
from .forms import CheckinForm


@login_required
@feature_required('FEATURE_CHECKIN')
def checkin_page(request):
    """
    Halaman Check-in Cepat Resepsionis (D-008, D-011, D-017).
    Memeriksa masa aktif secara instan saat kode dimasukkan / discan.
    """
    last_result = None
    form = CheckinForm()

    if request.method == 'POST':
        form = CheckinForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['member_code']
            member = Member.objects.filter(member_code__iexact=code).first()

            if not member:
                last_result = {
                    'status': 'not_found',
                    'code': code,
                    'title': 'KODE TIDAK DITEMUKAN',
                    'message': f"Member dengan kode '{code}' tidak terdaftar dalam sistem.",
                }
            else:
                # Periksa keaktifan masa aktif member (D-003, D-008)
                if member.is_membership_active:
                    checkin = Checkin.objects.create(
                        member=member,
                        method=Checkin.Method.CODE,
                        result=Checkin.Result.ALLOWED,
                        recorded_by=request.user
                    )
                    last_result = {
                        'status': 'allowed',
                        'member': member,
                        'checkin': checkin,
                        'title': 'CHECK-IN BERHASIL (MEMBER AKTIF)',
                        'message': f"Selamat Datang, {member.full_name}!",
                        'end_date': member.latest_membership.end_date,
                        'days_remaining': member.days_remaining,
                    }
                else:
                    # Member kedaluwarsa atau belum berpaket -> catat peringatan (D-008)
                    checkin = Checkin.objects.create(
                        member=member,
                        method=Checkin.Method.CODE,
                        result=Checkin.Result.EXPIRED_WARNING,
                        recorded_by=request.user
                    )
                    last_result = {
                        'status': 'expired_warning',
                        'member': member,
                        'checkin': checkin,
                        'title': 'PERINGATAN: MASA AKTIF KEDALUWARSA!',
                        'message': f"Keanggotaan {member.full_name} sudah habis atau belum memiliki paket aktif. Silakan tagih perpanjangan.",
                        'end_date': member.latest_membership.end_date if member.latest_membership else None,
                    }

            # Kosongkan form agar kursor langsung siap untuk input berikutnya
            form = CheckinForm()

    # Riwayat check-in hari ini di meja kasir
    today = timezone.localdate()
    today_checkins = Checkin.objects.filter(
        checked_in_at__date=today
    ).select_related('member', 'recorded_by').order_by('-checked_in_at')

    context = {
        'title': 'Check-in Cepat Member',
        'form': form,
        'last_result': last_result,
        'today_checkins': today_checkins,
        'total_today': today_checkins.count(),
        'allowed_today': today_checkins.filter(result=Checkin.Result.ALLOWED).count(),
        'warning_today': today_checkins.filter(result=Checkin.Result.EXPIRED_WARNING).count(),
    }
    return render(request, 'checkins/checkin.html', context)
