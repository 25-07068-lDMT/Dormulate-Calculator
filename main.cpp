#include <iostream> 
#include <fstream>
#include <iomanip>
#include <string>
#include <vector>
#include <map>
#include <ctime>

using namespace std;

#ifdef _WIN32
    #define CLEAR "cls"
#else
    #define CLEAR "clear"
#endif

// ===== CONFIG =====
const string DB_FILE = "dorm_records.json";

const vector<pair<string,string>> APPLIANCES = {
    {"Air Conditioner (hrs)", "ac"}, {"Induction Cooker (hrs)", "ic"},
    {"Multi-Purpose Cooker (hrs)", "mc"}, {"Rice Cooker (hrs)", "rc"},
    {"Clip Fan (hrs)", "cf"}, {"Laptop Charging (hrs)", "lc"}
};

const map<string,int> W = {
    {"ac",5}, {"ic",5}, {"mc",4}, {"rc",4}, {"cf",1}, {"lc",1}
};

// ===== DATA =====
struct Resident {
    string name;
    map<string,double> hrs;
    double score = 0;
};

vector<Resident> residents;

// ===== HELPERS =====
void sep(int n=60, char c='=') { cout << string(n, c) << "\n"; }
void header(const string& title) { cout << "\n" << string(60, '=') << "\n  " << title << "\n" << string(60, '=') << "\n"; }

string timestamp() {
    time_t now = time(nullptr);
    char buf[20];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", localtime(&now));
    return buf;
}

string trim(const string& s) {
    auto a = s.find_first_not_of(" \t"), b = s.find_last_not_of(" \t");
    return (a == string::npos) ? "" : s.substr(a, b - a + 1);
}

double input_float(const string& prompt, bool positive_only = false) {
    while (true) {
        cout << prompt;
        string line; getline(cin, line);
        try {
            double value = stod(trim(line));
            if (positive_only && value < 0.001) throw invalid_argument("Must be positive");
            return value;
        } catch (...) { cout << "  [!] Invalid input. Try again.\n"; }
    }
}

// ===== JSON =====
void save_history(const Resident& r, double total_bill, double share) {
    ifstream fi(DB_FILE);
    string content = "[]";
    if (fi) {
        getline(fi, content, '\0');
        size_t a = content.find('['), b = content.rfind(']');
        if (a != string::npos && b != string::npos)
            content = content.substr(a + 1, b - a - 1);
    }

    ostringstream entry;
    entry << fixed << setprecision(4);
    entry << "{\"name\":\"" << r.name << "\",\"score\":" << r.score << ",\"total_bill\":" << total_bill << ",\"share\":" << share << ",\"date\":\"" << timestamp() << "\"}";

    ofstream fo(DB_FILE);
    fo << "[\n" << content << (content.empty() ? "" : ",\n") << entry.str() << "\n]";
}

void view_history() {
    header("Payment History");
    ifstream fi(DB_FILE);
    if (!fi) { cout << "  No records found.\n"; return; }

    string raw((istreambuf_iterator<char>(fi)), {});
    if (raw.find('{') == string::npos) { cout << "  No records found.\n"; return; }

    auto extract = [&](const string& src, const string& key) -> string {
        size_t pos = src.find("\"" + key + "\"");
        if (pos == string::npos) return "";
        pos = src.find(':', pos) + 1;
        while (pos < src.size() && src[pos] == ' ') ++pos;
        if (src[pos] == '"') {
            size_t start = ++pos, end = src.find('"', start);
            return src.substr(start, end - start);
        } else {
            size_t end = pos;
            while (end < src.size() && src[end] != ',' && src[end] != '}') ++end;
            return src.substr(pos, end - pos);
        }
    };

    cout << "\n  " << left << setw(18) << "Name" << setw(14) << "Share (PHP)" << setw(14) << "Bill (PHP)" << "Date\n";
    cout << "  " << string(60, '-') << "\n";

    size_t pos = 0;
    int count = 0;
    while ((pos = raw.find('{', pos)) != string::npos && count < 50) {
        size_t end = raw.find('}', pos);
        string obj = raw.substr(pos, end - pos + 1);
        cout << "  " << left << setw(18) << extract(obj, "name") 
             << setw(14) << extract(obj, "share") 
             << setw(14) << extract(obj, "total_bill") 
             << extract(obj, "date") << "\n";
        pos = end + 1; ++count;
    }
    if (!count) cout << "  No records found.\n";
}

// ===== MENU ACTIONS =====
void add_resident() {
    header("Add Resident");
    cout << "  Name: "; string name; getline(cin, name);
    name = trim(name);
    if (name.empty()) { cout << "  [!] Name cannot be empty.\n"; return; }
    if (any_of(residents.begin(), residents.end(), [&name](const Resident& r) { return r.name == name; })) {
        cout << "  [!] '" << name << "' already exists.\n"; return;
    }
    Resident res{name};
    for (const auto& [label, key] : APPLIANCES) {
        double v = input_float("  " + label + " [w=" + to_string(W.at(key)) + "]: ");
        res.hrs[key] = v;
        res.score += v * W.at(key);
    }
    residents.push_back(res);
    cout << fixed << setprecision(1) << "\n  [OK] '" << name << "' added. Score: " << res.score << "\n";
}

void remove_resident() {
    header("Remove Resident");
    if (residents.empty()) { cout << "  No residents yet.\n"; return; }
    for (size_t i = 0; i < residents.size(); ++i)
        cout << "  [" << (i + 1) << "] " << residents[i].name << " (Score: " << fixed << setprecision(1) << residents[i].score << ")\n";
    
    cout << "  Remove # (0=cancel): "; string line; getline(cin, line);
    try {
        int c = stoi(line);
        if (c == 0) return;
        if (c < 1 || c >(int)residents.size()) { cout << "  [!] Invalid.\n"; return; }
        cout << "  [OK] '" << residents[c - 1].name << "' removed.\n";
        residents.erase(residents.begin() + c - 1);
    } catch (...) { cout << "  [!] Invalid input.\n"; }
}

void view_residents() {
    header("Current Residents");
    if (residents.empty()) { cout << "  No residents yet.\n"; return; }
    cout << "  " << left << setw(4) << "#" << setw(20) << "Name" << right << setw(8) << "Score\n";
    cout << "  " << string(34, '-') << "\n";
    for (size_t i = 0; i < residents.size(); ++i)
        cout << fixed << setprecision(1) << "  " << left << setw(4) << (i + 1) << setw(20) << residents[i].name << right << setw(8) << residents[i].score << "\n";
}

void calculate_bills() {
    header("Calculate Bills");
    if (residents.empty()) { cout << "  [!] Add residents first.\n"; return; }

    double bill = input_float("  Total Bill (PHP): ", true);
    double total_score = accumulate(residents.begin(), residents.end(), 0.0, [](double sum, const Resident& r) { return sum + r.score; });
    if (total_score == 0) { cout << "  [!] All scores are zero.\n"; return; }

    cout << "\n"; sep(60); cout << "RESULTS\n"; sep(60);
    cout << fixed << setprecision(2);
    cout << "Total Bill: PHP " << bill << "  |  Total Score: " << total_score << "\n\n";

    for (const auto& r : residents) {
        double share = (r.score / total_score) * bill;
        double pct   = (r.score / total_score) * 100.0;

        sep(60, '-');
        cout << "RESIDENT : " << r.name << "\n";
        cout << "Score    : " << fixed << setprecision(1) << r.score << " (" << setprecision(1) << pct << "%)\n";
        cout << "TO PAY   : PHP " << setprecision(2) << share << "\n";
        save_history(r, bill, share);
    }
    sep(60);
    cout << "\n  [OK] Saved to " << DB_FILE << "\n";
}

// ===== MAIN =====
int main() {
    ifstream chk(DB_FILE);
    if (!chk) { ofstream f(DB_FILE); f << "[]"; }

    while (true) {
        system(CLEAR);
        header("Dorm Utility Fair Share Calculator");
        cout << "  [1] Add Resident\n"
             << "  [2] Remove Resident\n"
             << "  [3] View Residents\n"
             << "  [4] Calculate Bills\n"
             << "  [5] View History\n"
             << "  [6] Exit\n\n"
             << "  Choice: ";
        string choice; getline(cin, choice);
        choice = trim(choice);

        if (choice == "1") add_resident();
        else if (choice == "2") remove_resident();
        else if (choice == "3") view_residents();
        else if (choice == "4") calculate_bills();
        else if (choice == "5") view_history();
        else if (choice == "6") { cout << "\n  Goodbye!\n"; break; }
        else cout << "  [!] Invalid option.\n";

        cout << "\n  Press Enter..."; string d; getline(cin, d);
    }
}
