# Content quality, repetition and natural editing

Use for editorial briefs, factual review, «тошнота», keyword repetition, readability, and “de-AI” editing. The result is useful, accurate prose for a particular reader. Never promise detector evasion, a ranking threshold, or an “AI-undetectable” percentage. Sources checked 2026-11-01; no text-analysis service or editing integration was run during package research.

## Start with the actual text

Obtain the draft or exact page extract, language and locale, intended reader, search intent, product facts, primary sources, brand voice, and desired next action. Separate body copy from navigation, disclaimers, code and quotations before comparing statistics; retain the extraction boundaries. Preserve an immutable original and its source/date. Start in English worldwide where the project brief applies; Russian terminology does not make the content campaign Russian.

If the draft is missing, produce a brief first: reader question; useful answer or deliverable; supported claims and evidence; outline; examples requiring real inputs; internal-link destinations; title/description candidates; and next action. Word count follows the answer's needs. Do not expand a thin idea to meet an arbitrary length. Google's [people-first evaluation](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) emphasizes useful original contributions, clear sourcing and factual accuracy.

## One bounded editorial pass

1. **Map claims.** List names, numbers, dates, prices, comparisons, quotations, product capabilities and causal claims with their source passages. Mark unsupported or stale claims. Preserve uncertainty and conditions; a stylistic rewrite must not turn an estimate into an observed result.
2. **Diagnose the reader's problem.** Flag unanswered questions, duplicate sections, repetitive sentence openings, vague superlatives, unnecessary throat-clearing, unnatural query insertions and confusing terminology. Keep necessary repetition in specifications, definitions, accessibility instructions and product names.
3. **Measure only with an available tool.** Prefer the project's existing configured linter or editor. Record version, language, extraction, rules and raw output. [textlint](https://github.com/textlint/textlint) is a ready local option for Markdown/plain text, but ships no rules: an installed executable without the appropriate rules is not an editorial check. Do not build a replacement text-analysis engine or upload unpublished material to an external service merely to fill a statistics field.
4. **Edit for meaning and voice.** Give the answer early, use concrete verbs, remove redundant claims, and vary rhythm where it improves comprehension. Preserve quotations, terminology, numerical meaning, links, code and structured data. Use the strongest selected model; a weaker model is not a “humanization” technique. The public [Humanizer skill](https://github.com/blader/humanizer) is an optional existing editing aid after source/version inspection, not a bundled or tested connector. Its output still requires the claim comparison.
5. **Compare and hand off.** Review the edited text against the original claim map and brief. Recheck any changed factual wording against its source. Re-run the same available diagnostics on the same extraction; explain remaining repetition rather than forcing a lower score.

## Interpret «тошнота» precisely

[Advego's classic definition](https://advego.com/v2/support/services/seo/1450/) is the square root of the occurrence count of the most frequent word, including its forms: nine occurrences give 3. It is not a percentage. Advego explicitly gives no universal recommended value and notes its dependence on text length. Do not label a different token counter “Advego classic” without matching its morphology rules.

[Advego's academic definition](https://advego.com/v2/support/services/seo/1451/) describes the density of frequently repeated words, expressed as a percentage, excluding stop words. That help page does not disclose a complete aggregation formula. Preserve the service's actual result and methodology label; do not invent an equation or equate it with the density of one keyword.

Keep distinct fields for word/character counts, frequent words, exact phrase repetition, tool-specific classic/academic values and readability when actually measured. Note tokenization, lemmatization and stop-word differences. No universal “below 3%” rule, detector score or vendor editorial range establishes Google/Bing/Yandex ranking eligibility. Synonym stuffing can harm precise technical prose. Google's [generative-content guidance](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) requires value and accuracy; mass generation without value can violate scaled-content policy regardless of how natural it sounds.

## Required output and failure limits

Deliver the edited text plus a compact fact diff: preserved claims, changed factual wording with sources, removals, unresolved claims and reviewer decisions. Include before/after diagnostics only when a tool actually ran; otherwise say `not measured`, with the exact missing dependency. Add an editorial handoff containing audience/locale, intent, final title/description, internal links, next action, source dates and review owner. Editing completion is separate from publication, indexing and acquired organic visits. Stop unsupported claims from entering publish-ready copy; retain a clearly marked draft when evidence is missing.
