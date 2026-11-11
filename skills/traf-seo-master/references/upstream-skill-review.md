# Reviewed upstream skills

Review dated 2026-11-12. Use the applicable task route for the adopted rules.

| Source module | Master route |
| --- | --- |
| Marketing Skills seo-audit | [Technical checks](technical-indexing.md), [measurement](search-engines.md), [query and competitor evidence](intelligence.md) |
| Marketing Skills ai-seo | [AI answers and agent task panels](ai-search.md) |
| Marketing Skills programmatic-seo | [Page families and publication](sites-publication.md) |
| Marketing Skills site-architecture | [Inventory, redirects and public origins](technical-indexing.md) |
| Marketing Skills schema | [Markup and feature eligibility](technical-indexing.md), [media and merchant feeds](media-seo.md) |

Marketing Skills was reviewed at commit 1f837447b20bb6f0e72d87b80ece1c221c362c7d. The scope includes all five core files, their 29 Markdown references and 51 evaluation scenarios. [Pinned source](https://github.com/coreyhaines31/marketingskills/tree/1f837447b20bb6f0e72d87b80ece1c221c362c7d/skills).

Claude SEO was reviewed at commit cca7e4a267991aca880efade1fd12e8498caf2ce. All 26 core skills and all 111 Markdown references were read. All 64 core implementation scripts, 19 agent definitions and nine extension families were also reviewed. The complete 505-file snapshot is accounted for by source, duplicate, fixture and illustrative-asset dispositions. [Implementation limits](source-runtime-review.md). The 38 FLOW prompt files share one template after normalizing titles, descriptions, headings and stage labels; the three Win prompts have their own bodies. [Pinned source](https://github.com/AgriciDaniel/claude-seo/tree/cca7e4a267991aca880efade1fd12e8498caf2ce).

| Claude SEO core group | Master route |
| --- | --- |
| seo, audit, page, technical, schema, sitemap | [Technical checks](technical-indexing.md), [site assessment](site-audits.md) |
| content, content-brief, competitor-pages, cluster, plan | [Content](content-briefs.md), [intelligence](intelligence.md), [acquisition](acquisition.md) |
| geo, agentic, sxo | [AI search](ai-search.md), [landing/user task](landing-design.md) |
| backlinks, local, maps | [Authority](distribution-authority.md), [conditional local checks](technical-indexing.md) |
| google, dataforseo | [Engine/account evidence](search-engines.md), [source qualification](upstream-maintenance.md) |
| drift, programmatic | [Refresh/recovery](recovery.md), [sites and publication](sites-publication.md) |
| images, image-gen, ecommerce | [Media](media-seo.md), [merchant eligibility](technical-indexing.md) |
| flow | Existing acquisition/content/distribution/outcome routes; individual prompt names do not establish distinct mechanisms |

The adopted refinements retain all 145 original check IDs. Changed methods and inputs have new revisions. Site findings, account authentication, source inspection, integration execution and acquired visits require their own evidence.

## Resolve source conflicts before adoption

The upstream recipes contain useful examples alongside context-dependent numerical suggestions. Select click depth, link counts, title/answer lengths, freshness cadence, cohort size and observation window from the actual task and evidence. A popularity count or an arbitrary score cannot establish a search outcome.

Google has a dedicated report for generative-feature impressions. Preserve its overlap with Web performance and its distinct metric semantics. The upstream statement that this report does not exist is superseded. [Google report](https://support.google.com/webmasters/answer/16984139).

Google retired FAQ rich results in May 2026. HowTo rich results and the sitelinks search box are also retired appearances. Matching Schema.org vocabulary can still serve an identified supported consumer. [Google updates](https://developers.google.com/search/updates).

For same-language regional duplicates, choose the intended preferred canonical and align localized relationships. Distinct translations require appropriate identities. The default locale can have an unprefixed URL under a consistent declared strategy. Apply index controls to the actual content and intent. [Google regional sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites).

Keep proposed machine formats and browser protocols conditional on the real workflow, consumer, implementation and current vendor contract. Preserve the actual audit mode and denominator. [Google AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [Chrome Agentic Browsing scoring](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring).

Review examples through the project's existing action authority. Installing a source package does not establish a working collector, account access, accepted publication or traffic.

The [reviewed rule ledger](reviewed-rules.json) records each adapted procedure and input, its effective criterion IDs, exact pinned source files/line ranges and separate official qualifications. Source inspection is distinct from tool execution.

The separately pinned SEO Cockpit companion has complete static reading coverage for 22 files and eight owning dependencies, including verified reuse of two identical dependency blobs; fifteen source-qualified cases are integrated into existing cost, metric, identity, performance and host checks. [Companion contracts](source-runtime-review.md#separately-pinned-seo-cockpit-companion).
