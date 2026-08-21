# Wrapper Website for Planck Stumper Generator

This is a lightweight static site that:
- Is indexable by Google
- Embeds (or links to) your Render-hosted Streamlit app
- Can be published on a grok.me subdomain or any custom domain

## Quick start

1. Open `index.html`
2. Replace **every** occurrence of:
   `https://YOUR-RENDER-APP.onrender.com`
   with your real Render URL
3. Replace `https://YOUR-DOMAIN.com/` with your final domain (optional but recommended for SEO)

## Deploy options

### A. Grok / xAI Build Mode (if available)
- Upload the `wrapper_site` folder or the single `index.html`
- Publish to a `*.grok.me` subdomain or connect a custom domain

### B. Cloudflare Pages / Netlify / Vercel (free)
1. Create a new project
2. Upload the `wrapper_site` folder (or just `index.html`)
3. Add your custom domain in the platform settings

### C. GitHub Pages
1. Create a new public repo
2. Upload `index.html`
3. Enable GitHub Pages in Settings → Pages

## SEO tips
- Keep the title and meta description accurate
- Once live, submit the URL in Google Search Console
- Add a simple `sitemap.xml` pointing to the homepage if you expand later
