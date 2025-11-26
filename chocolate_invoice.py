import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
import requests
from fpdf import FPDF
import os
import platform
import subprocess

# --- CONFIGURATION ---
MY_COMPANY_NAME = "LCHOCOLAT SRL"
MY_VAT = "BE 0704 898 010"
MY_IBAN = "BE16 0689 1091 2374"
MY_BIC = "GKCCBEBB"
MY_ADDRESS = "55, Avenue du Prince Héritier, 1200 BRUXELLES"
MY_CONTACT = "Tel: 0478.428.310 | office@lchocolat.com"
PRICE_PER_KG = 99.90

# --- THEME SETUP ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernInvoiceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("LCHOCOLAT Invoice Manager")
        self.geometry("1000x700")
        self.resizable(False, False)

        # Initialize Database
        self.init_db()

        # --- LAYOUT (Grid) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR (Inputs) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="LCHOCOLAT\nMANAGER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. Client Lookup Section
        self.lbl_client = ctk.CTkLabel(self.sidebar_frame, text="Client Details (Auto-fill)", anchor="w")
        self.lbl_client.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        self.entry_vat = ctk.CTkEntry(self.sidebar_frame, placeholder_text="VAT (e.g. BE0894524595)")
        self.entry_vat.grid(row=2, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.btn_search = ctk.CTkButton(self.sidebar_frame, text="Search VIES Database", command=self.lookup_vat, fg_color="#2A2D2E", border_width=2, border_color="#3B8ED0", text_color="#3B8ED0")
        self.btn_search.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.entry_name = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Client Name")
        self.entry_name.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.entry_address = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Address")
        self.entry_address.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # 2. Product Section
        self.lbl_prod = ctk.CTkLabel(self.sidebar_frame, text="Product Details", anchor="w")
        self.lbl_prod.grid(row=6, column=0, padx=20, pady=(20, 0), sticky="w")

        self.entry_qty = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Quantity (Kg)")
        self.entry_qty.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        self.entry_qty.bind("<KeyRelease>", self.calculate_totals)
        
        # TVA Rate Input (New Feature)
        self.frame_tva = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.frame_tva.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        
        self.lbl_tva_rate = ctk.CTkLabel(self.frame_tva, text="TVA %:", width=50, anchor="w")
        self.lbl_tva_rate.pack(side="left")
        
        self.entry_tva_rate = ctk.CTkEntry(self.frame_tva, width=60)
        self.entry_tva_rate.insert(0, "6") # Default 6%
        self.entry_tva_rate.pack(side="left", padx=5)
        self.entry_tva_rate.bind("<KeyRelease>", self.calculate_totals)

        # Generate Button (Bottom of Sidebar)
        self.btn_generate = ctk.CTkButton(self.sidebar_frame, text="GENERATE & SAVE", command=self.generate_invoice, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_generate.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Live Preview Cards
        self.info_frame = ctk.CTkFrame(self.main_frame, height=150)
        self.info_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_preview_title = ctk.CTkLabel(self.info_frame, text="Live Calculation", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_preview_title.pack(anchor="w", padx=20, pady=(10,5))

        self.lbl_base = ctk.CTkLabel(self.info_frame, text="Base: 0.00 €", font=ctk.CTkFont(size=14))
        self.lbl_base.pack(anchor="w", padx=20)
        
        self.lbl_tva = ctk.CTkLabel(self.info_frame, text="TVA: 0.00 €", font=ctk.CTkFont(size=14))
        self.lbl_tva.pack(anchor="w", padx=20)

        self.lbl_total = ctk.CTkLabel(self.info_frame, text="TOTAL: 0.00 €", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2CC985")
        self.lbl_total.pack(anchor="w", padx=20, pady=(5, 10))

        # History / Files List
        self.history_label = ctk.CTkLabel(self.main_frame, text="Invoice History", font=ctk.CTkFont(size=16, weight="bold"))
        self.history_label.pack(anchor="w", pady=(0, 5))

        # Scrollable list for invoices
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Database")
        self.scroll_frame.pack(fill="both", expand=True)

        # Open Directory Button
        self.btn_open_dir = ctk.CTkButton(self.main_frame, text="📂 Open Output Folder", command=self.open_directory, fg_color="transparent", border_width=1, text_color="gray")
        self.btn_open_dir.pack(fill="x", pady=(10, 0))

        self.load_history()

    # --- LOGIC ---

    def init_db(self):
        self.conn = sqlite3.connect('factures_db.sqlite')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS factures
                          (id INTEGER PRIMARY KEY, date TEXT, client TEXT, vat TEXT, qty REAL, total REAL, filename TEXT)''')
        self.conn.commit()

    def lookup_vat(self):
        vat_input = self.entry_vat.get().strip().upper().replace(" ", "").replace(".", "")
        if not vat_input: return
        country_code, number = vat_input[:2], vat_input[2:]
        url = f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country_code}/vat/{number}"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('isValid'):
                self.entry_name.delete(0, tk.END)
                self.entry_name.insert(0, data.get('name', ''))
                self.entry_address.delete(0, tk.END)
                self.entry_address.insert(0, data.get('address', ''))
            else:
                messagebox.showwarning("VIES", "VAT Invalid")
        except:
            messagebox.showerror("Error", "API Connection Failed")

    def calculate_totals(self, event=None):
        try:
            qty = float(self.entry_qty.get())
            tva_rate = float(self.entry_tva_rate.get())
            
            total_incl_vat = qty * PRICE_PER_KG
            # Formula: Total / (1 + rate/100) = Base
            base_price = total_incl_vat / (1 + (tva_rate / 100))
            vat_amount = total_incl_vat - base_price

            self.lbl_base.configure(text=f"Base: {base_price:.2f} €")
            self.lbl_tva.configure(text=f"TVA ({tva_rate}%): {vat_amount:.2f} €")
            self.lbl_total.configure(text=f"TOTAL: {total_incl_vat:.2f} €")
            return total_incl_vat, base_price, vat_amount, tva_rate
        except ValueError:
            self.lbl_total.configure(text="TOTAL: 0.00 €")
            return 0, 0, 0, 6

    def generate_invoice(self):
        total, base, vat, tva_rate = self.calculate_totals()
        if total == 0: return

        client_name = self.entry_name.get()
        client_vat = self.entry_vat.get()
        client_addr = self.entry_address.get()
        qty = float(self.entry_qty.get())
        today_date = datetime.date.today().strftime("%d.%m.%Y")
        
        # Get Next ID
        self.c.execute("SELECT MAX(id) FROM factures")
        result = self.c.fetchone()[0]
        next_id = 1 if result is None else result + 1
        invoice_num = f"{next_id}-{today_date}"

        # PDF Generation
        pdf = FPDF()
        pdf.add_page()
        
        # Sender
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, MY_COMPANY_NAME, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, MY_VAT, ln=True)
        pdf.cell(0, 5, f"Compte: {MY_IBAN}", ln=True)
        pdf.cell(0, 5, f"BIC: {MY_BIC}", ln=True)
        pdf.cell(0, 5, MY_ADDRESS, ln=True)
        pdf.cell(0, 5, MY_CONTACT, ln=True)
        pdf.ln(10)

        # Client
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 5, client_name, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, client_addr)
        pdf.cell(0, 5, f"TVA: {client_vat}", ln=True)
        pdf.ln(10)

        # Invoice Header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Facture {invoice_num}", ln=True)
        pdf.ln(5)

        # Table
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 10, "PRODUIT", 1)
        pdf.cell(30, 10, "Kg", 1)
        pdf.cell(30, 10, "PRIX/EUR", 1)
        pdf.cell(30, 10, "Base", 1)
        pdf.cell(20, 10, f"TVA {tva_rate}%", 1)
        pdf.cell(30, 10, "Total", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        pdf.cell(40, 10, "PRALINES", 1)
        pdf.cell(30, 10, f"{qty:.3f}", 1)
        pdf.cell(30, 10, f"{PRICE_PER_KG:.2f}", 1)
        pdf.cell(30, 10, f"{base:.2f}", 1)
        pdf.cell(20, 10, f"{vat:.2f}", 1)
        pdf.cell(30, 10, f"{total:.2f}", 1)
        pdf.ln()

        # Totals
        pdf.set_font("Arial", "B", 10)
        pdf.cell(100, 10, "TOTAL", 1)
        pdf.cell(30, 10, f"{base:.2f}", 1)
        pdf.cell(20, 10, f"{vat:.2f}", 1)
        pdf.cell(30, 10, f"{total:.2f}", 1)
        pdf.ln(20)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Virement: {total:.2f} EUR", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"DATE: {today_date}", ln=True)

        filename = f"Facture_{next_id}_{today_date}.pdf"
        pdf.output(filename)

        # Save to DB
        self.c.execute("INSERT INTO factures (id, date, client, vat, qty, total, filename) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (next_id, today_date, client_name, client_vat, qty, total, filename))
        self.conn.commit()
        
        self.load_history()
        messagebox.showinfo("Success", f"Invoice generated!")

    def load_history(self):
        # Clear existing items
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.c.execute("SELECT id, date, client, total, filename FROM factures ORDER BY id DESC")
        rows = self.c.fetchall()

        for row in rows:
            # Create a "Card" for each invoice
            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5, padx=5)
            
            # Left side text
            info_text = f"#{row[0]} | {row[1]}\n{row[2]}"
            lbl_info = ctk.CTkLabel(card, text=info_text, anchor="w", justify="left")
            lbl_info.pack(side="left", padx=10, pady=5)
            
            # Right side Price and Button
            btn_open = ctk.CTkButton(card, text="Open PDF", width=80, 
                                     command=lambda f=row[4]: self.open_pdf(f))
            btn_open.pack(side="right", padx=10)

            lbl_price = ctk.CTkLabel(card, text=f"{row[3]:.2f} €", font=ctk.CTkFont(weight="bold"))
            lbl_price.pack(side="right", padx=10)

    def open_pdf(self, filename):
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filename))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filename)
            else:                                   # linux
                subprocess.call(('xdg-open', filename))
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found. Was it deleted?")

    def open_directory(self):
        path = os.getcwd()
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', path])
        else:
            subprocess.call(['xdg-open', path])

if __name__ == "__main__":
    app = ModernInvoiceApp()
    app.mainloop()