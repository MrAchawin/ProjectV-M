import os
import sqlite3
from config import BASE_DIR

DB_NAME = os.path.join(BASE_DIR, "vending.db")

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """สร้างตารางและข้อมูลเริ่มต้นถ้ายังไม่มีฐานข้อมูล"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            category TEXT,
            price INTEGER,
            stock INTEGER,
            image TEXT
        )
    """)
    
    # เช็คว่ามีคอลัมน์ image หรือยัง (เผื่ออัปเดตจากเวอร์ชันเก่า)
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(products)")}
    if "image" not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN image TEXT")

    initial_data = [
        ("One Piece OP-12", "One Piece", 1750, 10, "onepiece op12.jpg"),
        ("One Piece OP-13", "One Piece", 1750, 10, "onepiece op13.jpg"),
        ("One Piece OP-14", "One Piece", 1750, 10, "onepiece op14.jpg"),
        ("One Piece OP-15", "One Piece", 1750, 10, "onepiece op15.jpg"),
        ("One Piece OP-16", "One Piece", 1750, 10, "onepiece op16.jpg"),
        ("One Piece OP-17", "One Piece", 1750, 5, "onepiece op17.jpg"),
        ("Pokemon Box 01", "Pokemon", 1200, 8, "pokemon01.jpg"),
        ("Pokemon Box 02", "Pokemon", 1200, 8, "pokemon02.jpg"),
        ("Pokemon Box 03", "Pokemon", 1200, 4, "pokemon03.jpg"),
        ("Pokemon Box 04", "Pokemon", 1200, 10, "pokemon04.jpg"),
        ("Pokemon Box 05", "Pokemon", 1200, 10, "pokemon05.jpg"),
        ("Pokemon Box 06", "Pokemon", 1200, 10, "pokemon06.jpg"),
        ("Vanguard D-CP01", "Vanguard", 900, 15, "vanguard01.jpg"),
        ("Vanguard D-CP02", "Vanguard", 900, 12, "vanguard02.jpg"),
        ("Vanguard D-CP03", "Vanguard", 900, 6, "vanguard03.jpg"),
        ("Vanguard D-CP04", "Vanguard", 900, 10, "vanguard04.jpg"),
        ("Vanguard D-CP05", "Vanguard", 900, 10, "vanguard05.jpg"),
        ("Vanguard D-CP06", "Vanguard", 900, 10, "vanguard06.jpg"),
    ]
    insert_product = """
        INSERT INTO products (name, category, price, stock, image)
        SELECT ?, ?, ?, ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = ?)
    """
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(insert_product, [(*product, product[0]) for product in initial_data])
        
    conn.commit()
    conn.close()

def get_all_products_full():
    """ดึงข้อมูลสินค้าทั้งหมด (สำหรับหน้าแรก)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, stock, image FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_products(category):
    """ดึงข้อมูลสินค้าแยกตามหมวดหมู่"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, stock, image FROM products WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_products():
    """ดึงแค่ชื่อและสต็อก (ใช้เช็คของตอนหยิบใส่ตะกร้า)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, stock FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_stocks(quantities):
    """ตัดสต็อกทุกรายการ หรือไม่ตัดเลย"""
    if any(qty <= 0 for qty in quantities.values()):
        return False

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        for name, qty in quantities.items():
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE name = ? AND stock >= ?",
                (qty, name, qty),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return False

        conn.commit()
        return True
    finally:
        conn.close()

def refill_products(refills):
    """เติมสต็อกสินค้า (ฝั่งแอดมิน)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    for name, qty in refills.items():
        if qty > 0:
            cursor.execute("UPDATE products SET stock = stock + ? WHERE name = ?", (qty, name))
    conn.commit()
    conn.close()