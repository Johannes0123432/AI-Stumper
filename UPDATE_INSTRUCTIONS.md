# How to Update the Adaptive Edition on Render

## New file
Replace your current `app.py` with the new Adaptive Edition.

## What is new
- **Procedural mode** now uses harder anti-memorization templates
  (groups of order p³ with exponent restriction, discriminant of period cubic, Hilbert tower degree, etc.)
- **Hard Adaptive mode**: asks a strong model to invent completely new traps on the fly
- Stricter filtering against the strongest available models
  (DeepSeek V4 Pro 0813 + current Gemini)
- Better randomization so pure recall fails more often

## Update steps on Render (GitHub method)

1. Open your GitHub repository
2. Click on `app.py`
3. Click the pencil icon (Edit)
4. Delete everything and paste the full content of the new `app.py`
5. Scroll down → Commit changes (message: "Adaptive Edition")
6. Go to Render dashboard → your service
7. It should auto-deploy. If not, click Manual Deploy → Deploy latest commit
8. Wait until status is Live

## After update
- Test “Procedural (fast, anti-mem)”
- Test “Hard Adaptive (LLM invents new traps)” – needs Google key
- Keep the filter turned on for best results
