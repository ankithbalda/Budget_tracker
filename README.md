# 🧾 Budget Tracker with Tkinter & SQLite

A **desktop application** built with **Python, Tkinter, and SQLite** to help you track daily expenses, visualize spending patterns, and manage your budget efficiently.  
It supports **multi-user login**, expense entry, editing, deletion, summary viewing, and graphical visualization.

---

## 🚀 Features

- **🔐 User Authentication** — Register/Login with username & password (stored in a local SQLite database).
- **💰 Expense Management**
  - Add expenses with date, category, amount, and description.
  - Edit or delete existing expenses.
- **📊 Summaries & Reports**
  - View total expenses grouped by category.
  - Graphical pie chart visualization of spending distribution using Matplotlib.
- **📅 Date Validation** — Ensures the date is entered in `YYYY-MM-DD` format.
- **📂 Local Database** — Uses SQLite (`budget.db`) for storing expenses per user.

---

## 📸 Screenshots

<img width="495" height="414" alt="Screenshot 2025-08-14 213316" src="https://github.com/user-attachments/assets/4de453ea-fe40-4d42-bb5e-e55c03cf481e" />
<img width="797" height="584" alt="Screenshot 2025-08-14 213335" src="https://github.com/user-attachments/assets/b8d9812a-8f59-44ac-9985-8190466da714" />

---

## 🛠 Technology Stack

- **Python 3**
- **Tkinter** — GUI framework
- **SQLite3** — Local database storage
- **Matplotlib** — Data visualization
- **ttk** — Themed Tkinter widgets

---

## 📦 Installation & Setup

1. **Clone the repository**

   git clone https://github.com/ankithbalda/Budget_tracker.git
   cd Budget_tracker


2. **Install dependencies**
This app uses built-in Python modules except for `matplotlib`. Install it via:
pip install matplotlib


3. **Run the application**
python test.py


4. The app will automatically create `budget.db` in the directory if it doesn’t exist.

---

## 📖 Usage

1. **Login / Register**
- If new, register with a username and password.
- If existing, log in with your credentials.

2. **Add Expenses**
- Enter the date (YYYY-MM-DD), category, amount, and optional description.
- Click **"Add Expense"** to save.

3. **Manage Expenses**
- **View All Expenses** — Displays all records.
- **Edit Selected** — Modify any expense entry.
- **Delete Selected** — Remove unwanted expenses.

4. **View Summary**
- Displays total expenses grouped by category.

5. **Visualize Expenses**
- Shows a pie chart of expenses by category.

6. **Logout**
- Ends your session and returns to the login screen.

---

## 🔑 Default Categories

- Food
- Rent
- Utilities
- Transport
- Entertainment
- Health
- Other

---

## 📂 Project Structure

📁 budget-tracker/

├── test.py # Main Tkinter + SQLite application

├── budget.db # SQLite database (auto-generated)

└── README.md # Project documentation


---

## 👨‍💻 Author

**Name:** Ankith Balda

**Email:** ankithbalda.wk@gmail.com

**LinkedIn:** https://www.linkedin.com/in/ankith-balda-812177278/

**GitHub:** https://github.com/ankithbalda

---

## ⭐ Contributing

Pull requests are welcome! If you’d like to contribute:
1. Fork the repo.
2. Create a feature branch.
3. Commit changes.
4. Submit a pull request.

---
