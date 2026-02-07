import base64
import json
import os
import requests
from datetime import datetime, timezone


def _b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")


def push_live_json(leaderboard=None, buys=None) -> None:
    """
    Safe: never breaks your bot.
    If config is missing or GitHub fails, it just returns.
    """
    try:
        owner = os.getenv("LIVE_REPO_OWNER", "").strip()
        repo = os.getenv("LIVE_REPO_NAME", "").strip()
        path = os.getenv("LIVE_FILE_PATH", "data/live.json").strip()
        branch = os.getenv("LIVE_BRANCH", "main").strip()
        token = os.getenv("GITHUB_TOKEN", "").strip()

        if not owner or not repo or not token:
            return

        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "leaderboard": leaderboard or [],
            "buys": buys or [],
        }

        api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "SpyTON-LiveSync",
        }

        # get current sha (if file exists)
        sha = None
        r = requests.get(api, headers=headers, params={"ref": branch}, timeout=20)
        if r.status_code == 200:
            sha = r.json().get("sha")

        body = {
            "message": f"SpyTON live update {payload['updated_at']}",
            "content": _b64(json.dumps(payload, indent=2)),
            "branch": branch,
        }
        if sha:
            body["sha"] = sha

        p = requests.put(api, headers=headers, json=body, timeout=20)
        # If GitHub rejects, do nothing (don’t crash bot)
        return
    except Exception:
        return
