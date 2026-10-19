import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ================= DATABASE =================

con = sqlite3.connect("support.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    complaint TEXT,
    category TEXT,
    department TEXT,
    priority TEXT,
    status TEXT,
    date TEXT
)
""")

con.commit()


# ================= KEYWORDS =================

keywords = {
    "Technical": [
        "internet",
        "wifi",
        "network",
        "error",
        "bug",
        "software",
        "computer",
        "not working",
    ],
    "Billing": [
        "payment",
        "bill",
        "billing",
        "charged",
        "refund",
        "money",
        "transaction",
        "price",
    ],
    "Account": ["login", "password", "account", "username", "sign in", "register"],
    "Delivery": ["delivery", "order", "shipping", "package", "parcel", "not arrived"],
}


# ================= DEPARTMENTS =================

departments = {
    "Technical": "Technical Support",
    "Billing": "Billing Department",
    "Account": "Account Support",
    "Delivery": "Delivery Team",
    "Other": "General Support",
}


# ================= CLASSIFICATION =================


def classify_complaint(complaint):

    text = complaint.lower()

    for category, words in keywords.items():
        for word in words:
            if word in text:
                return category

    return "Other"


# ================= PRIORITY =================


def get_priority(complaint):

    text = complaint.lower()

    urgent = ["urgent", "emergency", "critical", "immediately", "blocked"]

    for word in urgent:
        if word in text:
            return "High"

    return "Normal"


# ================= CREATE TICKET =================


def create_ticket():

    customer = name_entry.get().strip()
    complaint = complaint_entry.get().strip()

    if customer == "" or complaint == "":
        messagebox.showwarning("Warning", "Enter customer name and complaint")
        return

    category = classify_complaint(complaint)

    department = departments[category]

    priority = get_priority(complaint)

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
        """
    INSERT INTO tickets
    (customer, complaint, category, department,
     priority, status, date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (customer, complaint, category, department, priority, "Open", date),
    )

    con.commit()

    ticket_id = cur.lastrowid

    messagebox.showinfo(
        "Ticket Created",
        f"Ticket ID: T{ticket_id:03}\n"
        f"Category: {category}\n"
        f"Department: {department}\n"
        f"Priority: {priority}\n"
        f"Status: Open",
    )

    name_entry.delete(0, tk.END)
    complaint_entry.delete(0, tk.END)

    show_tickets()
    update_dashboard()


# ================= SHOW TICKETS =================


def show_tickets():

    for item in table.get_children():
        table.delete(item)

    cur.execute("SELECT * FROM tickets")

    for row in cur.fetchall():
        table.insert("", tk.END, values=row)


# ================= SEARCH =================


def search_tickets():

    keyword = search_entry.get().strip()

    for item in table.get_children():
        table.delete(item)

    cur.execute(
        """
    SELECT * FROM tickets
    WHERE customer LIKE ?
    OR complaint LIKE ?
    OR category LIKE ?
    """,
        ("%" + keyword + "%", "%" + keyword + "%", "%" + keyword + "%"),
    )

    for row in cur.fetchall():
        table.insert("", tk.END, values=row)


# ================= REVIEW CUSTOMER =================


def review_customer():

    selected = table.selection()

    if not selected:
        messagebox.showwarning("Warning", "First select a customer from the table")

        return

    item = table.item(selected[0])

    values = item["values"]

    review = tk.Toplevel(root)

    review.title("Customer Details Review")

    review.geometry("500x500")

    tk.Label(review, text="CUSTOMER DETAILS REVIEW", font=("Arial", 17, "bold")).pack(
        pady=15
    )

    details = (
        f"Ticket ID   : T{values[0]:03}\n\n"
        f"Customer    : {values[1]}\n\n"
        f"Complaint   : {values[2]}\n\n"
        f"Category    : {values[3]}\n\n"
        f"Department  : {values[4]}\n\n"
        f"Priority    : {values[5]}\n\n"
        f"Status      : {values[6]}\n\n"
        f"Date        : {values[7]}"
    )

    tk.Label(review, text=details, font=("Arial", 11), justify="left", anchor="w").pack(
        padx=30, pady=10
    )

    tk.Button(review, text="CLOSE", command=review.destroy, width=15).pack(pady=15)


# ================= UPDATE STATUS =================


def update_status():

    selected = table.selection()

    if not selected:
        messagebox.showwarning("Warning", "First select a ticket from the table")

        return

    item = table.item(selected[0])

    ticket_id = item["values"][0]

    new_status = status_var.get()

    cur.execute("UPDATE tickets SET status=? WHERE id=?", (new_status, ticket_id))

    con.commit()

    messagebox.showinfo("Success", f"Ticket T{ticket_id:03} updated to {new_status}")

    show_tickets()

    update_dashboard()


# ================= DASHBOARD =================


def update_dashboard():

    cur.execute("SELECT COUNT(*) FROM tickets")

    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'")

    opened = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tickets WHERE status='In Progress'")

    progress = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tickets WHERE status='Resolved'")

    resolved = cur.fetchone()[0]

    dashboard.config(
        text=f"Total: {total}   |   "
        f"Open: {opened}   |   "
        f"In Progress: {progress}   |   "
        f"Resolved: {resolved}"
    )


# ================= MAIN WINDOW =================

root = tk.Tk()

root.title("Customer Support Ticket Router")

root.geometry("1150x750")


# ================= TITLE =================

tk.Label(root, text="CUSTOMER SUPPORT TICKET ROUTER", font=("Arial", 20, "bold")).pack(
    pady=10
)

tk.Label(
    root, text="Automatic Customer Complaint Classification", font=("Arial", 11)
).pack()


# ================= INPUT =================

input_frame = tk.Frame(root)

input_frame.pack(pady=15)


tk.Label(input_frame, text="Customer Name:").grid(row=0, column=0, padx=10, pady=8)


name_entry = tk.Entry(input_frame, width=40)

name_entry.grid(row=0, column=1)


tk.Label(input_frame, text="Complaint:").grid(row=1, column=0, padx=10, pady=8)


complaint_entry = tk.Entry(input_frame, width=40)

complaint_entry.grid(row=1, column=1)


tk.Button(input_frame, text="CREATE TICKET", command=create_ticket, width=20).grid(
    row=2, column=0, columnspan=2, pady=10
)


# ================= RESULT =================

result = tk.Label(
    root, text="Enter a complaint and create a ticket", font=("Arial", 10)
)

result.pack()


# ================= DASHBOARD =================

dashboard = tk.Label(
    root,
    text="Total: 0 | Open: 0 | In Progress: 0 | Resolved: 0",
    font=("Arial", 11, "bold"),
)

dashboard.pack(pady=10)


# ================= SEARCH =================

search_frame = tk.Frame(root)

search_frame.pack(pady=5)


tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)


search_entry = tk.Entry(search_frame, width=30)

search_entry.pack(side=tk.LEFT, padx=5)


tk.Button(search_frame, text="SEARCH", command=search_tickets).pack(
    side=tk.LEFT, padx=5
)


tk.Button(search_frame, text="SHOW ALL", command=show_tickets).pack(side=tk.LEFT)


# ================= TABLE =================

columns = (
    "ID",
    "Customer",
    "Complaint",
    "Category",
    "Department",
    "Priority",
    "Status",
    "Date",
)


table = ttk.Treeview(root, columns=columns, show="headings", height=10)


for column in columns:
    table.heading(column, text=column)

    table.column(column, width=130)


table.pack(padx=10, pady=10, fill="both", expand=True)


# ================= REVIEW BUTTON =================

tk.Button(root, text="REVIEW CUSTOMER DETAILS", command=review_customer, width=25).pack(
    pady=5
)


# ================= UPDATE STATUS =================

update_frame = tk.Frame(root)

update_frame.pack(pady=15)


tk.Label(update_frame, text="UPDATE SELECTED TICKET:", font=("Arial", 11, "bold")).pack(
    side=tk.LEFT, padx=10
)


status_var = tk.StringVar()

status_var.set("Open")


status_menu = ttk.Combobox(
    update_frame,
    textvariable=status_var,
    values=["Open", "In Progress", "Resolved"],
    state="readonly",
    width=18,
)

status_menu.pack(side=tk.LEFT, padx=10)


tk.Button(update_frame, text="UPDATE STATUS", command=update_status, width=18).pack(
    side=tk.LEFT, padx=10
)


# ================= START =================

show_tickets()

update_dashboard()

root.mainloop()
