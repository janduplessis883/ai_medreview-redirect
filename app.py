import os, urllib.parse
import logging
from flask import Flask, request, redirect
from nltk.sentiment import SentimentIntensityAnalyzer

# one-time download
import nltk, ssl
try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context
nltk.download('vader_lexicon', quiet=True)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
sia = SentimentIntensityAnalyzer()

GOOGLE_REVIEW_URL = os.environ["GOOGLE_REVIEW_URL"]        # put yours in Render env-vars
THANK_YOU_URL     = os.environ.get("THANK_YOU_URL", "/static/thanks.html")

@app.route("/review")
def review():
    surgery  = request.args.get("surgery",  "unknown")
    feedback = request.args.get("feedback", "")
    if not feedback:                                   # paranoia
        return redirect(THANK_YOU_URL)

    score = sia.polarity_scores(feedback)["compound"]
    dest  = GOOGLE_REVIEW_URL if score >= 0.05 else THANK_YOU_URL

    # Log the required information
    logging.info(f"Freetext: '{feedback}', Surgery: '{surgery}', Sentiment Score: {score}, Output: '{dest}'")

    # optional: log to DB / Slack / whatever here – keeps latency <150 ms
    return redirect(dest)

# health-check that Render wants
@app.route("/")
def ok(): return "ok"
