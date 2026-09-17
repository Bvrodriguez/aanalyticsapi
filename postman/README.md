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
   dataset on the report suite and matches them to the target variable list, logging a
   summary to the Postman Console. It does **not** return attribute/column counts itself
   (confirmed live — see caveats below). **2.2's After-response script batch-fetches all
   17 known datasetIds itself via `pm.sendRequest`** — just click Send on 2.2 once and
   read the Console; no per-dataset copy/paste needed. (Collection Runner + a CSV data
   file would also work, but data-file iteration is gated behind a paid plan on some
   Postman accounts — `pm.sendRequest` isn't, so that's the reliable free path and what's
   actually wired into 2.2 now.) 2.3 still needs `datasetId` set manually per dataset if
   you want the raw TSV template view too.
3. **3. Data Flow Check (Reporting)** — 3.1 finds each target variable's classification
   dimension(s); 3.2 runs a 90-day report against one and flags whether real classified
   values come back or everything is unspecified/blank.
4. **4. Confirm via Export (optional)** — heavier but definitive: creates a small
   classification export job and reads back actual key → value rows.

Open **View → Show Postman Console** before running anything — the audit findings
(matches, missing variables, attribute counts, flowing/not-flowing verdicts) are logged
there, not just left in the raw response bodies.

## Known caveats

- `/classifications/datasets/compatibilityMetrics/{rsid}`'s response shape is now
  confirmed live (2026-09-17, `royalcaribbeanprod`): `{ report_suite_id, metrics: [{ id:
  [...shortCodes], datasets: [...datasetIds] }] }`. All 17 target variables came back
  with a dataset ID — the schema-level "does a classification dataset exist" question is
  answered yes for all of them on this suite.
- `/classifications/datasets/{datasetId}` is confirmed live too — all 17 target
  variables returned a real attribute/column count (no "unknown shape" fallback), so the
  guessed field name (one of `columns`/`schema`/`fields`/`attributes`) was correct for
  this account. See the Results table below.
- **evar66 and evar70 have live classification datasets** (`65a8fe7e43e2c836cb84c745` and
  `65a8cef442af6f5b8b4c5d98`) despite **neither appearing in the account's live
  `/dimensions` list at all** (only `evar65`/`evar67` and `prop70` exist nearby there).
  That's a real finding for the audit, independent of whether classification data is
  flowing: a classification config exists for a variable that isn't currently a
  reportable dimension. Worth raising with whoever owns the SDR.
- `listvar2` in the SDR's shorthand maps to the real dimension id `variables/listvariable2`.

## Results (royalcaribbeanprod, 2026-09-17)

Live attribute counts, ready to diff against the SDR:

| Variable | Attribute count |
|---|---|
| evar13 | 5 |
| evar14 | 3 |
| evar26 | 2 |
| evar32 | 11 |
| evar38 | 7 |
| evar50 | 2 |
| evar52 | 1 |
| evar58 | 17 |
| evar62 | 1 |
| evar66 | 2 |
| evar69 | 1 |
| evar70 | 1 |
| evar77 | 1 |
| evar87 | 10 |
| listvar2 | 3 |
| prop55 | 2 |
| tntbase | 13 |

`evar58` at 17 attributes stands out next to everything else in the 1-13 range, and
`evar52`/`evar62`/`evar69`/`evar70`/`evar77` sitting at exactly 1 attribute each are worth
confirming that's intentional rather than a stub/incomplete classification set —
independent of whatever the SDR says these should be.
