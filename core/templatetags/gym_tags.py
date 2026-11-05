from django import template

register = template.Library()


@register.filter(name='rupiah')
def rupiah(value):
    """
    Format angka integer/float ke format mata uang Rupiah standar Indonesia.
    Contoh:
        0 -> Rp0
        300000 -> Rp300.000
        2835000 -> Rp2.835.000
        15500000 -> Rp15.500.000
    """
    if value is None or value == "":
        return "Rp0"
    try:
        val = int(round(float(value)))
        formatted = f"{val:,}".replace(',', '.')
        return f"Rp{formatted}"
    except (ValueError, TypeError):
        return f"Rp{value}"

