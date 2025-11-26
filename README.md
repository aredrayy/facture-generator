<div align="center">

  <h1>🍫 LChocolat's Invoice Manager</h1>
  
  <p>
    <b>A Modern Desktop Invoicing Solution for LCHOCOLAT SRL</b>
  </p>

  <p>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    </a>
    <a href="https://github.com/TomSchimansky/CustomTkinter">
      <img src="https://img.shields.io/badge/UI-CustomTkinter-2CC985?style=for-the-badge&logo=python&logoColor=white" alt="CustomTkinter">
    </a>
    <a href="https://ec.europa.eu/taxation_customs/vies/">
      <img src="https://img.shields.io/badge/API-EU%20VIES-003399?style=for-the-badge&logo=europe&logoColor=white" alt="EU VIES">
    </a>
  </p>

  <br />
</div>

> **Note:** This tool was built to automate invoice generation for *LCHOCOLAT SRL*, replacing manual PDF editing with a database-driven Python application.

## ✨ Features

This application combines a beautiful **Glass/Dark Mode UI** with powerful automation tools.

* **🎨 Modern UI:** Built with `CustomTkinter` for a sleek, dark-themed, high-DPI interface.
* **🔍 Auto-Fill Client Data:** Connected directly to the **EU VIES Database**. Enter a VAT number (e.g., `BE0894524595`), and it instantly fetches the company name and address.
* **⚡ Live Calculations:** * Input quantity (Kg) and watch totals update instantly.
    * **Adjustable VAT:** Defaults to 6% (Food/Chocolate) but can be modified for other goods.
* **📄 PDF Generation:** Generates professional invoices that exactly match the company's stationery requirements using `FPDF`.
* **💾 Local Database:** All invoices are saved to a local `SQLite` database. You never lose track of a past invoice.
* **📂 File Manager:** View history and open PDFs directly from the app dashboard.

## 📸 Screenshots

![App Screenshot](screenshot.png)

## 🛠️ Tech Stack

* **Language:** Python 3
* **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Wrapper for Tkinter)
* **PDF Engine:** FPDF
* **Database:** SQLite3
* **Network:** Requests (for VIES API)

## 🚀 Installation & Usage

### Option 1: Run from Source

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/chocolate-invoice-manager.git](https://github.com/yourusername/chocolate-invoice-manager.git)
    cd chocolate-invoice-manager
    ```

2.  **Install dependencies:**
    ```bash
    pip install customtkinter fpdf requests
    ```

3.  **Run the app:**
    ```bash
    python chocolate_invoice_modern.py
    ```

## 🏗️ Building the EXE

If you want to compile this yourself using **PyInstaller**, run the following command to ensure all UI assets are bundled correctly:

```bash
pyinstaller --noconsole --onefile --collect-all customtkinter chocolate_invoice_modern.py