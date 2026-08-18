# Planck CURVD Stumper Generator

Public free version of the app.

## Features
- Procedural generation of CURVD stumper problems (Math & Physics)
- Techniques to defeat pure recall (hidden dependencies, wrong-answer attractors, etc.)
- Optional LLM-assisted generation
- Multi-model filter (Gemini + DeepSeek)
- Endless non-repeating problems via hash memory
- One-click export of Planck-ready `.txt`

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Render (recommended)

1. Create a free account at https://render.com
2. Create a new **Web Service**
3. Connect your GitHub repository (or upload the files)
4. Settings:
   - **Name**: planck-stumper (or any name)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Click **Create Web Service**
6. Wait 1–3 minutes. You will get a public URL like:
   `https://planck-stumper.onrender.com`

### Important Render notes
- Free tier spins down after 15 min of inactivity (first request after sleep takes ~30–50 s)
- For always-on you need a paid plan ($7/month)

## Deploy on Railway

1. Go to https://railway.app and login with GitHub
2. New Project → Deploy from GitHub repo
3. Add the files (`app.py` + `requirements.txt`)
4. Railway usually auto-detects Streamlit
5. If needed, set Start Command:
   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
6. Generate a public domain in the Settings tab

## Environment variables (optional)

You can later add:
- `GOOGLE_API_KEY`
- `OPENROUTER_API_KEY`

in the platform’s Environment / Variables section so users don’t have to paste keys every time (or so you can provide shared keys).

## Next step (payments)

After the free public version is live, we will add:
- Login system
- Admin (you) = free forever
- Simple license-key system **or** Stripe subscriptions

---

Created for Project Planck stumper generation.

## Feedback system (new)

The app now includes an in-app rating system in the sidebar:

- Star rating (1–5)
- Optional comment
- Optional email
- All feedback collected during the session can be downloaded as CSV by the app owner

After a user generates a few problems they are gently prompted to leave a rating.
