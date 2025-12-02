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
     <a href="https://nominatim.org/">
      <img src="https://img.shields.io/badge/Maps-Nominatim-green?style=for-the-badge&logo=openstreetmap&logoColor=white" alt="OpenStreetMap">
    </a>
  </p>

  <br />
</div>

> **Note:** This tool was built to automate invoice generation for *LCHOCOLAT SRL*, replacing manual PDF editing with a database-driven Python application.

## ✨ Features

This application combines a beautiful **Glass/Dark Mode UI** with powerful automation tools.

### 🧠 Smart Data Entry
* **🔍 VIES Integration:** Enter a VAT number (e.g., `BE0894524595`) to auto-fill the client's name and address using the EU database.
* **🗺️ Address Autocomplete:** Powered by **OpenStreetMap (Nominatim)**. Type a partial street name and let the app find the correct Street, Zip Code, and City.
* **📅 Date Picker:** Select invoice dates via a popup calendar or default to today.

### ⚡ Flexible Pricing & Calculations
* **⚖️ Weight vs. Fixed Price:** Switch between **Price per Kg** (default) or **Manual Price Override** (for services/fixed sets).
* **📝 Product Customization:** Rename "CHOCOLATES" to "PRALINES", "SERVICE", or any other custom text.
* **🔢 Dynamic IDs:** Auto-incrementing invoice numbers with the ability to manually override/backdate if needed.

### 📄 Professional Output
* **🖨️ Dynamic PDF Generation:** The invoice table automatically adapts columns based on the mode (hides "Quantity" column for fixed-price items).
* **💾 Database History:** Every invoice is saved to a local `SQLite` database.
* **❌ Management:** View history, open PDFs instantly, or delete incorrect entries directly from the interface.

## 📸 Screenshots

![App Screenshot](screenshot.png)

## 🛠️ Tech Stack

* **Language:** Python 3
* **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **PDF Engine:** FPDF
* **Date Picker:** tkcalendar
* **Database:** SQLite3
* **APIs:** EU VIES (Tax) & Nominatim (Maps)

## 🚀 Installation & Usage

### Option 1: Run from Source

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/chocolate-invoice-manager.git](https://github.com/yourusername/chocolate-invoice-manager.git)
    cd chocolate-invoice-manager
    ```

2.  **Install dependencies:**
    ```bash
    pip install customtkinter fpdf requests tkcalendar babel
    ```

3.  **Run the app:**
    ```bash
    python chocolate_invoice_modern.py
    ```

### Option 2: Run as Executable (Windows)

No Python installed? No problem.
1.  Go to the **Releases** page.
2.  Download `chocolate_invoice.exe`.
3.  Double-click to run.

---

## 🏗️ Building the EXE

If you want to compile this yourself using **PyInstaller**, you must use the following command to ensure all UI and Calendar assets are bundled correctly:

```bash
python -m PyInstaller --noconsole --onefile --collect-all customtkinter --collect-all tkcalendar --collect-all babel chocolate_invoice.py