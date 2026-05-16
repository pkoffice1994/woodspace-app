import csv
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, render_template, request

try:
    from twilio.rest import Client
    TWILIO_ENABLED = True
except ImportError:
    TWILIO_ENABLED = False

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = BASE_DIR / "leads.csv"
EPHEMERAL_CSV_PATH = Path("/tmp/leads.csv")

TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_WA_FROM = os.getenv("TWILIO_WA_FROM", "whatsapp:+14155238886")
OWNER_PHONE = os.getenv("OWNER_PHONE", "")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "").strip()


def get_storage_path():
    # Vercel writes are ephemeral, so use /tmp instead of the repo directory.
    if os.getenv("VERCEL"):
        return EPHEMERAL_CSV_PATH
    return DEFAULT_CSV_PATH

def send_whatsapp(name, phone, service, budget, message):
    if not TWILIO_ENABLED or not TWILIO_SID or not TWILIO_TOKEN or not OWNER_PHONE:
        print("[WhatsApp] Not configured — skipping")
        return
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        body = (
            f"🪵 *New WoodSpace Lead!*\n\n"
            f"👤 *Name:* {name}\n"
            f"📞 *Phone:* {phone}\n"
            f"🛠️ *Service:* {service or 'Not specified'}\n"
            f"💰 *Budget:* {budget or 'Not mentioned'}\n"
            f"📝 *Message:* {message or '-'}\n\n"
            f"⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        )
        client.messages.create(body=body, from_=TWILIO_WA_FROM, to=f"whatsapp:{OWNER_PHONE}")
        print("[WhatsApp] Sent!")
    except Exception as e:
        print(f"[WhatsApp Error] {e}")

def save_lead(name, phone, service, budget, message):
    csv_path = get_storage_path()
    file_exists = csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists or csv_path.stat().st_size == 0:
            writer.writerow(['Timestamp','Name','Phone','Service','Budget','Message'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, phone, service, budget, message])

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard_redirect():
    if DASHBOARD_URL:
        return redirect(DASHBOARD_URL)
    return (
        "<h2>Dashboard URL is not configured yet.</h2>"
        "<p>Add <code>DASHBOARD_URL</code> in your deployment settings, then reopen this page.</p>"
        "<a href='/'>Back to Home</a>"
    )

@app.route('/submit', methods=['POST'])
def submit():
    try:
        name    = request.form.get('name', '').strip()
        phone   = request.form.get('phone', '').strip()
        service = request.form.get('service', '').strip()
        budget  = request.form.get('budget', '').strip()
        message = request.form.get('message', '').strip()
        print(f"[New Lead] {name} | {phone} | {service}")
        save_lead(name, phone, service, budget, message)
        send_whatsapp(name, phone, service, budget, message)
        return render_template('success.html', name=name)
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2><a href='/'>Back</a>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
