import os
import json
import base64
import time
from typing import Any, Dict, List, Optional

import requests


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def push_live_json(*, leaderboard: List[Dict[str, Any]], buys: List[Dict[str, Any]]) -> None:
    """
    Writes `data/live.json` to your GitHub repo using the GitHub Contents API.
    Safe: if not configured or any error happens, it silently returns.

    Required env vars (Railway):
      - GITHUB_TOKEN   (classic PAT with repo contents write)
      - GITHUB_REPO    (e.g. "odegaardquantium-code/Wrb")
    Optional:
      - GITHUB_BRANCH  (default: "main")
      - GITHUB_PATH    (default: "data/live.json")
    """
    token = _env("GITHUB_TOKEN")
    repo = _env("GITHUB_REPO")
    if not token or not repo or "/" not in repo:
        return

    branch = _env("GITHUB_BRANCH", "main")
    path = _env("GITHUB_PATH", "data/live.json")

    # Keep payload small + stable
    payload = {
        "ts": int(time.time()),
        "leaderboard": leaderboard[:10],
        "buys": buys[:20],
    }
    content_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("ascii")

    api_base = "https://api.github.com"
    url = f"{api_base}/repos/{repo}/contents/{path}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "SpyTON-live-sync",
    }

    # Get current sha if file exists
    sha: Optional[str] = None
    try:
        r = requests.get(url, headers=headers, params={"ref": branch}, timeout=10)
        if r.status_code == 200:
            sha = (r.json() or {}).get("sha")
    except Exception:
        sha = None

    body: Dict[str, Any] = {
        "message": "SpyTON: update live.json",
        "content": content_b64,
        "branch": branch,
    }
    if sha:
        body["sha"] = sha

    try:
        requests.put(url, headers=headers, json=body, timeout=15)
    except Exception:
        return
