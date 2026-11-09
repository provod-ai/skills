# One-prompt project setup

Give the agent the unpacked `traf-seo-master` folder and the existing target project. Paste this prompt with the actual package/project paths:

> Read `<package>/SKILL.md` and the target project's instructions. Install this package locally for the host you are actually running: Codex, Claude Code or Cursor. Use `python3 <package>/scripts/seo-master.py doctor`, then `install --host <actual-host> --project <actual-project> --dry-run`. Inspect the plan; within this authorized local setup, run the same install without `--dry-run` if there is no conflict. Preserve all owner files, auth, global settings, current model/account and existing task/memory tools. Do not install or activate catalogue tools/providers or incur charges. Verify installed bytes with doctor, then explain actual instruction/helper/tool/auth/runtime coverage and start the requested SEO task. For a site audit, follow `references/site-audits.md`: use the full master, execute permitted applicable checks with actual tools and expert review, import real evidence and return findings/missing inputs. Creating an offline plan is an intermediate step. If a dependency is unavailable, report that exact gap and continue the safe independent part; never invent metrics or claim traffic from successful installation.

The host/path values are user environment inputs, not literal directory names to create. No new project should be initialized just to install the skill.

After setup, a concrete audit invocation is: **“Use traf-seo-master to add `<actual site>` and audit it with the full master. Reuse valid receipts, execute permitted checks, and return findings, authorized fixes/readback and missing inputs.”** Supply an existing project/source locator when available. Profiles and retained evidence distinguish sites; the shared registry supplies the same check universe. For portfolio gaps, request `site-missing --sites <actual sites root>` and continue through the permitted native checks, including never-audited sites and newer-registry gaps.

| Host | Project skill destination | Invocation |
|---|---|---|
| Codex | `.agents/skills/traf-seo-master/` | `$traf-seo-master` or matching task |
| Claude Code | `.claude/skills/traf-seo-master/` | `/traf-seo-master` or matching task |
| Cursor | `.cursor/skills/traf-seo-master/` | `/` skill selector or matching task |

Project discovery paths are documented by [OpenAI](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills) and [Cursor](https://cursor.com/docs/context/skills). Filesystem layout/copy checks do not establish actual model/runtime/tool compatibility in every product, remote session or operating system. Other agents can read SKILL.md explicitly if they support filesystem access, but automatic discovery is not claimed for them. A prompt alone does not grant tools or account access.

If the host was launched from an umbrella or different repository, a project-local skill may not be discovered from the target folder. Select the actual target project or use the installed SKILL.md explicitly; do not modify unrelated shared roots/global settings merely to force the current session's palette. Verify discovery separately from byte-correct installation.

Python 3 runs the local helper. The core install and site profile/evidence/report commands are offline and do not bundle Node/Chrome/Lighthouse or paid API clients. Actual collection and expert work use the native host's available tools; missing account/time access remains explicit. The optional single-URL `audit` collector requires Node >=22.19, existing Chrome and the explicitly pinned Lighthouse13.6.0 CLI; see [performance](references/performance.md). Any dependency installation follows the current project storage/permission rules and current official source, outside the copy-only installer.

Public `assets/lighthouse/package.json` and `package-lock.json` preserve the qualified optional dependency tree. If that tool is needed and local dependency installation is within scope, copy these manifests into an approved tool/cache folder and run `npm ci --ignore-scripts --no-audit --no-fund --prefix <tool-folder> --cache <approved-cache>`. Provide the resulting actual executable path to the audit helper; no credentials or model provider are configured by this step. Do not download Chrome or write caches into another storage contour implicitly.

Identical existing installs are reusable. A differing target is a conflict; preserve it and inspect its managed/owner changes rather than forcing a replacement. Do not edit user AGENTS/CLAUDE rules, registry credentials, `.env`, MCP configuration or model settings during bootstrap. New tool/source versions need a new bounded qualification; the source catalogue does not auto-update execution.
