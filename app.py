import os, urllib.parse
import logging
import requests
from flask import Flask, request, redirect
from nltk.sentiment import SentimentIntensityAnalyzer
# one-time download
import nltk, ssl
try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context
nltk.download('vader_lexicon', quiet=True)


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
sia = SentimentIntensityAnalyzer()

HEALTHPARTNERS_GOOGLE_REVIEW_URL = os.environ["HEALTHPARTNERS_GOOGLE_REVIEW_URL"]
STANHOPE_GOOGLE_REVIEW_URL = os.environ["STANHOPE_GOOGLE_REVIEW_URL"]
THANK_YOU_URL = os.environ.get("THANK_YOU_URL", "/static/thanks.html")
GOOGLE_REVIEW_REDIRECT_PAGE = "/static/google_review.html"


# Telegram configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_message(message):
    """Send a message to Telegram. Non-blocking, catches errors."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return  # Silently skip if not configured

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"  # Allows basic formatting
        }
        # Use timeout to keep latency low
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

@app.route("/review")
def review():
    surgery  = request.args.get("surgery",  "unknown")
    feedback = request.args.get("feedback", "")


    if not feedback:
        return redirect(THANK_YOU_URL)

    score = sia.polarity_scores(feedback)["compound"]

    google_review_url = None
    if score >= 0.70:
        if surgery == "Health-Partners-at-Violet-Melchett":
            google_review_url = HEALTHPARTNERS_GOOGLE_REVIEW_URL
        elif surgery == "Stanhope-Mews-Surgery":
            google_review_url = STANHOPE_GOOGLE_REVIEW_URL

    if google_review_url:
        # Before redirecting to the review page, we show an intermediate page
        dest = f"{GOOGLE_REVIEW_REDIRECT_PAGE}?dest={urllib.parse.quote(google_review_url)}"
    else:
        dest = THANK_YOU_URL


    # Log to application logs
    #
    # N.B. We log the ultimate destination, not the intermediate one
    log_dest = google_review_url or dest
    logging.info(f"Freetext: '{feedback}', Surgery: '{surgery}', Sentiment Score: {score}, Output: '{log_dest}'")

    # Log to Telegram
    action = "→ 🟢 Google Review" if google_review_url else "→ 🟠 Thank You"
    telegram_msg = f"""
<b>💾 New Feedback</b>
<b>Surgery:</b> {surgery}
<b>Sentiment:</b> {score:.3f} {action}
<b>Feedback:</b> {feedback}
""".strip()
    send_telegram_message(telegram_msg)

    return redirect(dest)

@app.route("/")
def ok():
    return "ok"
