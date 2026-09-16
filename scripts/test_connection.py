#!/usr/bin/env python3
"""Verifies Adobe Analytics API credentials by fetching report suites.

Usage: python scripts/test_connection.py
Requires ADOBE_* variables in .env (see .env.example).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from adobe_analytics import AdobeAnalyticsClient  # noqa: E402
from adobe_analytics.auth import AdobeAuthError  # noqa: E402
from adobe_analytics.client import AdobeAnalyticsError  # noqa: E402


def main() -> int:
    try:
        client = AdobeAnalyticsClient.from_env()
        company_id = client.discover_company_id()
        print(f"Authenticated. Global company ID: {company_id}")

        suites = client.get_report_suites(limit=5)
        names = [s.get("rsid") for s in suites.get("content", [])]
        print(f"Sample report suites ({len(names)} of {suites.get('totalElements', '?')}): {names}")
        return 0
    except KeyError as exc:
        print(f"Missing required environment variable: {exc}", file=sys.stderr)
        return 1
    except (AdobeAuthError, AdobeAnalyticsError) as exc:
        print(f"Connection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
