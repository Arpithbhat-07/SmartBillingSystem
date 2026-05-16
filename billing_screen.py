from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit,
    QComboBox, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QDesktopServices
from datetime import datetime
import os

from pdf_invoice import generate_invoice_pdf
from database import (
    generate_invoice_no, save_invoice, save_invoice_items,
    get_financial_year, get_invoice_header, get_invoice_items,
    invoice_exists, delete_invoice
)


class BillingScreen(QMainWindow):
    def __init__(self, view_only=False, invoice_no=None):
        super().__init__()
        self.view_only = view_only
        self.loaded_invoice_no = invoice_no
        self.updating = False

        self.setWindowTitle("Sales Invoice")
        self.showMaximized()

        # ================= MAIN =================
        central = QWidget()
        main = QVBoxLayout(central)
        main.setSpacing(10)

        # ================= TOP =================
        top = QHBoxLayout()
        top.addWidget(QLabel("<b>SALES INVOICE</b>"))
        top.addStretch()

        self.invoice_no = QLineEdit()
        self.invoice_date = QDateEdit(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)

        self.gst_type = QComboBox()
        self.gst_type.addItems(["CGST+SGST", "IGST"])
        self.gst_type.currentIndexChanged.connect(self.on_gst_type_changed)

        inv = QGridLayout()
        inv.addWidget(QLabel("Invoice No"), 0, 0)
        inv.addWidget(self.invoice_no, 0, 1)
        inv.addWidget(QLabel("Date"), 1, 0)
        inv.addWidget(self.invoice_date, 1, 1)
        inv.addWidget(QLabel("GST Type"), 2, 0)
        inv.addWidget(self.gst_type, 2, 1)

        top.addLayout(inv)
        main.addLayout(top)

        # ================= MIDDLE =================
        mid = QHBoxLayout()

        # -------- CUSTOMER --------
        cust = QGridLayout()
        cust.addWidget(QLabel("<b>Customer Details</b>"), 0, 0, 1, 2)

        self.c_name = QLineEdit()
        self.c_phone = QLineEdit()
        self.c_gst = QLineEdit()
        self.c_addr = QTextEdit()
        self.c_addr.setFixedHeight(70)

        cust.addWidget(QLabel("Name"), 1, 0)
        cust.addWidget(self.c_name, 1, 1)
        cust.addWidget(QLabel("Phone"), 2, 0)
        cust.addWidget(self.c_phone, 2, 1)
        cust.addWidget(QLabel("GST No"), 3, 0)
        cust.addWidget(self.c_gst, 3, 1)
        cust.addWidget(QLabel("Address"), 4, 0)
        cust.addWidget(self.c_addr, 4, 1)

        cust_box = QVBoxLayout()
        cust_box.addLayout(cust)
        cust_box.addStretch()

        cust_w = QWidget()
        cust_w.setLayout(cust_box)
        cust_w.setFixedWidth(350)

        # -------- TABLE --------
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "Item", "HSN", "Qty", "Rate", "GST %",
            "Taxable", "CGST", "SGST", "IGST", "Total"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.itemChanged.connect(self.on_item_changed)

        # -------- BUTTONS --------
        add_btn = QPushButton("+ Add Item")
        add_btn.clicked.connect(self.add_item_row)

        del_btn = QPushButton("− Delete Item")
        del_btn.clicked.connect(self.delete_item_row)

        save_btn = QPushButton("💾 Save Invoice")
        save_btn.clicked.connect(self.save_invoice_to_db)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        btn_row.addWidget(save_btn)

        table_box = QVBoxLayout()
        table_box.addWidget(self.table)
        table_box.addLayout(btn_row)

        table_w = QWidget()
        table_w.setLayout(table_box)

        mid.addWidget(cust_w)
        mid.addWidget(table_w)
        main.addLayout(mid)

        # -------- AMOUNT IN WORDS --------
        words_row = QHBoxLayout()
        self.amount_words = QLineEdit()
        self.amount_words.setReadOnly(True)
        words_row.addWidget(QLabel("Amount in Words:"))
        words_row.addWidget(self.amount_words)
        main.addLayout(words_row)

        self.setCentralWidget(central)

        # ================= INIT =================
        if view_only:
            self.load_invoice(invoice_no)
            self.lock_all()
        else:
            self.set_new_invoice_no()
            self.add_item_row()
            self.add_gap_and_total_rows()
            self.recalc_totals()

    # ================= HELPERS =================
    def set_new_invoice_no(self):
        self.invoice_no.setText(generate_invoice_no("SC"))

    def is_gap_or_total(self, row):
        return row >= self.table.rowCount() - 2

    # ================= ROWS =================
    def add_gap_and_total_rows(self):
        gap = self.table.rowCount()
        self.table.insertRow(gap)
        for c in range(10):
            self.table.setItem(gap, c, QTableWidgetItem(""))

        total = self.table.rowCount()
        self.table.insertRow(total)
        self.table.setItem(total, 0, QTableWidgetItem("TOTAL"))
        for c in range(1, 10):
            self.table.setItem(total, c, QTableWidgetItem(""))

    def add_item_row(self):
        row = max(0, self.table.rowCount() - 2)
        self.table.insertRow(row)

        for c, v in enumerate(["", "", "1", "0"]):
            self.table.setItem(row, c, QTableWidgetItem(v))

        gst = QComboBox()
        gst.addItems(["0", "5", "12", "18", "28"])
        gst.setCurrentText("18")
        gst.currentIndexChanged.connect(lambda _, r=row: self.recalc_row(r))
        self.table.setCellWidget(row, 4, gst)

        for c in range(5, 10):
            self.table.setItem(row, c, QTableWidgetItem("0.00"))

    def delete_item_row(self):
        row = self.table.currentRow()
        if row < 0 or self.is_gap_or_total(row):
            return
        self.table.removeRow(row)
        self.recalc_totals()

    # ================= GST =================
    def on_gst_type_changed(self):
        igst = self.gst_type.currentText() == "IGST"
        self.table.setColumnHidden(6, igst)
        self.table.setColumnHidden(7, igst)
        self.table.setColumnHidden(8, not igst)
        self.recalc_totals()

    # ================= CALC =================
    def on_item_changed(self, item):
        if self.updating or self.is_gap_or_total(item.row()):
            return
        self.recalc_row(item.row())

    def recalc_row(self, row):
        if self.is_gap_or_total(row):
            return

        self.updating = True
        try:
            qty = float(self.table.item(row, 2).text() or 0)
            rate = float(self.table.item(row, 3).text() or 0)
            gstp = float(self.table.cellWidget(row, 4).currentText())

            taxable = qty * rate
            gst_amt = taxable * gstp / 100

            cgst = sgst = igst = 0
            if self.gst_type.currentText() == "IGST":
                igst = gst_amt
            else:
                cgst = sgst = gst_amt / 2

            self.table.item(row, 5).setText(f"{taxable:.2f}")
            self.table.item(row, 6).setText(f"{cgst:.2f}")
            self.table.item(row, 7).setText(f"{sgst:.2f}")
            self.table.item(row, 8).setText(f"{igst:.2f}")
            self.table.item(row, 9).setText(f"{taxable + gst_amt:.2f}")
        finally:
            self.updating = False
            self.recalc_totals()

    def recalc_totals(self):
        tq = tt = tc = ts = ti = tg = 0

        for r in range(self.table.rowCount() - 2):
            if not self.table.item(r, 2):
                continue
            tq += float(self.table.item(r, 2).text() or 0)
            tt += float(self.table.item(r, 5).text() or 0)
            tc += float(self.table.item(r, 6).text() or 0)
            ts += float(self.table.item(r, 7).text() or 0)
            ti += float(self.table.item(r, 8).text() or 0)
            tg += float(self.table.item(r, 9).text() or 0)

        tr = self.table.rowCount() - 1

        def safe(col, val):
            if not self.table.item(tr, col):
                self.table.setItem(tr, col, QTableWidgetItem(""))
            self.table.item(tr, col).setText(val)

        safe(2, str(int(tq)))
        safe(5, f"{tt:.2f}")
        safe(6, f"{tc:.2f}" if self.gst_type.currentText() == "CGST+SGST" else "")
        safe(7, f"{ts:.2f}" if self.gst_type.currentText() == "CGST+SGST" else "")
        safe(8, f"{ti:.2f}" if self.gst_type.currentText() == "IGST" else "")
        safe(9, f"{tg:.2f}")

        self.amount_words.setText(self.amount_to_words(tg))

    # ================= SAVE =================
    def save_invoice_to_db(self):
        self.recalc_totals()

        inv_no = self.invoice_no.text().strip()

        if invoice_exists(inv_no):
            if QMessageBox.question(
                self, "Replace Invoice",
                f"Invoice '{inv_no}' exists.\nReplace it?",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.No:
                return
            delete_invoice(inv_no)

        try:
            tr = self.table.rowCount() - 1

            header = {
                "invoice_no": inv_no,
                "fy": get_financial_year(),
                "invoice_date": self.invoice_date.date().toString("yyyy-MM-dd"),
                "gst_type": self.gst_type.currentText(),
                "customer_name": self.c_name.text(),
                "phone": self.c_phone.text(),
                "gst_no": self.c_gst.text(),
                "address": self.c_addr.toPlainText(),
                "total_qty": int(self.table.item(tr, 2).text()),
                "taxable": float(self.table.item(tr, 5).text()),
                "cgst": float(self.table.item(tr, 6).text() or 0),
                "sgst": float(self.table.item(tr, 7).text() or 0),
                "igst": float(self.table.item(tr, 8).text() or 0),
                "grand_total": float(self.table.item(tr, 9).text()),
                "amount_words": self.amount_words.text(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            items = []
            for r in range(self.table.rowCount() - 2):
                if not self.table.item(r, 0):
                    continue
                items.append((
                    inv_no,
                    self.table.item(r, 0).text(),
                    self.table.item(r, 1).text(),
                    float(self.table.item(r, 2).text()),
                    float(self.table.item(r, 3).text()),
                    float(self.table.cellWidget(r, 4).currentText()),
                    float(self.table.item(r, 5).text()),
                    float(self.table.item(r, 6).text() or 0),
                    float(self.table.item(r, 7).text() or 0),
                    float(self.table.item(r, 8).text() or 0),
                    float(self.table.item(r, 9).text()),
                ))

            save_invoice(header)
            save_invoice_items(inv_no, items)

        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            return

        if QMessageBox.question(
            self, "Invoice Saved",
            "Invoice saved.\nGenerate PDF?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                path = generate_invoice_pdf(inv_no)
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            except Exception as e:
                QMessageBox.critical(self, "PDF Error", str(e))

        self.reset_form()

    # ================= RESET =================
    def reset_form(self):
        self.c_name.clear()
        self.c_phone.clear()
        self.c_gst.clear()
        self.c_addr.clear()
        self.table.setRowCount(0)
        self.gst_type.setCurrentIndex(0)
        self.set_new_invoice_no()
        self.add_item_row()
        self.add_gap_and_total_rows()
        self.recalc_totals()

    # ================= WORDS =================
    def amount_to_words(self, amount):
        rupees = int(amount)
        paisa = int(round((amount - rupees) * 100))

        ones = ["", "One", "Two", "Three", "Four", "Five", "Six",
                "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
                "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty",
                "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        def convert(n):
            if n < 20: return ones[n]
            if n < 100: return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")
            if n < 1000: return ones[n // 100] + " Hundred " + convert(n % 100)
            if n < 100000: return convert(n // 1000) + " Thousand " + convert(n % 1000)
            if n < 10000000: return convert(n // 100000) + " Lakh " + convert(n % 100000)
            return convert(n // 10000000) + " Crore " + convert(n % 10000000)

        words = f"Rupees {convert(rupees).strip()}"
        if paisa > 0:
            words += f" and {convert(paisa).strip()} Paisa"
        return words + " Only"
