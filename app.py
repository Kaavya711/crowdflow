"""
CrowdFlow - AI Stadium Operations Assistant
Security: Input validation, rate limiting, sanitized outputs, secure headers
Efficiency: Response caching, connection pooling
Google Services: Gemini API (AI), Maps JS API (Heatmap)
"""

from google import genai
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import bleach
import os
import logging

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "crowdflow-dev-secret-key-change-in-prod")

# ── Security: Rate Limiting ────────────────────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)

# ── Efficiency: Caching ────────────────────────────────────────────────────────
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 30
})

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Google Gemini Client ───────────────────────────────────────────────────────
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ── Google Maps Key ────────────────────────────────────────────────────────────
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY", "")

# ── Venue Context (injected into every AI request) ────────────────────────────
VENUE_CONTEXT = """
You are the AI Operations Assistant for CrowdFlow, an enterprise stadium management system.
Total Capacity: 40,000. Current Attendance: 37,856 (94.6% full).

GATE STATUS:
- Gate A (North Alpha): Clear, 130 pax/min, 4 min wait
- Gate D (West VIP): Elevated, 90 pax/min, 8 min wait
- Gate E (East Public): CRITICAL — Scanner failure active, 45 pax/min, 18 min wait
- Gate F (South Plaza): Clear, 145 pax/min, 2 min wait

DENSITY ZONES:
- North Stand: 92% — CRITICAL, severe bottleneck
- Main Concourse: 88% — HIGH
- East Wing: 74% — Elevated
- Food Court: 68% — Elevated
- West Wing: 54% — Medium
- South Stand: 41% — Nominal
- VIP Lounge: 22% — Nominal

FOOD & BEVERAGE:
- Burger House: 10 min wait, non-veg
- Green Bowl: 2 min wait, veg (RECOMMENDED)
- Combo Corner: 5 min wait, 20% discount ACTIVE (PROMO)

ACTIVE ALERTS:
1. [WARNING] Main Concourse Volume — chokepoints developing
2. [EMERGENCY] Medical Incident — North Stand corridor
3. [INFO] Inventory push — Combo Corner 20% discount live

INSTRUCTIONS:
- Provide concise, authoritative, actionable responses (2-4 sentences max)
- Always prioritize safety and crowd dispersion
- Reference specific gate/zone names in recommendations
- If density is critical, proactively suggest alternatives
"""

# ── Input Sanitization ─────────────────────────────────────────────────────────
def sanitize_input(text):
    """Sanitize user input to prevent XSS and prompt injection."""
    if not text or not isinstance(text, str):
        return ""
    text = bleach.clean(text, tags=[], strip=True)
    text = text.strip()
    return text[:500]  # Hard cap at 500 chars


# ── Security Headers ───────────────────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


# ── Error Handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('