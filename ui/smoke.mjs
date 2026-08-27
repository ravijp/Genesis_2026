/* Render every screen against a stub DOM and fail on the first thrown error or leaked field.
 *
 *   node ui/smoke.mjs
 *
 * There is no bundler, no test runner and no jsdom here on purpose -- the UI is three static files
 * and its check should not need more infrastructure than the UI itself. What this catches is the
 * class of bug that `node --check` cannot: a route that throws, a field renamed in `case_record()`
 * that the page still reads, an unescaped quote reaching innerHTML.
 *
 * `tests/test_ui.py` runs this, so it is part of `uv run pytest` when node is on PATH.
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const UI = dirname(fileURLToPath(import.meta.url));
const failures = [];

function element() {
  const el = {
    innerHTML: "",
    tabIndex: 0,
    focus() {},
    addEventListener() {},
    getAttribute() {
      return "CASE-1";
    },
    querySelectorAll() {
      return [];
    },
    setAttribute() {},
  };
  return el;
}

const nodes = { view: element(), crumbs: element(), provenance: element() };

const context = {
  window: {
    addEventListener() {},
    scrollTo() {},
  },
  document: {
    getElementById(id) {
      return nodes[id] || element();
    },
  },
  location: { hash: "" },
  URLSearchParams,
  console,
};
context.window.location = context.location;
context.globalThis = context;

vm.createContext(context);
vm.runInContext(readFileSync(join(UI, "data.js"), "utf8"), context);
const data = context.window.EARSHOT_DATA;
if (!data) {
  console.error("smoke: ui/data.js did not set window.EARSHOT_DATA");
  process.exit(1);
}

// Routes worth rendering: the queue, a case, its retro screen, a transcript, and two that must
// degrade to "not found" rather than throwing.
const caseId = data.queue.cases[0].case_id;
const evidence = data.cases[caseId].evidence[0];
const routes = [
  "#/queue",
  "#/",
  `#/case/${caseId}`,
  `#/case/${caseId}/retro`,
  `#/conversation/${evidence.conversation_id}?case=${caseId}&turn=${evidence.turn_index}`,
  "#/case/NO-SUCH-CASE",
  "#/conversation/NO-SUCH-CONVERSATION",
];

for (const hash of routes) {
  context.location.hash = hash;
  nodes.view.innerHTML = "";
  try {
    // Re-running app.js re-enters its IIFE, which routes on the current hash. Cheap, and it also
    // proves the script is safe to evaluate more than once.
    vm.runInContext(readFileSync(join(UI, "app.js"), "utf8"), context);
  } catch (err) {
    failures.push(`${hash}: threw ${err.message}`);
    continue;
  }
  const html = nodes.view.innerHTML;
  if (!html || html.length < 40) failures.push(`${hash}: rendered ${html.length} chars`);
  if (/undefined|\[object Object\]|NaN/.test(html)) {
    const hit = html.match(/.{0,60}(undefined|\[object Object\]|NaN).{0,60}/)[0];
    failures.push(`${hash}: rendered a placeholder value -> ...${hit}...`);
  }
}

// Answer-key discipline, checked at the last possible moment: what is actually in the browser.
const ANSWER_KEY = [
  "stratum",
  "outcome",
  "latent_risk",
  "financial_state",
  "seeded",
  "lead_days",
];
const serialized = JSON.stringify(data);
for (const field of ANSWER_KEY) {
  if (new RegExp(`"${field}"`).test(serialized)) failures.push(`answer-key field in data.js: ${field}`);
}

// Every cited conversation must be readable, or "read in context" is a dead link.
for (const [id, one] of Object.entries(data.cases)) {
  for (const row of one.evidence || []) {
    if (!data.conversations[row.conversation_id]) {
      failures.push(`${id} cites ${row.conversation_id}, which has no transcript`);
    }
  }
}

if (failures.length) {
  console.error("smoke FAILED:");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(`smoke OK: ${routes.length} routes, ${data.queue.count} cases, ` +
  `${Object.keys(data.conversations).length} transcripts`);
