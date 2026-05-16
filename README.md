# WoodSpace App

WoodSpace is a Flask-based lead capture website with a separate Streamlit dashboard for internal reporting.

## Included Files

- `app.py`: Main website
- `dashboard.py`: Internal dashboard
- `templates/`: HTML templates
- `requirements.txt`: Python dependencies
- `vercel.json`: Vercel deployment config for the Flask app

## Local Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Website:

```txt
http://127.0.0.1:5000
```

Dashboard:

```bash
streamlit run dashboard.py
```

## Deploy On Vercel

This repository is prepared for deploying the Flask website on Vercel.

### Environment Variables

Add these values in the Vercel project settings:

- `TWILIO_SID`
- `TWILIO_TOKEN`
- `TWILIO_WA_FROM`
- `OWNER_PHONE`
- `DASHBOARD_URL`

Use `.env.example` as the reference.

## Important Note

`leads.csv` is suitable for local development only. On Vercel, file storage is temporary, so lead records are not permanently stored there. For production use, connect a database or Google Sheet.
