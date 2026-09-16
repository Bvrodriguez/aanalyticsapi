"""Minimal client for the Adobe Analytics 2.0 API.

Handles OAuth Server-to-Server auth, company discovery, and report suite /
reporting calls. See: https://developer.adobe.com/analytics-apis/docs/2.0/
"""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

from .auth import OAuthServerToServerAuth

ANALYTICS_BASE_URL = "https://analytics.adobe.io"
DISCOVERY_URL = f"{ANALYTICS_BASE_URL}/discovery/me"


class AdobeAnalyticsError(RuntimeError):
    """Raised when the Adobe Analytics API returns an error response."""


class AdobeAnalyticsClient:
    """Authenticated client for Adobe Analytics 2.0 API calls."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        org_id: str,
        scopes: str,
        global_company_id: str | None = None,
    ) -> None:
        self._client_id = client_id
        self._org_id = org_id
        self._global_company_id = global_company_id
        self._auth = OAuthServerToServerAuth(client_id, client_secret, scopes)
        self._session = requests.Session()

    @classmethod
    def from_env(cls, env_file: str | None = ".env") -> "AdobeAnalyticsClient":
        """Builds a client from ADOBE_* environment variables, loading env_file first."""
        load_dotenv(env_file)

        client_id = os.environ["ADOBE_CLIENT_ID"]
        client_secret = os.environ["ADOBE_CLIENT_SECRET"]
        org_id = os.environ["ADOBE_ORG_ID"]
        scopes = os.environ["ADOBE_SCOPES"]
        global_company_id = os.environ.get("ADOBE_GLOBAL_COMPANY_ID") or None

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            org_id=org_id,
            scopes=scopes,
            global_company_id=global_company_id,
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._auth.get_access_token()}",
            "x-api-key": self._client_id,
            "x-gw-ims-org-id": self._org_id,
            "Content-Type": "application/json",
        }

    def discover_company_id(self) -> str:
        """Looks up the caller's report-suite company IDs and caches the first one."""
        response = self._session.get(DISCOVERY_URL, headers=self._headers(), timeout=30)
        self._raise_for_status(response)

        companies = response.json().get("imsOrgs", [])
        for org in companies:
            for company in org.get("companies", []):
                global_company_id = company.get("globalCompanyId")
                if global_company_id:
                    self._global_company_id = global_company_id
                    return global_company_id

        raise AdobeAnalyticsError("No report-suite company found for this org/credential")

    def _require_company_id(self) -> str:
        if not self._global_company_id:
            return self.discover_company_id()
        return self._global_company_id

    def get_report_suites(self, rsid_filter: str | None = None, limit: int = 10) -> dict:
        """Lists report suites visible to this credential."""
        company_id = self._require_company_id()
        params = {"limit": limit}
        if rsid_filter:
            params["rsidContains"] = rsid_filter

        response = self._session.get(
            f"{ANALYTICS_BASE_URL}/api/{company_id}/collections/suites",
            headers=self._headers(),
            params=params,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def run_report(self, report_request: dict) -> dict:
        """Runs a Reports API request body against /api/{companyId}/reports."""
        company_id = self._require_company_id()
        response = self._session.post(
            f"{ANALYTICS_BASE_URL}/api/{company_id}/reports",
            headers=self._headers(),
            json=report_request,
            timeout=60,
        )
        self._raise_for_status(response)
        return response.json()

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if not response.ok:
            raise AdobeAnalyticsError(
                f"Adobe Analytics API request failed ({response.status_code}): {response.text}"
            )
