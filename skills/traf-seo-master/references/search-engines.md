# Google, Bing and Yandex: evidence and measurement

Use for owned-property diagnosis, search performance, engine-specific indexing and AI-search reporting. Default to English worldwide, then the products' actual locales. Yandex support does not establish a Russian campaign. Sources checked 2026-11-01; no property, counter, account or authenticated integration was tested here.

## Establish the measurement contour

Obtain actual domains/locales, verified property/host/counter identifiers, account access, desired period, timezone, devices, search type, filters and baseline. Preserve provenance for owner exports. Do not infer login, ownership, zero traffic or current entitlement from an old grant, key locator, sign-in page or empty report.

Use an already available, verified read-only connector or owner export first. Before any API call, read the complete current official flow/example, identify provider/API family/account/app/version/base URL/auth/quota boundary, compare the exact planned request with the schema and example, and run one bounded read-only canary. Missing real identifiers or authorization blocks that call; continue public analysis without invented properties. Google's [experimental Analytics MCP source](https://github.com/googleanalytics/google-analytics-mcp) is a ready optional adapter, not a bundled or activated integration. Dashboard availability never proves a reporting API exists.

## Select the engine and evidence

| Need | Preferred owned source | Interpretation |
| --- | --- | --- |
| Google visibility | Search Console performance and URL Inspection | Impressions/clicks/index state; clicks are not analytics sessions. |
| Acquired visits | GA4 organic-search sessions or the existing site's equivalent | Preserve collection, consent, attribution and session definitions. |
| Bing visibility | Bing Webmaster Tools, including AI Performance where available | Search/citation evidence; not automatically user visits. |
| Yandex visibility | Verified Yandex Webmaster host | Engine-specific crawling/indexing/search evidence. |
| Yandex/user behavior | Metrica's actual counter and collection | Visits/events under that counter's configuration. |
| Yandex demand | Wordstat with explicit region/device/period | Yandex query counts, not worldwide all-engine demand or unique people. |

[Yandex Webmaster setup/API](https://yandex.com/support/webmaster/en/service/quick-start) requires verified site rights; follow its [OAuth access flow](https://yandex.com/dev/webmaster/doc/en/tasks/how-to-get-oauth) for API use. [Metrica API authorization](https://yandex.com/dev/metrika/en/intro/authorization) depends on actual counter access. [Wordstat's official API access](https://yandex.com/support2/wordstat/en/content/api-wordstat) additionally requires its account-specific access process and quotas. These are separate contours. Locale support is technical applicability, not proof of acquisition opportunity.

## Preserve totals, detail and freshness separately

Fetch one finalized aggregate for the declared Google period before drilling into queries/pages. [Search Analytics](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) returns top rows, not an exhaustive ledger; [extraction guidance](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data) documents 25,000 rows/request and 50,000/day/search type. Page/query grouping can drop data. [Anonymized queries](https://support.google.com/webmasters/answer/17010575), filters and aggregation differences prevent detail rows from necessarily summing to totals. Label detail coverage; do not manufacture a reconciliation.

The default API data state is finalized; fresh/incomplete states remain provisional. Preserve request/response freshness metadata and collection time. GA4 has distinct processing, row and [token/concurrency quotas](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas); use the actual property and [documented setup](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart). Preserve thresholding, sampling or other data-loss metadata when returned. Do not add Google clicks, Bing citations and analytics sessions into one “organic visits” total. The primary project outcome remains observed organic visits; publication, indexing and AI mentions are intermediate.

## Current AI-search distinctions

[Google's current AI guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) supersedes the older AI-features page on reporting/control. The dedicated [Generative AI performance report](https://support.google.com/webmasters/answer/16984139), rolled out worldwide August 31, 2026, measures AI Overviews/AI Mode **impressions**, with page/country/device/date dimensions and text/multimodal search types. Its data overlaps Web performance: do not add it again or invent AI-click attribution/API fields. Dates use PT; property/page aggregation differs. Missing reports can mean insufficient impressions. Exported unavailable `~`/`-` values become zero: preserve their unavailable status separately from observed zero.

The [Search generative AI control](https://support.google.com/webmasters/answer/16908024) also rolled out August 31. Read effective include/exclude and parent-property inheritance; default inclusion does not prove this property's actual setting. It governs links/grounding in Search AI features, separately from training and ordinary Search ranking/inclusion. Do not change it during diagnosis. Indexed/snippet eligibility still applies, without special AI schema/files; eligibility does not guarantee inclusion.

Bing launched [AI Performance](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/) in 2026 and added [Topics Portfolio beta](https://blogs.bing.com/webmaster/2026/10/introducing-topics-portfolio-beta-in-ai-performance/) in October. Treat citations, topic groupings and approximate opportunity signals as visibility/planning evidence, not rankings, clicks or causal lift. The [October 30 training/grounding announcement](https://blogs.bing.com/search/2026/10/your-content-your-choice-clearer-preferences-for-training-and-grounding/) starts honoring new preferences February 1, 2027; do not describe them as already effective on November 1, 2026. Recheck implementation dates before a later change.

## Diagnose and return raw evidence

[URL Inspection](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect) reports Google's stored indexed-version status, not a live test. Preserve `pageFetchState`, `robotsTxtState`, `indexingState`, `coverageState`, `lastCrawlTime`, `googleCanonical` and `userCanonical` exactly when returned; distinguish absent fields and analyst inference. Use the [response schema](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult), not a rewritten summary that erases disagreement. A research fetch failure or provider-specific 403 is not proof Googlebot is blocked.

[IndexNow](https://www.indexnow.org/faq) receipt acknowledges a notification, not indexing or traffic. Do not submit URLs during a read-only audit. Metrica screenshots, attribution reports and before/after movement are observations; causal lift requires a defensible comparison, with [attribution settings](https://www.yandex.com/support/metrica/en/reports/attribution-model) retained.

Return raw exports/requests with secrets redacted, finalized totals, provisional series, detail coverage, source-specific errors, diagnosed causes versus hypotheses, and the next bounded check. Report unavailable access as unknown. Never replay an UNKNOWN external effect or replace unavailable metrics with estimates presented as owned facts.

## Additional measurement checks dated 2026-11-12

Before attributing reporting movement to a site change, inspect the current [Google anomaly record](https://support.google.com/webmasters/answer/6211453) for the actual window/metrics. The documented GSC issue spanning 2025-05-13 through 2026-04-27 affected reported impressions and related CTR/position. Clicks were unaffected by that issue. Preserve the affected interval and frozen source.

Where current GA4 default-channel reporting applies, distinguish AI Assistant/ai-assistant from custom groups, recognizable referrers, Organic Search, Direct and unknown. Google AI Overviews/AI Mode are outside that AI Assistant channel. Keep the actual property, grouping type, collection window and attribution. Current definitions do not retroactively reclassify a retained export. [GA4 definitions](https://support.google.com/analytics/answer/9756891).

For CrUX History preserve per-period null and NaN/missing-data states separately from observed zero. Retain exact period boundaries; overlapping rolling windows are not independent samples. [CrUX History](https://developer.chrome.com/docs/crux/history-api).

Keyword Planner historical metrics are approximate and can group close variants. Preserve returned query/close_variants, country/language/network and dates, approximation and access limits. Competition and bid percentiles describe advertising. Account spending does not prove exact unrestricted search volume. [Historical metrics](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-historical-metrics).

## Adapter and report readback

Verify the expected and actual credential principal/scopes and exact target coverage. A domain property, a URL-prefix property and a GA4 stream/site or hostname filter have different populations. Preserve protocol, host and path rather than assuming www, bare domain and subdomains are equivalent.

Keep request dimensions, filters, aggregation, dataState, limits and raw source responses through the final report. Query/page rows are pairs, and a filtered aggregate remains filtered. Daily unique users cannot be summed into whole-period unique users; entry visits, visits, actions and pageviews retain their native definitions.

Inspect delivered export units, row counts and field mappings against the source. Preserve a row cap, missing inspection field, partial aggregate and unavailable/thresholded value as such. [Reviewed adapter limits](source-runtime-review.md).
