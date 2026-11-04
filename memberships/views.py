from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from members.models import Member
from packages.models import Package
from .models import Membership, Payment
from .forms import MembershipRenewForm


@login_required
def membership_create(request, member_id):
    """
    Pendaftaran / Perpanjangan Masa Aktif Member (Transaksi Terpadu Kasir).
    Menghitung tanggal mulai secara cerdas:
    - Jika member masih aktif: tanggal mulai = end_date lama + 1 hari (sisa hari akumulatif).
    - Jika member sudah kedaluwarsa: tanggal mulai = hari ini.
    """
    member = get_object_or_404(Member, pk=member_id)
    today = timezone.localdate()

    # Cek membership aktif saat ini
    latest_active = member.memberships.filter(end_date__gte=today).order_by('-end_date').first()

    if request.method == 'POST':
        form = MembershipRenewForm(request.POST)
        if form.is_valid():
            package = form.cleaned_data['package']
            method = form.cleaned_data['method']
            amount = form.cleaned_data['amount']
            custom_start = form.cleaned_data.get('custom_start_date')
            note = form.cleaned_data.get('note', '')

            # Tentukan start_date
            if custom_start:
                start_date = custom_start
            elif latest_active:
                start_date = latest_active.end_date + timedelta(days=1)
            else:
                start_date = today

            # Hitung end_date: start_date + duration_days - 1 hari
            end_date = start_date + timedelta(days=package.duration_days - 1)

            with transaction.atomic():
                # 1. Simpan periode keanggotaan
                membership = Membership.objects.create(
                    member=member,
                    package=package,
                    start_date=start_date,
                    end_date=end_date,
                    created_by=request.user
                )

                # 2. Catat pembayaran (terverifikasi langsung oleh kasir D-016)
                payment = Payment.objects.create(
                    membership=membership,
                    amount=amount,
                    method=method,
                    paid_at=timezone.now(),
                    status=Payment.Status.VERIFIED,
                    verified_by=request.user,
                    created_by=request.user,
                    note=note
                )

            messages.success(
                request,
                f"Paket '{package.name}' untuk {member.full_name} berhasil diaktifkan hingga {end_date.strftime('%d %b %Y')}!"
            )
            return redirect('payment_receipt', payment_id=payment.pk)
    else:
        # Initial form values
        initial_data = {}
        first_pkg = Package.objects.filter(is_active=True).first()
        if first_pkg:
            initial_data['package'] = first_pkg
            initial_data['amount'] = first_pkg.price
        form = MembershipRenewForm(initial=initial_data)

    context = {
        'title': f'Perpanjang Paket — {member.full_name}',
        'member': member,
        'form': form,
        'latest_active': latest_active,
        'packages': Package.objects.filter(is_active=True),
    }
    return render(request, 'memberships/membership_form.html', context)


@login_required
def payment_receipt(request, payment_id):
    """
    Tanda terima pembayaran (Struk Transaksi).
    Desain bersih ramah tangkapan layar untuk dikirim ke WhatsApp member atau dicetak.
    """
    payment = get_object_or_404(Payment, pk=payment_id)
    membership = payment.membership
    member = membership.member

    # Pesan WhatsApp siap kirim tanda terima
    wa_message = (
        f"Halo kak {member.full_name}, pembayaran membership *{membership.package.name}* "
        f"di *{request.user.gym_settings.get('gym_name', 'Flex Gym Bitung') if hasattr(request.user, 'gym_settings') else 'Flex Gym Bitung'}* "
        f"sebesar {payment.formatted_amount} telah berhasil diterima.\n\n"
        f"Kode Member: *{member.member_code}*\n"
        f"Masa Aktif: *{membership.start_date.strftime('%d/%m/%Y')} s/d {membership.end_date.strftime('%d/%m/%Y')}*\n\n"
        f"Terima kasih telah berolahraga bersama kami! 💪"
    )

    import urllib.parse
    wa_receipt_url = f"https://wa.me/{member.phone_wa}?text={urllib.parse.quote(wa_message)}" if member.phone_wa else ""

    context = {
        'title': f'Struk Pembayaran #{payment.pk:05d}',
        'payment': payment,
        'membership': membership,
        'member': member,
        'wa_receipt_url': wa_receipt_url,
    }
    return render(request, 'memberships/payment_receipt.html', context)
