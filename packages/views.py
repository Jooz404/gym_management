from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.decorators import role_required, owner_required
from .models import Package
from .forms import PackageForm


@login_required
def package_list(request):
    """Menampilkan daftar semua paket keanggotaan."""
    packages = Package.objects.all()
    context = {
        'title': 'Daftar Paket Keanggotaan',
        'packages': packages,
    }
    return render(request, 'packages/package_list.html', context)


@login_required
@owner_required
def package_create(request):
    """Menambah paket keanggotaan baru (khusus Owner)."""
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            package = form.save()
            messages.success(request, f"Paket '{package.name}' berhasil ditambahkan!")
            return redirect('package_list')
    else:
        form = PackageForm()

    context = {
        'title': 'Tambah Paket Keanggotaan',
        'form': form,
    }
    return render(request, 'packages/package_form.html', context)


@login_required
@owner_required
def package_update(request, pk):
    """Mengubah paket keanggotaan (khusus Owner)."""
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            package = form.save()
            messages.success(request, f"Perubahan paket '{package.name}' berhasil disimpan!")
            return redirect('package_list')
    else:
        form = PackageForm(instance=package)

    context = {
        'title': f'Ubah Paket: {package.name}',
        'form': form,
        'package': package,
    }
    return render(request, 'packages/package_form.html', context)


@login_required
@owner_required
def package_toggle_active(request, pk):
    """Mengaktifkan atau menonaktifkan paket dengan aman (tanpa menghapus data)."""
    if request.method == 'POST':
        package = get_object_or_404(Package, pk=pk)
        package.is_active = not package.is_active
        package.save()
        status_text = "diaktifkan" if package.is_active else "dinonaktifkan"
        messages.info(request, f"Paket '{package.name}' berhasil {status_text}.")
    return redirect('package_list')
