import os
from dotenv import load_dotenv

load_dotenv()

# APS OAuth credentials
CLIENT_ID = os.getenv("APS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET", "")
CALLBACK_URL = os.getenv("APS_CALLBACK_URL", "http://localhost:8080/api/auth/callback")
PORT = int(os.getenv("PORT", "8080"))

# APS OAuth endpoints
AUTH_BASE_URL = "https://developer.api.autodesk.com/authentication/v2"
AUTHORIZATION_URL = f"{AUTH_BASE_URL}/authorize"
TOKEN_URL = f"{AUTH_BASE_URL}/token"

# APS Data Management base URL
APS_BASE_URL = "https://developer.api.autodesk.com"

# Default scopes
SCOPES = "data:read data:write account:read"
