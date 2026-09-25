from database import get_products
from components import render_category


def open_one_piece_category(root, on_select, on_back, reserved_quantities=None):
    return render_category(
        root, "ONE PIECE CARD GAME", "#fbbf24", get_products("One Piece"),
        reserved_quantities, on_select, on_back,
    )