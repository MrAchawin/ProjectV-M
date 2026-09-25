import os
import tkinter as tk
from PIL import Image, ImageTk
from config import ADMIN_PIN, ASSETS_DIR
from database import update_stocks, get_all_products, refill_products

def Alert(parent, title, message, type_="info"):
    """หน้าต่างแจ้งเตือน (สำเร็จ, ผิดพลาด, เตือน)"""
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("340x180")
    win.config(bg="#1e293b")
    win.transient(parent)
    win.grab_set()
    
    # กำหนดสีตามประเภทของแจ้งเตือน
    colors = {"success": "#4ade80", "warning": "#fbbf24", "error": "#f87171", "info": "#38bdf8"}
    color = colors.get(type_, "#38bdf8")

    tk.Label(win, text=title, font=("Segoe UI", 13, "bold"), fg=color, bg="#1e293b").pack(pady=(20, 5))
    tk.Label(win, text=message, font=("Segoe UI", 10), fg="#94a3b8", bg="#1e293b", wraplength=280).pack(pady=5)
    tk.Button(win, text="ตกลง", bg=color, fg="#0f172a", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, command=win.destroy).pack(pady=15)

def Checkout(app):
    """หน้าสรุปตะกร้าสินค้า"""
    if not app.cart:
        Alert(app.root, "ตะกร้าว่าง", "ยังไม่มีสินค้าในตะกร้าของคุณเลยนะครับ", "info")
        return

    win = tk.Toplevel(app.root)
    win.title("ชำระเงินสินค้า")
    win.geometry("420x420")
    win.config(bg="#1e293b")
    win.transient(app.root)
    win.grab_set()

    tk.Label(win, text="รายการสินค้าในตะกร้า", font=("Segoe UI", 14, "bold"), bg="#1e293b", fg="#f8fafc").pack(pady=15)
    
    list_frame = tk.Frame(win, bg="#0f172a", highlightbackground="#334155", highlightthickness=1)
    list_frame.pack(fill="both", expand=True, padx=25, pady=5)
    # คิดตัง
    total = sum(info["price"] * info["qty"] for info in app.cart.values())
    for name, info in app.cart.items():
        sub = info["price"] * info["qty"]
        tk.Label(list_frame, text=f"{name}  (x{info['qty']})  =  {sub} THB", font=("Segoe UI", 10), bg="#0f172a", fg="#cbd5e1").pack(anchor="w", padx=15, pady=6)

    tk.Label(win, text=f"ยอดชำระ: {total} THB", font=("Segoe UI", 13, "bold"), fg="#4ade80", bg="#1e293b").pack(pady=12)

    def proceed_to_qr():
        # ตรวจสอบสต็อกก่อนเปิดหน้าชำระเงิน
        for name, info in app.cart.items():
            stock = next((s for n, s in get_all_products() if n == name), 0)
            if info["qty"] > stock:
                win.destroy()
                Alert(app.root, "สต็อกเปลี่ยนแปลง", f"สินค้า {name} มีจำนวนไม่พอ กรุณาตรวจสอบตะกร้าอีกครั้ง", "warning")
                app.cart.clear()
                app.Refresh_Ui()
                return
        win.destroy()
        open_qr_payment_window(app, total)

    tk.Button(win, text="ยืนยันการชำระเงิน", bg="#10b981", fg="#ffffff", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", command=proceed_to_qr).pack(fill="x", padx=25, pady=15)

def open_qr_payment_window(app, total):
    # หน้าสแกน
    win = tk.Toplevel(app.root)
    win.title("สแกนชำระเงิน")
    win.geometry("380x480")
    win.config(bg="#1e293b")
    win.transient(app.root)
    win.grab_set()

    tk.Label(win, text="สแกน QR Code เพื่อชำระเงิน", font=("Segoe UI", 14, "bold"), bg="#1e293b", fg="#f8fafc").pack(pady=(20, 10))
    tk.Label(win, text=f"ยอดชำระ: {total} THB", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#4ade80").pack(pady=(0, 15))

    # โหลดรูป QR Code
    try:
        qr_path = os.path.join(ASSETS_DIR, "QR.jpg")
        img = Image.open(qr_path)
        img.thumbnail((220, 220), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        qr_label = tk.Label(win, image=photo, bg="#1e293b")
        qr_label.image = photo 
        qr_label.pack(pady=10)
    except:
        tk.Label(win, text="[ไม่มีรูป QR.jpg]", font=("Segoe UI", 10), bg="#1e293b", fg="#f87171", width=25, height=10).pack(pady=10)

    def confirm_payment():
        if not update_stocks({name: info["qty"] for name, info in app.cart.items()}):
            win.destroy()
            Alert(app.root, "สต็อกเปลี่ยนแปลง", "สินค้าในตะกร้ามีจำนวนไม่พอ กรุณาตรวจสอบรายการอีกครั้ง", "warning")
            app.cart.clear()
            app.Refresh_Ui()
            return

        win.destroy()
        Alert(app.root, "สำเร็จ", "ชำระเงินเรียบร้อยแล้ว กรุณารับสินค้าที่ช่องรับสินค้า", "success")
        app.cart.clear()
        app.Refresh_Ui()

    btn_frame = tk.Frame(win, bg="#1e293b")
    btn_frame.pack(fill="x", padx=30, pady=15)

    tk.Button(btn_frame, text="ยกเลิก", bg="#475569", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", command=win.destroy).pack(side="left", expand=True, fill="x", padx=(0, 5))
    tk.Button(btn_frame, text="ชำระเงินสำเร็จ", bg="#10b981", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", command=confirm_payment).pack(side="right", expand=True, fill="x", padx=(5, 0))

def open_admin_window(app):
    """หน้าล็อกอินเข้าหลังบ้านเอาไว้เติมของอย่างเดียว"""
    win = tk.Toplevel(app.root)
    win.title("เติมของ")
    win.geometry("320x190")
    win.config(bg="#1e293b")
    win.transient(app.root)
    win.grab_set()

    tk.Label(win, text="รหัสผ่าน", font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#f8fafc").pack(pady=(20, 5))
    entry = tk.Entry(win, show="*", font=("Segoe UI", 12), justify="center", bg="#0f172a", fg="#f8fafc", insertbackground="white")
    entry.pack(fill="x", padx=30, pady=10)
    entry.focus()

    def verify():
        if entry.get() == ADMIN_PIN:
            win.destroy()
            open_admin_dashboard(app)
        else:
            Alert(win, "ผิดพลาด", "รหัสไม่ถูกต้อง", "error")
            entry.delete(0, tk.END)

    tk.Button(win, text="เข้าสู่ระบบ", bg="#3b82f6", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", command=verify).pack(fill="x", padx=30, pady=5)

def open_admin_dashboard(app):
    """หน้าระบบจัดการตู้สินค้า (บวก/ลบสต็อก)"""
    win = tk.Toplevel(app.root)
    win.title("จัดการตู้สินค้า")
    win.geometry("480x450")
    win.config(bg="#1e293b")
    win.transient(app.root)
    win.grab_set()

    tk.Label(win, text="เปิดตู้เติมสินค้า", font=("Segoe UI", 14, "bold"), bg="#1e293b", fg="#f8fafc").pack(pady=15)
    stock_container = tk.Frame(win, bg="#0f172a", highlightbackground="#334155", highlightthickness=1)
    stock_container.pack(fill="both", expand=True, padx=20, pady=5)

    vars_ = {}
    for name, stock in get_all_products():
        row = tk.Frame(stock_container, bg="#0f172a")
        row.pack(fill="x", padx=10, pady=5)
        
        tk.Label(row, text=name, font=("Segoe UI", 10), width=22, anchor="w", bg="#0f172a", fg="#f8fafc").pack(side="left")
        tk.Label(row, text=f"มี: {stock}", font=("Segoe UI", 9), width=8, bg="#0f172a", fg="#94a3b8").pack(side="left")
        
        q = tk.IntVar(value=0)
        vars_[name] = q
        
        tk.Button(row, text="-", width=2, bg="#334155", fg="#f8fafc", command=lambda v=q: v.set(max(0, v.get()-1))).pack(side="right", padx=2)
        tk.Label(row, textvariable=q, width=3, font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#f8fafc").pack(side="right", padx=2)
        tk.Button(row, text="+", width=2, bg="#334155", fg="#f8fafc", command=lambda v=q: v.set(v.get()+1)).pack(side="right", padx=2)

    def save():
        refills = {n: q.get() for n, q in vars_.items()}
        if any(refills.values()):
            refill_products(refills)
            Alert(app.root, "สำเร็จ", "อัปเดตสต็อกเรียบร้อยแล้ว", "success")
            app.Refresh_Ui()
        win.destroy()

    tk.Button(win, text="บันทึกข้อมูล", bg="#10b981", fg="#ffffff", font=("Segoe UI", 11, "bold"), relief="flat", command=save).pack(fill="x", padx=20, pady=15)