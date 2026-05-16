import os
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request

try:
    from twilio.rest import Client

    TWILIO_ENABLED = True
except ImportError:
    TWILIO_ENABLED = False

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_PATH = BASE_DIR / "woodspace.db"
EPHEMERAL_DB_PATH = Path("/tmp/woodspace.db")

TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_WA_FROM = os.getenv("TWILIO_WA_FROM", "whatsapp:+14155238886")
OWNER_PHONE = os.getenv("OWNER_PHONE", "")


def get_db_path():
    # Vercel storage is ephemeral. This keeps the app working, but records will not persist there.
    if os.getenv("VERCEL"):
        return EPHEMERAL_DB_PATH
    return LOCAL_DB_PATH


def get_connection():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT,
                budget TEXT,
                message TEXT
            )
            """
        )


def insert_lead(name, phone, service, budget, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO leads (created_at, name, phone, service, budget, message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (timestamp, name, phone, service, budget, message),
        )


def fetch_leads():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, name, phone, service, budget, message
            FROM leads
            ORDER BY datetime(created_at) DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def build_dashboard_context():
    leads = fetch_leads()
    today = datetime.now().date()
    week_cutoff = datetime.now() - timedelta(days=7)

    parsed_leads = []
    for lead in leads:
        created_at = None
        try:
            created_at = datetime.strptime(lead["created_at"], "%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError):
            pass

        enriched = dict(lead)
        enriched["created_dt"] = created_at
        parsed_leads.append(enriched)

    total_leads = len(parsed_leads)
    today_leads = [lead for lead in parsed_leads if lead["created_dt"] and lead["created_dt"].date() == today]
    week_leads = [lead for lead in parsed_leads if lead["created_dt"] and lead["created_dt"] >= week_cutoff]

    service_counter = Counter(
        lead["service"].strip() if lead["service"] else "Unspecified"
        for lead in parsed_leads
    )
    top_service = service_counter.most_common(1)[0][0] if service_counter else "Not available"

    by_date = Counter(
        lead["created_dt"].strftime("%d %b") for lead in parsed_leads if lead["created_dt"]
    )
    by_hour = Counter(
        lead["created_dt"].strftime("%H:00") for lead in parsed_leads if lead["created_dt"]
    )
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    by_weekday = Counter(
        lead["created_dt"].strftime("%A") for lead in parsed_leads if lead["created_dt"]
    )

    return {
        "leads": parsed_leads,
        "total_leads": total_leads,
        "today_leads": len(today_leads),
        "week_leads": len(week_leads),
        "top_service": top_service,
        "latest_lead_time": parsed_leads[0]["created_at"] if parsed_leads else "No leads yet",
        "service_labels": list(service_counter.keys()),
        "service_values": list(service_counter.values()),
        "date_labels": list(reversed(list(by_date.keys()))),
        "date_values": list(reversed(list(by_date.values()))),
        "hour_labels": [label for label, _ in sorted(by_hour.items())],
        "hour_values": [value for _, value in sorted(by_hour.items())],
        "weekday_labels": weekday_order,
        "weekday_values": [by_weekday.get(day, 0) for day in weekday_order],
        "storage_mode": "ephemeral" if os.getenv("VERCEL") else "persistent",
    }


def send_whatsapp(name, phone, service, budget, message):
    if not TWILIO_ENABLED or not TWILIO_SID or not TWILIO_TOKEN or not OWNER_PHONE:
        print("[WhatsApp] Not configured - skipping")
        return

    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        body = (
            "New WoodSpace Lead!\n\n"
            f"Name: {name}\n"
            f"Phone: {phone}\n"
            f"Service: {service or 'Not specified'}\n"
            f"Budget: {budget or 'Not mentioned'}\n"
            f"Message: {message or '-'}\n\n"
            f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        )
        client.messages.create(body=body, from_=TWILIO_WA_FROM, to=f"whatsapp:{OWNER_PHONE}")
        print("[WhatsApp] Sent")
    except Exception as error:
        print(f"[WhatsApp Error] {error}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", **build_dashboard_context())


@app.route("/submit", methods=["POST"])
def submit():
    try:
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        service = request.form.get("service", "").strip()
        budget = request.form.get("budget", "").strip()
        message = request.form.get("message", "").strip()

        insert_lead(name, phone, service, budget, message)
        send_whatsapp(name, phone, service, budget, message)
        return render_template("success.html", name=name)
    except Exception as error:
        return f"<h2>Error: {error}</h2><a href='/'>Back</a>"


init_db()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
