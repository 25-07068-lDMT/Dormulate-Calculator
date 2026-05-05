"""
Dorm Utility Fair Share Calculator 
Author: Igi Daniel Tuico 
This application allows dorm residents to input their usage of various appliances,
calculates their fair share of the total utility bill based on weighted usage, and
stores the records in a JSON file for future reference. The GUI is built using Tkinter
with a dark mode theme for better aesthetics and usability.

"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# ================= DARK MODE COLORS =================
BG_MAIN       = "#1e1e2e"   # main window background
BG_FRAME      = "#2a2a3d"   # frame / labelframe background
BG_ENTRY      = "#2f2f45"   # entry field background
BG_LISTBOX    = "#252538"   # listbox background
FG_TEXT       = "#cdd6f4"   # primary text
FG_MUTED      = "#6c7086"   # muted / secondary text
FG_TITLE      = "#89b4fa"   # accent titles
ACCENT_BLUE   = "#3498db"
ACCENT_GREEN  = "#27ae60"
ACCENT_RED    = "#e74c3c"
ACCENT_GRAY   = "#45475a"

# ================= JSON DATABASE SETUP =================
DATABASE_FILE = "dorm_utility_records.json"

def init_database():
    """Create JSON file if it doesn't exist"""
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({"records": []}, f, indent=4)

def load_records():
    """Load all records from JSON file"""
    try:
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("records", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_record(record):
    """Save a single record to JSON file"""
    records = load_records()
    records.append(record)
    with open(DATABASE_FILE, 'w') as f:
        json.dump({"records": records}, f, indent=4)

def get_recent_records(limit=50):
    """Get most recent records"""
    records = load_records()
    records.sort(key=lambda x: x.get('date', ''), reverse=True)
    return records[:limit]

# ================= APPLIANCE WEIGHTS =================
WEIGHTS = {
    'airconditioner':    5,
    'inductioncooker':   5,
    'multipurposecooker':4,
    'ricecooker':        4,
    'clipfan':           1,
    'laptopcharging':    1
}

# ================= MAIN APPLICATION =================
class DormUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dorm Utility Fair Share Calculator")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        self.residents = {}
        self._apply_dark_style()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_input_tab()
        self.create_results_tab()
        self.create_history_tab()

    # ── Dark ttk style ──────────────────────────────────────────────────────
    def _apply_dark_style(self):
        style = ttk.Style(self.root)
        style.theme_use("default")

        # Notebook tabs
        style.configure("TNotebook",
                        background=BG_MAIN,
                        borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=BG_FRAME,
                        foreground=FG_TEXT,
                        padding=[12, 5],
                        font=("Arial", 9, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", "#ffffff")])

        # Frames
        style.configure("TFrame", background=BG_MAIN)
        style.configure("TLabelframe",
                        background=BG_FRAME,
                        foreground=FG_TEXT,
                        bordercolor=FG_MUTED)
        style.configure("TLabelframe.Label",
                        background=BG_FRAME,
                        foreground=FG_TEXT,
                        font=("Arial", 9, "bold"))

        # Entries
        style.configure("TEntry",
                        fieldbackground=BG_ENTRY,
                        foreground=FG_TEXT,
                        insertcolor=FG_TEXT,
                        bordercolor=FG_MUTED,
                        relief="flat")

        # Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=BG_FRAME,
                        troughcolor=BG_MAIN,
                        arrowcolor=FG_MUTED)

    # ── Helper: dark tk.Label ────────────────────────────────────────────────
    def _label(self, parent, text, font=("Arial", 10), fg=None, bg=None):
        return tk.Label(parent,
                        text=text,
                        font=font,
                        fg=fg or FG_TEXT,
                        bg=bg or BG_FRAME)

    # ── Helper: dark tk.Button ───────────────────────────────────────────────
    def _button(self, parent, text, command, bg=ACCENT_BLUE,
                font=("Arial", 10, "bold"), **kwargs):
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg="#ffffff",
                         activebackground=bg, activeforeground="#ffffff",
                         font=font, cursor="hand2",
                         relief="flat", bd=0, **kwargs)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    def create_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="  Enter Data  ")

        # Title
        tk.Label(input_frame, text="Dorm Utility Calculator",
                 font=("Arial", 18, "bold"),
                 fg=FG_TITLE, bg=BG_MAIN).pack(pady=10)

        # --- Resident input frame ---
        resident_frame = ttk.LabelFrame(input_frame,
                                        text="Add Resident Usage", padding=10)
        resident_frame.pack(padx=20, pady=10, fill='x')

        self._label(resident_frame, "Resident Name:",
                    font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(resident_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)

        appliances = [
            ("Air Conditioner (hours):",    'airconditioner'),
            ("Induction Cooker (hours):",   'inductioncooker'),
            ("Multi-Purpose Cooker (hours):","multipurposecooker"),
            ("Rice Cooker (hours):",        'ricecooker'),
            ("Clip Fan (hours):",           'clipfan'),
            ("Laptop Charging (hours):",    'laptopcharging'),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(appliances, start=1):
            self._label(resident_frame, label,
                        font=("Arial", 9)).grid(row=i, column=0, sticky='w', pady=3)
            entry = ttk.Entry(resident_frame, width=15)
            entry.grid(row=i, column=1, pady=3, padx=5, sticky='w')
            entry.insert(0, "0")
            self.entries[key] = entry

            self._label(resident_frame, f"(Weight: {WEIGHTS[key]})",
                        font=("Arial", 8), fg=FG_MUTED
                        ).grid(row=i, column=2, sticky='w', padx=5)

        self._button(resident_frame, "+ Add Resident",
                     self.add_resident, bg=ACCENT_BLUE,
                     padx=10, pady=6
                     ).grid(row=len(appliances)+1, column=0,
                            columnspan=3, pady=10)

        # --- Current residents list ---
        list_frame = ttk.LabelFrame(input_frame,
                                    text="Current Residents", padding=10)
        list_frame.pack(padx=20, pady=10, fill='both', expand=True)

        self.residents_listbox = tk.Listbox(
            list_frame, height=8, font=("Courier", 9),
            bg=BG_LISTBOX, fg=FG_TEXT,
            selectbackground=ACCENT_BLUE, selectforeground="#ffffff",
            borderwidth=0, highlightthickness=0,
            relief="flat"
        )
        self.residents_listbox.pack(fill='both', expand=True)

        self._button(list_frame, "Remove Selected",
                     self.remove_resident, bg=ACCENT_RED,
                     font=("Arial", 9, "bold"), pady=5
                     ).pack(pady=5)

        # --- Calculate frame ---
        calc_frame = ttk.Frame(input_frame)
        calc_frame.pack(pady=10)

        tk.Label(calc_frame, text="Total Bill (PHP):",
                 font=("Arial", 11, "bold"),
                 fg=FG_TEXT, bg=BG_MAIN
                 ).grid(row=0, column=0, padx=5)

        self.bill_entry = ttk.Entry(calc_frame, width=15,
                                    font=("Arial", 11))
        self.bill_entry.grid(row=0, column=1, padx=5)

        self._button(calc_frame, "Calculate Bills",
                     self.calculate_bills, bg=ACCENT_GREEN,
                     font=("Arial", 12, "bold"), padx=20, pady=6
                     ).grid(row=0, column=2, padx=10)

    def create_results_tab(self):
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="  Results  ")

        tk.Label(results_frame, text="Calculation Results",
                 font=("Arial", 16, "bold"),
                 fg=FG_TITLE, bg=BG_MAIN).pack(pady=10)

        self.results_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD,
            font=("Courier", 10), height=35,
            bg=BG_LISTBOX, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            borderwidth=0, relief="flat",
            selectbackground=ACCENT_BLUE
        )
        self.results_text.pack(padx=20, pady=10, fill='both', expand=True)

    def create_history_tab(self):
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="  History  ")

        tk.Label(history_frame, text="Payment History",
                 font=("Arial", 16, "bold"),
                 fg=FG_TITLE, bg=BG_MAIN).pack(pady=10)

        self._button(history_frame, "Refresh History",
                     self.load_history, bg=ACCENT_GRAY,
                     font=("Arial", 10, "bold"), padx=10, pady=5
                     ).pack(pady=5)

        self.history_text = scrolledtext.ScrolledText(
            history_frame, wrap=tk.WORD,
            font=("Courier", 9), height=35,
            bg=BG_LISTBOX, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            borderwidth=0, relief="flat",
            selectbackground=ACCENT_BLUE
        )
        self.history_text.pack(padx=20, pady=10, fill='both', expand=True)

        self.load_history()

    # ── Logic (unchanged) ────────────────────────────────────────────────────
    def add_resident(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a resident name!")
            return
        if name in self.residents:
            messagebox.showerror("Error", f"{name} already exists!")
            return
        try:
            data = {}
            for key, entry in self.entries.items():
                value = float(entry.get())
                if value < 0:
                    raise ValueError(f"{key} cannot be negative")
                data[key] = value
            score = sum(data[key] * WEIGHTS[key] for key in WEIGHTS)
            data['score'] = score
            self.residents[name] = data
            self.residents_listbox.insert(tk.END, f"{name} (Score: {score:.1f})")
            self.name_entry.delete(0, tk.END)
            for entry in self.entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, "0")
            messagebox.showinfo("Success", f"{name} added successfully!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def remove_resident(self):
        selection = self.residents_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a resident to remove!")
            return
        index = selection[0]
        name = list(self.residents.keys())[index]
        del self.residents[name]
        self.residents_listbox.delete(index)
        messagebox.showinfo("Success", f"{name} removed!")

    def calculate_bills(self):
        if not self.residents:
            messagebox.showerror("Error", "Please add at least one resident!")
            return
        try:
            total_bill = float(self.bill_entry.get())
            if total_bill <= 0:
                raise ValueError("Bill must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid total bill amount!")
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
                "name": name,
                "airconditioner":    data['airconditioner'],
                "inductioncooker":   data['inductioncooker'],
                "multipurposecooker":data['multipurposecooker'],
                "ricecooker":        data['ricecooker'],
                "clipfan":           data['clipfan'],
                "laptopcharging":    data['laptopcharging'],
                "score":      data['score'],
                "total_bill": total_bill,
                "share":      share,
                "date":       current_time
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

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results)
        self.notebook.select(1)
        messagebox.showinfo("Success", "Bills calculated and saved to JSON database!")
        self.load_history()

    def load_history(self):
        records = get_recent_records(50)

        history  = "=" * 80 + "\n"
        history += "PAYMENT HISTORY (Last 50 Records)\n"
        history += "=" * 80 + "\n\n"

        if not records:
            history += "No records found.\n"
        else:
            history += f"{'Name':<20} {'Amount Paid':<15} {'Total Bill':<15} {'Date':<20}\n"
            history += "-" * 80 + "\n"
            for record in records:
                name       = record.get('name', 'Unknown')
                share      = record.get('share', 0)
                total_bill = record.get('total_bill', 0)
                date       = record.get('date', 'Unknown')
                history += f"{name:<20} PHP {share:>10.2f} PHP {total_bill:>10.2f} {date:<20}\n"

        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(1.0, history)

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    init_database()
    root = tk.Tk()
    app = DormUtilityApp(root)
    root.mainloop()
