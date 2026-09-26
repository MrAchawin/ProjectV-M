from database import get_products
from components import render_category


def vangurd(root, on_select, on_back, reserved_quantities=None):
    return render_category(
        root, "CARDFIGHT!! VANGUARD", "#f43f5e", get_products("Vanguard"),
        reserved_quantities, on_select, on_back,
    )