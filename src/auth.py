import json
import time
from base64 import b64encode
from pathlib import Path
from urllib.parse import urlencode

import requests

from . import config

TOKEN_FILE = Path(__file__).resolve().parent.parent / "tokens.json"

_token_data: dict | None = None


def _load_tokens() -> dict | None:
    """Load saved tokens from disk."""
    global _token_data
    try:
        if TOKEN_FILE.exists():
            _token_data = json.loads(TOKEN_FILE.read_text())
            return _token_data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _save_tokens(data: dict) -> None:
    """Persist tokens to disk."""
    global _token_data
    _token_data = data
    TOKEN_FILE.write_text(json.dumps(data, indent=2))


def _basic_header() -> str:
    """Build Basic auth header from client credentials."""
    creds = b64encode(f"{config.CLIENT_ID}:{config.CLIENT_SECRET}".encode()).decode()
    return f"Basic {creds}"


# ── 3-Legged OAuth ──────────────────────────────────────────────────────────


def get_authorization_url() -> str:
    """Return the Autodesk login URL to start the 3-legged flow."""
    params = urlencode({
        "response_type": "code",
        "client_id": config.CLIENT_ID,
        "redirect_uri": config.CALLBACK_URL,
        "scope": config.SCOPES,
    })
    return f"{config.AUTHORIZATION_URL}?{params}"


def exchange_code(code: str) -> dict:
    """Exchange an authorization code for access + refresh tokens."""
    resp = requests.post(
        config.TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.CALLBACK_URL,
        },
        headers={
            "Authorization": _basic_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    tokens = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_at": time.time() + data["expires_in"],
    }
    _save_tokens(tokens)
    return tokens


def refresh_access_token() -> dict:
    """Refresh the access token using the stored refresh token."""
    stored = _token_data or _load_tokens()
    if not stored or not stored.get("refresh_token"):
        raise RuntimeError("No refresh token available. Re-authenticate via /api/auth/login")

    resp = requests.post(
        config.TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": stored["refresh_token"],
            "scope": config.SCOPES,
        },
        headers={
            "Authorization": _basic_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    tokens = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", stored["refresh_token"]),
        "expires_at": time.time() + data["expires_in"],
    }
    _save_tokens(tokens)
    return tokens


# ── 2-Legged OAuth (client credentials) ─────────────────────────────────────


def get_two_legged_token() -> dict:
    """Get a 2-legged token for server-to-server calls."""
    resp = requests.post(
        config.TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "scope": config.SCOPES,
        },
        headers={
            "Authorization": _basic_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        "access_token": data["access_token"],
        "expires_at": time.time() + data["expires_in"],
    }


# ── Token helper ─────────────────────────────────────────────────────────────


def get_access_token() -> str:
    """Return a valid access token, auto-refreshing if expired."""
    stored = _token_data or _load_tokens()
    if not stored:
        raise RuntimeError(
            f"Not authenticated. Visit http://localhost:{config.PORT}/api/auth/login"
        )
    # Refresh 60s before expiry
    if time.time() > stored["expires_at"] - 60:
        refreshed = refresh_access_token()
        return refreshed["access_token"]
    return stored["access_token"]


def load_tokens() -> dict | None:
    """Public wrapper to check saved tokens."""
    return _token_data or _load_tokens()
