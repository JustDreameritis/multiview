"""Demo file with intentional issues for multiview to find."""
import sqlite3
import os
import pickle
import subprocess

# Hardcoded secret (Code Quality + Security will catch)
API_KEY = "sk-prod-12345678abcdef"
DATABASE_URL = "postgres://admin:password123@db.example.com/prod"


def get_user(user_id):
    """Get user by ID - has SQL injection vulnerability."""
    conn = sqlite3.connect("users.db")
    # SQL injection - user_id inserted directly into query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = conn.execute(query).fetchone()
    conn.close()
    return result


def search_users(name):
    """Search users - another SQL injection point."""
    conn = sqlite3.connect("users.db")
    # SQL injection via string formatting
    cursor = conn.execute("SELECT * FROM users WHERE name LIKE '%" + name + "%'")
    return cursor.fetchall()


def run_command(user_input):
    """Execute system command - command injection vulnerability."""
    # Command injection - user input passed directly to shell
    os.system(f"echo {user_input} >> log.txt")
    subprocess.call(f"grep {user_input} data.txt", shell=True)


def load_user_data(data_bytes):
    """Load serialized data - insecure deserialization."""
    # Insecure deserialization - never unpickle untrusted data
    return pickle.loads(data_bytes)


def process_items(items):
    """Process items - O(n^2) performance issue."""
    results = []
    # O(n^2) nested loop - should use set or dict
    for item in items:
        for other in items:
            if item != other:
                results.append(item + other)
    return results


def find_duplicates(data):
    """Find duplicates - inefficient O(n^2) approach."""
    duplicates = []
    # O(n^2) when O(n) is possible with set
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    return duplicates


def calculate_total(items):
    """Calculate total - unbounded memory growth."""
    all_results = []
    # Unbounded list growth - could exhaust memory
    for item in items:
        for i in range(item.count):
            all_results.append(item.value * i)
    return sum(all_results)


def send_notification(user):
    """Send notification - missing None checks."""
    # Missing None check - will crash if user.email is None
    email = user.email.lower()
    name = user.profile.display_name.strip()

    # Missing None check on nested attribute
    phone = user.contact_info.phone.replace("-", "")

    print(f"Sending to {email}, {name}, {phone}")


def divide_values(a, b):
    """Divide values - missing zero check."""
    # Division by zero not handled
    return a / b


def get_item_at_index(items, index):
    """Get item - off-by-one and bounds issues."""
    # Off-by-one: should be < len(items), not <=
    if index <= len(items):
        return items[index]  # IndexError when index == len(items)
    return None


def parse_config(config_str):
    """Parse config - boundary issues."""
    parts = config_str.split(":")
    # Assumes at least 3 parts without checking
    host = parts[0]
    port = int(parts[1])  # Will crash if not a number
    path = parts[2]  # IndexError if < 3 parts
    return host, port, path


def compare_prices(price1, price2):
    """Compare prices - floating point comparison issue."""
    # Floating point comparison - unreliable
    if price1 == price2:  # Should use math.isclose()
        return "equal"
    return "different"


class DataProcessor:
    """Processor class - God class anti-pattern."""

    def __init__(self):
        self.data = []
        self.cache = {}
        self.config = {}
        self.logger = None
        self.db_conn = None
        self.http_client = None
        self.queue = []
        self.metrics = {}

    # Too many responsibilities in one class
    def load_data(self): pass
    def save_data(self): pass
    def process_data(self): pass
    def validate_data(self): pass
    def transform_data(self): pass
    def export_data(self): pass
    def import_data(self): pass
    def backup_data(self): pass
    def restore_data(self): pass
    def analyze_data(self): pass
    def visualize_data(self): pass
    def send_report(self): pass
    def log_activity(self): pass
    def update_metrics(self): pass
    def sync_with_remote(self): pass


# Circular import potential (Architecture issue)
# from .module_a import helper  # module_a imports this file

# Dead code - never called
def unused_function():
    """This function is never used anywhere."""
    return "I'm dead code"

UNUSED_CONSTANT = 42  # Never referenced


# Magic numbers without explanation
def calculate_score(value):
    """Calculate score - magic numbers."""
    if value > 73:  # What is 73?
        return value * 1.15  # What is 1.15?
    elif value > 42:  # What is 42?
        return value * 0.85  # What is 0.85?
    return value * 0.5  # What is 0.5?


# DRY violation - repeated code
def format_user_name(user):
    name = user.first_name.strip().title()
    name = name + " " + user.last_name.strip().title()
    return name

def format_employee_name(employee):
    name = employee.first_name.strip().title()
    name = name + " " + employee.last_name.strip().title()
    return name

def format_customer_name(customer):
    name = customer.first_name.strip().title()
    name = name + " " + customer.last_name.strip().title()
    return name


# Overly complex conditional
def get_discount(user, order, promo_code, is_holiday, is_weekend):
    """Calculate discount - complex nested conditionals."""
    if user.is_premium:
        if order.total > 100:
            if promo_code:
                if is_holiday:
                    if is_weekend:
                        return 0.35
                    else:
                        return 0.30
                else:
                    if is_weekend:
                        return 0.25
                    else:
                        return 0.20
            else:
                if is_holiday:
                    return 0.15
                else:
                    return 0.10
        else:
            if promo_code:
                return 0.10
            else:
                return 0.05
    else:
        if promo_code:
            return 0.05
        else:
            return 0
