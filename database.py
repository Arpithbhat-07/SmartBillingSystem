import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "billing.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    con = get_connection()
    cur = con.cursor()

    # FY-wise invoice counter
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoice_counter (
        fy TEXT PRIMARY KEY,
        last_no INTEGER
    )
    """)

    # Invoice header
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_invoice (
        invoice_no TEXT PRIMARY KEY,
        fy TEXT,
        invoice_date TEXT,
        gst_type TEXT,
        customer_name TEXT,
        phone TEXT,
        gst_no TEXT,
        address TEXT,
        total_qty INTEGER,
        taxable REAL,
        cgst REAL,
        sgst REAL,
        igst REAL,
        grand_total REAL,
        amount_words TEXT,
        created_at TEXT
    )
    """)

    # Invoice items
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        item_name TEXT,
        hsn TEXT,
        qty REAL,
        rate REAL,
        gst_percent REAL,
        taxable REAL,
        cgst REAL,
        sgst REAL,
        igst REAL,
        total REAL,
        FOREIGN KEY(invoice_no) REFERENCES sales_invoice(invoice_no)
    )
    """)

    con.commit()
    con.close()
def invoice_exists(invoice_no):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM sales_invoice WHERE invoice_no=?", (invoice_no,))
    exists = cur.fetchone() is not None
    con.close()
    return exists

def get_financial_year(date_obj=None):
    if not date_obj:
        date_obj = datetime.now()
    y, m = date_obj.year, date_obj.month
    return f"{y}{str(y+1)[-2:]}" if m >= 4 else f"{y-1}{str(y)[-2:]}"


def generate_invoice_no(prefix="SC"):
    con = get_connection()
    cur = con.cursor()

    fy = get_financial_year()
    cur.execute("SELECT last_no FROM invoice_counter WHERE fy=?", (fy,))
    row = cur.fetchone()

    if row is None:
        next_no = 1
        cur.execute("INSERT INTO invoice_counter VALUES (?,?)", (fy, next_no))
    else:
        next_no = row[0] + 1
        cur.execute("UPDATE invoice_counter SET last_no=? WHERE fy=?", (next_no, fy))

    con.commit()
    con.close()
    return f"{prefix}-{str(next_no).zfill(3)}/{fy}"


def save_invoice(header: dict):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
    INSERT INTO sales_invoice VALUES (
        :invoice_no, :fy, :invoice_date, :gst_type,
        :customer_name, :phone, :gst_no, :address,
        :total_qty, :taxable, :cgst, :sgst, :igst,
        :grand_total, :amount_words, :created_at
    )
    """, header)
    con.commit()
    con.close()


def save_invoice_items(invoice_no, items):
    con = get_connection()
    cur = con.cursor()
    cur.executemany("""
    INSERT INTO sales_invoice_items (
        invoice_no, item_name, hsn, qty, rate, gst_percent,
        taxable, cgst, sgst, igst, total
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, items)
    con.commit()
    con.close()


def get_all_sales_invoices():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
    SELECT invoice_no, invoice_date, customer_name, gst_type, grand_total
    FROM sales_invoice ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def get_invoice_header(invoice_no):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM sales_invoice WHERE invoice_no=?", (invoice_no,))
    row = cur.fetchone()
    con.close()
    return row


def get_invoice_items(invoice_no):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
    SELECT item_name, hsn, qty, rate, gst_percent,
           taxable, cgst, sgst, igst, total
    FROM sales_invoice_items WHERE invoice_no=?
    """, (invoice_no,))
    rows = cur.fetchall()
    con.close()
    return rows

def delete_invoice(invoice_no):
    con = get_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM sales_invoice_items WHERE invoice_no=?", (invoice_no,))
    cur.execute("DELETE FROM sales_invoice WHERE invoice_no=?", (invoice_no,))

    con.commit()
    con.close()



