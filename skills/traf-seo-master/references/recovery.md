# Monitoring, loss diagnosis and bounded recovery

Keep current raw observations alongside derived dashboards. Retain requested/effective market, engine/device/date/window/depth, provider/method/status, completeness, exact source/trace/job ID and raw hash. A previous best rank may be displayed as stale history but must not overwrite a current missing/failed observation. Missing data is not zero or confirmed disappearance.

Classify the actual failure before changing the asset:

| Signal | Distinguishing evidence | Response |
|---|---|---|
| No fresh metrics/rank | Collector freshness, errors, correct scope, quota/completeness, same-scope own totals. | Repair collection; don't diagnose content from a broken dashboard. |
| HTTP403/429/5xx | Provider/body/trace/Retry-After and official status/notice. | Source-specific treatment; not every403 is throttling and not every403 is a ban. |
| Public/bot access blocked | Real fetch/render, robots/headers, server/CDN logs and verified bot identity. | Correct the evidenced configuration within authority and observe later genuine fetches. |
| Canonical/index loss | Raw fetch/index/robots plus userCanonical/googleCanonical and actual URL history. | Fix the demonstrated cause; notifications are not an indexing guarantee. |
| Rank/click/CTR decay | Final comparable cohorts, demand/seasonality, SERP and site changes. | Targeted refresh/merge/link/repair with an explicit hypothesis, not blind volume. |
| Completely vanished pages | Anti-join against previous eligible cohort, not only rows present in both windows. | Distinguish disappearance from collection truncation and retain losers. |
| Host/account/manual action | Actual notice, affected section/property/searcher-country/engine and current rule version. | Official cause removal/review/support path; no assumed global banned-bit or automatic new identity. |
| Traffic but failed use | Normal landing/signup/useful-result/payment path and own event coverage. | Repair the failed user step; traffic alone is not commercial acceptance. |

Bot user-agent strings are not identity. Record verified/spoofed/unverified, method and checked time; use official IP/forward-confirmed DNS where appropriate, with a trusted proxy chain. Raw log storage/retention and privacy follow the owning project; don't deploy a warehouse before a concrete coverage need.

For any externally mutating/paid job, keep intent, operation key, reservation, authoritative receipt, target revision and reconciliation state. A worker deadline does not cancel an outstanding handler; an unknown create/send stays UNKNOWN. Do not duplicate a possibly completed action or release its reservation merely because a process restarted. Reconcile or prove not-applied before another bounded submission.

Each diagnostic retry records observed failure, hypothesis, one distinguishing change when possible, expected result and call/time/spend bound. Preserve completed work and failed/unknown receipts. After repeated point fixes expose untested dependencies, freeze the whole candidate and reproduce the intended path instead of issuing more micro-releases.

Use current ready collectors only after verifying raw semantics; e.g. [gsccli](https://github.com/nalyk/gsccli), [Octopus](https://github.com/octopusOn/octopusOnPageSEO) and available [Bisibility](https://github.com/CorgiCorner/bisibility) observation contracts. Their presence does not grant live property/log access. Output a classified incident, smallest supported correction, readback and actual observed recovery/remaining uncertainty, not a provider-blame claim from a generic error.
