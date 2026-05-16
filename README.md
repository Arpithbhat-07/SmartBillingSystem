# Smart Billing System

A desktop billing and invoice management application built with Python for service centers and small businesses. The system supports invoice creation, GST calculation, invoice history, PDF generation, and customer billing management through a clean GUI.

---

## Features

### Invoice Management

- Create sales invoices
- Auto-generated invoice numbering
- Custom invoice number support
- Duplicate invoice detection
- Replace existing invoices
- Customer information management
- GST type selection:
  - CGST + SGST
  - IGST

### Item Management

- Add multiple products/services
- Quantity and rate entry
- Automatic GST calculations
- Automatic totals calculation
- Amount in words conversion

### Invoice History

- View all invoices
- Search invoices
- Open invoice details
- Delete invoices
- Multi-select invoice deletion

### PDF Generation

- Professional invoice PDF export
- Excel-style invoice layout
- Times New Roman formatting
- Company logo support
- GST-compatible invoice structure
- Auto-open generated PDF

### Database Features

- SQLite database storage
- Invoice persistence
- Item storage
- Financial-year invoice numbering

---

## Technologies Used

- Python 3
- PySide6
- SQLite
- ReportLab
- PyInstaller

---

## Project Structure

```text
SmartBillingSystem/
│
├── assets/
│   ├── logo.png
│   └── app.ico
│
├── billing_screen.py
├── database.py
├── invoice_history.py
├── pdf_invoice.py
├── backup_utils.py
├── main.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

### Clone repository

```bash
git clone <repo-url>

cd SmartBillingSystem
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

### Run application

```bash
python main.py
```

---

## Author

Arpith

B.E. AIML Student

GitHub:
https://github.com/Arpithbhat-07
