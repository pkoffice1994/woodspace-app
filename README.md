# WoodSpace App

WoodSpace is a Flask-based lead capture website with an integrated dashboard in the same application.

## Included Files

- `app.py`: Main website
- `dashboard.py`: Compatibility launcher that runs the same Flask app
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

```txt
http://127.0.0.1:5000/dashboard
```

## Deploy On Vercel

This repository is prepared for deploying the Flask website on Vercel.

### Environment Variables

Add these values in the Vercel project settings:

- `TWILIO_SID`
- `TWILIO_TOKEN`
- `TWILIO_WA_FROM`
- `OWNER_PHONE`

Use `.env.example` as the reference.

## Important Note

The app now stores leads in `woodspace.db`. This works well locally or on hosting with persistent disk storage. On Vercel, file storage is temporary, so online lead records are not guaranteed to remain after cold starts or redeploys. For permanent online lead storage, deploy this app on a platform with persistent storage or connect an external database.
