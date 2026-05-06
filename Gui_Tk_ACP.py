"""
Dorm Utility Fair Share Calculator 
Author: Igi Daniel Tuico 
This application allows dorm residents to input their usage of various appliances, calculates a "score" 
based on weighted usage, and then divides the total utility bill proportionally. It also saves records to a JSON file for history tracking.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# COLOR SCHEME
BG_MAIN       = "#1e1e2e"
BG_FRAME      = "#2a2a3d"
BG_ENTRY      = "#2f2f45"
BG_LISTBOX    = "#252538"
FG_TEXT       = "#cdd6f4"
FG_MUTED      = "#6c7086"
FG_TITLE      = "#89b4fa"
ACCENT_BLUE   = "#3498db"
ACCENT_GREEN  = "#27ae60"
ACCENT_RED    = "#e74c3c"
ACCENT_GRAY   = "#45475a"

# JSON DATABASE
DATABASE_FILE = "dorm_utility_records.json"
MAX_RECORDS = 1000

def init_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({"records": []}, f, indent=4)

def load_records():
    try:
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("records", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_record(record):
    """Save a record and trim to MAX_RECORDS (keeps newest MAX_RECORDS)."""
    records = load_records()
    records.append(record)
    if len(records) > MAX_RECORDS:
        records = records[-MAX_RECORDS:]
    with open(DATABASE_FILE, 'w') as f:
        json.dump({"records": records}, f, indent=4)

def get_recent_records(limit=MAX_RECORDS):
    records = load_records()
    records.sort(key=lambda x: x.get('date', ''), reverse=True)
    return records[:limit]

WEIGHTS = {
    'airconditioner':    5,
    'inductioncooker':   5,
    'multipurposecooker':4,
    'ricecooker':        4,
    'clipfan':           1,
    'laptopcharging':    1
}

class DormUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dorm Utility Fair Share Calculator")
        self.root.geometry("870x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        self.residents = {}
        self.logo_image = None  # keep reference to PhotoImage
        self._apply_dark_style()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_input_tab()
        self.create_results_tab()
        self.create_history_tab()

    def _apply_dark_style(self):
        style = ttk.Style(self.root)
        style.theme_use("default")
        style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=BG_FRAME,
                        foreground=FG_TEXT,
                        padding=[12, 5],
                        font=("Arial", 9, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", "#ffffff")])
        style.configure("TFrame", background=BG_MAIN)
        style.configure("TLabelframe", background=BG_FRAME, foreground=FG_TEXT, bordercolor=FG_MUTED)
        style.configure("TLabelframe.Label", background=BG_FRAME, foreground=FG_TEXT, font=("Arial", 9, "bold"))
        style.configure("TEntry", fieldbackground=BG_ENTRY, foreground=FG_TEXT, insertcolor=FG_TEXT, bordercolor=FG_MUTED, relief="flat")
        style.configure("Vertical.TScrollbar", background=BG_FRAME, troughcolor=BG_MAIN, arrowcolor=FG_MUTED)

    def _label(self, parent, text, font=("Arial", 10), fg=None, bg=None):
        return tk.Label(parent, text=text, font=font, fg=fg or FG_TEXT, bg=bg or BG_FRAME)

    def _button(self, parent, text, command, bg=ACCENT_BLUE, font=("Arial", 10, "bold"), **kwargs):
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg="#ffffff", activebackground=bg, activeforeground="#ffffff",
                         font=font, cursor="hand2", relief="flat", bd=0, **kwargs)

    def load_logo(self, filename="calculator_logo.png", size=(64, 64)):
        """Try to load the logo image. Returns a PhotoImage or None."""
        if not os.path.exists(filename):
            return None
        try:
            if PIL_AVAILABLE:
                img = Image.open(filename).convert("RGBA")
                img = img.resize(size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            else:
                photo = tk.PhotoImage(file=filename)  # works for PNG/GIF in many TK builds
            self.logo_image = photo
            return photo
        except Exception:
            return None

    # Create a small header (logo + title) to reuse across tabs
    def create_header_frame(self, parent, title_text):
        header = tk.Frame(parent, bg=BG_MAIN)
        header.pack(pady=10, fill='x')

        logo = self.load_logo("calculator_logo.png", size=(64, 64))
        if logo:
            logo_label = tk.Label(header, image=logo, bg=BG_MAIN)
            logo_label.image = logo
            logo_label.pack(side='left', padx=(20, 10))
        else:
            # fallback: calculator/number emoji — no leaf anywhere
            emoji_label = tk.Label(header, text="🔢", font=("Arial", 30), fg=FG_TITLE, bg=BG_MAIN)
            emoji_label.pack(side='left', padx=(20, 10))

        title_label = tk.Label(header, text=title_text, font=("Times New Roman", 25, "underline"),
                               fg=FG_TITLE, bg=BG_MAIN)
        title_label.pack(side='left', padx=10)

        return header

    def create_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="  Enter Data  ")

        # header with calculator logo/emoji (no leaf)
        self.create_header_frame(input_frame, "Dorm Utility Calculator")

        # --- Resident input frame ---
        resident_frame = ttk.LabelFrame(input_frame, text="Add Resident Usage", padding=10)
        resident_frame.pack(padx=20, pady=10, fill='x')

        self._label(resident_frame, "Resident Name:", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(resident_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)

        appliances = [
            ("Air Conditioner (hours):",    'airconditioner'),
            ("Induction Cooker (hours):",   'inductioncooker'),
            ("Multi-Purpose Cooker (hours):",'multipurposecooker'),
            ("Rice Cooker (hours):",        'ricecooker'),
            ("Clip Fan (hours):",           'clipfan'),
            ("Laptop Charging (hours):",    'laptopcharging'),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(appliances, start=1):
            self._label(resident_frame, label, font=("Arial", 9)).grid(row=i, column=0, sticky='w', pady=3)
            entry = ttk.Entry(resident_frame, width=15)
            entry.grid(row=i, column=1, pady=3, padx=5, sticky='w')
            entry.insert(0, "0")
            self.entries[key] = entry
            self._label(resident_frame, f"(Weight: {WEIGHTS[key]})", font=("Arial", 8), fg=FG_MUTED).grid(row=i, column=2, sticky='w', padx=5)

        self._button(resident_frame, "+ Add Resident", self.add_resident, bg=ACCENT_BLUE, padx=10, pady=6).grid(row=len(appliances)+1, column=0, columnspan=3, pady=10)

        # --- Calculate frame: place right under resident input (moved up) ---
        calc_frame = ttk.Frame(input_frame)
        calc_frame.pack(pady=(0, 10))  # smaller top padding so it's closer to resident frame

        tk.Label(calc_frame, text="Total Bill (PHP):", font=("Arial", 11, "bold"), fg=FG_TEXT, bg=BG_MAIN).grid(row=0, column=0, padx=5)
        self.bill_entry = ttk.Entry(calc_frame, width=15, font=("Arial", 11))
        self.bill_entry.grid(row=0, column=1, padx=5)

        self._button(calc_frame, "Calculate Bills", self.calculate_bills, bg=ACCENT_GREEN, font=("Arial", 12, "bold"), padx=20, pady=6).grid(row=0, column=2, padx=10)

        # --- Current residents list (placed after calc_frame) ---
        list_frame = ttk.LabelFrame(input_frame, text="Current Residents", padding=10)
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)

        self.residents_listbox = tk.Listbox(list_frame, height=8, font=("Courier", 9),
                                           bg=BG_LISTBOX, fg=FG_TEXT,
                                           selectbackground=ACCENT_BLUE, selectforeground="#ffffff",
                                           borderwidth=0, highlightthickness=0, relief="flat")
        self.residents_listbox.pack(fill='both', expand=True)

        self._button(list_frame, "Remove Selected", self.remove_resident, bg=ACCENT_RED, font=("Arial", 9, "bold"), pady=5).pack(pady=5)

    def create_results_tab(self):
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="  Results  ")

        # header with calculator logo/emoji
        self.create_header_frame(results_frame, "Calculation Receipt")

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=("Courier", 10), height=35,
                                                     bg=BG_LISTBOX, fg=FG_TEXT, insertbackground=FG_TEXT,
                                                     borderwidth=0, relief="flat", selectbackground=ACCENT_BLUE)
        self.results_text.pack(padx=20, pady=10, fill='both', expand=True)

    def create_history_tab(self):
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="  History  ")

        # header with calculator logo/emoji
        self.create_header_frame(history_frame, "Payment History")

        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, font=("Courier", 9), height=35,
                                                     bg=BG_LISTBOX, fg=FG_TEXT, insertbackground=FG_TEXT,
                                                     borderwidth=0, relief="flat", selectbackground=ACCENT_BLUE)
        self.history_text.pack(padx=20, pady=10, fill='both', expand=True)

        # Defer initial load so the widget is fully initialized
        self.root.after(100, self.load_history)

    def add_resident(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Resident name cannot be empty.")
            return
        if name in self.residents:
            messagebox.showerror("Error", f"'{name}' already exists.")
            return
        try:
            data = {}
            for key, entry in self.entries.items():
                val = float(entry.get())
                if val < 0:
                    messagebox.showerror("Error", "Values cannot be negative.")
                    return
                data[key] = val
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for appliance hours.")
            return

        score = sum(data[k] * WEIGHTS[k] for k in WEIGHTS)
        data['score'] = score
        self.residents[name] = data
        self.update_residents_listbox()
        messagebox.showinfo("Added", f"'{name}' added. Score: {score:.1f}")

    def remove_resident(self):
        sel = self.residents_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "No resident selected.")
            return
        idx = sel[0]
        name = self.residents_listbox.get(idx).split()[1]  # listbox format below uses index + name
        # safer approach: keep ordered list when building listbox
        # rebuild listbox to find mapping
        names = list(self.residents.keys())
        if idx < len(names):
            name = names[idx]
            del self.residents[name]
            self.update_residents_listbox()
            messagebox.showinfo("Removed", f"'{name}' removed.")
        else:
            messagebox.showerror("Error", "Failed to remove resident.")

    def update_residents_listbox(self):
        self.residents_listbox.delete(0, tk.END)
        for i, (name, data) in enumerate(self.residents.items(), start=1):
            self.residents_listbox.insert(tk.END, f"{i:>2}. {name}  (Score: {data['score']:.1f})")

    def calculate_bills(self):
        if not self.residents:
            messagebox.showerror("Error", "Please add at least one resident first!")
            return
        try:
            total_bill = float(self.bill_entry.get())
            if total_bill <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid Total Bill (greater than 0).")
            return

        total_score = sum(r['score'] for r in self.residents.values())
        if total_score == 0:
            messagebox.showerror("Error", "Total score is zero. No usage recorded!")
            return

        results  = "=" * 80 + "\n"
        results += "DORM UTILITY BILL CALCULATION RESULTS\n"
        results += "=" * 80 + "\n\n"
        results += f"Total Bill: PHP {total_bill:.2f}\n"
        results += f"Total Score: {total_score:.2f}\n\n"

        highest = max(self.residents, key=lambda x: self.residents[x]['score'])
        lowest  = min(self.residents, key=lambda x: self.residents[x]['score'])

        results += f"[HIGH] Highest Consumer: {highest}\n"
        results += f"[LOW]  Lowest Consumer:  {lowest}\n\n"
        results += "=" * 80 + "\n\n"

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for name, data in self.residents.items():
            share      = data['score'] / total_score * total_bill
            percentage = data['score'] / total_score * 100

            record = {
                "name":               name,
                "airconditioner":     data['airconditioner'],
                "inductioncooker":    data['inductioncooker'],
                "multipurposecooker": data['multipurposecooker'],
                "ricecooker":         data['ricecooker'],
                "clipfan":            data['clipfan'],
                "laptopcharging":     data['laptopcharging'],
                "score":              data['score'],
                "total_bill":         total_bill,
                "share":              share,
                "date":               current_time
            }
            save_record(record)

            results += f"{'='*80}\n"
            results += f"RECEIPT FOR: {name.upper()}\n"
            results += f"{'='*80}\n"
            results += f"Usage Breakdown (Hours x Weight = Points):\n"
            results += f"  - Air Conditioner:      {data['airconditioner']:>6.1f}h x {WEIGHTS['airconditioner']} = {data['airconditioner']*WEIGHTS['airconditioner']:>6.1f}\n"
            results += f"  - Induction Cooker:     {data['inductioncooker']:>6.1f}h x {WEIGHTS['inductioncooker']} = {data['inductioncooker']*WEIGHTS['inductioncooker']:>6.1f}\n"
            results += f"  - Multi-Purpose Cooker: {data['multipurposecooker']:>6.1f}h x {WEIGHTS['multipurposecooker']} = {data['multipurposecooker']*WEIGHTS['multipurposecooker']:>6.1f}\n"
            results += f"  - Rice Cooker:          {data['ricecooker']:>6.1f}h x {WEIGHTS['ricecooker']} = {data['ricecooker']*WEIGHTS['ricecooker']:>6.1f}\n"
            results += f"  - Clip Fan:             {data['clipfan']:>6.1f}h x {WEIGHTS['clipfan']} = {data['clipfan']*WEIGHTS['clipfan']:>6.1f}\n"
            results += f"  - Laptop Charging:      {data['laptopcharging']:>6.1f}h x {WEIGHTS['laptopcharging']} = {data['laptopcharging']*WEIGHTS['laptopcharging']:>6.1f}\n"
            results += f"\nCalculation:\n"
            results += f"  Your Total Score:   {data['score']:.2f}\n"
            results += f"  Global Total Score: {total_score:.2f}\n"
            results += f"  Your Share:         {percentage:.2f}%\n"
            results += f"\n  AMOUNT TO PAY: PHP {share:.2f}\n"
            results += f"{'='*80}\n\n"

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results)
        self.results_text.config(state=tk.DISABLED)

        # refresh history tab contents after calculation
        self.load_history()

        messagebox.showinfo("Done", "Bills calculated and saved to JSON database!")

    def load_history(self):
        """Load and display payment history from JSON database (up to MAX_RECORDS)."""
        records = get_recent_records(MAX_RECORDS)

        history  = "=" * 95 + "\n"
        history += "PAYMENT HISTORY (Last records, up to 1000)\n"
        history += "=" * 95 + "\n\n"

        if not records:
            history += "No records found.\n"
        else:
            history += f"{'Name':<20} {'Amount Paid':<20} {'Total Bill':<20} {'Date':<30}\n"
            history += "-" * 95 + "\n"
            for record in records:
                name       = record.get('name', 'Unknown')
                share      = record.get('share', 0)
                total_bill = record.get('total_bill', 0)
                date       = record.get('date', 'Unknown')
                history += f"{name:<20} PHP {share:>14.2f}   PHP {total_bill:>14.2f}   {date:<30}\n"

        try:
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(1.0, history)
            self.history_text.config(state=tk.DISABLED)
        except tk.TclError:
            self.root.after(50, self.load_history)

if __name__ == "__main__":
    init_database()
    root = tk.Tk()
    app = DormUtilityApp(root)
    root.mainloop()
