# PUBLIC RELEASE AUDIT

## 1. Stale README Claims
- The previous `README.md` stated "178/178 tests passing", which is out of date. The final verified test count is **236/236**.
- The previous `README.md` contained the sentence "datasets are currently unavailable" unconditionally. It has been updated to reflect the verified CIC-IDS2017 real-dataset experimental phase.
- Claims about a single "840-second (14 minute)" lead time have been appropriately contextualized.

## 2. Stale Test Counts
- References to 178 tests or 84 tests in frontend documentation have been updated (or are correctly sourced from actual data) to reflect the 236 backend tests.

## 3. Stale Dataset Claims
- Any claims mentioning "production deployed" or implying universal live benchmark guarantees have been scrubbed.
- The `CIC-IDS2017` historical dataset is strictly classified as a "historical replay experiment".
- A "Novel-Class Limitation" disclaimer has been added to address BOTNET and SCANNING models not being explicitly trained.

## 4. Stale Architecture Claims
- There are no remaining references to Kafka, Spark, Redis, MLflow, LSTM, or Transformer models across the UI and final reports. SENTRANET is strictly dual-engine (XGBoost + Isolation Forest) built on FastAPI and React.

## 5. Public Artifacts That Should Not Be Committed
- `sentranet.db` (the SQLite local runtime state) was being tracked. It has been removed from tracking and added to `.gitignore`.
- `.db`, `.sqlite`, and `.sqlite3` extensions have been added to `.gitignore`.

## 6. Frontend/Public-Demo Gaps
- The frontend was missing a dedicated Landing Experience to summarize the pipeline before entering the SOC. This was solved by creating `LandingPage.tsx` and updating routing.
- The Evaluation Page was lacking explicit CIC-IDS2017 limitation disclaimers. It has been updated to show exactly: ~3.1M FLOWS → 2,454 WINDOWS → 60/20/20 CHRONOLOGICAL SPLIT.
- The Live Network monitoring page was missing a disclaimer about OS-level permissions. This has been resolved.

## 7. Security Concerns
- `.env.example` verified to contain safe dummy values.
- No RBAC or undocumented fake-authorization middlewares were found.
- No private API keys or tokens are hardcoded.

## 8. Recommended Minimal Fixes
- Implemented `LandingPage.tsx`.
- Refactored `SimulationBanner.tsx` text.
- Cleaned git tracking of local state files.
- Recompiled and executed `pytest` to guarantee system stability (236/236 passed).
