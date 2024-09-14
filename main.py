import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('personal_finance.db')
cursor = conn.cursor()

# Create necessary tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        category TEXT,
        amount REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        budget REAL,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    )
''')

conn.commit()

# Function to set background image with persistent reference
def set_background(window):
    try:
        bg_image = Image.open("D:/Code World/Python/bg.jpg")  # Update your image path
        bg_image = bg_image.resize((600, 650))
        bg_photo = ImageTk.PhotoImage(bg_image)
        
        # Store the image in the window's attribute to prevent garbage collection
        window.bg_photo = bg_photo
        
        background_label = tk.Label(window, image=bg_photo)
        background_label.place(relwidth=1, relheight=1)
    except FileNotFoundError:
        messagebox.showwarning("Warning", "Background image not found!")

# Function to register a user
def register_user(username, password):
    try:
        cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")

# Function to handle login
def login_user(username, password, window):
    cursor.execute("SELECT id FROM Users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    if result:
        window.destroy()  # Close login window
        open_user_menu(result[0])  # Open user menu with user_id
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Function to open the registration window
def open_registration_window():
    registration_window = tk.Toplevel()
    registration_window.title("Register")
    registration_window.geometry("600x650+450+100")
    registration_window.resizable(False, False)
    set_background(registration_window)

    tk.Label(registration_window, text="Register", font=("Times New Roman", 18)).pack(pady=10)

    tk.Label(registration_window, text="Username:", font=("Times New Roman", 14)).pack(pady=5)
    reg_username = tk.StringVar()
    tk.Entry(registration_window, textvariable=reg_username).pack()

    tk.Label(registration_window, text="Password:", font=("Times New Roman", 14)).pack(pady=5)
    reg_password = tk.StringVar()
    tk.Entry(registration_window, textvariable=reg_password, show="*").pack()

    tk.Button(registration_window, text="Register", font=("Times New Roman", 14),
              command=lambda: register_user(reg_username.get(), reg_password.get())).pack(pady=10)

# Function to open the login window
def open_login_window():
    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.geometry("600x650+450+100")
    login_window.resizable(False, False)
    set_background(login_window)

    tk.Label(login_window, text="Login", font=("Times New Roman", 18)).pack(pady=10)

    tk.Label(login_window, text="Username:", font=("Times New Roman", 14)).pack(pady=5)
    login_username = tk.StringVar()
    tk.Entry(login_window, textvariable=login_username).pack()

    tk.Label(login_window, text="Password:", font=("Times New Roman", 14)).pack(pady=5)
    login_password = tk.StringVar()
    tk.Entry(login_window, textvariable=login_password, show="*").pack()

    tk.Button(login_window, text="Login", font=("Times New Roman", 14),
              command=lambda: login_user(login_username.get(), login_password.get(), login_window)).pack(pady=10)

# Function to save a transaction
def save_transaction(user_id, t_type, category, amount, date):
    cursor.execute("INSERT INTO Transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)", 
                   (user_id, t_type, category, amount, date))
    conn.commit()
    messagebox.showinfo("Transaction", "Transaction added successfully!")

# Function to update an existing transaction
def update_transaction(transaction_id, t_type, category, amount, date):
    cursor.execute("UPDATE Transactions SET type = ?, category = ?, amount = ?, date = ? WHERE id = ?", 
                   (t_type, category, amount, date, transaction_id))
    conn.commit()
    messagebox.showinfo("Transaction", "Transaction updated successfully!")

# Function to delete a transaction
def delete_transaction(transaction_id):
    cursor.execute("DELETE FROM Transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    messagebox.showinfo("Transaction", "Transaction deleted successfully!")

# Function to view all transactions
def view_transactions(user_id):
    cursor.execute("SELECT id, type, category, amount, date FROM Transactions WHERE user_id = ?", (user_id,))
    transactions = cursor.fetchall()

    transactions_window = tk.Toplevel()
    transactions_window.title("View Transactions")
    transactions_window.geometry("600x650+450+100")
    transactions_window.resizable(False, False)
    set_background(transactions_window)

    text_area = tk.Text(transactions_window, font=("Times New Roman", 14))
    text_area.pack(pady=10)

    if transactions:
        for transaction in transactions:
            text_area.insert(tk.END, f"Transaction ID: {transaction[0]}, Type: {transaction[1]}, "
                                     f"Category: {transaction[2]}, Amount: {transaction[3]}, Date: {transaction[4]}\n")
    else:
        text_area.insert(tk.END, "No transactions found.")

    text_area.config(state="disabled")

# Function to open Delete Transaction window
def open_delete_transaction_window(user_id):
    delete_window = tk.Toplevel()
    delete_window.title("Delete Transaction")
    delete_window.geometry("600x650+450+100")
    delete_window.resizable(False, False)
    set_background(delete_window)

    tk.Label(delete_window, text="Delete Transaction", font=("Times New Roman", 18)).pack(pady=10)

    tk.Label(delete_window, text="Enter Transaction ID:", font=("Times New Roman", 14)).pack(pady=5)
    transaction_id = tk.IntVar()
    tk.Entry(delete_window, textvariable=transaction_id).pack()

    tk.Button(delete_window, text="Delete", font=("Times New Roman", 14),
              command=lambda: delete_transaction(transaction_id.get())).pack(pady=10)

# Function to set a budget for a category
def set_budget(user_id, category, budget):
    cursor.execute("INSERT OR REPLACE INTO Budget (user_id, category, budget) VALUES (?, ?, ?)",
                   (user_id, category, budget))
    conn.commit()
    messagebox.showinfo("Budget", "Budget set successfully!")
    
# Function to notify if expenses exceed budget
def check_budget_exceeded(user_id, category):
    cursor.execute("SELECT SUM(amount) FROM Transactions WHERE user_id = ? AND type = 'Expense' AND category = ?", 
                   (user_id, category))
    total_spent = cursor.fetchone()[0] or 0

    cursor.execute("SELECT budget FROM Budget WHERE user_id = ? AND category = ?", (user_id, category))
    budget = cursor.fetchone()
    set_background(set_budget)
    if budget and total_spent > budget[0]:
        messagebox.showwarning("Budget Exceeded", f"You have exceeded your budget for {category}!")
    else:
        messagebox.showinfo("Budget", f"You are within the budget for {category}.")

# Function to generate and display a monthly report
def generate_monthly_report(user_id, month, year):
    cursor.execute("""
        SELECT category, SUM(amount) FROM Transactions 
        WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ? AND type = 'Expense'
        GROUP BY category
    """, (user_id, f"{month:02}", year))
    report_data = cursor.fetchall()

    report_window = tk.Toplevel()
    report_window.title("Monthly Report")
    report_window.geometry("600x650+450+100")
    report_window.resizable(False, False)
    set_background(generate_monthly_report)
    text_area = tk.Text(report_window, font=("Times New Roman", 14))
    text_area.pack(pady=10)

    text_area.insert(tk.END, f"Monthly Report for {month}/{year}\n\n")
    for category, amount in report_data:
        text_area.insert(tk.END, f"Category: {category}, Amount: {amount}\n")

    text_area.config(state="disabled")

# Function to generate and display a yearly report
def generate_yearly_report(user_id, year):
    cursor.execute("""
        SELECT category, SUM(amount) FROM Transactions 
        WHERE user_id = ? AND strftime('%Y', date) = ? AND type = 'Expense'
        GROUP BY category
    """, (user_id, year))
    report_data = cursor.fetchall()

    report_window = tk.Toplevel()
    report_window.title("Yearly Report")
    report_window.geometry("600x650+450+100")
    report_window.resizable(False, False)

    text_area = tk.Text(report_window, font=("Times New Roman", 14))
    text_area.pack(pady=10)

    text_area.insert(tk.END, f"Yearly Report for {year}\n\n")
    for category, amount in report_data:
        text_area.insert(tk.END, f"Category: {category}, Amount: {amount}\n")

    text_area.config(state="disabled")

# Function to open Set Budget window
def open_set_budget_window(user_id):
    budget_window = tk.Toplevel()
    budget_window.title("Set Budget")
    budget_window.geometry("600x650+450+100")
    budget_window.resizable(False, False)

    tk.Label(budget_window, text="Set Budget", font=("Times New Roman", 18)).pack(pady=10)

    tk.Label(budget_window, text="Category:", font=("Times New Roman", 14)).pack(pady=5)
    category = tk.StringVar()
    tk.Entry(budget_window, textvariable=category).pack()

    tk.Label(budget_window, text="Budget Amount:", font=("Times New Roman", 14)).pack(pady=5)
    budget = tk.DoubleVar()
    tk.Entry(budget_window, textvariable=budget).pack()

    tk.Button(budget_window, text="Set Budget", font=("Times New Roman", 14),
              command=lambda: set_budget(user_id, category.get(), budget.get())).pack(pady=10)

import calendar

# Function to open the report window and select either monthly or yearly report
def open_report_window(user_id):
    report_window = tk.Toplevel()
    report_window.title("Generate Report")
    report_window.geometry("600x400+450+100")
    report_window.resizable(False, False)
    set_background(report_window)

    tk.Label(report_window, text="Select Report Type", font=("Times New Roman", 18)).pack(pady=10)

    report_type = tk.StringVar()
    report_type.set("monthly")  # Default option

    tk.Radiobutton(report_window, text="Monthly", variable=report_type, value="monthly", font=("Times New Roman", 14)).pack(pady=5)
    tk.Radiobutton(report_window, text="Yearly", variable=report_type, value="yearly", font=("Times New Roman", 14)).pack(pady=5)

    # Entry fields for selecting the year and month
    tk.Label(report_window, text="Year (YYYY):", font=("Times New Roman", 14)).pack(pady=5)
    year_var = tk.StringVar()
    year_entry = tk.Entry(report_window, textvariable=year_var, font=("Times New Roman", 14))
    year_entry.pack()

    tk.Label(report_window, text="Month (MM):", font=("Times New Roman", 14)).pack(pady=5)
    month_var = tk.StringVar()
    month_entry = tk.Entry(report_window, textvariable=month_var, font=("Times New Roman", 14))
    month_entry.pack()

    tk.Button(report_window, text="Generate Report", font=("Times New Roman", 14),
              command=lambda: generate_report(user_id, report_type.get(), year_var.get(), month_var.get())).pack(pady=20)

# Function to generate and display a report (monthly or yearly)
def generate_report(user_id, report_type, year, month):
    report_display_window = tk.Toplevel()
    report_display_window.title(f"{report_type.capitalize()} Report")
    report_display_window.geometry("600x650+450+100")
    report_display_window.resizable(False, False)
    set_background(report_display_window)

    # Initialize variables to store income, expenses, and savings
    total_income = 0
    total_expenses = 0

    # Validate year and month inputs
    if not year.isdigit() or (report_type == "monthly" and not month.isdigit()):
        messagebox.showerror("Input Error", "Please enter valid year and month.")
        return

    # Fetch transactions based on the selected report type
    if report_type == "monthly":
        cursor.execute('''SELECT type, amount FROM Transactions
                          WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?''',
                       (user_id, year, f"{int(month):02d}"))
    else:
        cursor.execute('''SELECT type, amount FROM Transactions
                          WHERE user_id = ? AND strftime('%Y', date) = ?''',
                       (user_id, year))

    transactions = cursor.fetchall()

    # Calculate total income, expenses, and savings
    for transaction in transactions:
        if transaction[0] == "Income":
            total_income += transaction[1]
        else:
            total_expenses += transaction[1]

    savings = total_income - total_expenses

    # Display the totals in the report window
    tk.Label(report_display_window, text=f"Total Income: {total_income}", font=("Times New Roman", 14)).pack(pady=5)
    tk.Label(report_display_window, text=f"Total Expenses: {total_expenses}", font=("Times New Roman", 14)).pack(pady=5)
    tk.Label(report_display_window, text=f"Savings: {savings}", font=("Times New Roman", 14)).pack(pady=5)

    # Function to create a bar graph of income vs expenses
    def create_bar_graph():
        canvas = tk.Canvas(report_display_window, width=500, height=400)
        canvas.pack(pady=20)

        # Calculate the scale for the bar heights
        max_value = max(total_income, total_expenses, 1)
        income_bar_height = (total_income / max_value) * 300
        expenses_bar_height = (total_expenses / max_value) * 300

        # Draw bars for income and expenses
        canvas.create_rectangle(100, 400 - income_bar_height, 200, 400, fill="green", outline="black", width=2)
        canvas.create_text(150, 410, text="Income", font=("Times New Roman", 12))

        canvas.create_rectangle(300, 400 - expenses_bar_height, 400, 400, fill="red", outline="black", width=2)
        canvas.create_text(350, 410, text="Expenses", font=("Times New Roman", 12))

    # Create bar graph button
    tk.Button(report_display_window, text="Show Bar Graph", font=("Times New Roman", 14),
              command=create_bar_graph).pack(pady=10)


# Function to open Add Transaction window
def open_add_transaction_window(user_id):
    transaction_window = tk.Toplevel()
    transaction_window.title("Add Transaction")
    transaction_window.geometry("600x650+450+100")
    transaction_window.resizable(False, False)
    set_background(transaction_window)

    tk.Label(transaction_window, text="Add Transaction", font=("Times New Roman", 18)).pack(pady=10)

    tk.Label(transaction_window, text="Type:", font=("Times New Roman", 14)).pack(pady=5)
    t_type = tk.StringVar()
    ttk.Combobox(transaction_window, textvariable=t_type, values=["Income", "Expense"]).pack()

    tk.Label(transaction_window, text="Category:", font=("Times New Roman", 14)).pack(pady=5)
    category = tk.StringVar()
    tk.Entry(transaction_window, textvariable=category).pack()

    tk.Label(transaction_window, text="Amount:", font=("Times New Roman", 14)).pack(pady=5)
    amount = tk.DoubleVar()
    tk.Entry(transaction_window, textvariable=amount).pack()

    tk.Label(transaction_window, text="Date (YYYY-MM-DD):", font=("Times New Roman", 14)).pack(pady=5)
    date = tk.StringVar()
    tk.Entry(transaction_window, textvariable=date).pack()

    tk.Button(transaction_window, text="Add", font=("Times New Roman", 14),
              command=lambda: save_transaction(user_id, t_type.get(), category.get(), amount.get(), date.get())).pack(pady=10)

# Function to open user menu
def open_user_menu(user_id):
    menu_window = tk.Toplevel()
    menu_window.title("User Menu")
    menu_window.geometry("600x650+450+100")
    menu_window.resizable(False, False)
    set_background(menu_window)

    tk.Label(menu_window, text="User Menu", font=("Times New Roman", 18)).pack(pady=10)

    tk.Button(menu_window, text="Add Transaction", font=("Times New Roman", 14),
              command=lambda: open_add_transaction_window(user_id)).pack(pady=5)
    
    tk.Button(menu_window, text="View Transactions", font=("Times New Roman", 14),
              command=lambda: view_transactions(user_id)).pack(pady=5)

    tk.Button(menu_window, text="Delete Transaction", font=("Times New Roman", 14),
              command=lambda: open_delete_transaction_window(user_id)).pack(pady=5)

    tk.Button(menu_window, text="Set Budget", font=("Times New Roman", 14),
              command=lambda: open_set_budget_window(user_id)).pack(pady=5)

    tk.Button(menu_window, text="Generate Reports", font=("Times New Roman", 14),
              command=lambda: open_report_window(user_id)).pack(pady=5)


# Main window
root = tk.Tk()
root.title("Personal Finance Management")
root.geometry("600x650+450+100")
root.resizable(False, False)
set_background(root)

tk.Label(root, text="Personal Finance Management", font=("Times New Roman", 18)).pack(pady=10)

tk.Button(root, text="Register", font=("Times New Roman", 14), command=open_registration_window).pack(pady=5)
tk.Button(root, text="Login", font=("Times New Roman", 14), command=open_login_window).pack(pady=5)

root.mainloop()
