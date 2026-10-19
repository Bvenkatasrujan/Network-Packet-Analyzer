from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "support.db"


# ================= DATABASE =================


def get_db():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con


def create_database():

    con = get_db()

    con.execute("""
    CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT NOT NULL,
        complaint TEXT NOT NULL,
        category TEXT,
        department TEXT,
        priority TEXT,
        status TEXT,
        date TEXT
    )
    """)

    con.commit()
    con.close()


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

    urgent_words = ["urgent", "emergency", "critical", "immediately", "blocked"]

    for word in urgent_words:
        if word in text:
            return "High"

    return "Normal"


# ================= HOME =================


@app.route("/")
def home():

    return render_template("index.html")


# ================= CREATE TICKET =================


@app.route("/api/tickets", methods=["POST"])
def create_ticket():

    data = request.get_json()

    customer = data.get("customer", "").strip()
    complaint = data.get("complaint", "").strip()

    if customer == "" or complaint == "":
        return jsonify({"error": "Customer name and complaint are required"}), 400

    category = classify_complaint(complaint)

    department = departments[category]

    priority = get_priority(complaint)

    status = "Open"

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    con = get_db()

    cursor = con.execute(
        """
    INSERT INTO tickets
    (customer, complaint, category,
     department, priority, status, date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (customer, complaint, category, department, priority, status, date),
    )

    con.commit()

    ticket_id = cursor.lastrowid

    con.close()

    return jsonify(
        {
            "message": "Ticket created successfully",
            "ticket": {
                "id": ticket_id,
                "ticket_id": f"T{ticket_id:03}",
                "customer": customer,
                "complaint": complaint,
                "category": category,
                "department": department,
                "priority": priority,
                "status": status,
                "date": date,
            },
        }
    )


# ================= GET ALL TICKETS =================


@app.route("/api/tickets", methods=["GET"])
def get_tickets():

    con = get_db()

    tickets = con.execute("""
    SELECT * FROM tickets
    ORDER BY id DESC
    """).fetchall()

    con.close()

    result = []

    for ticket in tickets:
        result.append(dict(ticket))

    return jsonify(result)


# ================= GET ONE TICKET =================


@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):

    con = get_db()

    ticket = con.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()

    con.close()

    if ticket is None:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify(dict(ticket))


# ================= UPDATE STATUS =================


@app.route("/api/tickets/<int:ticket_id>/status", methods=["PUT"])
def update_status(ticket_id):

    data = request.get_json()

    status = data.get("status")

    allowed_status = ["Open", "In Progress", "Resolved"]

    if status not in allowed_status:
        return jsonify({"error": "Invalid status"}), 400

    con = get_db()

    ticket = con.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()

    if ticket is None:
        con.close()

        return jsonify({"error": "Ticket not found"}), 404

    con.execute(
        """
    UPDATE tickets
    SET status=?
    WHERE id=?
    """,
        (status, ticket_id),
    )

    con.commit()

    con.close()

    return jsonify(
        {
            "message": "Status updated successfully",
            "ticket_id": f"T{ticket_id:03}",
            "status": status,
        }
    )


# ================= SEARCH =================


@app.route("/api/search", methods=["GET"])
def search_tickets():

    keyword = request.args.get("keyword", "").strip()

    con = get_db()

    tickets = con.execute(
        """
    SELECT * FROM tickets
    WHERE customer LIKE ?
       OR complaint LIKE ?
       OR category LIKE ?
       OR department LIKE ?
    ORDER BY id DESC
    """,
        (
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%",
        ),
    ).fetchall()

    con.close()

    result = []

    for ticket in tickets:
        result.append(dict(ticket))

    return jsonify(result)


# ================= DASHBOARD =================


@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    con = get_db()

    total = con.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]

    opened = con.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'").fetchone()[
        0
    ]

    progress = con.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='In Progress'"
    ).fetchone()[0]

    resolved = con.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Resolved'"
    ).fetchone()[0]

    con.close()

    return jsonify(
        {"total": total, "open": opened, "in_progress": progress, "resolved": resolved}
    )


# ================= START SERVER =================

if __name__ == "__main__":
    create_database()

    print("======================================")
    print(" CUSTOMER SUPPORT TICKET ROUTER")
    print(" Backend Server Started")
    print("======================================")
    print("Open: http://127.0.0.1:5000")

    app.run(debug=True)
