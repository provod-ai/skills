# Technical SEO, structured data and indexation

Establish actual site/tenant/locale, public URLs, current source/constructor and allowed changes. Inspect representative templates plus the documented crawl scope before selecting a ready auditor. A single page cannot certify a site; lab SEO checks cannot establish indexation or ranking. Reuse an available ready crawler/auditor; do not build a new crawler around one unknown URL.

Check discovery and rendered content, HTTP status/redirect chains, robots and robots headers, canonical/user-vs-engine canonical, sitemap consistency, internal-link graph, duplicate/soft-404/thin variants, locale/hreflang relationships and important asset accessibility. Distinguish raw HTML from client rendering and public content from an authenticated application shell. Preserve request time, actual/effective URL, headers, rendering mode, depth/coverage and failures.

For CMS-backed archives, article links, documentation, redirects, media and optional search notifications, use the [blog and documentation release checks](blog-release.md).

## Structured data

Choose schema from the real page/user task. Extract/validate syntax and required properties using current official schema/feature guidance. Match markup to visible sourced facts: availability, price/currency, author, dates, breadcrumbs, products and review claims cannot be fabricated to satisfy JSON. Report syntax, factual consistency and rich-result eligibility separately. Valid markup does not guarantee a rich result or traffic. Never add fake ratings or imply unsupported product capabilities.

## Indexation is an observed stage

For own verified properties, retain raw inspection fields such as fetch state, robots/index state and both declared/Google canonicals. Successful fetching does not prove canonical correctness or index inclusion. Page discovery, crawl, index, ranking, click and useful outcome are different milestones. Keep full failures/misses rather than replacing them with previous best ranks.

Ordinary content uses crawlable links and sitemaps; [IndexNow](https://www.indexnow.org/faq) notifies participating engines. The [Google Indexing API](https://developers.google.com/search/apis/indexing-api/v3/using-api) is restricted to eligible JobPosting and live-video page cases, not a general article fast-indexing service. Submission acknowledgement does not guarantee indexing. Before any live notification, confirm current endpoint flow, exact scope, authority, item receipts and quota.

When repairing, freeze one coherent candidate and target identity; change the evidenced cause and read back public output. For visible UI changes, perform actual browser navigation, screenshot inspection and console checks using the host's available browser tooling; don't infer appearance from build success. Preserve useful owner WIP and avoid unrelated framework/site rewrites.

Outputs: severity-prioritized findings with exact URLs/templates/evidence and tested scope; concrete repair/diff where authorized; readback and remaining index/rank uncertainty. Source: [Google crawling/indexing docs](https://developers.google.com/search/docs/crawling-indexing), [localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions), [structured-data guidance](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data).

## Architecture, origins and output boundaries

For a restructuring or migration retain old/current/intended URL, page role, status, title, main content, canonical, links and relevant search/conversion evidence. Preserve useful identities. Test redirects to equivalent destinations and update internal links. A retired page without an equivalent needs an intentional removal response.

For a proxied section verify public canonical, sitemap, Open Graph, assets, analytics and consent separately from origin controls. Confirm that origin-level noindex does not leak into production. Navigation placement and reachability are observed graph facts; choose acceptable depth and layout from the user task.

At a JSON-LD HTML embedding boundary, test data with literal less-than characters and a script-closing string in an authorized isolated fixture or source test. Preserve original data through safe serialization and validate parsed JSON and the actual served script boundary. A plain JSON response is a different output context. [Next.js guidance](https://nextjs.org/docs/app/guides/json-ld).

Check the current supported-feature contract for the requested search appearance. As reviewed 2026-11-12, Google FAQ rich results, HowTo rich results and the sitelinks search box are retired. Their vocabulary may still serve matching content for an identified consumer. [Google updates](https://developers.google.com/search/updates).

For an actually advertised optional action tool, inspect registered description and actual handler, privileges, validation and consequential-action confirmation under the observed protocol/browser version. For an actual Lighthouse Agentic Browsing result, retain X/N, every audit's state, exact version/browser/date and compatible denominators. [Chrome scoring](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring).

## Applicable local profiles

For an eligible real local business compare current official profile and public site/schema facts. Retain identity, category, actual services, customer-facing hours, reachable phone, destination URLs, verification source and unavailable fields. Distinguish storefront, hybrid and service-area business, preserving supported hidden operating addresses. Corrections and neutral review requests follow the task's actual authority. [Google service areas](https://support.google.com/business/answer/9157481).

When a geo-grid is requested retain query, coordinates, device, date, result depth and every planned point. Distinguish measured position, not found within depth, provider error and unavailable observation. Qualify provider precision and cost. A sample grid does not establish visibility throughout the territory.

## URL resolution and selected UGC programs

Where an actual HTML document uses an effective base element, resolve relative links and media, including fragment references, using that document base. Preserve raw and resolved targets and apply the intended cross-origin safety boundary. [HTML document base](https://html.spec.whatwg.org/multipage/urls-and-fetching.html#document-base-urls).

For a genuinely applicable high-volume UGC platform considering Google's UGC Fresh Data Program, check the current program, public stable content and creator profiles, moderation/quality, technical readiness and actual admission. Program application, eligibility and search appearance are separate observations. [Google program](https://developers.google.com/search/docs/appearance/ugc-fresh-data-program).
