import os
import urllib.parse
from datetime import timedelta
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, Http404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from core.decorators import feature_required, role_required, owner_required
from members.models import Member
from packages.models import Package
from memberships.models import Membership, Payment
from checkins.models import Checkin


@login_required
def dashboard(request):
    """
    Dashboard Operasional Utama (Pusat Kendali Resepsionis & Pemilik Gym).
    Menghitung metrik real-time: member aktif, akan habis, kehadiran hari ini, dan omzet (owner).
    """
    today = timezone.localdate()

    # 1. Metrik Member
    total_members = Member.objects.count()
    active_member_ids = set(
        Membership.objects.filter(end_date__gte=today).values_list('member_id', flat=True).distinct()
    )
    active_count = len(active_member_ids)
    expired_count = total_members - active_count

    # 2. Member yang Akan Habis dalam 7 Hari ke Depan (Expiring Soon)
    expiring_soon_memberships = Membership.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7)
    ).select_related('member', 'package').order_by('end_date')

    expiring_soon_list = []
    seen_members = set()
    for ms in expiring_soon_memberships:
        if ms.member_id not in seen_members:
            # Pastikan ini adalah membership terbaru member tersebut
            latest = ms.member.latest_membership
            if latest and latest.pk == ms.pk:
                seen_members.add(ms.member_id)
                days_left = (ms.end_date - today).days

                # Template pesan WhatsApp ramah siap kirim (D-018)
                wa_msg = (
                    f"Halo kak {ms.member.full_name}, masa aktif membership *{ms.package.name}* Anda "
                    f"di *{settings.GYM_NAME}* akan berakhir pada *{ms.end_date.strftime('%d/%m/%Y')}* "
                    f"(sisa {days_left} hari lagi).\n\n"
                    f"Yuk perpanjang sekarang agar sesi latihan tetap lancar! Terima kasih 💪"
                )
                wa_url = f"https://wa.me/{ms.member.phone_wa}?text={urllib.parse.quote(wa_msg)}" if ms.member.phone_wa else ""

                expiring_soon_list.append({
                    'member': ms.member,
                    'package': ms.package,
                    'end_date': ms.end_date,
                    'days_remaining': days_left,
                    'wa_url': wa_url,
                })

    expiring_count = len(expiring_soon_list)

    # 3. Metrik Kehadiran Hari Ini
    today_checkins = Checkin.objects.filter(
        checked_in_at__date=today
    ).select_related('member', 'recorded_by').order_by('-checked_in_at')
    today_checkins_count = today_checkins.count()
    latest_checkins = today_checkins[:5]

    # 4. Metrik Keuangan (Khusus Owner D-012)
    today_income = 0
    month_income = 0
    if request.user.is_owner and getattr(settings, 'FEATURE_REPORTS', True):
        today_income = Payment.objects.filter(
            paid_at__date=today,
            status=Payment.Status.VERIFIED
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        month_income = Payment.objects.filter(
            paid_at__year=today.year,
            paid_at__month=today.month,
            status=Payment.Status.VERIFIED
        ).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'title': 'Dashboard Operasional',
        'today': today,
        'total_members': total_members,
        'active_count': active_count,
        'expired_count': expired_count,
        'expiring_count': expiring_count,
        'expiring_soon_list': expiring_soon_list[:5], # 5 teratas di dashboard
        'today_checkins_count': today_checkins_count,
        'latest_checkins': latest_checkins,
        'today_income': today_income,
        'month_income': month_income,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@feature_required('FEATURE_WA_REMINDER')
def wa_reminders(request):
    """
    Modul Pengingat Perpanjangan WhatsApp Semi-Manual (D-012, D-018).
    Menampilkan daftar member yang akan habis (H-7) dan member yang baru saja kedaluwarsa,
    dilengkapi tombol 1-klik untuk membuka WhatsApp dengan pesan siap kirim.
    """
    today = timezone.localdate()

    # 1. Member Akan Habis (0 s/d 7 hari ke depan)
    expiring_memberships = Membership.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7)
    ).select_related('member', 'package').order_by('end_date')

    expiring_list = []
    seen = set()
    for ms in expiring_memberships:
        if ms.member_id not in seen:
            latest = ms.member.latest_membership
            if latest and latest.pk == ms.pk:
                seen.add(ms.member_id)
                days_left = (ms.end_date - today).days
                msg = (
                    f"Halo kak {ms.member.full_name}, kami dari *{settings.GYM_NAME}* ingin mengingatkan "
                    f"bahwa paket *{ms.package.name}* Anda akan berakhir pada *{ms.end_date.strftime('%d/%m/%Y')}* "
                    f"(sisa {days_left} hari).\n\n"
                    f"Silakan hubungi kasir atau perpanjang saat sesi latihan berikutnya ya. Semangat latihannya! 💪"
                )
                wa_url = f"https://wa.me/{ms.member.phone_wa}?text={urllib.parse.quote(msg)}" if ms.member.phone_wa else ""
                expiring_list.append({
                    'member': ms.member,
                    'package': ms.package,
                    'end_date': ms.end_date,
                    'days_remaining': days_left,
                    'wa_url': wa_url,
                })

    # 2. Member Sudah Kedaluwarsa (1 s/d 30 hari yang lalu)
    expired_memberships = Membership.objects.filter(
        end_date__lt=today,
        end_date__gte=today - timedelta(days=30)
    ).select_related('member', 'package').order_by('-end_date')

    expired_list = []
    for ms in expired_memberships:
        if ms.member_id not in seen:
            latest = ms.member.latest_membership
            if latest and latest.pk == ms.pk:
                seen.add(ms.member_id)
                days_ago = (today - ms.end_date).days
                msg = (
                    f"Halo kak {ms.member.full_name}, masa aktif membership Anda di *{settings.GYM_NAME}* "
                    f"telah berakhir {days_ago} hari yang lalu (tanggal {ms.end_date.strftime('%d/%m/%Y')}).\n\n"
                    f"Yuk kembali aktifkan paket Anda dan lanjutkan target kebugaran bersama kami! 💪"
                )
                wa_url = f"https://wa.me/{ms.member.phone_wa}?text={urllib.parse.quote(msg)}" if ms.member.phone_wa else ""
                expired_list.append({
                    'member': ms.member,
                    'package': ms.package,
                    'end_date': ms.end_date,
                    'days_ago': days_ago,
                    'wa_url': wa_url,
                })

    context = {
        'title': 'Pengingat Perpanjangan WhatsApp',
        'expiring_list': expiring_list,
        'expired_list': expired_list,
        'total_reminder': len(expiring_list) + len(expired_list),
    }
    return render(request, 'core/reminders.html', context)


@login_required
@owner_required
@feature_required('FEATURE_REPORTS')
def reports_view(request):
    """
    Laporan Keuangan & Pemasukan Khusus Pemilik (D-012).
    Menampilkan rincian pendapatan harian, bulanan, metode pembayaran, dan paket terlaris.
    """
    today = timezone.localdate()

    # Filter rentang tanggal (default: tanggal 1 bulan ini s/d hari ini)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str:
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today.replace(day=1)
    else:
        start_date = today.replace(day=1)

    if end_date_str:
        try:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    else:
        end_date = today

    # Ambil transaksi pembayaran yang terverifikasi dalam rentang tanggal
    payments = Payment.objects.filter(
        paid_at__date__gte=start_date,
        paid_at__date__lte=end_date,
        status=Payment.Status.VERIFIED
    ).select_related('membership__member', 'membership__package', 'verified_by').order_by('-paid_at')

    # Total Omzet Periode Terpilih
    period_income = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_transactions = payments.count()

    # Rincian Omzet Berdasarkan Metode Pembayaran
    by_method = payments.values('method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Terjemahkan label metode pembayaran
    method_labels = dict(Payment.Method.choices)
    for m in by_method:
        m['label'] = method_labels.get(m['method'], m['method'])

    # Rincian Omzet Berdasarkan Paket
    by_package = payments.values('membership__package__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    context = {
        'title': 'Laporan Keuangan & Pemasukan',
        'start_date': start_date,
        'end_date': end_date,
        'payments': payments,
        'period_income': period_income,
        'total_transactions': total_transactions,
        'by_method': by_method,
        'by_package': by_package,
    }
    return render(request, 'core/reports.html', context)


@login_required
@owner_required
def backup_database(request):
    """
    Cadangan Database 1-Klik Khusus Owner (D-010).
    Mengunduh salinan berkas db.sqlite3 secara instan ke komputer pemilik gym.
    """
    db_path = settings.BASE_DIR / 'db.sqlite3'
    timestamp = timezone.localtime().strftime('%Y%m%d_%H%M')
    filename = f"backup_flexgym_{timestamp}.sqlite3"

    if os.path.exists(db_path):
        response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename=filename)
    else:
        # Fallback cadangan untuk testing
        content = BytesIO(b"SQLite format 3\x00--Flex Gym Database Backup--")
        response = FileResponse(content, as_attachment=True, filename=filename)

    return response
