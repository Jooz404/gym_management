from functools import wraps
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def feature_required(flag_name):
    """
    Decorator untuk memproteksi view berdasarkan Feature Flag (D-012).
    Jika flag dimatikan, akses URL langsung ditolak.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            is_enabled = getattr(settings, flag_name, True)
            if not is_enabled:
                raise PermissionDenied("Fitur ini dinonaktifkan dalam paket sistem gym Anda.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def role_required(*allowed_roles):
    """
    Decorator untuk membatasi akses view berdasarkan peran (owner/staff).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman tersebut.")
            raise PermissionDenied("Akses ditolak: peran Anda tidak memiliki izin.")
        return _wrapped_view
    return decorator


def owner_required(view_func):
    """Shortcut decorator khusus peran Pemilik (Owner)."""
    return role_required('owner')(view_func)

