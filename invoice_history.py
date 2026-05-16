from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel
)
from PySide6.QtCore import Qt

from database import get_all_sales_invoices
from billing_screen import BillingScreen
from PySide6.QtWidgets import QPushButton, QMessageBox
from database import delete_invoice


class InvoiceHistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice History")
        self.resize(900, 500)

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("Sales Invoice History")
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Invoice No", "Date", "Customer", "GST Type", "Total"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.open_invoice)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        layout.addWidget(self.table)
        self.setCentralWidget(central)
        btn_delete = QPushButton("🗑 Delete Invoice")
        btn_delete.clicked.connect(self.delete_selected_invoice)
        layout.addWidget(btn_delete)

        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        for row_data in get_all_sales_invoices():
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(row_data):
                item = QTableWidgetItem(str(val))
                if c == 4:
                    item.setTextAlignment(Qt.AlignRight)
                self.table.setItem(r, c, item)

    def open_invoice(self, row, col):
        invoice_no = self.table.item(row, 0).text()
        self.viewer = BillingScreen(view_only=True, invoice_no=invoice_no)
        self.viewer.show()

    def delete_selected_invoice(self):
        selected_rows = set(
            index.row() for index in self.table.selectedIndexes()
        )

        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select one or more invoices to delete."
            )
            return

        invoice_nos = []
        for row in selected_rows:
            invoice_nos.append(self.table.item(row, 0).text())

        invoice_list = "\n".join(invoice_nos)

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete the following invoices?\n\n"
            f"{invoice_list}\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        for inv_no in invoice_nos:
            delete_invoice(inv_no)

        self.load_data()

        QMessageBox.information(
            self,
            "Deleted",
            f"{len(invoice_nos)} invoice(s) deleted successfully."
        )
