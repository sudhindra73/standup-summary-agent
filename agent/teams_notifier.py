import os
import requests
from dotenv import load_dotenv

load_dotenv()

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

def send_to_teams(message, title="📣 Sprint Summary Report"):
    if not TEAMS_WEBHOOK_URL:
        print("[ERROR] TEAMS_WEBHOOK_URL not set")
        return False

    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": title,
        "themeColor": "0076D7",
        "title": title,
        "text": message
    }

    try:
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("[✅] Sent summary to Microsoft Teams.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send message to Teams: {e}")
        return False
