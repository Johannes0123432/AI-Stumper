# How to Update Your App on Render

## Files you need to replace
- `app.py`  (updated with strongest DeepSeek model + Gemini fallbacks)

## Method 1 – If you deployed from GitHub (Recommended)

1. Go to your GitHub repository that Render is connected to.
2. Replace the old `app.py` with the new one (drag & drop or upload).
3. Commit the change (GitHub will show “Commit changes”).
4. Go to your Render dashboard → select your Web Service.
5. Render will automatically detect the new commit and start a new deploy.
6. Wait 1–3 minutes until status shows **Live**.

That’s it. The new version is online.

## Method 2 – Manual redeploy (if needed)

1. Open your service on Render.
2. Go to the **Manual Deploy** section (or the three dots menu).
3. Click **Clear build cache & deploy** or **Deploy latest commit**.
4. Wait for the deploy to finish.

## What changed in this update

- DeepSeek now uses the strongest model: `deepseek/deepseek-v4-pro-0813`
- Automatic fallbacks if that model is unavailable
- Gemini still uses current models (`gemini-3.6-flash` and fallbacks)
- Better error handling

## After updating

Test both modes:
- Procedural generation
- LLM-assisted generation
- Multi-model filter (Gemini + DeepSeek)

You should no longer see the old `gemini-2.5-flash` 404 errors.
