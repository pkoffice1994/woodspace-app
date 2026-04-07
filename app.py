from flask import Flask, render_template, request
import csv
import os
from datetime import datetime

try:
    from twilio.rest import Client
    TWILIO_ENABLED = True
except ImportError:
    TWILIO_ENABLED = False

app = Flask(__name__)

TWILIO_SID     = ""
TWILIO_TOKEN   = ""
TWILIO_WA_FROM = "whatsapp:+14155238886"
OWNER_PHONE    = "+91XXXXXXXXXX"

def send_whatsapp(name, phone, service, budget, message):
    if not TWILIO_ENABLED or not TWILIO_SID:
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
    file_exists = os.path.isfile('leads.csv')
    with open('leads.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp','Name','Phone','Service','Budget','Message'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, phone, service, budget, message])

@app.route('/')
def home():
    return render_template('index.html')

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
    app.run(debug=True)
