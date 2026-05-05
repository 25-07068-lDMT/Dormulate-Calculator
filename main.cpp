#include <iostream>
#include <fstream>
#include <map>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <ctime>
#include <sstream>

using namespace std;

// ================= STRUCTURES =================

// Structure to hold resident utility usage data
struct ResidentData {
    float airconditioner;      // Hours used
    float inductioncooker;     // Hours used
    float multipurposecooker;  // Hours used
    float ricecooker;          // Hours used
    float clipfan;             // Hours used
    float laptopcharging;      // Hours used
    float score;               // Calculated weighted score
};

// Structure to hold a single bill record for database storage
struct BillRecord {
    string name;               // Resident name
    float airconditioner;      // Hours used
    float inductioncooker;     // Hours used
    float multipurposecooker;  // Hours used
    float ricecooker;          // Hours used
    float clipfan;             // Hours used
    float laptopcharging;      // Hours used
    float score;               // Resident's score
    float total_bill;          // Total dorm bill
    float share;               // Amount resident owes
    string date;               // Date/time of calculation
};

// ================= JSON DATABASE SETUP =================

// Database file name (stores JSON records)
const string DATABASE_FILE = "dorm_utility_records.json";

// Function to get current date and time as string
// Returns: Formatted string "YYYY-MM-DD HH:MM:SS"
string get_current_datetime() {
    time_t now = time(0);
    struct tm* timeinfo = localtime(&now);
    char buffer[80];
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);
    return string(buffer);
}

// Function to initialize database file if it doesn't exist
// Creates empty JSON structure: {"records": []}
void init_database() {
    ifstream file(DATABASE_FILE);
    if (!file.good()) {
        ofstream outfile(DATABASE_FILE);
        outfile << "{\"records\": []}" << endl;
        outfile.close();
    }
    file.close();
}

// Function to append a bill record to the JSON database
// Parameters: record - The BillRecord to save
void save_record(const BillRecord& record) {
    // Read existing records from file
    ifstream infile(DATABASE_FILE);
    string content((istreambuf_iterator<char>(infile)), istreambuf_iterator<char>());
    infile.close();

    // Simple JSON parsing: remove closing bracket and add new record
    // Find the last ']' and insert new record before it
    size_t pos = content.find_last_of(']');
    if (pos != string::npos) {
        // Build JSON object for the new record
        stringstream json_record;
        json_record << "    {\n"
                    << "      \"name\": \"" << record.name << "\",\n"
                    << "      \"airconditioner\": " << record.airconditioner << ",\n"
                    << "      \"inductioncooker\": " << record.inductioncooker << ",\n"
                    << "      \"multipurposecooker\": " << record.multipurposecooker << ",\n"
                    << "      \"ricecooker\": " << record.ricecooker << ",\n"
                    << "      \"clipfan\": " << record.clipfan << ",\n"
                    << "      \"laptopcharging\": " << record.laptopcharging << ",\n"
                    << "      \"score\": " << record.score << ",\n"
                    << "      \"total_bill\": " << record.total_bill << ",\n"
                    << "      \"share\": " << record.share << ",\n"
                    << "      \"date\": \"" << record.date << "\"\n"
                    << "    }\n";

        // Add comma if there are existing records
        if (content.find("\"name\"") != string::npos && content.find("[") + 1 != content.find("{")) {
            content.insert(pos - 1, ",\n");
        }
        content.insert(pos, json_record.str());

        // Write updated content back to file
        ofstream outfile(DATABASE_FILE);
        outfile << content;
        outfile.close();
    }
}

// ================= APPLIANCE WEIGHTS =================

// Map defining weight/importance of each appliance for fair share calculation
// Higher weight = more impact on utility bill
map<string, int> WEIGHTS = {
    {"airconditioner",     5},    // Air conditioner uses most power
    {"inductioncooker",    5},    // Induction cooker uses significant power
    {"multipurposecooker", 4},    // Multi-purpose cooker
    {"ricecooker",         4},    // Rice cooker
    {"clipfan",            1},    // Clip fan uses minimal power
    {"laptopcharging",     1}     // Laptop charging uses minimal power
};

// ================= HELPER FUNCTIONS =================

// Function to clear the terminal screen
// Works on both Windows (cls) and Unix/Linux (clear)
void clear_screen() {
    #ifdef _WIN32
        system("cls");
    #else
        system("clear");
    #endif
}

// Function to print a formatted header section
// Parameters: title - The header text to display
void print_header(const string& title) {
    cout << "\n";
    cout << string(60, '=') << endl;
    cout << "  " << title << endl;
    cout << string(60, '=') << endl;
}

// Function to prompt user for a float input with validation
// Parameters: 
//   prompt - Question to display to user
//   allow_negative - If false, rejects negative numbers
// Returns: Valid float value entered by user
float prompt_float(const string& prompt, bool allow_negative = false) {
    float value;
    while (true) {
        cout << prompt;
        if (cin >> value) {
            cin.ignore();  // Clear input buffer
            if (!allow_negative && value < 0) {
                cout << "  [!] Value cannot be negative. Try again." << endl;
                continue;
            }
            return value;
        } else {
            cin.clear();  // Clear error flag
            cin.ignore(10000, '\n');  // Clear input buffer
            cout << "  [!] Invalid number. Try again." << endl;
        }
    }
}

// Function to prompt user for a positive float (greater than 0)
// Parameters: prompt - Question to display to user
// Returns: Valid positive float value
float prompt_positive_float(const string& prompt) {
    float value;
    while (true) {
        value = prompt_float(prompt);
        if (value <= 0) {
            cout << "  [!] Value must be greater than 0. Try again." << endl;
            continue;
        }
        return value;
    }
}

// ================= CORE APPLICATION CLASS =================

class DormUtilityApp {
private:
    // Map storing resident names and their usage data
    // Key: resident name, Value: ResidentData structure
    map<string, ResidentData> residents;

public:
    // Constructor: initializes the application
    DormUtilityApp() {}

    // ── Add Resident Method ────────────────────────────────────────────────────
    // Prompts user to input a new resident and their appliance usage hours
    // Calculates weighted score based on WEIGHTS map
    void add_resident() {
        print_header("Add Resident Usage");

        // Get resident name from user
        string name;
        cout << "  Resident Name: ";
        getline(cin, name);

        // Validate name is not empty
        if (name.empty()) {
            cout << "  [ERROR] Name cannot be empty!" << endl;
            return;
        }

        // Check if resident already exists
        if (residents.find(name) != residents.end()) {
            cout << "  [ERROR] '" << name << "' already exists!" << endl;
            return;
        }

        // Create new resident data structure
        ResidentData data;
        cout << endl;

        // Prompt for each appliance usage in hours
        // Weight values shown to user for reference
        data.airconditioner = prompt_float(
            "  Air Conditioner (hours) [Weight: " + 
            to_string(WEIGHTS["airconditioner"]) + "]: "
        );
        data.inductioncooker = prompt_float(
            "  Induction Cooker (hours) [Weight: " + 
            to_string(WEIGHTS["inductioncooker"]) + "]: "
        );
        data.multipurposecooker = prompt_float(
            "  Multi-Purpose Cooker (hours) [Weight: " + 
            to_string(WEIGHTS["multipurposecooker"]) + "]: "
        );
        data.ricecooker = prompt_float(
            "  Rice Cooker (hours) [Weight: " + 
            to_string(WEIGHTS["ricecooker"]) + "]: "
        );
        data.clipfan = prompt_float(
            "  Clip Fan (hours) [Weight: " + 
            to_string(WEIGHTS["clipfan"]) + "]: "
        );
        data.laptopcharging = prompt_float(
            "  Laptop Charging (hours) [Weight: " + 
            to_string(WEIGHTS["laptopcharging"]) + "]: "
        );

        // Calculate weighted score: sum of (hours * weight) for each appliance
        data.score = (data.airconditioner * WEIGHTS["airconditioner"]) +
                     (data.inductioncooker * WEIGHTS["inductioncooker"]) +
                     (data.multipurposecooker * WEIGHTS["multipurposecooker"]) +
                     (data.ricecooker * WEIGHTS["ricecooker"]) +
                     (data.clipfan * WEIGHTS["clipfan"]) +
                     (data.laptopcharging * WEIGHTS["laptopcharging"]);

        // Store resident in map
        residents[name] = data;

        // Display confirmation with score
        cout << fixed << setprecision(1);
        cout << "\n  [OK] '" << name << "' added! Score: " << data.score << endl;
    }

    // ── Remove Resident Method ──────────────────────────────────────────────────
    // Displays list of residents and removes selected one
    void remove_resident() {
        print_header("Remove Resident");

        // Check if any residents exist
        if (residents.empty()) {
            cout << "  [!] No residents added yet." << endl;
            return;
        }

        // Display all current residents with numbers
        cout << "  Current Residents:" << endl;
        vector<string> names;
        int counter = 1;
        for (const auto& pair : residents) {
            names.push_back(pair.first);
            cout << "    [" << counter << "] " << pair.first 
                 << "  (Score: " << fixed << setprecision(1) << pair.second.score << ")" << endl;
            counter++;
        }

        // Prompt user to select resident number to remove
        int choice;
        cout << "\n  Enter number to remove (0 to cancel): ";
        if (!(cin >> choice)) {
            cin.clear();
            cin.ignore(10000, '\n');
            cout << "  [ERROR] Please enter a valid number." << endl;
            return;
        }
        cin.ignore();

        // Validate selection
        if (choice == 0) {
            return;  // Cancel operation
        }
        if (choice < 1 || choice > (int)names.size()) {
            cout << "  [ERROR] Invalid selection." << endl;
            return;
        }

        // Remove selected resident
        string name = names[choice - 1];
        residents.erase(name);
        cout << "  [OK] '" << name << "' removed!" << endl;
    }

    // ── View Current Residents Method ───────────────────────────────────────────
    // Displays table of all residents and their scores
    void view_residents() {
        print_header("Current Residents");

        // Check if any residents exist
        if (residents.empty()) {
            cout << "  No residents added yet." << endl;
            return;
        }

        // Print table header
        cout << "  " << setw(4) << left << "#" 
             << setw(20) << left << "Name" 
             << setw(8) << right << "Score" << endl;
        cout << "  " << string(36, '-') << endl;

        // Print each resident in table format
        int counter = 1;
        for (const auto& pair : residents) {
            cout << "  " << setw(4) << left << counter
                 << setw(20) << left << pair.first
                 << setw(8) << right << fixed << setprecision(1) << pair.second.score << endl;
            counter++;
        }
    }

    // ── Calculate Bills Method ──────────────────────────────────────────────────
    // Main calculation function:
    // 1. Gets total bill from user
    // 2. Calculates fair share for each resident based on weighted scores
    // 3. Displays detailed receipt for each resident
    // 4. Saves records to JSON database
    void calculate_bills() {
        print_header("Calculate Bills");

        // Validate residents exist
        if (residents.empty()) {
            cout << "  [ERROR] Please add at least one resident first!" << endl;
            return;
        }

        // Prompt for total dorm utility bill
        float total_bill = prompt_positive_float("  Enter Total Bill (PHP): ");

        // Calculate sum of all residents' scores
        float total_score = 0;
        for (const auto& pair : residents) {
            total_score += pair.second.score;
        }

        // Validate total score is not zero
        if (total_score == 0) {
            cout << "  [ERROR] Total score is zero. No usage recorded!" << endl;
            return;
        }

        // Build results output string
        string results = "";
        results += string(80, '=') + "\n";
        results += "DORM UTILITY BILL CALCULATION RESULTS\n";
        results += string(80, '=') + "\n\n";

        // Display total bill and score
        stringstream ss;
        ss << fixed << setprecision(2);
        ss << "Total Bill: PHP " << total_bill << "\n";
        results += ss.str();
        ss.str("");
        ss.clear();
        ss << "Total Score: " << total_score << "\n\n";
        results += ss.str();

        // Find highest and lowest consumers
        string highest = "";
        string lowest = "";
        float highest_score = -1;
        float lowest_score = FLT_MAX;

        for (const auto& pair : residents) {
            if (pair.second.score > highest_score) {
                highest_score = pair.second.score;
                highest = pair.first;
            }
            if (pair.second.score < lowest_score) {
                lowest_score = pair.second.score;
                lowest = pair.first;
            }
        }

        results += "[HIGH] Highest Consumer: " + highest + "\n";
        results += "[LOW]  Lowest Consumer:  " + lowest + "\n";
        results += string(80, '=') + "\n\n";

        // Get current date/time for records
        string current_time = get_current_datetime();

        // Calculate and display bill for each resident
        for (const auto& pair : residents) {
            const string& name = pair.first;
            const ResidentData& data = pair.second;

            // Calculate fair share: (resident score / total score) * total bill
            float share = (data.score / total_score) * total_bill;
            float percentage = (data.score / total_score) * 100;

            // Create bill record for database
            BillRecord record;
            record.name = name;
            record.airconditioner = data.airconditioner;
            record.inductioncooker = data.inductioncooker;
            record.multipurposecooker = data.multipurposecooker;
            record.ricecooker = data.ricecooker;
            record.clipfan = data.clipfan;
            record.laptopcharging = data.laptopcharging;
            record.score = data.score;
            record.total_bill = total_bill;
            record.share = share;
            record.date = current_time;

            // Save record to JSON database
            save_record(record);

            // Format receipt output
            ss.str("");
            ss.clear();
            ss << fixed << setprecision(1);

            results += string(80, '=') + "\n";
            results += "RECEIPT FOR: " + name + "\n";
            results += string(80, '=') + "\n";
            results += "Usage Breakdown (Hours x Weight = Points):\n";
            results += "  - Air Conditioner:      ";
            ss << setw(6) << data.airconditioner << "h x " << WEIGHTS["airconditioner"] 
               << " = " << setw(6) << (data.airconditioner * WEIGHTS["airconditioner"]) << "\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(1);
            results += "  - Induction Cooker:     ";
            ss << setw(6) << data.inductioncooker << "h x " << WEIGHTS["inductioncooker"] 
               << " = " << setw(6) << (data.inductioncooker * WEIGHTS["inductioncooker"]) << "\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(1);
            results += "  - Multi-Purpose Cooker: ";
            ss << setw(6) << data.multipurposecooker << "h x " << WEIGHTS["multipurposecooker"] 
               << " = " << setw(6) << (data.multipurposecooker * WEIGHTS["multipurposecooker"]) << "\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(1);
            results += "  - Rice Cooker:          ";
            ss << setw(6) << data.ricecooker << "h x " << WEIGHTS["ricecooker"] 
               << " = " << setw(6) << (data.ricecooker * WEIGHTS["ricecooker"]) << "\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(1);
            results += "  - Clip Fan:             ";
            ss << setw(6) << data.clipfan << "h x " << WEIGHTS["clipfan"] 
               << " = " << setw(6) << (data.clipfan * WEIGHTS["clipfan"]) << "\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(1);
            results += "  - Laptop Charging:      ";
            ss << setw(6) << data.laptopcharging << "h x " << WEIGHTS["laptopcharging"] 
               << " = " << setw(6) << (data.laptopcharging * WEIGHTS["laptopcharging"]) << "\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(2);
            results += "\nCalculation:\n";
            results += "  Your Total Score:   " + to_string(data.score) + "\n";
            results += "  Global Total Score: " + to_string(total_score) + "\n";
            ss << "  Your Share:         " << setprecision(2) << percentage << "%\n";
            results += ss.str();

            ss.str("");
            ss.clear();
            ss << fixed << setprecision(2);
            ss << "\n  AMOUNT TO PAY: PHP " << share << "\n";
            results += ss.str();

            results += string(80, '=') + "\n\n";
        }

        // Display complete results
        cout << "\n" << results;
        cout << "  [OK] Bills calculated and saved to JSON database!" << endl;
    }

    // ── Load Payment History Method ─────────────────────────────────────────────
    // Reads JSON database and displays last 50 payment records
    // Shows: resident name, amount paid, total bill, and date
    void load_history() {
        print_header("Payment History (Last 50 Records)");

        // Read JSON file
        ifstream file(DATABASE_FILE);
        string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
        file.close();

        // Simple check: if no records found, display message
        if (content.find("\"name\"") == string::npos) {
            cout << "  No records found." << endl;
            return;
        }

        // Display table header
        cout << "\n  " << setw(20) << left << "Name"
             << setw(15) << left << "Amount Paid"
             << setw(15) << left << "Total Bill"
             << setw(20) << left << "Date" << endl;
        cout << "  " << string(74, '-') << endl;

        // Parse and display each record (simplified JSON parsing)
        // In production, would use proper JSON library
        size_t pos = 0;
        int count = 0;
        while ((pos = content.find("\"name\"", pos)) != string::npos && count < 50) {
            // Extract name
            size_t name_start = content.find("\"", pos + 7) + 1;
            size_t name_end = content.find("\"", name_start);
            string name = content.substr(name_start, name_end - name_start);

            // Extract share (amount paid)
            size_t share_pos = content.find("\"share\"", pos);
            size_t share_start = content.find(":", share_pos) + 1;
            size_t share_end = content.find(",", share_start);
            string share_str = content.substr(share_start, share_end - share_start);
            
            // Extract total_bill
            size_t bill_pos = content.find("\"total_bill\"", pos);
            size_t bill_start = content.find(":", bill_pos) + 1;
            size_t bill_end = content.find(",", bill_start);
            string bill_str = content.substr(bill_start, bill_end - bill_start);

            // Extract date
            size_t date_pos = content.find("\"date\"", pos);
            size_t date_start = content.find("\"", date_pos + 7) + 1;
            size_t date_end = content.find("\"", date_start);
            string date = content.substr(date_start, date_end - date_start);

            // Display record
            cout << "  " << setw(20) << left << name
                 << "PHP " << setw(10) << right << fixed << setprecision(2) << stof(share_str)
                 << "PHP " << setw(10) << right << fixed << setprecision(2) << stof(bill_str)
                 << setw(20) << left << date << endl;

            pos += 6;
            count++;
        }
    }

    // ── Main Menu and Event Loop ────────────────────────────────────────────────
    // Displays menu and handles user choices until exit
    void run() {
        while (true) {
            print_header("Dorm Utility Fair Share Calculator");
            cout << "  [1] Add Resident\n";
            cout << "  [2] Remove Resident\n";
            cout << "  [3] View Current Residents\n";
            cout << "  [4] Calculate Bills\n";
            cout << "  [5] View Payment History\n";
            cout << "  [6] Exit\n";
            cout << endl;

            string choice;
            cout << "  Choose an option [1-6]: ";
            getline(cin, choice);

            // Route to appropriate function based on user choice
            if (choice == "1") {
                add_resident();
            } else if (choice == "2") {
                remove_resident();
            } else if (choice == "3") {
                view_residents();
            } else if (choice == "4") {
                calculate_bills();
            } else if (choice == "5") {
                load_history();
            } else if (choice == "6") {
                cout << "\n  Goodbye!\n" << endl;
                break;
            } else {
                cout << "  [!] Invalid option. Please choose 1-6." << endl;
            }

            cout << "\n  Press Enter to continue...";
            cin.get();
        }
    }
};

// ================= MAIN EXECUTION =================

// Entry point: initializes database and runs application
int main() {
    // Create JSON database file if it doesn't exist
    init_database();

    // Create application instance and run main loop
    DormUtilityApp app;
    app.run();

    return 0;
}
