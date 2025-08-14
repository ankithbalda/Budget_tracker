import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Database Setup ---

def initialize_database():
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    # Users table for simple login/auth
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Expenses with user_id foreign key for multi-user support
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

# --- Login Window ---

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Budget Tracker - Login")
        self.geometry('500x380')
        self.resizable(False, False)

        tk.Label(self, text="Username").pack(pady=(20, 5))
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=(15, 5))
        tk.Button(self, text="Register", command=self.register).pack()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        conn = sqlite3.connect('budget.db')
        c = conn.cursor()
        c.execute('SELECT user_id FROM users WHERE username=? AND password=?', (username, password))
        result = c.fetchone()
        conn.close()

        if result:
            user_id = result[0]
            self.destroy()
            app = BudgetTrackerApp(user_id, username)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password to register.")
            return

        conn = sqlite3.connect('budget.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now login.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()


    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()


# --- Main Budget Tracker Application ---

class BudgetTrackerApp(tk.Tk):
    CATEGORIES = ["Food", "Rent", "Utilities", "Transport", "Entertainment", "Health", "Other"]

    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.title(f"Budget Tracker - User: {username}")
        self.geometry('800x550')

        # Configure grid for resizable table
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(5, weight=1)

        # Input form area
        labels = ["Date (YYYY-MM-DD)", "Category", "Amount", "Description"]
        self.entries = {}

        for i, text in enumerate(labels):
            tk.Label(self, text=text, font=('Arial', 10, 'bold')).grid(row=i, column=0, padx=10, pady=5, sticky='w')

        # Date Entry
        self.entries["Date (YYYY-MM-DD)"] = tk.Entry(self, font=('Arial', 10))
        self.entries["Date (YYYY-MM-DD)"].grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        # Category Dropdown
        self.category_var = tk.StringVar()
        self.category_var.set(self.CATEGORIES[0])
        category_dropdown = ttk.Combobox(self, textvariable=self.category_var, values=self.CATEGORIES, state="readonly", font=('Arial', 10))
        category_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Amount Entry
        self.entries["Amount"] = tk.Entry(self, font=('Arial', 10))
        self.entries["Amount"].grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # Description Entry
        self.entries["Description"] = tk.Entry(self, font=('Arial', 10))
        self.entries["Description"].grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        # TreeView Table
        columns = ('ID', 'Date', 'Category', 'Amount', 'Description')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')
        self.tree.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        # Buttons Frame
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Add Expense", width=15, command=self.add_expense).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="View All Expenses", width=15, command=self.view_expenses_in_gui).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Edit Selected", width=15, command=self.edit_selected_expense).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Delete Selected", width=15, command=self.delete_selected_expense).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="View Summary", width=15, command=self.view_summary).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Visualize Expenses", width=15, command=self.visualize_expenses).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Logout", width=15, command=self.logout).grid(row=1, column=3, padx=5, pady=5)

        self.view_expenses_in_gui()

    # --- Helper Methods ---

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def add_expense(self):
        date = self.entries["Date (YYYY-MM-DD)"].get().strip()
        category = self.category_var.get()
        amount_text = self.entries["Amount"].get().strip()
        description = self.entries["Description"].get().strip()

        if not date or not category or not amount_text:
            messagebox.showerror("Input Error", "Date, Category, and Amount fields cannot be empty.")
            return

        if not self.validate_date(date):
            messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a positive number.")
            return

        try:
            conn = sqlite3.connect('budget.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (user_id, date, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.user_id, date, category, amount, description))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return

        messagebox.showinfo("Success", "Expense added successfully!")
        self.clear_inputs()
        self.view_expenses_in_gui()

    def clear_inputs(self):
        self.entries["Date (YYYY-MM-DD)"].delete(0, tk.END)
        self.category_var.set(self.CATEGORIES[0])
        self.entries["Amount"].delete(0, tk.END)
        self.entries["Description"].delete(0, tk.END)

    def view_expenses_in_gui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            conn = sqlite3.connect('budget.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, date, category, amount, description FROM expenses WHERE user_id = ? ORDER BY date DESC', (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                self.tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred while fetching data: {e}")

    def get_selected_expense_id(self):
        selected = self.tree.selection()
        if not selected:
            return None
        return self.tree.item(selected[0])['values'][0]

    def delete_selected_expense(self):
        expense_id = self.get_selected_expense_id()
        if expense_id is None:
            messagebox.showwarning("Selection Error", "Please select an expense to delete.")
            return
        answer = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected expense?")
        if answer:
            try:
                conn = sqlite3.connect('budget.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM expenses WHERE id=? AND user_id=?', (expense_id, self.user_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Expense deleted successfully.")
                self.view_expenses_in_gui()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

    def edit_selected_expense(self):
        expense_id = self.get_selected_expense_id()
        if expense_id is None:
            messagebox.showwarning("Selection Error", "Please select an expense to edit.")
            return

        conn = sqlite3.connect('budget.db')
        cursor = conn.cursor()
        cursor.execute('SELECT date, category, amount, description FROM expenses WHERE id=? AND user_id=?', (expense_id, self.user_id))
        expense = cursor.fetchone()
        conn.close()

        if not expense:
            messagebox.showerror("Error", "Selected expense not found.")
            return

        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Expense")
        edit_win.geometry('350x250')
        edit_win.transient(self)
        edit_win.grab_set()

        tk.Label(edit_win, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        date_entry = tk.Entry(edit_win)
        date_entry.grid(row=0, column=1, padx=10, pady=5)
        date_entry.insert(0, expense[0])

        tk.Label(edit_win, text="Category:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(edit_win, textvariable=category_var, values=self.CATEGORIES, state='readonly')
        category_dropdown.grid(row=1, column=1, padx=10, pady=5)
        category_var.set(expense[1])

        tk.Label(edit_win, text="Amount:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        amount_entry = tk.Entry(edit_win)
        amount_entry.grid(row=2, column=1, padx=10, pady=5)
        amount_entry.insert(0, str(expense[2]))

        tk.Label(edit_win, text="Description:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        desc_entry = tk.Entry(edit_win)
        desc_entry.grid(row=3, column=1, padx=10, pady=5)
        desc_entry.insert(0, expense[3] if expense[3] else "")

        def save_changes():
            new_date = date_entry.get().strip()
            new_category = category_var.get()
            new_amount_text = amount_entry.get().strip()
            new_description = desc_entry.get().strip()

            if not new_date or not new_category or not new_amount_text:
                messagebox.showerror("Input Error", "Date, Category, and Amount fields cannot be empty.")
                return
            if not self.validate_date(new_date):
                messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
                return
            try:
                new_amount = float(new_amount_text)
                if new_amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Amount must be a positive number.")
                return

            try:
                conn = sqlite3.connect('budget.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE expenses
                    SET date = ?, category = ?, amount = ?, description = ?
                    WHERE id = ? AND user_id = ?
                ''', (new_date, new_category, new_amount, new_description, expense_id, self.user_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Expense updated successfully.")
                self.view_expenses_in_gui()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

        tk.Button(edit_win, text="Save", command=save_changes).grid(row=4, column=0, columnspan=2, pady=15)

    def view_summary(self):
        try:
            conn = sqlite3.connect('budget.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, SUM(amount) AS total_spent
                FROM expenses
                WHERE user_id=?
                GROUP BY category
            ''', (self.user_id,))
            summary_data = cursor.fetchall()
            conn.close()

            if not summary_data:
                messagebox.showinfo("Summary", "No expense data available to summarize.")
                return

            summary_win = tk.Toplevel(self)
            summary_win.title("Expense Summary by Category")
            summary_win.geometry('400x300')

            columns = ('Category', 'Total Spent (₹)')
            summary_tree = ttk.Treeview(summary_win, columns=columns, show='headings')
            for col in columns:
                summary_tree.heading(col, text=col)
                summary_tree.column(col, anchor='center')
            summary_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            for category, total in summary_data:
                summary_tree.insert('', tk.END, values=(category, f"₹{total:.2f}"))

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred while fetching summary: {e}")

    def visualize_expenses(self):
        try:
            conn = sqlite3.connect('budget.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, SUM(amount) 
                FROM expenses WHERE user_id=?
                GROUP BY category
            ''', (self.user_id,))
            data = cursor.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("Visualization", "No expense data to visualize.")
                return

            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]

            fig, ax = plt.subplots(figsize=(6, 4))
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
            ax.set_title('Expense Distribution by Category')

            vis_win = tk.Toplevel(self)
            vis_win.title("Expense Visualization")

            canvas = FigureCanvasTkAgg(fig, master=vis_win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Visualization Error", f"An error occurred: {e}")

    def logout(self):
        answer = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if answer:
            self.destroy()
            login = LoginWindow()
            login.mainloop()


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
