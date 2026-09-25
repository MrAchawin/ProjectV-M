import os
import tkinter as tk
from PIL import Image, ImageTk
from config import ASSETS_DIR


def render_category(root, title_text, accent_color, products, reserved_quantities, on_select, on_back):
    if not callable(on_select) or not callable(on_back):
        raise ValueError("on_select and on_back must be callable")

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#0f172a")
    root.title(f"CARD DROP / {title_text}")

    header = tk.Frame(root, bg="#0f172a")
    header.pack(fill="x", padx=25, pady=(20, 10))
    tk.Label(header, text=title_text, font=("Segoe UI", 24, "bold"), bg="#0f172a", fg=accent_color).pack(anchor="w")
    tk.Label(header, text="เลือกชุดการ์ดสะสมลงตะกร้า", font=("Segoe UI", 10), bg="#0f172a", fg="#94a3b8").pack(anchor="w")
    tk.Button(
        root, text="← กลับหน้าหลัก", font=("Segoe UI", 10, "bold"),
        bg="#1e293b", fg="#f8fafc", activebackground="#334155",
        relief="flat", padx=12, pady=6, cursor="hand2", command=on_back,
    ).pack(anchor="w", padx=25, pady=(5, 10))

    frame = tk.Frame(root, bg="#0f172a")
    frame.pack(fill="both", expand=True, padx=20, pady=10)
    for column in range(3):
        frame.grid_columnconfigure(column, weight=1)

    reserved_quantities = reserved_quantities or {}
    image_refs = []
    for index, (_, name, _, price, stock, image_path) in enumerate(products):
        available = max(0, stock - reserved_quantities.get(name, 0))
        card = tk.Frame(frame, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
        card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=8, pady=8)

        image_box = tk.Frame(card, bg="#eeeff3", height=180)
        image_box.pack(fill="x", padx=10, pady=(10, 5))
        image_box.pack_propagate(False)
        path = image_path if os.path.isabs(image_path) else os.path.join(ASSETS_DIR, image_path)
        try:
            image = Image.open(path)
            image.thumbnail((160, 165), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_refs.append(photo)
            image_label = tk.Label(image_box, image=photo, bg="#0b0f19")
            image_label.image = photo
            image_label.pack(expand=True)
        except (OSError, ValueError):
            tk.Label(image_box, text="ไม่มีรูปภาพ", bg="#f3f3f3", fg="#64748b").pack(expand=True)

        tk.Label(card, text=name, font=("Segoe UI", 11, "bold"), bg="#1e293b", fg="#f8fafc", wraplength=180).pack(padx=8, pady=(5, 2))
        tk.Label(
            card, text=f"฿ {price}  |  เหลือ {available} ชิ้น",
            font=("Segoe UI", 9, "bold"), bg="#1e293b",
            fg="#4ade80" if available else "#f87171",
        ).pack(pady=(0, 10))
        tk.Button(
            card,
            text="เลือกสินค้า" if available else "สินค้าหมด",
            state="normal" if available else "disabled",
            bg=accent_color if available else "#475569",
            fg="#0f172a" if available else "#94a3b8",
            activebackground="#fde047", relief="flat",
            cursor="hand2" if available else "arrow",
            command=lambda n=name, p=price: on_select({"name": n, "price": p}),
        ).pack(fill="x", padx=12, pady=(0, 14))

    return image_refs