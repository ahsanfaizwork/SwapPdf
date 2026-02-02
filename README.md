Mergify
=======

A small Flask-based PDF conversion web app with these features:
- Merge PDFs
- Split a PDF into single-page PDFs (zipped)
- Convert multiple images into a single PDF
- Extract PDF pages to PNG images (zipped)
- Basic PDF re-save "compress" fallback (better compression via `pikepdf`/Ghostscript)

Quick start (local)
-------------------

1. Create a venv and activate it:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install deps:

```pwsh
pip install -r requirements.txt
```

3. Run:

```pwsh
python app.py
```

Open http://localhost:5000

Deploy
------

- Render: create a new Web Service, connect repo, set `start` command to `python app.py`, and expose port 5000.
- Heroku / Fly / any container platform: build the Dockerfile and deploy.

Monetization ideas
------------------
- Add Stripe Checkout or subscriptions for premium features (batch limits, priority processing, watermark removal).
- Offer a hosted SaaS with a freemium tier: free conversions with limits + paid plans.
- Integrate analytics and marketing landing pages.

Notes & Next steps
------------------
- For much better compression use `pikepdf` or run Ghostscript on the server; these may require native libraries.
- Add user accounts and Stripe integration to collect payment and lock premium endpoints.
- Add file size limits, virus scanning, and rate limits before public deployment.
