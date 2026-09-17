#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseDocument } from "yaml";

// Synchronized with the public https://api.provod.ai/mcp tools/list contract.
export const HOSTED_MCP_TOOL_NAMES = Object.freeze([
  "models_explore",
  "generate_image",
  "generate_video",
  "generate_image_batch",
  "generate_video_batch",
  "show_generations",
  "job_status",
  "job_display",
  "jobs_wait",
  "show_generation_by_ids",
  "media_upload",
  "media_import_url",
  "media_confirm",
  "media_upload_widget",
  "show_medias",
  "balance",
  "transactions",
  "list_workspaces",
  "show_plans_and_credits",
  "confirm_billing_purchase",
]);

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const skillRoot = path.join(root, "skills");
const requiredSkills = ["provod-mcp", "provod-media", "provod-provider"];
const requiredFields = ["name", "description", "version", "author", "license", "platforms", "metadata"];
const allowedTopLevelFields = new Set(requiredFields);

function fail(message) {
  throw new Error(message);
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function parseFrontmatter(content, relativePath) {
  if (!content.startsWith("---\n")) fail(`${relativePath}: frontmatter must start at byte 0`);
  const end = content.indexOf("\n---\n", 4);
  if (end < 0) fail(`${relativePath}: frontmatter is not closed`);
  const raw = content.slice(4, end);
  const document = parseDocument(raw, { strict: true, uniqueKeys: true });
  if (document.errors.length || document.warnings.length) {
    fail(`${relativePath}: invalid YAML frontmatter: ${[...document.errors, ...document.warnings][0].message}`);
  }
  const data = document.toJS();
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    fail(`${relativePath}: frontmatter must be a YAML mapping`);
  }
  for (const key of Object.keys(data)) {
    if (!allowedTopLevelFields.has(key)) fail(`${relativePath}: unknown frontmatter field ${key}`);
  }
  for (const field of requiredFields) {
    if (!Object.hasOwn(data, field)) fail(`${relativePath}: missing frontmatter field ${field}`);
  }
  if (!content.slice(end + 5).trim()) fail(`${relativePath}: body is empty`);
  for (const field of ["name", "description", "version", "author", "license"]) {
    if (typeof data[field] !== "string") fail(`${relativePath}: ${field} must be a string`);
  }
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(data.name)) fail(`${relativePath}: invalid skill name`);
  if (!/^\d+\.\d+\.\d+$/.test(data.version)) fail(`${relativePath}: version must be semver`);
  if (!data.description.startsWith("Use when ") || !data.description.endsWith(".")) {
    fail(`${relativePath}: description must be a trigger sentence`);
  }
  if (data.description.length > 60) fail(`${relativePath}: description exceeds 60 characters`);
  if (!Array.isArray(data.platforms) || !data.platforms.length || data.platforms.some((value) => typeof value !== "string")) {
    fail(`${relativePath}: platforms must be a non-empty inline list`);
  }
  if (
    !data.metadata ||
    typeof data.metadata !== "object" ||
    Array.isArray(data.metadata) ||
    JSON.stringify(Object.keys(data.metadata)) !== JSON.stringify(["hermes"]) ||
    !data.metadata.hermes ||
    typeof data.metadata.hermes !== "object" ||
    Array.isArray(data.metadata.hermes) ||
    JSON.stringify(Object.keys(data.metadata.hermes)) !== JSON.stringify(["tags", "related_skills"]) ||
    !Array.isArray(data.metadata.hermes.tags) ||
    !data.metadata.hermes.tags.length ||
    data.metadata.hermes.tags.some((value) => typeof value !== "string") ||
    !Array.isArray(data.metadata.hermes.related_skills) ||
    data.metadata.hermes.related_skills.some((value) => typeof value !== "string")
  ) {
    fail(`${relativePath}: invalid metadata.hermes frontmatter`);
  }
  return data;
}

function validateLinks(content, sourcePath) {
  for (const match of content.matchAll(/(?<!!)\[[^\]]+\]\(([^)]+)\)/g)) {
    const target = match[1].trim().split("#", 1)[0];
    if (!target || /^(?:https?:|mailto:)/i.test(target)) continue;
    if (path.isAbsolute(target) || target.includes("\\")) fail(`${sourcePath}: link must be relative: ${target}`);
    const resolved = path.resolve(path.dirname(path.join(root, sourcePath)), decodeURIComponent(target));
    if (!resolved.startsWith(`${root}${path.sep}`) || !existsSync(resolved)) {
      fail(`${sourcePath}: broken relative link: ${target}`);
    }
  }
}

function validateNoSecrets(content, sourcePath) {
  const patterns = [
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
    /\bghp_[A-Za-z0-9]{20,}\b/,
    /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
    /\bAKIA[A-Z0-9]{16}\b/,
    /\bsk-[A-Za-z0-9]{20,}\b/,
    /\bxox[baprs]-[A-Za-z0-9-]{20,}\b/,
    /\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|secret)\b\s*[:=]\s*["']?[A-Za-z0-9_./+=-]{16,}/i,
    /\b(?:npm|pypi)-[A-Za-z0-9_-]{20,}\b/,
    /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b/,
    /https?:\/\/[^\s/:]+:[^\s/@]+@/,
  ];
  if (patterns.some((pattern) => pattern.test(content))) fail(`${sourcePath}: possible secret detected`);
}

function validateNoStaticModels(content, sourcePath) {
  if (/^#{1,6}\s+.*\bmodels?\s*$/im.test(content)) {
    fail(`${sourcePath}: static model list heading is forbidden`);
  }
  if (/recommendedModels\s*[:=]/.test(content)) fail(`${sourcePath}: static recommendedModels is forbidden`);
  if (/^\s*[-*]\s+`?[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*`?\s*$/im.test(content)) {
    fail(`${sourcePath}: static model-like bullet catalog is forbidden`);
  }
}

function listFiles(relativeDirectory) {
  const absoluteDirectory = path.join(root, relativeDirectory);
  if (!existsSync(absoluteDirectory)) return [];

  return readdirSync(absoluteDirectory, { withFileTypes: true })
    .filter((entry) => ![".git", "node_modules"].includes(entry.name))
    .sort((left, right) => left.name.localeCompare(right.name))
    .flatMap((entry) => {
      const relativePath = path.posix.join(relativeDirectory, entry.name);

      return entry.isDirectory() ? listFiles(relativePath) : [relativePath];
    });
}

function loadSkills() {
  const directories = readdirSync(skillRoot)
    .filter((entry) => statSync(path.join(skillRoot, entry)).isDirectory())
    .sort();
  if (JSON.stringify(directories) !== JSON.stringify(requiredSkills)) {
    fail(`skills directory must contain exactly: ${requiredSkills.join(", ")}`);
  }

  const seen = new Set();
  return directories.map((directory) => {
    const relativePath = `skills/${directory}/SKILL.md`;
    const absolutePath = path.join(root, relativePath);
    if (!existsSync(absolutePath)) fail(`${relativePath}: missing canonical skill`);
    const bytes = readFileSync(absolutePath);
    const content = bytes.toString("utf8");
    const metadata = parseFrontmatter(content, relativePath);
    if (metadata.name !== directory) fail(`${relativePath}: name must match its directory`);
    if (seen.has(metadata.name)) fail(`${relativePath}: duplicate skill name ${metadata.name}`);
    seen.add(metadata.name);
    validateLinks(content, relativePath);
    validateNoSecrets(content, relativePath);
    validateNoStaticModels(content, relativePath);
    return { ...metadata, bytes, content, path: relativePath };
  });
}

function validateToolContract(skills) {
  const mcp = skills.find((skill) => skill.name === "provod-mcp");
  const routingSection = mcp.content.match(/## Tool Routing\n([\s\S]*?)\n## Procedure/)?.[1];
  if (!routingSection) fail("provod-mcp: missing Tool Routing section");
  const routed = [...routingSection.matchAll(/`([a-z][a-z0-9_]+)`/g)].map((match) => match[1]);
  const unique = [...new Set(routed)];
  if (JSON.stringify(unique) !== JSON.stringify(HOSTED_MCP_TOOL_NAMES)) {
    fail("provod-mcp: routed tools must equal the hosted MCP manifest in canonical order");
  }

  for (const skill of skills) {
    for (const match of skill.content.matchAll(/`([a-z][a-z0-9_-]+)`/g)) {
      const name = match[1];
      if (!HOSTED_MCP_TOOL_NAMES.includes(name)) {
        fail(`${skill.path}: unknown MCP-style tool name ${name}`);
      }
    }
  }
}

function buildIndex(skills) {
  const version = JSON.parse(readFileSync(path.join(root, "package.json"), "utf8")).version;
  return `${JSON.stringify(
    {
      schemaVersion: 1,
      version,
      skills: skills.map((skill) => ({
        name: skill.name,
        description: skill.description,
        path: skill.path,
        sha256: sha256(skill.bytes),
      })),
    },
    null,
    2,
  )}\n`;
}

export function validate({ writeIndex = false } = {}) {
  const releaseFiles = listFiles(".");
  for (const relativePath of releaseFiles) {
    const absolutePath = path.join(root, relativePath);
    if (!existsSync(absolutePath)) continue;
    const content = readFileSync(absolutePath, "utf8");
    validateNoSecrets(content, relativePath);
  }
  for (const relativePath of ["README.md", "LICENSE"]) {
    validateLinks(readFileSync(path.join(root, relativePath), "utf8"), relativePath);
  }
  const skills = loadSkills();
  validateToolContract(skills);
  const expectedIndex = buildIndex(skills);
  const indexPath = path.join(root, "index.json");
  if (writeIndex) writeFileSync(indexPath, expectedIndex);
  if (!existsSync(indexPath) || readFileSync(indexPath, "utf8") !== expectedIndex) {
    fail("index.json is stale; run npm run build:index");
  }
  validateNoSecrets(expectedIndex, "index.json");
  return { indexSha256: sha256(Buffer.from(expectedIndex)), skillCount: skills.length };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  try {
    const result = validate({ writeIndex: process.argv.includes("--write-index") });
    console.log(`Validated ${result.skillCount} skills and ${HOSTED_MCP_TOOL_NAMES.length} MCP tools.`);
    console.log(`index.json sha256 ${result.indexSha256}`);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
