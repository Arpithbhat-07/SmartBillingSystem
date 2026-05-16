import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QLabel, QVBoxLayout, QWidget
)
from PySide6.QtGui import QIcon

from database import init_db
from backup_utils import backup_database
from billing_screen import BillingScreen
from invoice_history import InvoiceHistoryWindow

APP_STYLE = """
/* =========================
   MAIN WINDOW
========================= */
QMainWindow {
    background-color: #1e1e2e;
}

/* =========================
   TEXT / LABELS
========================= */
QLabel {
    color: #e5e7eb;
    font-size: 13px;
}

/* =========================
   BUTTONS
========================= */
QPushButton {
    background-color: #2563eb;
    color: white;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

/* =========================
   INPUT FIELDS
========================= */
QLineEdit, QTextEdit, QDateEdit, QComboBox {
    background-color: #111827;
    color: #e5e7eb;
    border: 1px solid #374151;
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #2563eb;
}

/* =========================
   TABLES
========================= */
QTableWidget {
    background-color: #111827;
    color: #e5e7eb;
    gridline-color: #374151;
    selection-background-color: #2563eb;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #2563eb;
    color: white;
}

/* =========================
   TABLE HEADERS
========================= */
QHeaderView::section {
    background-color: #1f2933;
    color: #e5e7eb;
    padding: 6px;
    border: 1px solid #374151;
    font-weight: bold;
}

/* =========================
   SCROLLBARS (CLEAN)
========================= */
QScrollBar:vertical {
    background: #111827;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #374151;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4b5563;
}
"""



class BillingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Billing System")
        self.setFixedSize(420, 360)
        self.setWindowIcon(QIcon("assets/icon.ico"))

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Smart Billing System")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        layout.addWidget(title)

        btn_invoice = QPushButton("New Sales Invoice")
        btn_invoice.clicked.connect(self.open_sales_invoice)

        btn_history = QPushButton("Invoice History")
        btn_history.clicked.connect(self.open_invoice_history)

        layout.addWidget(btn_invoice)
        layout.addWidget(btn_history)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.statusBar().showMessage("Ready")

    def open_sales_invoice(self):
        self.invoice_window = BillingScreen()
        self.invoice_window.show()

    def open_invoice_history(self):
        self.history_window = InvoiceHistoryWindow()
        self.history_window.show()

if __name__ == "__main__":
    init_db()
    backup_database()

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    window = BillingApp()
    window.show()
    sys.exit(app.exec())
