# Run the shared master on sites

Use this reference for a full audit, a new site, the same audit across brands or fleet missing work. The invoking native agent performs collection and judgment; the Python helper validates profiles/evidence and produces reports. An offline report or a list of actor prompts is an intermediate artifact.

## One request, actual execution

An owner can invoke the installed skill with:

> Use traf-seo-master to add this site and audit it with the full master. Reuse valid evidence, execute the permitted applicable checks, and return findings, fixes/readback where authorized, and exact missing inputs. Site: `<actual origin>`; project/source: `<actual selected root or locator>`.

For an enrolled portfolio:

> Use traf-seo-master on the enrolled sites. Include never-audited sites and gaps added by the current registry. Execute the permitted missing checks; retain account/time dependencies and prioritize the next useful work per site.

Derive known inputs from the selected brief, existing profiles and retained receipts. Do not make the owner repeat a questionnaire. A genuine missing target/account/authority is recorded precisely; it does not block unrelated permitted work.

## Resolve the site and full check universe

1. Read the selected project's latest instructions/brief and actual active source selector. Resolve the physical root and storage rules. Keep action authority separate from a technical capability or stored key.
2. Create or reuse `sites/<site-id>/profile.json` under that project using the shipped [profile](../assets/examples/site-audit/profile.json) and [empty-evidence](../assets/examples/site-audit/evidence.json) examples and current helper contract. These examples enroll an unknown fixture; empty evidence demonstrates missing work, not successful execution. Preserve stable site identity, canonical origins/aliases, explicit allowed targets, publisher/template families, actual locales/markets, input/account locators, scope and sampling policy. Keep credentials outside profiles. Unknown capabilities, property ownership and locales remain unknown; do not infer them from the brand or URL count.
3. Enumerate every record in [checks.json](checks.json), including machine, expert, account and longitudinal classes. Use the helper/local parsing to select relevant rows instead of loading the entire registry/graph into context. Evaluate each assertion's applicability, inputs, required facets, coverage and acceptance against this profile. Use the check's `source_provenance` and [source-coverage.json](source-coverage.json) for the relevant rules; load exact source excerpts when needed. A route or source count is not a count of executed checks.
4. Reuse retained evidence only when site, check revision, source/config/serving identity, target, facet, coverage and time/window match. Confirm the actual bytes against the recorded hashes. Reference existing heavy artifacts rather than copying or recollecting them to fill a new folder. Preserve historical/stale/failed results with their limits.

Every profile gets the same registry IDs. Site facts decide applicability and expanded target units, not whether a category is silently omitted. `not-applicable` needs a reason with evidence. Missing access, an absent collector, a failed fetch or an unknown product fact stays undetermined/blocked/unknown as appropriate. A representative sample cannot certify the unobserved inventory.

## Execute remaining permitted checks now

Select by the check's actual assertion and evidence facets, then use the mature tool already available in this host. Discover narrowly; do not assume a catalogue CLI, MCP or specialist is installed. Continue through independent work when one lane lacks access.

| Needed evidence | Native execution | Retain and limit |
|---|---|---|
| Source/configuration and inventory | Read the exact selected checkout/config and existing XML/URL inventory with available `git`, `rg` or read-only parsers. Compare the assertion with the implementation, not its README claim. | Source revision/tree, file/line or hash, actual counts and exclusions. Source output does not prove public serving. |
| Public status, headers, robots, sitemap, raw HTML/assets | Use available HTTP tooling such as `curl` for the bounded allowed URL set. Preserve redirect destinations, headers, body, timestamp, tool/version and failed results. Inspect actual returned content. | Effective target and coverage; avoid credential-bearing URLs. A request from this host does not establish genuine search-bot access. |
| Rendered HTML, interaction or visual behavior | Discover the current host's browser surface, navigate the actual allowed target, inspect DOM/visible screenshot and console, and exercise the relevant user path. | Raw versus rendered state, viewport, target/config and screenshot/console evidence. Browser availability alone is not an executed check. |
| Single-page lab performance | Reuse a matching retained Lighthouse receipt or run the existing `audit --url` adapter with a qualified executable; see [Performance](performance.md). | Raw report, version, conditions and receipt. Lab performance cannot pass field CWV, indexation or a whole-site coverage facet. |
| Demand, intent, useful differentiation, content truth and acquisition | Perform the check's expert method on exact query/URL/asset rows and source excerpts. Read real winners and misses, inspect the actual product/user task and conversion path, and explain the evidence-to-verdict inference. Use [Intelligence](intelligence.md), [Acquisition](acquisition.md) or the task route as needed. | Reviewed item IDs, source/date/market, comparison scope, falsifier and rationale. A source summary or an unsupported opinion is insufficient. Estimates remain estimates. |
| Search/analytics account or real engine state | Use an actually available authorized integration/export with the correct account, property, API family, quota and window. Read official flow before a new integration. | Property locator without secrets, filters, complete window/denominator and raw response/export. No access means unknown, never zero or not-applicable. |
| Longitudinal outcome | Read existing complete comparable periods with the check's required window. Reconcile acquisition to relevant visits/useful actions where available. | Actual dates, missing slices and denominators. A future window is pending work; no scheduler is created by this skill. |

The package ships a Lighthouse adapter, not a new crawler. Where a larger sitemap/log/crawl task truly needs another tool, inspect the relevant source/capability rows and use a qualified ready collector. The prior advertools, Octopus or gsccli source assessments are candidates, not proof of installation, authentication or runtime. Qualify only the smallest selected real input before adoption; preserve provider/account/purpose/cap and do not activate a service because it appears in the catalogue.

A bounded unauthenticated public capture can use the existing `curl` interface below. Replace paths/URL with the allowed profile target, use a fresh evidence directory on the approved storage, and record the command, UTC timestamp, version and result alongside these bytes. Inspect the final URL before following a destination outside the allowed origins; handle that hop explicitly. Do not add auth/cookies or turn this into an unbounded crawl.

```sh
curl --silent --show-error --max-time 30 --max-redirs 0 \
  --dump-header /actual/fresh-evidence/headers.txt \
  --output /actual/fresh-evidence/body.html \
  --write-out '%{http_code} %{url_effective}\n' \
  https://example.com/
```

Do not replay completed or UNKNOWN effects to “verify” them. Read retained receipts and reconcile the original operation. Read-only audit authority does not authorize index submissions, CMS publication, login/account changes, model/provider calls or source writes. New paid cap remains whatever the owner approved; for the current seo-traf work it is **$0**.

When parallel work helps, use bounded native collaborators with check IDs/revisions, selected site/run, owned output, exact allowed roots/targets, inputs/hashes, relevant source excerpts, expected evidence/acceptance and permission boundary. Preserve others' work and the selected strong model. Inspect each actual result before importing it. Packets do not replace execution and do not create another controller.

## Evidence import and missing work

Use the shipped profile/evidence examples and actual `--help` contract for JSON fields. The profile explicitly records `source_config_binding`: site identity, source kind/revision, config hash and serving origin/revision; unknown values stay null. An observation may use only the primary binding or an explicitly declared alternative in `source_config_bindings`, keeping local and public contexts separate. A profile hash alone does not establish a config/deployment revision. A file-based source proof uses `source: {kind: "files", revision: null, files_sha256: {"actual/path": "actual SHA256"}}`; retain the actual file bytes and hashes. Public HTTP facts need the bindings required by their assertion, usually site/origin, rather than an invented Git/deployment revision. File proof alone does not establish source-to-public equivalence.

The evidence manifest binds the site/profile hash, registry version and as-of time. Each artifact declares its hash, observation time, collector/version, target, exact source/config binding, scope, facets, coverage and limitations. Each observation names the canonical check ID/revision, target/scope, applicability, execution, verdict and artifact IDs with a reason; provenance aliases are not executable IDs. Account metrics/outcomes require complete dated intervals and the check's minimum window. A current account/property snapshot may instead declare `evidence_requirement.window_policy.mode: snapshot` in the check and `window: {complete: true, observed_at: <ISO UTC>}` in evidence; do not invent a one-day interval for it. Include matching fix readbacks where required. Required nonnull binding fields must be observed; do not infer them or invent a collector run to satisfy schema.

### Join the exact population and context

Typed checks declare `evidence_requirement.target_unit`, allowed `population_scope` values and an exact semantic `population_role`. Copy those strings from the actual check. The profile's `coverage_policy.contexts[context_id]` declares `scope` and one exact already-declared `source_config_binding`. Its `populations[population_ref]` declares `target_unit`, one `scope_kind`, `population_role`, `context_id`, positive `total`, `selection_basis`, actual hashed `provenance` and exactly one of `members` or `membership_manifest`.

Choose the scope honestly: `sitewide` covers the complete universe for that role; `declared-selection` proves only its frozen selected members; `named-resource` names an exact resource; `review-case` names a real question/decision. A review-case also needs nonempty `required_input_refs`, each with `id`, actual `path`, `sha256` and `purpose`; one report cannot replace missing substantive inputs. Freeze selection independently of the verdict. A retrospective selection remains labelled and cannot establish sitewide generality.

Artifact `coverage` joins by `population_ref` and `context_id`, then supplies `target_unit`, `mode`, `total`, `observed` and exactly one of `observed_members` or `observed_membership_manifest`. All required facets must join the same population/context/member set. The profile's member set supplies the denominator; artifact counts cannot declare it. `full` requires exact declared/observed set equality after duplicate rejection. A sample is a subset, including equality, subject to the check's existing minimum. Null totals, report-count `1`, equal counts with different members, or generic site-global units cannot satisfy a typed population. Legitimate resource/case `1` must name that actual resource/case and its provenance.

Both manifest fields use `{path, sha256, format, member_field}`. `json-members-v1` reads the dotpath to a simple array of unique nonempty string IDs; `csv-column-v1` reads one exact named CSV column. Relative paths resolve from the original profile/evidence JSON's directory, not a copied run directory. Retain that input base and hashes; edited/missing manifests or review inputs invalidate reuse. The same population/context must also survive aggregation and fix readback; another cohort cannot close the original failure.

This partial shape matches `seo-technical-crawl-robots-response` revision 2. Copy it into the corresponding existing profile/artifact objects, replacing the provenance path/hash with the actual retained selection record. The context binding must exactly equal a declared profile binding. It proves only the named robots resource, not a site's URL inventory.

```json
{
  "coverage_policy": {
    "contexts": {
      "public-production": {
        "scope": "public",
        "source_config_binding": {
          "site_id": "example-static",
          "source": {"kind": "unknown", "revision": null},
          "config_sha256": null,
          "serving": {"origin": "https://example.com", "revision": null}
        }
      }
    },
    "populations": {
      "public-robots-v1": {
        "target_unit": "resources",
        "scope_kind": "named-resource",
        "population_role": "named-robots-resource",
        "context_id": "public-production",
        "total": 1,
        "members": ["https://example.com/robots.txt"],
        "selection_basis": "The exact robots resource required by this check",
        "provenance": {"path": "ACTUAL_SELECTION_RECORD", "sha256": "ACTUAL_SHA256"}
      }
    }
  }
}
```

```json
{
  "coverage": {
    "population_ref": "public-robots-v1",
    "context_id": "public-production",
    "target_unit": "resources",
    "mode": "full",
    "total": 1,
    "observed": 1,
    "observed_members": ["https://example.com/robots.txt"]
  }
}
```

Keep distinct universes distinct: root-sitemap declared URLs differ from all eligible published URLs; known sitemap roots/children include unresolved or failed branches; local-candidate and production populations differ even at equal counts. A selected browser/model/sitemap case cannot pass a sitewide assertion. A known root inventory can omit separate blog branches. Verify complete eligible publication across all required sections. Sitemap canonical-membership work also needs the actual hashed eligible-published comparator and expert comparison; missing comparator evidence stays unknown.

### Prove a conditional check is not applicable

For `applicability: not-applicable`, prove the substantive domain condition false before positive-execution admission. `applicability_basis` must contain `condition_met: false`, `condition_statement` exactly equal to the current check's `applies_if.statement`, `reason_kind: domain-fact`, an existing exact `context_id`, and `artifact_ids` exactly equal to the observation's nonempty artifact IDs. It also needs `authority: {kind, complete: true, boundary}`, nonempty actual hashed `required_input_refs: [{id, path, sha256, purpose}]`, and `facts: [{artifact_id, locator, statement}]` citing every proof artifact. Authority kinds are `complete-owned-source`, `authoritative-owned-inventory` or `owning-product-contract`; the boundary names the actual closed version/scope.

Proof artifacts retain normal hash/date/site/target/scope/binding fields, use facet `applicability-fact`, and match the selected context. Their `coverage` may be `{}` for this applicability-only proof; do not fabricate positive assets. Empty coverage remains invalid for positive execution. `complete: true` alone is insufficient: every authority input must exist/hash-match, and native source/expert review must substantiate the cited false condition. A `files` source boundary must include every file's matching authority input.

An always check cannot be N/A. Missing accounts, data, inputs, runtime, collectors or windows do not prove a domain predicate false; copying `source_condition` or readiness does not substitute for it. Owned-source absence is limited to its immutable source/package context; unbound source absence cannot establish production absence. Existing freshness/conflict/no-replay guards remain. Valid N/A returns `execution: not-run`, `verdict: unknown` with explicit proof scope/date; it is neither a passed execution nor an observed-fixed transition. Invalid/incomplete applicability proof remains undetermined/unknown.

Run these from the target project using the actual package path. These commands are offline profile/report operations. Output directories must be fresh; examples use a stable site ID and a chosen run ID, not a new service or database. Set the as-of instant after the collected observations; do not reuse a historical example date for fresh evidence.

```sh
python3 /actual/package/scripts/seo-master.py site-add \
  --profile sites/example/profile.json \
  --out out/master-audits/example/registration-v1

audit_as_of_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 /actual/package/scripts/seo-master.py site-audit \
  --profile sites/example/profile.json \
  --evidence out/master-audits/example/evidence-v1.json \
  --out out/master-audits/example/run-v1 \
  --as-of "$audit_as_of_utc"

python3 /actual/package/scripts/seo-master.py site-missing \
  --run out/master-audits/example/run-v1

python3 /actual/package/scripts/seo-master.py site-missing --sites sites
```

`site-add` validates the supplied profile and emits the initial full check plan. It does not collect evidence. `site-audit` validates/imports the supplied evidence, writes an immutable full matrix/findings/missing/native handoffs and updates the hash-bound current-run pointer only after a valid import. `site-missing` accepts exactly one of `--run` or `--sites`. The fleet form considers every enrolled `*/profile.json`, including those with no run, and compares older results against the current registry so a new check cannot disappear behind an old report. A malformed profile, pointer, run or retained artifact produces that enrollment's explicit `status: error` disposition and a full unknown/error matrix; healthy and never-audited peers still receive their results. The aggregate status is `PARTIAL` with `error_count` and nonzero exit when any enrollment fails. Exit zero means the operation/report is valid, not that checks passed.

Before replacing a current pointer, the importer validates its retained run/history and carries governing unresolved failures, pending readback and effect receipts into an immutable `effective-evidence.json`. Its artifacts retain their original physical input bases, IDs and hashes; reusing an ID for different evidence rejects the import. `evidence.json` remains the exact new manifest. `history_runs` links hash-bound prior runs; corrupted history rejects import without changing the pointer. The effective evidence is also used by both missing-work report forms. Do not copy internal `_retained_*` metadata into a new manifest: it is reserved for validated history.

A newer dated healthy observation can coexist with an unresolved old failure. Only an explicit valid observed-fixed readback for the same check revision, target, scope, source/config binding, population and context supersedes that failure; changed profile/check/source contracts remain visible and cannot be cross-joined into a pass. Previous candidate details remain in immutable history while their governing failure is carried. UNKNOWN/possibly-sent receipts remain unresolved with `replay: false`; a normal fix readback cannot reconcile an uncertain external effect. Completed/sent receipts remain preserved without turning an expired former pass into a new failure.

Keep applicability (`applicable`, `not-applicable`, `undetermined`), execution (`not-run`, `completed`, `blocked`, `error`), verdict (`pass`, `fail`, `unknown`) and freshness (`current`, `dated`, `stale`, `binding-mismatch`, `unverified`) distinct. A failed executed check is useful evidence. A malformed/wrong-site/edited artifact cannot promote a pass; preserve it as a failure to import and correct the actual binding or evidence. Do not change a claimed outcome merely to make validation succeed.

For a qualified exact snapshot, the check's `expiry.basis` and `expiry.timeliness_policy.mode` may be `dated-snapshot` with no TTL. An actual complete account `window_policy.mode: snapshot` also admits only a dated verdict when the registry has no TTL and no qualified current policy. `freshness: dated` can verify the fact only at its recorded target/date/window; it does not claim the fact remains current. Report `dated_evidenced` separately from `current_evidenced`. The row's `temporal_scope.claim: recorded-date-only` preserves the audit as-of and supporting artifact/provider/window dates. A dated public HTTP observation can establish what that target returned then without claiming its Git revision or today's search rank. Required identity/scope/facet/coverage bindings still apply. Null TTL never means evergreen.

Use the actual underlying data dates: `observation.data_as_of`, the observation's interval end/snapshot date, `artifact.data_observed_at` or `artifact.data_window.end` when present. The oldest supporting date governs freshness; a new fetch/import cannot refresh an old SERP/rank/report window. Apart from the actual dated account-snapshot admission above, `current-required` evidence with null TTL and no qualified timeliness policy stays unverified/unknown. Do not invent a refresh interval or a qualification assertion to obtain a current pass. Immutable source/package facts may remain current only at their matching qualified content binding.

### Source/task-qualified timeliness and method windows

An optional profile `assessment_policies` object is keyed by policy ID; an observation selects one through `assessment_policy_id`. This is data for the existing validator, not a new registry, controller or scheduler. Each policy contains exact `check_id`, `check_revision`, `method` (equal to the full current check method), `scope`, `target`, `context_id`, `population_ref`, `source_config_binding`, a substantive `task`, and nonempty `authority_refs`. Each authority reference has `source_id`, `locator`, `criterion`, `path` and `sha256`. By default its `authority_kind` is `upstream-source` and its source ID must be one of this check's upstream sources. For an exact authorized owner/task criterion, use `authority_kind: task-instruction`, add the policy's real `task_id`, and make the reference source ID equal that task ID; the hashed file must be the actual instruction. The local source bytes must exist/hash-match and contain the exact quoted criterion. Cite the actual applicable source or authorized task instruction; never relabel a fixture, unrelated source or model assertion as policy authority. Authority files join the retained hashed input inventory.

A policy can specify `timeliness: {mode, data_basis, rationale, criterion}`. `mode` is `dated-snapshot` or `max-age`; `data_basis` must be `oldest-supporting-data`, and `criterion` must equal a quoted authority criterion. `max-age` additionally requires explicit positive finite `max_age_seconds` justified by that source/task. It fills an unspecified TTL; an existing stricter registry TTL still governs. A dated registry contract cannot become current through this field. An actual provider/data date remains authoritative even when retrieval is newer.

For a non-snapshot account/longitudinal observation, `window.complete: true` and a valid start/end still need actual method evidence. A registry `window_policy.mode: complete` with `min_window_days: null` imposes no numeric duration by itself. A `method-defined` window additionally needs policy `window: {mode, min_window_days, minimum_basis, rationale, acceptance_criteria}`. Its mode equals the registry mode; its nonempty acceptance criteria are exact quoted authority criteria. An explicit positive source/task minimum uses `minimum_basis: explicit-source-minimum`; a supported absence of a numeric minimum uses `min_window_days: null` and `minimum_basis: no-duration-minimum`. Neither can weaken an existing registry minimum.

The actual observation's `window.assessment` contains the exact current `method` and `acceptance`, a substantive native `rationale`, `input_results` in the exact order of every current check input, and `criteria`. Each input result contains its exact `input`, native `assessment`, and nonempty `data_refs: [{artifact_id, format: json-field-v1, locator, value_sha256}]`. The artifact must be selected by the observation. A locator is a dotted object-field path into the hashed JSON artifact; its value is a nonempty object or array of nonempty objects containing the actual method input data. `value_sha256` hashes UTF-8 JSON serialized with sorted keys, compact separators and ASCII escapes. Each input needs a distinct actual field; membership/provenance/fixture boilerplate alone cannot supply method data.

Each criterion contains `statement`, `result` (`pass`/`fail`), substantive native `rationale`, and `input_indices` linking the assessed input results. Statements exactly cover the policy criteria; their input indices collectively cover every check input. The observation's verdict must match those criterion results. Missing inputs, copied method text, a generic `qualified: true`, a cohort member list or an unbacked minimum cannot qualify a result. The validator verifies structure, exact bindings and evidence provenance; the native actor remains responsible for the semantic adequacy of the source/task policy and actual method assessment. A short complete window or validated native assessment alone never proves causality, target achievement or a traffic forecast.

Inspect `findings.md`, `missing.md` and their underlying rows. A dated pass remains visible in missing work because the current state is not established; preserve its historical verdict rather than converting it to a current pass or discarding it. Check unresolved facets, incomplete samples, absent inputs, source conflicts, stale/mismatched evidence and pending readback. Execute remaining authorized independent checks and import their real results into another fresh run. Reports and current-run pointers retain evidence; existing owning issues/memory retain current task context.

## Findings, fixes and return

Prioritize a finding by the affected real user/search path, severity, template/URL scope and evidence. Explain the assertion, observed deviation, exact target and bounded repair. Apply a fix only within current source ownership and authorization, then verify the same path. Preserve the original failure and distinguish source-changed, candidate-verified and observed-fixed. A local/source result cannot close a current-public facet; publication success cannot close indexation or traffic.

Return the real executed work, reused receipts with their limits, prioritized findings/fixes/readback, immutable run paths and precise unresolved dependencies. Include all/applicable/undetermined/current-evidenced/dated-evidenced/failed/unresolved denominators, sample coverage and latest source/serving identity. Keep historical-only findings distinct from unresolved current claims. Do not report a single all-SEO score, claim every discovered source was studied, or promise visits from a checklist. The next site must be addable through its profile and evidence without editing the master.
