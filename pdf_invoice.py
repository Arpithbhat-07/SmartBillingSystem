import os
import sys

def resource_path(relative_path):
    """Works both in normal Python and PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from database import get_invoice_header, get_invoice_items

BASE_DIR = os.path.dirname(__file__)
logo_path = os.path.join(BASE_DIR, "assets", "icon.ico")

# ================= FONT SETUP =================
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(
    TTFont(
        "TimesNew",
        resource_path("assets/times.ttf")
    )
)

pdfmetrics.registerFont(
    TTFont(
        "TimesNewBold",
        resource_path("assets/timesbd.ttf")
    )
)

FONT = "TimesNew"
FONT_BOLD = "TimesNewBold"


# ================= PAGE CONFIG =================
PAGE_W, PAGE_H = A4
LEFT = 12 * mm
TOP = PAGE_H - 12 * mm


# ================= GRID DEFINITIONS =================
COL_WIDTHS = [
    10,  # Sl No
    54,  # Description
    12,  # HSN
    10,  # Qty
    16,  # Rate
    19,  # Taxable
    10,  # GST %
    16,  # CGST
    16,  # SGST
    22,  # Total
]

ROW_H = 7.5 * mm
HEADER_H = 10 * mm

styles = getSampleStyleSheet()

def money(val):
    try:
        return f"₹{float(val):,.2f}"
    except:
        return ""

def draw_wrapped_cell_middle(
    c, x, y, w, h, text,
    align="center", bold=False, fs=9
):
    # Draw cell border
    c.rect(x, y - h, w, h)

    style = styles["Normal"]
    style.fontName = FONT_BOLD if bold else FONT
    style.fontSize = fs
    style.leading = fs + 2
    style.alignment = {
        "left": 0,
        "center": 1,
        "right": 2
    }[align]

    p = Paragraph(text, style)

    # Calculate wrapped text size
    pw, ph = p.wrap(w - 4, h)

    # Vertical middle calculation
    text_y = y - ((h + ph) / 2)

    # Draw text
    p.drawOn(c, x + 2, text_y)




# ================= DRAW HELPERS =================
def draw_cell(c, x, y, w, h, text="", align="left", bold=False, fs=9):
    c.rect(x, y - h, w, h)
    c.setFont(FONT_BOLD if bold else FONT, fs)

    if text:
        if align == "right":
            c.drawRightString(x + w - 2, y - h + 2, text)
        elif align == "center":
            c.drawCentredString(x + w / 2, y - h + 2, text)
        else:
            c.drawString(x + 2, y - h + 2, text)

def resource_path(relative_path):
    """ Get absolute path to resource (works for PyInstaller & normal run) """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ================= MAIN =================
def generate_invoice_pdf(invoice_no):
    header = get_invoice_header(invoice_no)
    items = get_invoice_items(invoice_no)

    (
        inv_no, fy, inv_date, gst_type,
        cname, phone, gstin, addr,
        total_qty, taxable, cgst, sgst, igst,
        grand_total, words, _
    ) = header

    safe_no = invoice_no.replace("/", "-")
    out_dir = os.path.join("invoices", fy)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{safe_no}.pdf")

    c = canvas.Canvas(path, pagesize=A4)
    y = TOP

    # ================= LOGO =================
    logo_path = resource_path("assets/icon.ico")   # change if needed

    logo_width = 35 * mm     # control logo size
    logo_height = 30 * mm

    c.drawImage(
        logo_path,
        LEFT,
        y = TOP - 25 * mm,     # important: image draws from bottom-left
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask="auto"
    )


    # ================= HEADER =================
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(PAGE_W / 2, y, "TAX INVOICE")
    y -= 8 * mm

    c.setFont(FONT_BOLD, 15)
    c.drawCentredString(PAGE_W / 2, y, "TECH SERVICE CENTER")
    y -= 6 * mm

    c.setFont(FONT, 10)
    c.drawCentredString(
        PAGE_W / 2, y,
        "123 Business Avenue, Tech City, Karnataka - 560001"
    )
    y -= 5 * mm

    c.drawCentredString(
        PAGE_W / 2, y,
        "Ph No: 9876543210, 9123456780, 9000000000"
    )
    y -= 5 * mm

    c.drawCentredString(
        PAGE_W / 2, y,
        "State : Karnataka  |  State Code : 29   GSTIN : 29ABCDE1234F1Z5"
    )
    y -= 10 * mm

    # ================= BILL TO / INVOICE =================
    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT, y, "Bill To:")
    y -= ROW_H

    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT + 135 * mm, y, "Invoice No    :")
    c.drawString(LEFT + 160 * mm, y, inv_no)
    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT, y, f"Name     : ")
    c.setFont(FONT, 11)
    c.drawString(LEFT + 17 * mm, y, cname)
    y -= ROW_H

    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT, y, f"Address : ")
    c.setFont(FONT, 11)
    c.drawString(LEFT + 17 * mm, y, addr)
    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT + 135 * mm, y, "Invoice Date :")
    c.setFont(FONT, 11)
    c.drawString(LEFT + 160 * mm, y, inv_date)
    y -= ROW_H

    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT, y, f"Party GSTIN : ")
    c.setFont(FONT, 11)
    c.drawString(LEFT + 26 * mm, y, gstin)
    y -= 6 * mm

    # ================= TABLE HEADER =================
    x = LEFT
    headers = [
        "Sl No", "Description", "HSN Code", "Qty", "Rate",
        "Taxable Value", "GST Rate",
        "IGST Amount" if gst_type == "IGST" else "CGST Amount",
        "" if gst_type == "IGST" else "SGST Amount",
        "Total Amount"
    ]

    for i, htxt in enumerate(headers):
        w = COL_WIDTHS[i] * mm
        if gst_type == "IGST" and i == 8:
            continue
        draw_wrapped_cell_middle(c, x, y, w, HEADER_H, htxt, "center", True)
        x += w

    y -= HEADER_H

    # ================= ITEM ROWS =================
    max_rows = 10
    for idx in range(max_rows):
        x = LEFT
        if idx < len(items):
            (
                name, hsn, qty, rate, gstp,
                tx, cg, sg, ig, tot
            ) = items[idx]
        else:
            name = hsn = ""
            qty = rate = gstp = tx = cg = sg = ig = tot = ""

        row = [
            str(idx+1) if name else "",
            name,
            hsn,

            str(int(qty)) if qty else "",

            money(rate),

            money(tx),

            f"{gstp:.0f}%" if gstp else "",

            money(ig) if gst_type=="IGST"
            else money(cg),

            "" if gst_type=="IGST"
            else money(sg),

            money(tot)
        ]

        for i, val in enumerate(row):
            if gst_type == "IGST" and i == 8:
                continue
            w = COL_WIDTHS[i] * mm
            if i in (0, 2, 3, 6):           # Sl No, HSN, Qty
                align = "center"
            elif i >= 3:             # numeric columns
                align = "right"
            else:                    # text columns
                align = "left"
            draw_wrapped_cell_middle(
                c, x, y, w, ROW_H,
                val,
                align=align,
                fs=10
            )
            x += w

        y -= ROW_H

    # ================= TOTALS =================
    y -= 6.5 * mm
    c.setFont(FONT_BOLD, 10)
    c.drawRightString(LEFT + 162 * mm, y, "Untaxed Amount :")
    c.setFont(FONT, 10)
    c.drawRightString(LEFT + 180 * mm, y, money(taxable))
    y -= ROW_H

    c.setFont(FONT_BOLD, 10)
    tax_amt = igst if gst_type == "IGST" else (cgst + sgst)
    c.drawRightString(LEFT + 162 * mm, y, "Tax Amount :")
    c.setFont(FONT, 10)
    c.drawRightString(LEFT + 180 * mm, y, money(tax_amt))
    y -= ROW_H

    c.setFont(FONT_BOLD, 12)
    c.drawRightString(LEFT + 162 * mm, y, "Total Amount :")
    c.drawRightString(LEFT + 180 * mm, y, money(grand_total))
    y -= 10 * mm

    # ================= IN WORDS =================
    c.setFont(FONT_BOLD, 12)
    c.drawString(LEFT, y, "In Words :")
    c.drawString(LEFT + 25 * mm, y, words)
    y -= 15 * mm

    # ================= BANK DETAILS =================
    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT, y, "Bank Details:")
    y -= ROW_H

    c.setFont(FONT, 11)
    c.drawString(LEFT, y, "Bank Name : Demo Bank")
    y -= ROW_H
    c.drawString(LEFT, y, "Account Number : XXXX123456789")
    y -= ROW_H
    c.drawString(LEFT, y, "Branch : Demo Branch")
    y -= ROW_H
    c.drawString(LEFT, y, "IFSC Code : DEMO000123")
    y -= 12 * mm

    # ================= TERMS =================
    c.setFont(FONT_BOLD, 11)
    c.drawString(LEFT, y, "Terms And Conditions:")
    y -= ROW_H

    c.setFont(FONT, 11)
    terms = [
        "1. Products once delivered are subject to company policies.",
        "2. Warranty Gives Is On Behalf Of Company.",
        "3. All Disputes Subject To Bangalore Jurisdiction.",
        "4. Interest @24% Will Be Charged If Not Paid Within Due Date."
    ]

    for t in terms:
        c.drawString(LEFT, y, t)
        y -= ROW_H

    # ================= FOOTER =================
    

    c.save()
    return path