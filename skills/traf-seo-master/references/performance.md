# Performance and the included Lighthouse adapter

Use a current ready collector and distinguish a reproducible lab audit from real-user Core Web Vitals. Record exact URL/time, mobile/desktop conditions, version, throttling, network/device and coverage. One successful lab run does not establish field performance, a whole-site audit, indexation, rankings or acquired audience. Obtain real-user data where available and compare like scopes/time windows.

The shipped helper wraps official Lighthouse **13.6.0**. Its Node requirement is **>=22.19**; an existing Chrome installation is separate. The copy-only package installer does not install these dependencies. Use a verified local executable and current official flow. A current-page provider/access error is evidence, not permission to switch accounts/proxies or guess bypass flags.

```text
python3 scripts/seo-master.py audit --url https://example.com/ --lighthouse /actual/path/to/lighthouse --out /actual/fresh/output --timeout 180
```

The adapter invokes the documented JSON/headless CLI with performance, SEO, accessibility and best-practices categories; no shell command interpolation, credential header or automated retry. It expects a fresh output directory and rejects query/fragment URLs to avoid accidentally persisting access-bearing URLs. POSIX audit runtime is required by this helper; other OS runtime is unverified. Install/copy checks remain separate.

Outputs retain `raw-lighthouse.json`, stdout/stderr, `audit-receipt.json` and normalized `audit-summary.json`. Raw hashes, exact tool version, duration and errors qualify the result. Interpret scoreDisplayMode: notApplicable, manual, informative, explicit collection errors and genuinely unknown checks are distinct. Informative can retain a native score of1 without being a passed audit. RuntimeError/nonzero/timeout/malformed output fail; missing values never become zero/empty-success. A lab audit with bad scores may be a completed **measurement**, not an accepted page or growth result. Read explanations: a robots fetch blocked by collector/CSP is not proof of an invalid site's robots file.

All heavy output, temporary browser profiles and caches follow the selected project's storage rules. The adapter sets its child's TMPDIR under the fresh output; never attach it to an owner's live authenticated Chrome profile. On timeout only the adapter's own child process group is cleaned up. Preserve the attempted result; no unchanged automatic retry. Any diagnostic retry records the observed failure, changed variable, expected distinguishing result and bound.

Prioritize changes by a real user path: loading/interaction/layout stability, critical resources, rendering, unused blocking work, media/font delivery and affected template distribution. Don't chase a score by removing necessary user value or count one template as the entire site. Keep reduced-motion/accessibility and actual mobile checks in the product path.

Official sources: [versioned Lighthouse repository](https://github.com/GoogleChrome/lighthouse), [headless guidance](https://github.com/GoogleChrome/lighthouse/blob/main/docs/headless-chrome.md), [Chrome Lighthouse documentation](https://developer.chrome.com/docs/lighthouse/overview). Requalify changes to toolchain/config before comparing runs. Field metrics and statistical targets come from current owning sources, not a copied fixed score promise.
