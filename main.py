"""
Dorm Utility Fair Share Calculator - CLI Version
Author: Igi Daniel Tuico (JSON Database Version)
No GUI / Terminal Only
"""

import json
import os
from datetime import datetime

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
    'airconditioner':     5,
    'inductioncooker':    5,
    'multipurposecooker': 4,
    'ricecooker':         4,
    'clipfan':            1,
    'laptopcharging':     1
}

# ================= HELPERS =================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def prompt_float(prompt, allow_negative=False):
    """Prompt until a valid float is entered"""
    while True:
        try:
            value = float(input(prompt).strip())
            if not allow_negative and value < 0:
                print("  [!] Value cannot be negative. Try again.")
                continue
            return value
        except ValueError:
            print("  [!] Invalid number. Try again.")

def prompt_positive_float(prompt):
    """Prompt until a positive float is entered"""
    while True:
        value = prompt_float(prompt)
        if value <= 0:
            print("  [!] Value must be greater than 0. Try again.")
            continue
        return value

# ================= CORE LOGIC =================
class DormUtilityApp:
    def __init__(self):
        self.residents = {}   # { name: { appliance: hours, ..., 'score': float } }

    # ── Add Resident ────────────────────────────────────────────────────────
    def add_resident(self):
        print_header("Add Resident Usage")

        name = input("  Resident Name: ").strip()
        if not name:
            print("  [ERROR] Name cannot be empty!")
            return
        if name in self.residents:
            print(f"  [ERROR] '{name}' already exists!")
            return

        appliances = [
            ("Air Conditioner (hours)",    'airconditioner'),
            ("Induction Cooker (hours)",   'inductioncooker'),
            ("Multi-Purpose Cooker (hours)",'multipurposecooker'),
            ("Rice Cooker (hours)",        'ricecooker'),
            ("Clip Fan (hours)",           'clipfan'),
            ("Laptop Charging (hours)",    'laptopcharging'),
        ]

        print()
        data = {}
        for label, key in appliances:
            value = prompt_float(f"  {label} [Weight: {WEIGHTS[key]}]: ")
            data[key] = value

        score = sum(data[key] * WEIGHTS[key] for key in WEIGHTS)
        data['score'] = score
        self.residents[name] = data

        print(f"\n  [OK] '{name}' added! Score: {score:.1f}")

    # ── Remove Resident ──────────────────────────────────────────────────────
    def remove_resident(self):
        print_header("Remove Resident")

        if not self.residents:
            print("  [!] No residents added yet.")
            return

        names = list(self.residents.keys())
        print("  Current Residents:")
        for i, name in enumerate(names, start=1):
            score = self.residents[name]['score']
            print(f"    [{i}] {name}  (Score: {score:.1f})")

        try:
            choice = int(input("\n  Enter number to remove (0 to cancel): ").strip())
            if choice == 0:
                return
            if not (1 <= choice <= len(names)):
                print("  [ERROR] Invalid selection.")
                return
        except ValueError:
            print("  [ERROR] Please enter a valid number.")
            return

        name = names[choice - 1]
        del self.residents[name]
        print(f"  [OK] '{name}' removed!")

    # ── View Current Residents ───────────────────────────────────────────────
    def view_residents(self):
        print_header("Current Residents")

        if not self.residents:
            print("  No residents added yet.")
            return

        print(f"  {'#':<4} {'Name':<20} {'Score':>8}")
        print("  " + "-" * 36)
        for i, (name, data) in enumerate(self.residents.items(), start=1):
            print(f"  {i:<4} {name:<20} {data['score']:>8.1f}")

    # ── Calculate Bills ──────────────────────────────────────────────────────
    def calculate_bills(self):
        print_header("Calculate Bills")

        if not self.residents:
            print("  [ERROR] Please add at least one resident first!")
            return

        total_bill = prompt_positive_float("  Enter Total Bill (PHP): ")

        total_score = sum(r['score'] for r in self.residents.values())
        if total_score == 0:
            print("  [ERROR] Total score is zero. No usage recorded!")
            return

        # ── Build output (identical format to GUI version) ──
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
                "name":              name,
                "airconditioner":    data['airconditioner'],
                "inductioncooker":   data['inductioncooker'],
                "multipurposecooker":data['multipurposecooker'],
                "ricecooker":        data['ricecooker'],
                "clipfan":           data['clipfan'],
                "laptopcharging":    data['laptopcharging'],
                "score":             data['score'],
                "total_bill":        total_bill,
                "share":             share,
                "date":              current_time
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

        print("\n" + results)
        print("  [OK] Bills calculated and saved to JSON database!")

    # ── Payment History ──────────────────────────────────────────────────────
    def load_history(self):
        print_header("Payment History (Last 50 Records)")

        records = get_recent_records(50)

        if not records:
            print("  No records found.")
            return

        print(f"\n  {'Name':<20} {'Amount Paid':<15} {'Total Bill':<15} {'Date':<20}")
        print("  " + "-" * 74)

        for record in records:
            name       = record.get('name', 'Unknown')
            share      = record.get('share', 0)
            total_bill = record.get('total_bill', 0)
            date       = record.get('date', 'Unknown')
            print(f"  {name:<20} PHP {share:>10.2f} PHP {total_bill:>10.2f} {date:<20}")

    # ── Main Menu ────────────────────────────────────────────────────────────
    def run(self):
        while True:
            print_header("Dorm Utility Fair Share Calculator")
            print("  [1] Add Resident")
            print("  [2] Remove Resident")
            print("  [3] View Current Residents")
            print("  [4] Calculate Bills")
            print("  [5] View Payment History")
            print("  [6] Exit")
            print()

            choice = input("  Choose an option [1-6]: ").strip()

            if   choice == '1': self.add_resident()
            elif choice == '2': self.remove_resident()
            elif choice == '3': self.view_residents()
            elif choice == '4': self.calculate_bills()
            elif choice == '5': self.load_history()
            elif choice == '6':
                print("\n  Goodbye!\n")
                break
            else:
                print("  [!] Invalid option. Please choose 1-6.")

            input("\n  Press Enter to continue...")

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    init_database()
    app = DormUtilityApp()
    app.run()
