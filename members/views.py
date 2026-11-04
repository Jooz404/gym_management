from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
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
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Perubahan profil member '{member.full_name}' berhasil disimpan!")
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
