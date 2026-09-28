# Planck Stumper – Wrapper / Landing Page (Option 3)

This static site is designed to be indexed by Google. It embeds and links to your Render Streamlit app.

## Files in this folder
- `index.html` – main landing page
- `google6e443770e8a4b5dd.html` – Google Search Console verification file
- `robots.txt`
- `sitemap.xml`

## Step-by-step: Deploy + Verify with Google (Option 3)

### 1. Choose a free static host (pick one)

**A. Cloudflare Pages (recommended)**
1. Go to https://pages.cloudflare.com
2. Sign up / log in
3. Create a project → Upload assets
4. Drag the entire `website` (or `wrapper_site`) folder
5. Deploy
6. You will get a free URL like `https://something.pages.dev`
7. (Optional) Add a custom domain later

**B. Netlify**
1. Go to https://app.netlify.com
2. Drag & drop the folder
3. Get a `*.netlify.app` URL

**C. GitHub Pages**
1. Create a new public repo (or use a `/docs` or `/website` folder in your existing repo)
2. Upload these files
3. Settings → Pages → Deploy from branch

**D. Render Static Site**
1. New → Static Site
2. Connect the repo or upload
3. Publish directory = the folder containing index.html

### 2. After the site is live

1. Open your new URL + the verification file, for example:
   ```
   https://your-new-site.pages.dev/google6e443770e8a4b5dd.html
   ```
2. You must see exactly this text on the page:
   ```
   google-site-verification: google6e443770e8a4b5dd.html
   ```

### 3. Verify in Google Search Console

1. Go to https://search.google.com/search-console
2. Add property → URL prefix → enter your new static site URL
3. Choose **HTML file** verification method
4. The filename should already match (`google6e443770e8a4b5dd.html`)
5. Click **Verify**

### 4. Request indexing

1. In Search Console use the URL Inspection tool
2. Paste your homepage URL
3. Click **Request Indexing**

### 5. Update sitemap & robots (important)

After you know your final domain, edit these two files and replace `YOUR-WRAPPER-DOMAIN`:

- `robots.txt`
- `sitemap.xml`

Then re-upload / re-deploy.

### 6. Link structure

The landing page already points to:
https://ai-stumper.onrender.com/

Google will index the nice static page, and users (and Googlebot) can reach the Streamlit app from there.

---

That is the complete Option 3 flow.
