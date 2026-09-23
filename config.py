import os
import json
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")
if ALLOWED_USER_ID:
    ALLOWED_USER_ID = int(ALLOWED_USER_ID)

# SDK / API Mode Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# CLI Mode Config
CLI_COMMAND = os.getenv("CLI_COMMAND", "agy") # ou gemini, dependendo de como está instalado

STATE_FILE = "logs/bot_state.json"

def get_current_mode() -> str:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("mode", "cli")
        except:
            return "cli"
    return "cli"

def set_current_mode(mode: str):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open(STATE_FILE, "w") as f:
        json.dump({"mode": mode}, f)
