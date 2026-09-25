import os
import tkinter as tk
from PIL import Image, ImageTk
from config import ASSETS_DIR
from database import init_db, get_all_products, get_all_products_full, get_products
from popups import Alert, Checkout, open_admin_window

# เริ่มต้นระบบฐานข้อมูล (ถ้ายังไม่มีจะสร้างให้อัตโนมัติ)
init_db()

class VendingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ตู้การ์ดเกมมาครับอ้าย")
        self.root.geometry("850x800")
        self.root.configure(bg="#0f172a")
        
        self.cart = {}
        self.current_cat = "สินค้าทั้งหมด"
        self.image_refs = []  # ป้องกันไม่ให้รูปภาพหาย (Garbage Collection)
        
        self.UI()

    def UI(self):
        top_frame = tk.Frame(self.root, bg="#1e293b", height=80)
        top_frame.pack(fill="x")
        cat_frame = tk.Frame(top_frame, bg="#1e293b")
        cat_frame.pack(side="left", padx=15, pady=15)
        self.cat_buttons = {}
        for cat in ["สินค้าทั้งหมด", "One Piece", "Pokemon", "Vanguard"]:
            btn = tk.Button(cat_frame, text=cat, font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=10, cursor="hand2",
                            command=lambda c=cat: self.Category(c))
            btn.pack(side="left", padx=6)
            self.cat_buttons[cat] = btn

        tk.Button(top_frame, text="เติมสินค้า", bg="#041C3F", fg="#4ade80", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=10, cursor="hand2",
                  command=lambda: open_admin_window(self)).pack(side="right", padx=20, pady=15)
        self.center_frame = tk.Frame(self.root, bg="#0f172a")
        self.center_frame.pack(fill="both", expand=True, padx=15, pady=5)
        bottom_frame = tk.Frame(self.root, bg="#1e293b", height=90)
        bottom_frame.pack(fill="x")
        self.lbl_cart_total = tk.Label(bottom_frame, text="0 THB", font=("Segoe UI", 16, "bold"), fg="#4ade80", bg="#1e293b")
        self.lbl_cart_total.pack(side="left", padx=30, pady=25)
        tk.Button(bottom_frame, text="ตะกร้าสินค้า", bg="#041C3F", fg="#4ade80", font=("Segoe UI", 12, "bold"), relief="flat", padx=25, pady=12, cursor="hand2",
                  command=lambda: Checkout(self)).pack(side="right", padx=25, pady=15)

        # โหลดหน้าแรก
        self.Category("สินค้าทั้งหมด")

    def Category(self, cat):
        self.current_cat = cat
        for c, btn in self.cat_buttons.items():
            btn.config(bg="#fbbf24" if c == cat else "#334155", fg="#0f172a" if c == cat else "#f8fafc")
        self.Refresh_Ui()

    def Refresh_Ui(self):
        total_price = sum(i["price"] * i["qty"] for i in self.cart.values())
        self.lbl_cart_total.config(text=f"{total_price} THB")
        for w in self.center_frame.winfo_children(): 
            w.destroy()
        self.image_refs.clear()
        canvas = tk.Canvas(self.center_frame, bg="#0f172a", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.center_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#0f172a")
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        
        products = get_all_products_full() if self.current_cat == "สินค้าทั้งหมด" else get_products(self.current_cat)
        reserved = {n: i["qty"] for n, i in self.cart.items()}

        for index, (_, name, _, price, stock, img_path) in enumerate(products):
            avail = max(0, stock - reserved.get(name, 0))
            
            card = tk.Frame(scrollable, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
            columns_per_row = 5
            card.grid(row=index // columns_per_row, column=index % columns_per_row, sticky="nsew", padx=15, pady=12)
            content_frame = tk.Frame(card, bg="#1e293b")
            content_frame.pack(side="top", fill="both", expand=True)
            full_path = img_path if os.path.isabs(img_path) else os.path.join(ASSETS_DIR, img_path)
            try:
                img = Image.open(full_path)
                img.thumbnail((160, 160), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_refs.append(photo)
                tk.Label(content_frame, image=photo, bg="#1e293b").pack(pady=10)
            except:
                tk.Label(content_frame,  bg="#1e293b", fg="#64748b", height=10).pack()
            tk.Label(content_frame, text=name, font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#f8fafc", wraplength=250, height=2).pack(pady=(0, 5))
            btn_text = f"+ {price} THB" if avail > 0 else "สินค้าหมด"
            btn_bg = "#fbbf24" if avail > 0 else "#475569"
            btn_state = "normal" if avail > 0 else "disabled"
            cursor_style = "hand2" if avail > 0 else "arrow"
            tk.Button(card, text=btn_text, bg=btn_bg, fg="#0f172a" if avail > 0 else "white",
                      font=("Segoe UI", 10, "bold"), relief="flat", cursor=cursor_style, state=btn_state,
                      command=lambda n=name, p=price: self.add_cart(n, p)).pack(side="bottom", fill="x", padx=15, pady=(0, 15))

    def add_cart(self, name, price):
        stock = next((s for n, s in get_all_products() if n == name), 0)
        if self.cart.get(name, {}).get("qty", 0) >= stock:
            Alert(self.root, "สินค้าหมด", "สินค้าเหลือไม่พอ", "warning")
            return
        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {"price": price, "qty": 1}
            
        self.Refresh_Ui()
if __name__ == "__main__":
    root = tk.Tk()
    app = VendingApp(root)
    root.mainloop()