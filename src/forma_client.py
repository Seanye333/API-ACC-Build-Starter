import requests

from . import config
from .auth import get_two_legged_token


class AccBuildAPI:
    """Wrapper around Autodesk Construction Cloud (ACC) Build APIs (2-legged auth)."""

    def __init__(self, account_id: str):
        self.base_url = config.APS_BASE_URL
        self.account_id = account_id

    def _headers(self) -> dict:
        token = get_two_legged_token()["access_token"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict | None = None):
        resp = requests.get(f"{self.base_url}{path}", headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json_data: dict | None = None):
        resp = requests.post(f"{self.base_url}{path}", headers=self._headers(), json=json_data)
        resp.raise_for_status()
        return resp.json()

    # ── Projects ─────────────────────────────────────────────────────────

    def list_projects(self) -> list[dict]:
        """List all projects in the account."""
        data = self._get(
            f"/construction/admin/v1/accounts/{self.account_id}/projects"
        )
        return data.get("results", [])

    def get_project(self, project_id: str) -> dict:
        """Get a single project by ID."""
        return self._get(
            f"/construction/admin/v1/accounts/{self.account_id}/projects/{project_id}"
        )

    # ── RFIs ─────────────────────────────────────────────────────────────

    def list_rfis(self, project_id: str) -> list[dict]:
        """List all RFIs in a project."""
        data = self._get(f"/bim360/rfis/v2/containers/{project_id}/rfis")
        return data.get("results", [])

    def get_rfi(self, project_id: str, rfi_id: str) -> dict:
        """Get a single RFI by ID."""
        return self._get(f"/bim360/rfis/v2/containers/{project_id}/rfis/{rfi_id}")

    def create_rfi(self, project_id: str, payload: dict) -> dict:
        """Create a new RFI."""
        return self._post(f"/bim360/rfis/v2/containers/{project_id}/rfis", payload)

    # ── Submittals ───────────────────────────────────────────────────────

    def list_submittals(self, project_id: str) -> list[dict]:
        """List all submittals in a project."""
        data = self._get(f"/bim360/submittals/v2/containers/{project_id}/items")
        return data.get("results", [])

    def get_submittal(self, project_id: str, submittal_id: str) -> dict:
        """Get a single submittal by ID."""
        return self._get(
            f"/bim360/submittals/v2/containers/{project_id}/items/{submittal_id}"
        )

    # ── Issues ───────────────────────────────────────────────────────────

    def list_issues(self, project_id: str) -> list[dict]:
        """List all issues in a project."""
        data = self._get(f"/issues/v1/containers/{project_id}/quality-issues")
        return data.get("data", [])

    # ── Generic ──────────────────────────────────────────────────────────

    def request(self, method: str, path: str, **kwargs):
        """Generic request for any endpoint."""
        resp = requests.request(
            method, f"{self.base_url}{path}", headers=self._headers(), **kwargs
        )
        resp.raise_for_status()
        return resp.json()
