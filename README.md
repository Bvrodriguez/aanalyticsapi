# aanalyticsapi

Python client for the [Adobe Analytics 2.0 API](https://developer.adobe.com/analytics-apis/docs/2.0/),
using OAuth Server-to-Server authentication.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. In the [Adobe Developer Console](https://developer.adobe.com/console), create (or open) a
   project and add the **Adobe Analytics API** with an **OAuth Server-to-Server** credential.
   From the credential's details page, copy:
   - Client ID
   - Client Secret
   - Organization ID (IMS org ID)
   - Scopes (exact string shown on the credential page)

3. Copy `.env.example` to `.env` and fill in those values. `.env` is git-ignored — never commit
   real credentials, and never paste them into chat or share them outside the Developer Console
   and your own `.env` file.

4. Verify the connection:

   ```bash
   python scripts/test_connection.py
   ```

   On success this prints the discovered Global Company ID and a sample of visible report suites.

## Usage

```python
from adobe_analytics import AdobeAnalyticsClient

client = AdobeAnalyticsClient.from_env()

suites = client.get_report_suites(limit=10)

report = client.run_report({
    "rsid": "your-report-suite-id",
    "globalFilters": [
        {"type": "dateRange", "dateRange": "2024-01-01T00:00:00.000/2024-01-31T00:00:00.000"}
    ],
    "metricContainer": {"metrics": [{"id": "metrics/visits"}]},
    "dimension": "variables/daterangeday",
})
```

`AdobeAnalyticsClient` handles token fetch/refresh and company-ID discovery automatically; call
`get_report_suites` / `run_report` directly once credentials are configured.

## Notes

- Access tokens are cached in memory per `AdobeAnalyticsClient` instance and refreshed
  automatically shortly before they expire.
- If you already know your Global Company ID, set `ADOBE_GLOBAL_COMPANY_ID` in `.env` to skip
  the discovery call.
