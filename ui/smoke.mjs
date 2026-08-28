/* Render every screen against a stub DOM and fail on the first thrown error or leaked field.
 *
 *   node ui/smoke.mjs
 *
 * There is no bundler, no test runner and no jsdom here on purpose -- the UI is static files and
 * its check should not need more infrastructure than the UI itself. What this catches is the class
 * of bug that `node --check` cannot: a route that throws, a field renamed in `case_record()` that
 * the page still reads, an unescaped quote reaching innerHTML, an answer-key field in a fixture.
 *
 * The stub is deliberately just rich enough for the two screens that build DOM nodes rather than
 * innerHTML (the live board moves rows by transform, which needs real element objects). Timers
 * are stubbed to no-ops, so the stream player paints its first frame and stops -- deterministic,
 * and no interval outlives the process.
 *
 * `tests/test_ui.py` runs this, so it is part of `uv run pytest` when node is on PATH.
 */

import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const UI = dirname(fileURLToPath(import.meta.url));
const failures = [];

function element() {
  const el = {
    innerHTML: "",
    textContent: "",
    className: "",
    tabIndex: 0,
    style: {},
    children: [],
    onclick: null,
    oninput: null,
    focus() {},
    addEventListener() {},
    getAttribute() {
      return "0";
    },
    setAttribute() {},
    appendChild(child) {
      this.children.push(child);
      return child;
    },
    removeChild(child) {
      this.children = this.children.filter((c) => c !== child);
      return child;
    },
    insertBefore(child) {
      this.children.unshift(child);
      return child;
    },
    querySelector() {
      return null;
    },
    querySelectorAll() {
      return [];
    },
  };
  return el;
}

/* Memoised by id, so `player.nodes.board` is the same node across paints -- otherwise the board's
 * appendChild/removeChild bookkeeping is checking a different element every frame and a real
 * "removed a node that is not a child" bug would not surface here. */
const nodes = {};
function byId(id) {
  if (!nodes[id]) nodes[id] = element();
  return nodes[id];
}

const context = {
  window: {
    addEventListener() {},
    scrollTo() {},
  },
  document: {
    getElementById: byId,
    createElement() {
      return element();
    },
  },
  location: { hash: "", protocol: "file:", replace(h) { context.location.hash = h; } },
  URLSearchParams,
  console,
  // No-ops: the player schedules its next frame through these, and a smoke run wants exactly one
  // painted frame per route rather than a timer racing the assertions.
  setTimeout() { return 0; },
  clearTimeout() {},
  XMLHttpRequest: function () {
    return { open() {}, send() { throw new Error("no server under file://"); } };
  },
};
context.window.location = context.location;
context.globalThis = context;

vm.createContext(context);
for (const file of ["util.js", "data.js", "stream.js", "live.js"]) {
  const path = join(UI, file);
  if (!existsSync(path)) {
    console.error(`smoke: ui/${file} is missing. Build it:`);
    console.error(
      file === "stream.js"
        ? "  uv run earshot stream --tenant all && uv run python tools/stream_fixture.py"
        : "  uv run python tools/ui_fixture.py"
    );
    process.exit(1);
  }
  vm.runInContext(readFileSync(path, "utf8"), context);
}

const data = context.window.EARSHOT_DATA;
const stream = context.window.EARSHOT_STREAM;
if (!data) {
  console.error("smoke: ui/data.js did not set window.EARSHOT_DATA");
  process.exit(1);
}
if (!stream || !stream.tenants || !stream.tenants.length) {
  console.error("smoke: ui/stream.js did not set window.EARSHOT_STREAM with tenants");
  process.exit(1);
}

// Routes worth rendering: the reviewer screens over the recorded investigate run, the two demo
// screens over each streamed tenant, a streamed case and its retro, and several that must degrade
// to "not found" rather than throwing.
const caseId = data.queue.cases[0].case_id;
const evidence = data.cases[caseId].evidence[0];
const routes = [
  "#/",
  "#/portfolio",
  "#/queue",
  `#/case/${caseId}`,
  `#/case/${caseId}/retro`,
  `#/conversation/${evidence.conversation_id}?case=${caseId}&turn=${evidence.turn_index}`,
  "#/case/NO-SUCH-CASE",
  "#/conversation/NO-SUCH-CONVERSATION",
  "#/stream",
  "#/stream/NO-SUCH-TENANT",
  "#/no-such-screen",
];

for (const block of stream.tenants) {
  const tid = block.tenant.tenant_id;
  routes.push(`#/stream/${tid}`);
  const streamCaseId = Object.keys(block.cases)[0];
  if (streamCaseId) {
    const row = (block.cases[streamCaseId].evidence || [])[0];
    routes.push(`#/stream/${tid}/case/${streamCaseId}`);
    routes.push(`#/stream/${tid}/case/${streamCaseId}/retro`);
    if (row) {
      routes.push(
        `#/stream/${tid}/conversation/${row.conversation_id}` +
          `?case=${streamCaseId}&turn=${row.turn_index}`
      );
    }
  } else {
    failures.push(`${tid}: streamed no cases, so the demo has no verdict to show`);
  }
}

for (const hash of routes) {
  context.location.hash = hash;
  for (const id of Object.keys(nodes)) nodes[id].innerHTML = "";
  try {
    // Re-running app.js re-enters its IIFE, which routes on the current hash. Cheap, and it also
    // proves the script is safe to evaluate more than once.
    vm.runInContext(readFileSync(join(UI, "app.js"), "utf8"), context);
  } catch (err) {
    failures.push(`${hash}: threw ${err.message}`);
    continue;
  }
  // The stream screen builds its panels into child nodes rather than into #view, so check both.
  const html =
    nodes.view.innerHTML +
    Object.keys(nodes)
      .filter((id) => id !== "view")
      .map((id) => nodes[id].innerHTML)
      .join("");
  if (!html || html.length < 40) failures.push(`${hash}: rendered ${html.length} chars`);
  if (/undefined|\[object Object\]|NaN/.test(html)) {
    const hit = html.match(/.{0,60}(undefined|\[object Object\]|NaN).{0,60}/)[0];
    failures.push(`${hash}: rendered a placeholder value -> ...${hit}...`);
  }
}

// Answer-key discipline, checked at the last possible moment: what is actually in the browser.
// Both fixtures, because the stream one is newer and is exactly where "just the stratum, for
// colour" would be added one day.
const ANSWER_KEY = [
  "stratum",
  "outcome",
  "latent_risk",
  "financial_state",
  "seeded",
  "lead_days",
  "trajectory",
];
for (const [name, blob] of [["data.js", data], ["stream.js", stream]]) {
  const serialized = JSON.stringify(blob);
  for (const field of ANSWER_KEY) {
    if (new RegExp(`"${field}"`).test(serialized)) {
      failures.push(`answer-key field in ${name}: ${field}`);
    }
  }
}

// Every cited conversation must be readable, or "read in context" is a dead link.
for (const [id, one] of Object.entries(data.cases)) {
  for (const row of one.evidence || []) {
    if (!data.conversations[row.conversation_id]) {
      failures.push(`${id} cites ${row.conversation_id}, which has no transcript`);
    }
  }
}

for (const block of stream.tenants) {
  const tid = block.tenant.tenant_id;
  for (const [id, one] of Object.entries(block.cases)) {
    for (const row of one.evidence || []) {
      if (!block.conversations[row.conversation_id]) {
        failures.push(`${tid}/${id} cites ${row.conversation_id}, which has no transcript`);
      }
    }
  }
  // Every frame the player will paint must have a transcript behind it: the call panel renders
  // the arriving conversation turn by turn, and a missing one is a blank panel, not an error.
  for (const frame of block.frames) {
    if (!block.conversations[frame.conversation_id]) {
      failures.push(`${tid}: frame ${frame.i} has no transcript for ${frame.conversation_id}`);
      break;
    }
  }
  // The disclosure is a fact about the build, so it is asserted rather than trusted.
  if (block.manifest.asr !== "none") {
    failures.push(`${tid}: manifest.asr is ${block.manifest.asr}, expected "none"`);
  }
}

if (failures.length) {
  console.error("smoke FAILED:");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
const frames = stream.tenants.reduce((n, b) => n + b.frames.length, 0);
console.log(
  `smoke OK: ${routes.length} routes, ${data.queue.count} recorded cases, ` +
    `${stream.tenants.length} tenants, ${frames} stream frames`
);
