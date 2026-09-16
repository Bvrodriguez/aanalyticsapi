"""OAuth Server-to-Server authentication for Adobe Analytics API.

See: https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/
"""

from __future__ import annotations

import time

import requests

IMS_TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"

# Refresh a bit early so a token never expires mid-request.
_EXPIRY_SAFETY_MARGIN_SECONDS = 60


class AdobeAuthError(RuntimeError):
    """Raised when Adobe IMS rejects a token request."""


class OAuthServerToServerAuth:
    """Fetches and caches IMS access tokens via the client_credentials grant."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: str,
        token_url: str = IMS_TOKEN_URL,
        session: requests.Session | None = None,
    ) -> None:
        if not client_id or not client_secret or not scopes:
            raise ValueError("client_id, client_secret, and scopes are required")
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._token_url = token_url
        self._session = session or requests.Session()
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def get_access_token(self) -> str:
        if self._access_token is None or time.monotonic() >= self._expires_at:
            self._refresh()
        assert self._access_token is not None
        return self._access_token

    def _refresh(self) -> None:
        response = self._session.post(
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": self._scopes,
            },
            timeout=30,
        )
        if not response.ok:
            raise AdobeAuthError(
                f"IMS token request failed ({response.status_code}): {response.text}"
            )

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise AdobeAuthError(f"IMS token response missing access_token: {payload}")

        # Adobe IMS v3 returns expires_in in milliseconds, unlike standard OAuth.
        expires_in_seconds = int(payload.get("expires_in", 0)) / 1000

        self._access_token = access_token
        self._expires_at = time.monotonic() + max(expires_in_seconds - _EXPIRY_SAFETY_MARGIN_SECONDS, 0)
