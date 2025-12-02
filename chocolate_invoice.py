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
from tkcalendar import Calendar
import re

# --- CONFIGURATION ---
MY_COMPANY_NAME = "LCHOCOLAT SRL"
MY_VAT = "BE 0704 898 010"
MY_IBAN = "BE16 0689 1091 2374"
MY_BIC = "GKCCBEBB"
MY_ADDRESS = "55, Avenue du Prince Héritier, 1200 BRUXELLES"
MY_CONTACT = "Tel: 0478.428.310 | office@lchocolat.com"
STANDARD_PRICE_PER_KG = 99.90

# --- THEME SETUP ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ModernInvoiceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("LCHOCOLAT Invoice Manager")
        self.geometry("1100x950") 
        self.resizable(False, False)

        self.init_db()

        # --- LAYOUT (Grid) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR (Inputs) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(22, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="LCHOCOLAT\nMANAGER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 0. Invoice Number
        self.lbl_inv_num = ctk.CTkLabel(self.sidebar_frame, text="Invoice Number (ID):", anchor="w")
        self.lbl_inv_num.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.entry_inv_id = ctk.CTkEntry(self.sidebar_frame, placeholder_text="ID")
        self.entry_inv_id.grid(row=2, column=0, padx=20, pady=(5, 5), sticky="ew")

        # 1. Date Selection
        self.lbl_date = ctk.CTkLabel(self.sidebar_frame, text="Date:", anchor="w")
        self.lbl_date.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="w")

        self.date_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.date_frame.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="ew")

        self.entry_date = ctk.CTkEntry(self.date_frame)
        self.entry_date.pack(side="left", fill="x", expand=True)
        self.entry_date.insert(0, datetime.date.today().strftime("%d.%m.%Y"))

        self.btn_calendar = ctk.CTkButton(self.date_frame, text="📅", width=40, command=self.open_calendar_popup)
        self.btn_calendar.pack(side="right", padx=(5, 0))

        # 2. Client Lookup
        self.lbl_client = ctk.CTkLabel(self.sidebar_frame, text="Client Details", anchor="w")
        self.lbl_client.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.entry_vat = ctk.CTkEntry(self.sidebar_frame, placeholder_text="VAT (e.g. BE0894524595)")
        self.entry_vat.grid(row=6, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.btn_search = ctk.CTkButton(self.sidebar_frame, text="Search VIES (VAT)", command=self.lookup_vat, 
                                        fg_color="#2A2D2E", border_width=2, border_color="#3B8ED0", text_color="#3B8ED0")
        self.btn_search.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        self.entry_name = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Client Name")
        self.entry_name.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        # --- ADDRESS SECTION ---
        self.entry_street = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Street & Number")
        self.entry_street.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        self.addr_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.addr_frame.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        self.entry_zip = ctk.CTkEntry(self.addr_frame, placeholder_text="Zip", width=60)
        self.entry_zip.pack(side="left", padx=(0, 5))

        self.entry_city = ctk.CTkEntry(self.addr_frame, placeholder_text="City/Commune")
        self.entry_city.pack(side="left", fill="x", expand=True)
        
        self.btn_addr_search = ctk.CTkButton(self.addr_frame, text="🔍", width=30, command=self.autocomplete_address,
                                            fg_color="#444", hover_color="#666")
        self.btn_addr_search.pack(side="left", padx=(5, 0))

        # Optional Fields
        self.entry_phone = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Phone (Optional)")
        self.entry_phone.grid(row=11, column=0, padx=20, pady=5, sticky="ew")
        
        self.entry_email = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Email (Optional)")
        self.entry_email.grid(row=12, column=0, padx=20, pady=5, sticky="ew")

        # 3. Product Section
        self.lbl_prod = ctk.CTkLabel(self.sidebar_frame, text="Product Details", anchor="w")
        self.lbl_prod.grid(row=13, column=0, padx=20, pady=(15, 0), sticky="w")

        # Product Name Override
        self.entry_product_name = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Product Name")
        self.entry_product_name.insert(0, "CHOCOLATES")
        self.entry_product_name.grid(row=14, column=0, padx=20, pady=5, sticky="ew")

        # Pricing Logic Switch
        self.pricing_mode = ctk.StringVar(value="weight")
        self.switch_price_mode = ctk.CTkSwitch(self.sidebar_frame, text="Manual Price / Override", command=self.toggle_price_mode, 
                                               variable=self.pricing_mode, onvalue="fixed", offvalue="weight")
        self.switch_price_mode.grid(row=15, column=0, padx=20, pady=(5, 5), sticky="w")

        # Quantity Input
        self.entry_qty = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Quantity (Kg)")
        self.entry_qty.grid(row=16, column=0, padx=20, pady=5, sticky="ew")
        self.entry_qty.bind("<KeyRelease>", self.calculate_totals)

        # Fixed Price Input
        self.entry_fixed_price = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Total Price (€)")
        self.entry_fixed_price.bind("<KeyRelease>", self.calculate_totals)
        
        # TVA Rate
        self.frame_tva = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.frame_tva.grid(row=17, column=0, padx=20, pady=5, sticky="ew")
        
        self.lbl_tva_rate = ctk.CTkLabel(self.frame_tva, text="TVA %:", width=50, anchor="w")
        self.lbl_tva_rate.pack(side="left")
        
        self.entry_tva_rate = ctk.CTkEntry(self.frame_tva, width=60)
        self.entry_tva_rate.insert(0, "6")
        self.entry_tva_rate.pack(side="left", padx=5)
        self.entry_tva_rate.bind("<KeyRelease>", self.calculate_totals)

        # Generate Button
        self.btn_generate = ctk.CTkButton(self.sidebar_frame, text="GENERATE & SAVE", command=self.generate_invoice, 
                                          height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_generate.grid(row=18, column=0, padx=20, pady=20, sticky="ew")

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Preview
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

        # History
        self.history_label = ctk.CTkLabel(self.main_frame, text="Invoice History", font=ctk.CTkFont(size=16, weight="bold"))
        self.history_label.pack(anchor="w", pady=(0, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Database")
        self.scroll_frame.pack(fill="both", expand=True)

        self.btn_open_dir = ctk.CTkButton(self.main_frame, text="📂 Open Output Folder", command=self.open_directory, 
                                          fg_color="transparent", border_width=1, text_color="gray")
        self.btn_open_dir.pack(fill="x", pady=(10, 0))

        self.load_history()
        self.set_next_invoice_number()

    # --- LOGIC ---

    def init_db(self):
        self.conn = sqlite3.connect('factures_db.sqlite')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS factures
                          (id INTEGER PRIMARY KEY, date TEXT, client TEXT, vat TEXT, qty REAL, total REAL, filename TEXT)''')
        self.conn.commit()

    def set_next_invoice_number(self):
        self.c.execute("SELECT MAX(id) FROM factures")
        result = self.c.fetchone()[0]
        next_id = 1 if result is None else result + 1
        self.entry_inv_id.delete(0, tk.END)
        self.entry_inv_id.insert(0, str(next_id))

    def open_calendar_popup(self):
        top = ctk.CTkToplevel(self)
        top.title("Pick Date")
        top.geometry("300x250")
        top.grab_set()
        cal = Calendar(top, selectmode='day', date_pattern='dd.mm.yyyy')
        cal.pack(padx=10, pady=10, expand=True, fill="both")
        def set_date():
            self.entry_date.delete(0, tk.END)
            self.entry_date.insert(0, cal.get_date())
            top.destroy()
        btn_select = ctk.CTkButton(top, text="Select", command=set_date)
        btn_select.pack(pady=10)

    def toggle_price_mode(self):
        if self.pricing_mode.get() == "fixed":
            self.entry_qty.grid_forget()
            self.entry_fixed_price.grid(row=16, column=0, padx=20, pady=5, sticky="ew")
            self.entry_fixed_price.delete(0, tk.END)
            self.entry_fixed_price.focus()
        else:
            self.entry_fixed_price.grid_forget()
            self.entry_qty.grid(row=16, column=0, padx=20, pady=5, sticky="ew")
            self.entry_qty.delete(0, tk.END)
            self.entry_qty.focus()
        self.calculate_totals()

    def autocomplete_address(self):
        query = self.entry_street.get().strip()
        if not query:
            messagebox.showinfo("Tip", "Type a street name first.")
            return

        if "belgium" not in query.lower() and "belgique" not in query.lower():
            query += " Belgium"

        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': query, 'format': 'json', 'addressdetails': 1, 'limit': 1}
        headers = {'User-Agent': 'InvoiceApp/1.0'}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            if data:
                addr = data[0].get('address', {})
                road = addr.get('road', '')
                house = addr.get('house_number', '')
                postcode = addr.get('postcode', '')
                city = addr.get('city', addr.get('town', addr.get('village', '')))
                
                full_street = f"{road} {house}".strip()
                if full_street:
                    self.entry_street.delete(0, tk.END)
                    self.entry_street.insert(0, full_street)
                if postcode:
                    self.entry_zip.delete(0, tk.END)
                    self.entry_zip.insert(0, postcode)
                if city:
                    self.entry_city.delete(0, tk.END)
                    self.entry_city.insert(0, city)
            else:
                messagebox.showwarning("Not Found", "No address found.")
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

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
                
                raw_addr = data.get('address', '')
                if raw_addr:
                    parts = raw_addr.split('\n')
                    street_part = parts[0].strip()
                    zip_city_part = parts[-1].strip() if len(parts) > 1 else ""

                    match = re.match(r"(\d{4})\s+(.*)", zip_city_part)
                    self.entry_street.delete(0, tk.END)
                    self.entry_street.insert(0, street_part)

                    if match:
                        zip_code, city = match.groups()
                        self.entry_zip.delete(0, tk.END)
                        self.entry_zip.insert(0, zip_code)
                        self.entry_city.delete(0, tk.END)
                        self.entry_city.insert(0, city)
                    else:
                        self.entry_zip.delete(0, tk.END)
                        self.entry_city.delete(0, tk.END)
                        self.entry_city.insert(0, zip_city_part)
            else:
                messagebox.showwarning("VIES", "VAT Invalid")
        except:
            messagebox.showerror("Error", "API Connection Failed")

    def calculate_totals(self, event=None):
        try:
            tva_rate = float(self.entry_tva_rate.get())
        except ValueError:
            tva_rate = 6.0

        total_incl_vat = 0.0

        if self.pricing_mode.get() == "weight":
            try:
                qty = float(self.entry_qty.get())
                total_incl_vat = qty * STANDARD_PRICE_PER_KG
            except ValueError:
                total_incl_vat = 0.0
        else:
            try:
                total_incl_vat = float(self.entry_fixed_price.get())
            except ValueError:
                total_incl_vat = 0.0

        try:
            base_price = total_incl_vat / (1 + (tva_rate / 100))
            vat_amount = total_incl_vat - base_price
        except ZeroDivisionError:
            base_price = 0
            vat_amount = 0

        self.lbl_base.configure(text=f"Base: {base_price:.2f} €")
        self.lbl_tva.configure(text=f"TVA ({tva_rate}%): {vat_amount:.2f} €")
        self.lbl_total.configure(text=f"TOTAL: {total_incl_vat:.2f} €")
        
        return total_incl_vat, base_price, vat_amount, tva_rate

    def generate_invoice(self):
        total, base, vat, tva_rate = self.calculate_totals()
        if total == 0: 
            messagebox.showerror("Error", "Check quantity or price.")
            return

        try:
            custom_id = int(self.entry_inv_id.get())
        except ValueError:
            messagebox.showerror("Error", "Invoice Number must be a number.")
            return

        client_name = self.entry_name.get()
        client_vat = self.entry_vat.get()
        street = self.entry_street.get()
        zip_code = self.entry_zip.get()
        city = self.entry_city.get()
        client_full_addr = f"{street}\n{zip_code} {city}"
        
        client_phone = self.entry_phone.get()
        client_email = self.entry_email.get()
        
        prod_name = self.entry_product_name.get().strip()
        if not prod_name: prod_name = "CHOCOLATES"

        # Setup Values based on Mode
        is_weight_mode = (self.pricing_mode.get() == "weight")

        if is_weight_mode:
            try:
                qty_val = float(self.entry_qty.get())
            except: qty_val = 0
            unit_price_val = STANDARD_PRICE_PER_KG
            # Formatted text for columns
            qty_str = f"{qty_val:.3f} kg"
            unit_price_str = f"{unit_price_val:.2f}"
        else:
            qty_val = 1.0 # DB filler
            unit_price_val = total
            # Formatted text
            qty_str = "" # Not used in fixed mode
            unit_price_str = f"{total:.2f}"

        selected_date = self.entry_date.get()
        if not selected_date: selected_date = datetime.date.today().strftime("%d.%m.%Y")
            
        invoice_num_str = f"{custom_id}-{selected_date}"
        filename = f"Facture_{custom_id}_{selected_date}.pdf"

        # Check DB
        try:
            self.c.execute("INSERT INTO factures (id, date, client, vat, qty, total, filename) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (custom_id, selected_date, client_name, client_vat, qty_val, total, filename))
            self.conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Invoice #{custom_id} already exists!")
            return

        # PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Header
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
        pdf.multi_cell(0, 5, client_full_addr)
        pdf.cell(0, 5, f"{client_vat}", ln=True)
        if client_phone: pdf.cell(0, 5, f"Tel: {client_phone}", ln=True)
        if client_email: pdf.cell(0, 5, f"Email: {client_email}", ln=True)
        pdf.ln(10)

        # Invoice Info
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Facture {invoice_num_str}", ln=True)
        pdf.ln(5)

        # --- DYNAMIC TABLE ---
        pdf.set_font("Arial", "B", 10)

        if is_weight_mode:
            # 6 Columns (Product, Qty, Price, Base, Vat, Total)
            pdf.cell(40, 10, "PRODUIT / SERVICE", 1)
            pdf.cell(30, 10, "Quantite", 1)
            pdf.cell(30, 10, "PRIX/UNIT", 1)
            pdf.cell(30, 10, "Base", 1)
            pdf.cell(20, 10, f"TVA {tva_rate}%", 1)
            pdf.cell(30, 10, "Total", 1)
            pdf.ln()

            pdf.set_font("Arial", "", 10)
            pdf.cell(40, 10, prod_name.upper(), 1)
            pdf.cell(30, 10, qty_str, 1) # Shows "5.000 kg"
            pdf.cell(30, 10, unit_price_str, 1)
            pdf.cell(30, 10, f"{base:.2f}", 1)
            pdf.cell(20, 10, f"{vat:.2f}", 1)
            pdf.cell(30, 10, f"{total:.2f}", 1)
            pdf.ln()

        else:
            # 5 Columns (Product is wider, NO Quantity Column)
            pdf.cell(70, 10, "PRODUIT / SERVICE", 1) # 40 + 30 = 70
            pdf.cell(30, 10, "PRIX/UNIT", 1)
            pdf.cell(30, 10, "Base", 1)
            pdf.cell(20, 10, f"TVA {tva_rate}%", 1)
            pdf.cell(30, 10, "Total", 1)
            pdf.ln()

            pdf.set_font("Arial", "", 10)
            pdf.cell(70, 10, prod_name.upper(), 1)
            # Skip qty cell
            pdf.cell(30, 10, unit_price_str, 1)
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
        pdf.cell(0, 10, f"DATE: {selected_date}", ln=True)

        pdf.output(filename)
        
        self.load_history()
        self.set_next_invoice_number()
        messagebox.showinfo("Success", f"Invoice #{custom_id} generated!")

    def delete_invoice(self, inv_id):
        confirm = messagebox.askyesno("Confirm Delete", f"Delete invoice #{inv_id}?")
        if confirm:
            self.c.execute("DELETE FROM factures WHERE id=?", (inv_id,))
            self.conn.commit()
            self.load_history()
            self.set_next_invoice_number()

    def load_history(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.c.execute("SELECT id, date, client, total, filename FROM factures ORDER BY id DESC")
        rows = self.c.fetchall()

        for row in rows:
            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5, padx=5)
            
            info_text = f"#{row[0]} | {row[1]}\n{row[2]}"
            lbl_info = ctk.CTkLabel(card, text=info_text, anchor="w", justify="left")
            lbl_info.pack(side="left", padx=10, pady=5)
            
            btn_del = ctk.CTkButton(card, text="✕", width=30, fg_color="#FF5555", hover_color="#CC0000",
                                    command=lambda r=row[0]: self.delete_invoice(r))
            btn_del.pack(side="right", padx=(5, 10))

            btn_open = ctk.CTkButton(card, text="Open PDF", width=80, 
                                     command=lambda f=row[4]: self.open_pdf(f))
            btn_open.pack(side="right", padx=5)

            lbl_price = ctk.CTkLabel(card, text=f"{row[3]:.2f} €", font=ctk.CTkFont(weight="bold"))
            lbl_price.pack(side="right", padx=10)

    def open_pdf(self, filename):
        try:
            if platform.system() == 'Darwin':       
                subprocess.call(('open', filename))
            elif platform.system() == 'Windows':    
                os.startfile(filename)
            else:                                   
                subprocess.call(('xdg-open', filename))
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")

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