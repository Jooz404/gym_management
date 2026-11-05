import csv
import io
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404
from django.utils import timezone
from packages.models import Package
from memberships.models import Membership, Payment
from .models import Member
from .forms import MemberForm


@login_required
def member_list(request):
    """
    Menampilkan daftar member dengan fitur pencarian instan nama atau kode member.
    """
    query = request.GET.get('q', '').strip()
    members = Member.objects.all()

    if query:
        members = members.filter(
            Q(full_name__icontains=query) |
            Q(member_code__icontains=query) |
            Q(phone_wa__icontains=query)
        )

    context = {
        'title': 'Daftar Member',
        'members': members,
        'query': query,
        'total_members': Member.objects.count(),
        'total_active': Member.objects.filter(is_active=True).count(),
    }
    return render(request, 'members/member_list.html', context)


@login_required
def member_create(request):
    """Mendaftarkan member baru (alur cepat staf kasir < 2 menit)."""
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Member '{member.full_name}' dengan kode {member.member_code} berhasil didaftarkan!")

            # Peringatan lembut jika ada member aktif lain dengan nama serupa
            name_duplicates = Member.objects.filter(full_name__iexact=member.full_name).exclude(pk=member.pk)
            if name_duplicates.exists():
                other = name_duplicates.first()
                messages.warning(
                    request,
                    f"Perhatian: Ditemukan member lain dengan nama serupa: '{other.full_name}' ({other.member_code}). "
                    f"Pastikan ini bukan pendaftaran ganda untuk orang yang sama."
                )

            # Peringatan lembut jika nomor WhatsApp digunakan bersama
            if member.phone_wa:
                phone_duplicates = Member.objects.filter(phone_wa=member.phone_wa).exclude(pk=member.pk)
                if phone_duplicates.exists():
                    other_phone = phone_duplicates.first()
                    messages.info(
                        request,
                        f"Catatan: Nomor WhatsApp {member.phone_wa} juga digunakan oleh member '{other_phone.full_name}' ({other_phone.member_code})."
                    )

            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm()

    context = {
        'title': 'Daftar Member Baru',
        'form': form,
    }
    return render(request, 'members/member_form.html', context)


@login_required
def member_update(request, pk):
    """Mengubah data profil member."""
    member = get_object_or_404(Member, pk=pk)
    was_active = member.is_active
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            if was_active and not member.is_active:
                messages.warning(
                    request,
                    f"Perhatian: Akun member '{member.full_name}' telah DINONAKTIFKAN / DIBLOKIR. "
                    f"Member ini tidak akan diizinkan check-in ke gym."
                )
            elif not was_active and member.is_active:
                messages.success(
                    request,
                    f"Akun member '{member.full_name}' telah DIAKTIFKAN kembali! Member kini dapat check-in."
                )
            else:
                messages.success(request, f"Perubahan profil member '{member.full_name}' berhasil disimpan!")

            # Cek duplikasi nomor HP jika ada
            if member.phone_wa:
                phone_duplicates = Member.objects.filter(phone_wa=member.phone_wa).exclude(pk=member.pk)
                if phone_duplicates.exists():
                    other_phone = phone_duplicates.first()
                    messages.info(
                        request,
                        f"Catatan: Nomor WhatsApp {member.phone_wa} juga digunakan oleh member '{other_phone.full_name}' ({other_phone.member_code})."
                    )

            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm(instance=member)

    context = {
        'title': f'Ubah Data Member: {member.full_name}',
        'form': form,
        'member': member,
    }
    return render(request, 'members/member_form.html', context)


@login_required
def member_detail(request, pk):
    """Melihat profil detail member, kartu keanggotaan, dan riwayat aktivitas."""
    member = get_object_or_404(Member, pk=pk)
    context = {
        'title': f'Detail Member — {member.full_name}',
        'member': member,
    }
    return render(request, 'members/member_detail.html', context)


def parse_date_flexibly(date_str: str, default_date=None):
    """Membantu parsing format tanggal yang bervariasi dari Excel/CSV."""
    if not date_str or not date_str.strip():
        return default_date or timezone.localdate()
    cleaned = date_str.strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return default_date or timezone.localdate()


@login_required
def member_import_csv(request):
    """
    Fasilitas Impor Data Catatan Kertas / Buku Kasir via berkas CSV (Fase 6).
    Memasukkan puluhan hingga ratusan data member lama sekaligus dalam hitungan detik.
    """
    import_results = None

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Format berkas harus berekstensi .csv!")
            return redirect('member_import_csv')

        try:
            # Membaca dengan encoding utf-8-sig untuk membuang BOM bawaan Excel
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            success_count = 0
            skipped_count = 0
            errors = []

            today = timezone.localdate()

            with transaction.atomic():
                for row_idx, row in enumerate(reader, start=2):
                    # Normalisasi nama kolom (lowercase & strip)
                    norm_row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}

                    full_name = norm_row.get('nama_lengkap') or norm_row.get('nama') or norm_row.get('name')
                    if not full_name:
                        skipped_count += 1
                        errors.append(f"Baris {row_idx}: Nama lengkap kosong, dilewati.")
                        continue

                    phone_wa = norm_row.get('nomor_whatsapp') or norm_row.get('whatsapp') or norm_row.get('no_hp') or ""
                    notes = norm_row.get('catatan') or norm_row.get('notes') or "Data migrasi dari buku kertas"
                    join_date = parse_date_flexibly(norm_row.get('tanggal_bergabung'), today)

                    # Buat objek Member
                    member = Member.objects.create(
                        full_name=full_name,
                        phone_wa=phone_wa,
                        join_date=join_date,
                        notes=notes,
                        is_active=True
                    )

                    # Jika ada data paket lama
                    package_name = norm_row.get('nama_paket') or norm_row.get('paket')
                    if package_name:
                        pkg = Package.objects.filter(name__icontains=package_name).first()
                        if not pkg:
                            pkg = Package.objects.filter(is_active=True).first()

                        if pkg:
                            start_date = parse_date_flexibly(norm_row.get('tanggal_mulai'), today)
                            end_date_str = norm_row.get('tanggal_berakhir')
                            if end_date_str:
                                end_date = parse_date_flexibly(end_date_str, start_date + timedelta(days=pkg.duration_days - 1))
                            else:
                                end_date = start_date + timedelta(days=pkg.duration_days - 1)

                            ms = Membership.objects.create(
                                member=member,
                                package=pkg,
                                start_date=start_date,
                                end_date=end_date,
                                created_by=request.user
                            )

                            Payment.objects.create(
                                membership=ms,
                                amount=pkg.price,
                                method=Payment.Method.CASH,
                                status=Payment.Status.VERIFIED,
                                verified_by=request.user,
                                created_by=request.user,
                                note='Migrasi data lama buku fisik'
                            )

                    success_count += 1

            messages.success(
                request,
                f"Proses impor selesai! Sebanyak {success_count} data member berhasil dimasukkan ke sistem."
            )
            import_results = {
                'success_count': success_count,
                'skipped_count': skipped_count,
                'errors': errors,
            }

        except Exception as e:
            messages.error(request, f"Gagal membaca berkas CSV: {str(e)}")

    context = {
        'title': 'Impor Data Member dari CSV',
        'import_results': import_results,
    }
    return render(request, 'members/member_import.html', context)


@login_required
def download_import_template(request):
    """Mengunduh berkas template CSV standar untuk diisi pengelola gym."""
    template_path = settings.BASE_DIR / 'docs' / 'template_import_member.csv'
    if not os.path.exists(template_path):
        raise Http404("Berkas template tidak ditemukan.")
    return FileResponse(open(template_path, 'rb'), as_attachment=True, filename='template_import_member_flexgym.csv')
