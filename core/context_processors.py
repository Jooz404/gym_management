from django.conf import settings


def gym_settings(request):
    """Menyediakan pengaturan identitas gym ke semua template HTML."""
    return {
        'gym_name': getattr(settings, 'GYM_NAME', 'Flex Gym Bitung'),
    }


def feature_flags(request):
    """Menyediakan status feature flag (D-012) ke semua template HTML."""
    return {
        'feature_checkin': getattr(settings, 'FEATURE_CHECKIN', True),
        'feature_reports': getattr(settings, 'FEATURE_REPORTS', True),
        'feature_wa_reminder': getattr(settings, 'FEATURE_WA_REMINDER', True),
    }

