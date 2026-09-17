import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const expectedTools = [
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
];

function run(cwd, ...args) {
  return execFileSync(process.execPath, args, { cwd, encoding: "utf8" });
}

function fixture() {
  const target = mkdtempSync(path.join(tmpdir(), "provod-skills-contract-"));
  for (const entry of [
    ".github",
    "README.md",
    "LICENSE",
    "package-lock.json",
    "package.json",
    "index.json",
    "scripts",
    "skills",
    "test",
  ]) {
    cpSync(path.join(root, entry), path.join(target, entry), { recursive: true });
  }
  if (existsSync(path.join(root, "node_modules"))) {
    symlinkSync(path.join(root, "node_modules"), path.join(target, "node_modules"), "dir");
  }
  return target;
}

function alter(cwd, relativePath, transform) {
  const target = path.join(cwd, relativePath);
  writeFileSync(target, transform(readFileSync(target, "utf8")));
}

function assertInvalid(cwd, message, args = ["--write-index"]) {
  const result = spawnSync(process.execPath, ["scripts/validate.mjs", ...args], {
    cwd,
    encoding: "utf8",
  });
  assert.equal(result.status, 1);
  assert.match(result.stderr, message);
}

test("validator accepts the complete release contract", () => {
  const output = run(root, "scripts/validate.mjs");
  assert.match(output, /Validated 3 skills and 20 MCP tools\./);
});

test("frontmatter fields are mandatory", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-provider/SKILL.md", (text) => text.replace(/^description:.*\n/m, ""));
  assertInvalid(cwd, /missing frontmatter field description/);
});

test("skill names are unique and match their directories", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-provider/SKILL.md", (text) =>
    text.replace("name: provod-provider", "name: provod-mcp"),
  );
  assertInvalid(cwd, /name must match its directory|duplicate skill name/);
});

test("relative links must resolve inside the repository", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-media/SKILL.md", (text) => `${text}\n[missing](../missing.md)\n`);
  assertInvalid(cwd, /broken relative link/);
});

test("secret-shaped content is rejected", () => {
  const cwd = fixture();
  const fakeSecret = ["ghp", "abcdefghijklmnopqrstuvwxyz123456"].join("_");
  alter(cwd, "skills/provod-media/SKILL.md", (text) => `${text}\n${fakeSecret}\n`);
  assertInvalid(cwd, /possible secret detected/);
});

test("secret validation covers workflow and release files", () => {
  const cwd = fixture();
  const fakeSecret = ["ghp", "abcdefghijklmnopqrstuvwxyz123456"].join("_");
  alter(cwd, ".github/workflows/release.yml", (text) => `${text}\n# ${fakeSecret}\n`);
  assertInvalid(cwd, /possible secret detected/);
});

test("static model lists are rejected", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-provider/SKILL.md", (text) => `${text}\n## Models\n\n- example/model-1\n`);
  assertInvalid(cwd, /static model list heading is forbidden/);
});

test("malformed or unknown frontmatter is rejected", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-provider/SKILL.md", (text) =>
    text.replace("license: MIT", "license: MIT\ninvalid_yaml: ["),
  );
  assertInvalid(cwd, /unknown frontmatter field|invalid (?:YAML )?frontmatter/);
});

test("syntactically malformed YAML frontmatter is rejected", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-provider/SKILL.md", (text) =>
    text.replace("author: provod.ai", "THIS IS NOT: [VALID\nauthor: provod.ai"),
  );
  assertInvalid(cwd, /frontmatter|yaml/i);
});

test("generic API keys are rejected", () => {
  const cwd = fixture();
  const genericSecret = ["api", "key"].join("_") + ' = "supersecretvalue123456789"';
  alter(cwd, ".github/workflows/validate.yml", (text) => `${text}\n# ${genericSecret}\n`);
  assertInvalid(cwd, /secret/i);
});

test("Slack-style tokens are rejected", () => {
  const cwd = fixture();
  const slackToken = ["xoxb", "123456789012", "abcdefghijklmnopqrstuvwx"].join("-");
  alter(cwd, ".github/workflows/validate.yml", (text) => `${text}\n# ${slackToken}\n`);
  assertInvalid(cwd, /secret/i);
});

test("model-like bullet catalogs are rejected under arbitrary headings", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-provider/SKILL.md", (text) =>
    `${text}\n## Available options\n\n- acme/image-v1\n`,
  );
  assertInvalid(cwd, /static model/i);
});

test("multipart confirmation documents every required argument", () => {
  const content = readFileSync(path.join(root, "skills/provod-media/SKILL.md"), "utf8");
  const payload = content.match(/Finish with `media_confirm`, supplying `(\{[^\n]+\})` for every/)?.[1];

  assert.ok(payload, "media_confirm example payload is required");
  assert.deepEqual(Object.keys(JSON.parse(payload)), ["media_id", "parts"]);
});

test("MCP routing uses the exact hosted tool manifest", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-mcp/SKILL.md", (text) => text.replace("`balance`", "`get_balance`"));
  assertInvalid(cwd, /routed tools must equal the hosted MCP manifest/);
});

test("unknown hyphenated tool-like names are rejected", () => {
  const cwd = fixture();
  alter(cwd, "skills/provod-media/SKILL.md", (text) => `${text}\nCall \`bogus-tool\`.\n`);
  assertInvalid(cwd, /unknown MCP-style tool name/);
});

test("index generation is byte-for-byte deterministic", () => {
  const before = readFileSync(path.join(root, "index.json"));
  run(root, "scripts/validate.mjs", "--write-index");
  const after = readFileSync(path.join(root, "index.json"));
  assert.deepEqual(after, before);
  assert.equal(after.at(-1), 10, "index must end with one newline");
});

test("a stale generated index is rejected", () => {
  const cwd = fixture();
  alter(cwd, "index.json", (text) => text.replace('"schemaVersion": 1', '"schemaVersion": 2'));
  assertInvalid(cwd, /index.json is stale/, []);
});

test("canonical MCP manifest contains the exact hosted tool names", async () => {
  const { HOSTED_MCP_TOOL_NAMES } = await import("../scripts/validate.mjs");
  assert.deepEqual(HOSTED_MCP_TOOL_NAMES, expectedTools);
});
