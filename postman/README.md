# Classification audit (Postman)

Checks whether the SDR's classified variables (evar13, evar14, evar26, evar32, evar38,
evar52, evar58, evar66, evar69, evar70, evar77, evar87, listvar2, prop55, evar62, evar50,
tntbase) on report suite `royalcaribbeanprod` actually have classification data flowing,
and surfaces the live "# of Attributes" per variable so it can be diffed against the SDR.

## Import

1. Postman → Import → select both files in this folder:
   - `classification-audit.postman_collection.json`
   - `classification-audit.postman_environment.json`
2. Select the **RCG Adobe Analytics - Classification Audit** environment (top-right
   environment picker).
3. Fill in `client_id`, `client_secret`, `org_id` from your Adobe Developer Console
   OAuth Server-to-Server credential (same values as this repo's `.env` — see the
   top-level README). Never commit these into the environment file itself.

## Run order

1. **1. Auth** — run both requests once per session (tokens expire); everything else
   reuses the saved `access_token` / `globalCompanyId`.
2. **2. Classification Schema & Attribute Counts** — 2.1 lists every classification
   dataset on the report suite and tries to match them to the target variable list,
   logging a summary (including live attribute/column counts) to the Postman Console.
   Copy a matched `datasetId` into the environment variable of the same name, then run
   2.2/2.3 for that dataset.
3. **3. Data Flow Check (Reporting)** — 3.1 finds each target variable's classification
   dimension(s); 3.2 runs a 90-day report against one and flags whether real classified
   values come back or everything is unspecified/blank.
4. **4. Confirm via Export (optional)** — heavier but definitive: creates a small
   classification export job and reads back actual key → value rows.

Open **View → Show Postman Console** before running anything — the audit findings
(matches, missing variables, attribute counts, flowing/not-flowing verdicts) are logged
there, not just left in the raw response bodies.

## Known caveats

- The exact JSON field names returned by `/classifications/datasets/compatibilityMetrics/{rsid}`
  and `/classifications/datasets/{datasetId}` aren't documented in Adobe's public API
  reference in enough detail to hardcode with certainty, and couldn't be verified live
  from the environment this collection was built in (no credentials/network access to
  Adobe there). The endpoints themselves are confirmed real (pulled from the
  [aanalytics2](https://github.com/pitchmuc/adobe-analytics-api-2.0) Python client's
  source). The 2.1 test script tries several likely field names and dumps the raw first
  item if nothing matches — adjust the `shortCode()`/`attrCount()` helpers in that
  request's Tests tab once you see the real shape.
- `evar66` and `evar70` don't appear at all in the current live `/dimensions` list for
  this account (only `evar65`/`evar67` and `prop70` exist nearby). Worth confirming
  against the SDR directly — they may have been removed, renamed, or never implemented,
  independent of whether classification data is flowing.
- `listvar2` in the SDR's shorthand maps to the real dimension id `variables/listvariable2`.
