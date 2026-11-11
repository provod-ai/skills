# Reviewed collector and plugin contracts

Source pin is AgriciDaniel/claude-seo at cca7e4a267991aca880efade1fd12e8498caf2ce. Qualify the intended host, provider/account, transport and output before using an upstream collector. Code inspection establishes implementation and known limits; a real result needs its own controlled input and receipt. [Pinned implementation](https://github.com/AgriciDaniel/claude-seo/tree/cca7e4a267991aca880efade1fd12e8498caf2ce/scripts).

| Area | Source observation | Check before reuse |
| --- | --- | --- |
| URL safety and rendering | requests DNS pinning, Chromium resolution and CONNECT proxy behavior have different boundaries | Verify the actual transport, allowed destinations, redirects, isolation and missing/degraded states |
| Raw HTML and document base | Fetch/body/output caps and local parsing affect available facts | Retain response status, final URL, effective HTML base, raw/resolved references, truncation and parse failures |
| Sitemap discovery | Default traversal limits children and depth; nested indexes remain unfollowed | Reconcile every root, child, nested branch, EOF, error and eligible-page comparator before complete coverage |
| GSC reporting | Query/page pairs, filtered aggregates and partial sums have distinct denominators | Retain request dimensions/filters, aggregation/dataState, raw response and totals/detail coverage |
| Report exports | Percent values, normalized inspection fields and export row limits can diverge | Check final artifact units, populated fields, actual/source row counts and missingness |
| GA4 and Matomo | Daily unique users cannot be summed as period-unique; entry visits, visits and actions differ | Preserve native metric names, whole-period aggregates, scopes, thresholding and unknowns |
| Property and credentials | Available credentials and domain matching can select a broader or different contour | Verify actual principal, granted scopes, protocol/host/path, property, stream/site and expected selection |
| Field/lab performance | Numerical scores, missing CLS, per-side origin fallback and skipped drift checks can be misleading | Preserve native audit modes, unknowns, target type and matched collection windows |
| LCP cause | Ratios of separately aggregated component p75 values do not decompose one p75 visit | Use a justified statistical method or corresponding traces/observations and test the causal hypothesis |
| Visual defaults | Some visual fields are initialized to success without calculating geometry | Inspect screenshots, actual measurements, actions and errors rather than copying default booleans |
| Common Crawl graph | Byte/time/decompression limits can end a partial stream without absence proof | Retain dataset release, graph scope, EOF/cap/error, matched population and incomplete/unknown states |
| Paid tasks and notifications | Estimates and independent ledgers do not ensure task-level cost control or uncertain-write recovery | Bind exact account/provider/units/budget before effect, preserve intent, original operation IDs/raw receipts and UNKNOWN |
| Merchant/schema generation | Templates can insert locale, currency, zero price or delivery defaults | Verify actual offer/page/feed facts, eligibility and output boundary |
| IPTC and image derivatives | exiftool failure can look like missing metadata; inject can overwrite input | Preserve original files and distinguish read failure, absent tag and verified generated derivative |
| Optional protocols | Endpoint availability and a green process exit do not prove a working action | Inspect parsed status/content, actual handler, privilege and confirmation in the intended browser |
| Hooks/installers | Hook skips, host-specific configuration and broad uninstall patterns have limited proof | Qualify native host behavior, preserve shared config and remove only verified owned files |

The implementation review includes all 64 core script files, all 19 agent files and nine extension families. All 111 files in the core test/fixture directory were read as source evidence. Dependencies, source tests, provider calls, installers and integration actions require separate runtime qualification. The reference does not install or activate them.

## Preserve the underlying evidence

A zero exit can indicate a completed report operation with errors or no data. Read the actual schema/status, expected artifacts and population before assigning a site verdict. Retain a null, NaN, skipped/manual/informative, not-found-within-depth, partial source or transport error distinctly. Domain absence, no risk, eligibility, deliberate 404 and completed crawl each require matching evidence.

For every account adapter use the actual credential principal and target scope. An explicitly chosen credential source must not silently fall through to another account. A read-only setup check requests only the necessary scopes and proves a bounded authorized read of the intended resource.

Before an uncertain state-changing retry, reconcile the original provider operation ID or supported idempotency key against durable receipts. A reset command in an example or an approximate local cost tracker does not authorize clearing execution history.

When returning a spreadsheet, HTML or other rendered report, inspect the delivered file itself against the raw source. For example, a CTR fraction of 0.025 represents 2.5 percent; a query appearing on two page rows remains one query with two query/page observations. Preserve coverage and warnings across presentation.

Use this code review together with [upstream maintenance](upstream-maintenance.md), [site assessment](site-audits.md), [engine measurement](search-engines.md) and the [current skill-source review](upstream-skill-review.md).
## Separately pinned SEO Cockpit companion

The marketplace links a separate [SEO Cockpit snapshot](https://github.com/AgriciDaniel/claude-seo/tree/cf97b4785f4241b9367d654c60c7207dc3afcf68/plugins/seo-cockpit). All 22 companion files and eight owning dependencies are covered by complete static reads: six changed dependency versions were fully read and two exact duplicate blobs reuse previously verified full reads. The companion includes 85 test declarations. This is source qualification; the upstream test result and live hook behavior were not reproduced. The [rule ledger](reviewed-rules.json) retains all fifteen concrete cases.

Its paid-route guard recognizes a finite set of hosts, scripts and events. Enumerate every compound/concurrent operation and reserve the aggregate against the shared cap before effects; use one serialized boundary for every writer sharing the same account/cap when reservation is unavailable. Table estimates, ask/allow flags and post-call logs do not establish actual billed units, successful execution or absence of an uncertain operation.

Compare dashboard labels with actual request dates, source aggregation and clipping. Retain query errors, warnings, sample limits and the difference between daily averages and native period aggregates. A latest non-null CrUX point cannot stand in for a later missing period, and a partial chart set cannot establish good CWV. An eight-item display does not establish that only eight findings exist; a completed main turn or report path does not prove all child audits finished or the file exists.

Bind cached results and saved Maps grids to the actual selected site/business/property/configuration/window. Verify an explicit source root and exact loaded version, real event registration, credential propagation and file/export side effects. The companion's readiness doctor and README are inputs to qualification. In particular, an ordinary command can export an account-derived HTML file when its pane is absent; inspect the actual output and its intended destination.


The older linked Merchant helper and current source both default a missing currency to USD and strip commas during normalization. Preserve actual raw units and parsing semantics instead of treating those defaults as facts. The older linked CrUX trend helper also substitutes zero percent for a zero baseline; the current snapshot handles that case differently, and the Cockpit tab does not consume this trends field. Inspect exact producer version and task-level status/result completeness before using either helper result.
