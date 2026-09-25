from database import get_products
from components import render_category


def open_pokemon_category(root, on_select, on_back, reserved_quantities=None):
    return render_category(
        root, "POKEMON TCG", "#38bdf8", get_products("Pokemon"),
        reserved_quantities, on_select, on_back,
    )