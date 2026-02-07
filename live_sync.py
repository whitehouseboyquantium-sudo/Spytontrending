import os
import json
import base64
import requests
from datetime import datetime

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("LIVE_REPO_OWNER")
REPO = os.getenv("LIVE_REPO_NAME")
PATH = os.getenv("LIVE_FILE_PATH", "data/live.json")
BRANCH = os.getenv("LIVE_BRANCH", "main")

def push_live_data(leaderboard=None, buys=None):
    if not GITHUB_TOKEN:
        print("No GitHub token set")
        return

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # get current file SHA
    r = requests.get(url, headers=headers, params={"ref": BRANCH})
    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")

    data = {
        "updated_at": datetime.utcnow().isoformat(),
        "leaderboard": leaderboard or [],
        "buys": buys or []
    }

    encoded = base64.b64encode(
        json.dumps(data, indent=2).encode()
    ).decode()

    payload = {
        "message": "Update live data",
        "content": encoded,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=headers, json=payload)

    if res.status_code not in (200, 201):
        print("GitHub update failed:", res.text)
    else:
        print("Live data updated")
