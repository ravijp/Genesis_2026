/* The colour gate. Renders every route, cascades the real stylesheets over the real markup, and
 * fails on any foreground/background pair the UI actually puts on screen that a person cannot
 * read.
 *
 *   node ui/contrast.mjs            # the table, and a non-zero exit if anything fails
 *   node ui/contrast.mjs --all      # print every pair, including the ones that pass
 *
 * WHY IT WORKS THIS WAY. "Sophisticated" is unfalsifiable and a hand-written list of colour pairs
 * is one forgotten line from a hole — the same failure mode as a hand-maintained list of files to
 * guard (working-agreements §6). So nothing here is listed. The routes come from the same set
 * `smoke.mjs` renders, the markup comes from running the actual application against a stub DOM,
 * the rules come from parsing the actual stylesheets, and the pairs fall out of a small cascade
 * over the two. Delete a token and this script reports fewer pairs; restyle a row and the pair
 * it produces changes with it.
 *
 * That cuts both ways, so the discovery is asserted: the run fails if it finds no pairs, if
 * either theme produces none, or if any of the SENTINELS below — the screens and controls this
 * product is judged on — stops appearing. A gate that would pass with the UI deleted is worse
 * than no gate.
 *
 * WHAT IT CHECKS.
 *   text   >= 4.5:1   body copy (WCAG 2.2 AA, 1.4.3)
 *   large  >= 3.0:1   >= 24px, or >= 18.66px and bold
 *   ui     >= 3.0:1   a border that identifies a control or a region (1.4.11)
 *   decor  reported   a hairline between rows of ONE surface, which identifies nothing. WCAG
 *                     1.4.11 is about component identification, and gating row rules at 3:1 turns
 *                     a dense table into a wireframe. The ratios are printed so the choice is
 *                     visible rather than hidden in a threshold.
 *
 * It also fails on `opacity` below 1 on anything carrying text. That is not a contrast rule, it
 * is this product's rule: a sub-threshold signal is retained and still readable, and dimming it
 * would draw the incumbent behaviour the whole entry inverts (D-030).
 *
 * BOTH THEMES, and the tenant override. `--accent` is re-pointed per deployment by an inline
 * style, so the accent this checks under `#/desk` is the hex in `stream.js`, not the default in
 * `styles.css` — which is the whole reason `--accent` never carries text.
 */

import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const UI = dirname(fileURLToPath(import.meta.url));
const SHOW_ALL = process.argv.includes("--all");
const SHEETS = ["styles.css", "demo.css", "console.css"];

/* Screens and controls whose colours are load-bearing. Each is a CSS class that must still be
 * found carrying text somewhere in the rendered set. They are not a list of what to CHECK —
 * everything is checked — they are a list of what must still EXIST, so this cannot go green by
 * discovering nothing. */
const SENTINELS = [
  "cns-standin",    // the permanent stand-in label
  "cns-illus",      // "Illustrative ... nobody decides here"
  "op-btn",         // the inert decision buttons
  "op-conf",        // confidence, always a number
  "op-table",       // the ledger
  "provenance",     // the always-on provenance banner
  "op-prov",        // our panel's own provenance footer
  "cns-qrow",       // a queue row
  "boardrow",       // a re-ranking board row
];

const failures = [];
const notes = [];

/* ================================================================= 1. CSS ==================== */

function stripComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, "");
}

/* Flatten a stylesheet into rules, remembering which @media each came from. Only two media
 * queries matter: the dark scheme (a second theme) and everything else (skipped — this checks the
 * desktop layout, and a narrow viewport changes padding, not colour). */
function parseSheet(css, file) {
  const src = stripComments(css);
  const rules = [];
  let i = 0;
  function block(end, media) {
    while (i < end) {
      const brace = src.indexOf("{", i);
      if (brace < 0 || brace >= end) break;
      const prelude = src.slice(i, brace).trim();
      // find the matching close brace
      let depth = 1;
      let j = brace + 1;
      while (j < src.length && depth > 0) {
        if (src[j] === "{") depth++;
        else if (src[j] === "}") depth--;
        j++;
      }
      const body = src.slice(brace + 1, j - 1);
      if (prelude.startsWith("@media")) {
        const dark = /prefers-color-scheme\s*:\s*dark/.test(prelude);
        const skip = /max-width|prefers-reduced-motion/.test(prelude);
        if (!skip) {
          const save = i;
          i = brace + 1;
          block(j - 1, dark ? "dark" : media);
          i = save;
        }
      } else if (prelude.startsWith("@")) {
        // @keyframes and friends: no cascade, no pairs.
      } else {
        for (const sel of prelude.split(",")) {
          const s = sel.trim();
          if (s) rules.push({ selector: s, decls: parseDecls(body), media, file, order: rules.length });
        }
      }
      i = j;
    }
  }
  block(src.length, null);
  return rules;
}

function parseDecls(body) {
  const out = [];
  let depth = 0, start = 0;
  for (let k = 0; k < body.length; k++) {
    const ch = body[k];
    if (ch === "(") depth++;
    else if (ch === ")") depth--;
    else if (ch === ";" && depth === 0) {
      push(body.slice(start, k));
      start = k + 1;
    }
  }
  push(body.slice(start));
  function push(chunk) {
    const t = chunk.trim();
    if (!t) return;
    const c = t.indexOf(":");
    if (c < 0) return;
    out.push([t.slice(0, c).trim(), t.slice(c + 1).trim()]);
  }
  return out;
}

const allRules = [];
for (const name of SHEETS) {
  const path = join(UI, name);
  if (!existsSync(path)) {
    console.error(`contrast: ui/${name} is missing`);
    process.exit(1);
  }
  for (const r of parseSheet(readFileSync(path, "utf8"), name)) {
    r.order = allRules.length;
    allRules.push(r);
  }
}

/* ---- selectors ------------------------------------------------------------------------------ */

const STATE_PSEUDOS = new Set(["hover", "focus", "focus-visible", "active", "visited"]);

function parseSelector(sel) {
  // ::before / ::after paint no text and get no pairs.
  if (sel.includes("::")) return null;
  const parts = sel.split(/\s*([> ])\s*/).filter((p) => p.trim() !== "");
  const steps = [];
  let combinator = null;
  let state = null;
  for (const part of parts) {
    if (part === ">" || part === " ") { combinator = part.trim() || " "; continue; }
    const compound = { tag: null, classes: [], id: null, weight: 0 };
    const re = /([.#]?)([A-Za-z0-9_-]+)|:{1,2}([A-Za-z-]+)(\([^)]*\))?/g;
    let m;
    while ((m = re.exec(part))) {
      if (m[3] !== undefined) {
        if (STATE_PSEUDOS.has(m[3])) state = m[3];
        compound.weight += 10;         // structural pseudos are ignored for matching, not for weight
      } else if (m[1] === ".") { compound.classes.push(m[2]); compound.weight += 10; }
      else if (m[1] === "#") { compound.id = m[2]; compound.weight += 100; }
      else { compound.tag = m[2].toLowerCase(); compound.weight += 1; }
    }
    steps.push({ compound, combinator });
    combinator = null;
  }
  if (!steps.length) return null;
  const weight = steps.reduce((n, s) => n + s.compound.weight, 0);
  return { steps, weight, state };
}

function matchesCompound(el, c) {
  if (c.tag && c.tag !== el.tag) return false;
  if (c.id && c.id !== el.id) return false;
  for (const cls of c.classes) if (!el.classes.includes(cls)) return false;
  return true;
}

function matches(el, parsed) {
  const steps = parsed.steps;
  if (!matchesCompound(el, steps[steps.length - 1].compound)) return false;
  let node = el;
  for (let k = steps.length - 2; k >= 0; k--) {
    const want = steps[k + 1].combinator === ">" ? "child" : "descendant";
    let cur = node.parent;
    if (want === "child") {
      if (!cur || !matchesCompound(cur, steps[k].compound)) return false;
      node = cur;
    } else {
      let found = null;
      while (cur) {
        if (matchesCompound(cur, steps[k].compound)) { found = cur; break; }
        cur = cur.parent;
      }
      if (!found) return false;
      node = found;
    }
  }
  return true;
}

for (const r of allRules) r.parsed = parseSelector(r.selector);

/* ================================================================= 2. colour ================== */

function hexToRgb(hex) {
  let h = hex.replace("#", "").trim();
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  return [0, 2, 4].map((k) => parseInt(h.slice(k, k + 2), 16));
}
function rgbToHex(rgb) {
  return "#" + rgb.map((v) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, "0")).join("");
}
function luminance(rgb) {
  const lin = rgb.map((v) => {
    const c = v / 255;
    return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
}
function contrast(a, b) {
  const la = luminance(a), lb = luminance(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}
function over(fg, bg) {
  // fg = {rgb, a}; bg = opaque rgb
  return fg.rgb.map((v, k) => v * fg.a + bg[k] * (1 - fg.a));
}

/* Resolve a CSS colour expression against an element's custom-property scope.
 * Returns { rgb, a, token } or null. `token` is the outermost --name, which is what the report
 * prints and what decides whether a border is a component boundary or a row rule. */
function colorOf(expr, props, depth = 0) {
  if (!expr || depth > 8) return null;
  const v = expr.trim();
  if (v === "transparent" || v === "none" || v === "inherit" || v === "currentColor") return null;

  let m = /^var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,\s*([\s\S]+))?\)$/.exec(v);
  if (m) {
    const raw = props[m[1]];
    const inner = raw !== undefined ? colorOf(raw, props, depth + 1) : (m[2] ? colorOf(m[2], props, depth + 1) : null);
    if (!inner) return null;
    return { ...inner, token: m[1] };
  }
  m = /^#[0-9a-fA-F]{3,8}$/.exec(v);
  if (m) {
    const h = v.replace("#", "");
    if (h.length === 8) return { rgb: hexToRgb("#" + h.slice(0, 6)), a: parseInt(h.slice(6, 8), 16) / 255, token: v };
    return { rgb: hexToRgb(v), a: 1, token: v };
  }
  m = /^rgba?\(([^)]+)\)$/.exec(v);
  if (m) {
    const n = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return { rgb: [n[0], n[1], n[2]], a: n.length > 3 ? n[3] : 1, token: v };
  }
  m = /^color-mix\(\s*in\s+srgb\s*,\s*([\s\S]+?)\s+([\d.]+)%\s*,\s*([\s\S]+?)\s*\)$/.exec(v);
  if (m) {
    const a = parseFloat(m[2]) / 100;
    const first = colorOf(m[1], props, depth + 1);
    const second = m[3].trim() === "transparent" ? null : colorOf(m[3], props, depth + 1);
    if (!first) return null;
    if (!second) return { rgb: first.rgb, a: first.a * a, token: first.token };
    return {
      rgb: first.rgb.map((c, k) => c * a + second.rgb[k] * (1 - a)),
      a: 1,
      token: first.token,
    };
  }
  const NAMED = { white: [255, 255, 255], black: [0, 0, 0], red: [255, 0, 0] };
  if (NAMED[v]) return { rgb: NAMED[v], a: 1, token: v };
  return null;
}

/* A `background:` or `border:` shorthand — pull the colour out of it. */
function colorFromShorthand(value, props) {
  const parts = value.match(/(var\((?:[^()]|\([^()]*\))*\)|color-mix\((?:[^()]|\([^()]*\))*\)|rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}|[A-Za-z-]+)/g) || [];
  for (const p of parts) {
    const c = colorOf(p, props);
    if (c) return c;
  }
  return null;
}

function lengthOf(expr, props, depth = 0) {
  if (!expr || depth > 6) return null;
  const v = expr.trim();
  const m = /^var\(\s*(--[A-Za-z0-9_-]+)\s*\)$/.exec(v);
  if (m) return props[m[1]] !== undefined ? lengthOf(props[m[1]], props, depth + 1) : null;
  const n = /^(-?[\d.]+)px$/.exec(v);
  return n ? parseFloat(n[1]) : null;
}

/* ================================================================= 3. render ================== */

/* The same stub DOM smoke.mjs uses, plus a tag name and a real parent link so the created nodes
 * (the live board's rows) can be put back where they belong in the tree. */
function makeContext() {
  const created = [];
  function element(tag) {
    const el = {
      tag: tag || "div",
      innerHTML: "", textContent: "", className: "", id: "", tabIndex: 0,
      style: {}, children: [], onclick: null, oninput: null,
      focus() {}, addEventListener() {},
      getAttribute() { return "0"; }, setAttribute() {},
      appendChild(child) { this.children.push(child); return child; },
      removeChild(child) { this.children = this.children.filter((c) => c !== child); return child; },
      insertBefore(child) { this.children.unshift(child); return child; },
      querySelector() { return null; }, querySelectorAll() { return []; },
    };
    created.push(el);
    return el;
  }
  const nodes = {};
  function byId(id) {
    if (!nodes[id]) { nodes[id] = element("div"); nodes[id].id = id; }
    return nodes[id];
  }
  const context = {
    window: { addEventListener() {}, scrollTo() {} },
    document: {
      getElementById: byId,
      createElement: (t) => element(t),
      querySelectorAll() { return []; },
      querySelector() { return null; },
    },
    location: { hash: "", protocol: "file:", replace(h) { context.location.hash = h; } },
    URLSearchParams, console,
    setTimeout() { return 0; }, clearTimeout() {},
    XMLHttpRequest: function () { return { open() {}, send() { throw new Error("no server"); } }; },
  };
  context.window.location = context.location;
  context.globalThis = context;
  vm.createContext(context);
  return { context, nodes };
}

const { context, nodes } = makeContext();
for (const file of ["util.js", "data.js", "stream.js", "live.js", "console.js"]) {
  const path = join(UI, file);
  if (!existsSync(path)) {
    console.error(`contrast: ui/${file} is missing — run the fixtures first (see ui/README.md)`);
    process.exit(1);
  }
  vm.runInContext(readFileSync(path, "utf8"), context);
}
const data = context.window.EARSHOT_DATA;
const stream = context.window.EARSHOT_STREAM;
if (!data || !stream) {
  console.error("contrast: ui/data.js or ui/stream.js did not load");
  process.exit(1);
}

/* The routes worth colouring: every distinct screen. Built from the fixtures rather than typed,
 * for the same reason smoke.mjs builds its own. */
const caseId = data.queue.cases[0].case_id;
const evidence = data.cases[caseId].evidence[0];
const block = stream.tenants[0];
const streamCaseId = Object.keys(block.cases)[0];
const routes = [
  "#/", "#/desk", "#/desk/call", "#/deployment", "#/portfolio", "#/queue", "#/stream",
  `#/stream/${block.tenant.tenant_id}`,
  `#/case/${encodeURIComponent(caseId)}`,
  `#/case/${encodeURIComponent(caseId)}/retro`,
  `#/conversation/${evidence.conversation_id}?case=${caseId}&turn=${evidence.turn_index}`,
  `#/desk/case/${encodeURIComponent(streamCaseId)}`,
  "#/desk/team/none",
  ...Object.keys(block.tenant.teams || {}).map((s) => `#/desk/team/${s}`),
];

/* ================================================================= 4. HTML ==================== */

const VOID = new Set(["br", "hr", "img", "input", "meta", "link", "source", "col", "wbr"]);

function parseHTML(html, root) {
  const stack = [root];
  const re = /<!--[\s\S]*?-->|<\/([a-zA-Z0-9-]+)\s*>|<([a-zA-Z0-9-]+)((?:"[^"]*"|'[^']*'|[^>"'])*?)(\/?)>|([^<]+)/g;
  let m;
  while ((m = re.exec(html))) {
    if (m[0].startsWith("<!--")) continue;
    if (m[1]) {
      if (stack.length > 1) stack.pop();
    } else if (m[2]) {
      const tag = m[2].toLowerCase();
      const attrs = m[3] || "";
      const cls = /class\s*=\s*"([^"]*)"/.exec(attrs);
      const id = /\bid\s*=\s*"([^"]*)"/.exec(attrs);
      const style = /style\s*=\s*"([^"]*)"/.exec(attrs);
      const node = {
        tag,
        classes: cls ? cls[1].split(/\s+/).filter(Boolean) : [],
        id: id ? id[1] : "",
        inline: style ? parseDecls(style[1]) : [],
        children: [],
        text: "",
        parent: stack[stack.length - 1],
      };
      node.parent.children.push(node);
      if (!VOID.has(tag) && !m[4]) stack.push(node);
    } else if (m[5]) {
      const t = m[5].replace(/&[a-z]+;|&#\d+;/g, "x").trim();
      if (t) stack[stack.length - 1].text += t;
    }
  }
  return root;
}

/* Put each stub node's markup back under the element that carries its id, so a row the player
 * created with `document.createElement` is coloured inside the panel it actually lives in. */
function attach(node, tree) {
  const host = findById(tree, node.id) || tree;
  parseHTML(node.innerHTML, host);
  for (const child of node.children) {
    const el = {
      tag: child.tag,
      classes: (child.className || "").split(/\s+/).filter(Boolean),
      id: child.id || "",
      inline: [],
      children: [],
      text: "",
      parent: host,
    };
    host.children.push(el);
    parseHTML(child.innerHTML, el);
  }
}
function findById(node, id) {
  if (!id) return null;
  if (node.id === id) return node;
  for (const c of node.children) {
    const hit = findById(c, id);
    if (hit) return hit;
  }
  return null;
}

/* The static shell in index.html is part of every screen and carries the provenance banner, so it
 * is read from the file rather than assumed. */
const shellHtml = readFileSync(join(UI, "index.html"), "utf8");
const shellBody = shellHtml.slice(shellHtml.indexOf("<body>") + 6, shellHtml.indexOf("</body>"));

function renderTree(hash) {
  context.location.hash = hash;
  for (const id of Object.keys(nodes)) { nodes[id].innerHTML = ""; nodes[id].children = []; }
  vm.runInContext(readFileSync(join(UI, "app.js"), "utf8"), context);
  /* The stream's first frame has an empty ledger, so the board — the one screen where a row is
     coloured by whether it crossed — paints nothing until conversations have arrived. Scrub it
     forward through its own control, exactly as a viewer would, so those rows are real markup
     rather than a screen this gate never sees. */
  if (/^#\/stream\/[^/]+$/.test(hash) && nodes.scrub && typeof nodes.scrub.oninput === "function") {
    nodes.scrub.oninput({ target: { value: 80 } });
  }
  const root = { tag: "body", classes: [], id: "", inline: [], children: [], text: "", parent: null };
  parseHTML(shellBody, root);
  for (const id of Object.keys(nodes)) attach(nodes[id], root);
  return root;
}

/* ================================================================= 5. cascade ================= */

const INHERITED_PROPS = ["color", "font-size", "font-weight", "font-family"];

function computed(el, theme, parentComputed, parentProps) {
  const own = { props: { ...parentProps }, style: {} };
  const hits = [];
  for (const r of allRules) {
    if (!r.parsed) continue;
    if (r.media === "dark" && theme !== "dark") continue;
    if (r.media === "dark" && theme === "dark") { /* applies */ }
    if (r.parsed.state) continue;                      // states handled separately
    // `:root` seeds the document once, in `walk`. Re-applying it per element would let it
    // overwrite an inherited custom property — which is exactly how the tenant's inline
    // `--accent` silently stopped reaching this gate the first time it was written.
    if (r.selector === ":root") continue;
    if (matches(el, r.parsed)) hits.push(r);
  }
  hits.sort((a, b) => (a.parsed ? a.parsed.weight : 0) - (b.parsed ? b.parsed.weight : 0) || a.order - b.order);
  for (const r of hits) {
    for (const [prop, value] of r.decls) {
      if (prop.startsWith("--")) own.props[prop] = value;
      else own.style[prop] = value;
    }
  }
  for (const [prop, value] of el.inline) {
    if (prop.startsWith("--")) own.props[prop] = value;
    else own.style[prop] = value;
  }
  // inheritance
  own.inherited = {};
  for (const p of INHERITED_PROPS) {
    own.inherited[p] = own.style[p] !== undefined ? own.style[p] : (parentComputed ? parentComputed.inherited[p] : undefined);
  }
  own.rules = hits;
  return own;
}

/* The hover/focus variants of the rules that matched this element, so a hover fill is checked
 * against the text sitting on it rather than assumed harmless. */
function stateOverlays(el, theme) {
  const out = {};
  for (const r of allRules) {
    if (!r.parsed || !r.parsed.state) continue;
    if (r.media === "dark" && theme !== "dark") continue;
    if (!matches(el, r.parsed)) continue;
    out[r.parsed.state] = out[r.parsed.state] || {};
    for (const [prop, value] of r.decls) if (!prop.startsWith("--")) out[r.parsed.state][prop] = value;
  }
  return out;
}

function backgroundOf(style, props) {
  if (style["background-color"] !== undefined) return colorOf(style["background-color"], props) || colorFromShorthand(style["background-color"], props);
  if (style["background"] !== undefined) return colorFromShorthand(style["background"], props);
  return null;
}

const BORDER_PROPS = [
  "border", "border-color", "border-top", "border-right", "border-bottom", "border-left",
  "border-top-color", "border-right-color", "border-bottom-color", "border-left-color",
];

/* A hairline whose only job is to separate two rows of one surface identifies no component.
 * Everything else is a boundary and is gated at 3:1. */
const DECOR_TOKENS = new Set(["--line", "--c-line", "--c-chrome-line"]);

/* A `*-soft` fill is a wash BEHIND content, not a mark drawn ON it: the text it grounds is
 * checked as text, and asking the wash itself to clear 3:1 against the page would forbid every
 * tinted band in the UI. A leaf element filled with anything else is a mark — a meter fill, a
 * threshold rule, a status dot — and is gated. */
const isWash = (token) => typeof token === "string" && token.endsWith("-soft");

/* ================================================================= 6. walk ==================== */

const pairs = new Map();
const seenClasses = new Set();

function record(role, fg, bg, ratio, where, extra, tag) {
  const key = `${role}|${fg.label}|${bg.label}|${extra || ""}|${where}`;
  const prev = pairs.get(key);
  if (prev) { prev.count++; return; }
  pairs.set(key, { role, fg, bg, ratio, where, extra: extra || "", tag: tag || "", count: 1 });
}

function labelOf(c) {
  return c.token && c.token.startsWith("--") ? c.token : rgbToHex(c.rgb);
}

function walk(el, theme, parentComputed, parentProps, bgStack) {
  const c = computed(el, theme, parentComputed, parentProps);
  for (const cls of el.classes) seenClasses.add(cls);

  const ownBg = backgroundOf(c.style, c.props);
  let stack = bgStack;
  if (ownBg) {
    stack = ownBg.a >= 0.999
      ? [{ rgb: ownBg.rgb, token: ownBg.token }]
      : [...bgStack, { rgb: ownBg.rgb, token: ownBg.token, a: ownBg.a }];
  }
  const flat = flatten(stack);

  const opacity = c.style["opacity"];
  const hasText = el.text.length > 0;

  if (hasText && opacity !== undefined && parseFloat(opacity) < 1) {
    failures.push(
      `.${el.classes.join(".") || el.tag} carries text at opacity ${opacity} — evidence in this ` +
        `product is never dimmed (D-030)`
    );
  }

  if (hasText) {
    const fgExpr = c.inherited["color"];
    const fg = fgExpr ? colorOf(fgExpr, c.props) : null;
    if (fg && flat) {
      const rgb = fg.a >= 0.999 ? fg.rgb : over(fg, flat.rgb);
      const size = lengthOf(c.inherited["font-size"], c.props) ?? 16;
      const weight = parseInt(c.inherited["font-weight"] || "400", 10) || 400;
      const large = size >= 24 || (size >= 18.66 && weight >= 700);
      record(
        large ? "large" : "text",
        { label: labelOf(fg), hex: rgbToHex(rgb) },
        { label: flat.label, hex: rgbToHex(flat.rgb) },
        contrast(rgb, flat.rgb),
        selectorish(el),
        `${size}px`,
        el.tag
      );
    }
  }

  /* A leaf with a fill and no text is a graphical mark: a meter fill, a threshold rule, a status
     dot. WCAG 1.4.11 covers those too, and on this UI they are the objects that say "crossed". */
  if (ownBg && !hasText && el.children.length === 0 && ownBg.a >= 0.05) {
    const ground = flatten(bgStack);
    // An element filled with exactly its own ground colour draws nothing and is not a mark — a
    // sticky header repeating the surface under it, for instance.
    if (ground && rgbToHex(ownBg.rgb) !== rgbToHex(ground.rgb)) {
      const rgb = ownBg.a >= 0.999 ? ownBg.rgb : over(ownBg, ground.rgb);
      record(
        isWash(ownBg.token) ? "decor" : "ui",
        { label: labelOf(ownBg), hex: rgbToHex(rgb) },
        { label: ground.label, hex: rgbToHex(ground.rgb) },
        contrast(rgb, ground.rgb),
        selectorish(el),
        "mark",
        el.tag
      );
    }
  }

  // borders
  for (const prop of BORDER_PROPS) {
    const value = c.style[prop];
    if (value === undefined) continue;
    if (/\b0(px)?\b/.test(value) && !/\d+px\s/.test(value)) continue;
    const col = colorFromShorthand(value, c.props);
    if (!col || col.a < 0.05) continue;
    const ground = flatten(bgStack) || flat;
    if (!ground) continue;
    const rgb = col.a >= 0.999 ? col.rgb : over(col, ground.rgb);
    const role = DECOR_TOKENS.has(col.token) ? "decor" : "ui";
    record(
      role,
      { label: labelOf(col), hex: rgbToHex(rgb) },
      { label: ground.label, hex: rgbToHex(ground.rgb) },
      contrast(rgb, ground.rgb),
      selectorish(el),
      prop,
      el.tag
    );
  }

  // hover / focus states that change a surface under existing text
  const overlays = stateOverlays(el, theme);
  for (const [state, style] of Object.entries(overlays)) {
    const bg = backgroundOf(style, c.props);
    if (!bg || bg.a < 0.999) continue;
    const under = { rgb: bg.rgb, label: labelOf(bg) };
    for (const kid of textDescendants(el)) {
      const kc = computed(kid.el, theme, kid.parentComputed, kid.parentProps);
      const fg = kc.inherited["color"] ? colorOf(kc.inherited["color"], kc.props) : null;
      if (!fg) continue;
      const rgb = fg.a >= 0.999 ? fg.rgb : over(fg, under.rgb);
      const size = lengthOf(kc.inherited["font-size"], kc.props) ?? 16;
      record(
        "text",
        { label: labelOf(fg), hex: rgbToHex(rgb) },
        { label: under.label, hex: rgbToHex(under.rgb) },
        contrast(rgb, under.rgb),
        `${selectorish(el)}:${state}`,
        `${size}px`,
        kid.el.tag
      );
    }
  }

  for (const kid of el.children) walk(kid, theme, c, c.props, stack);
}

/* Elements under `el` that carry text and inherit `el`'s background (i.e. draw no ground of their
 * own). Used only for hover, where the fill changes under text that is already there. */
function textDescendants(el, parentComputed, parentProps, out = [], depth = 0) {
  if (depth > 4) return out;
  for (const kid of el.children) {
    if (kid.text) out.push({ el: kid, parentComputed, parentProps });
    textDescendants(kid, parentComputed, parentProps, out, depth + 1);
  }
  if (el.text) out.unshift({ el, parentComputed, parentProps });
  return out;
}

function flatten(stack) {
  if (!stack.length) return null;
  let base = stack[0];
  let rgb = base.rgb;
  let label = base.token && base.token.startsWith("--") ? base.token : rgbToHex(base.rgb);
  for (let k = 1; k < stack.length; k++) {
    const layer = stack[k];
    rgb = over({ rgb: layer.rgb, a: layer.a ?? 1 }, rgb);
    label = `${layer.token && layer.token.startsWith("--") ? layer.token : rgbToHex(layer.rgb)}@${Math.round((layer.a ?? 1) * 100)}% on ${label}`;
  }
  return { rgb, label };
}

/* `.op-table td.num` rather than `.num`: the region an element sits in is what makes a pair
 * reviewable, and it is also what lets the ledger check below find ledger cells without anyone
 * writing down where the ledger is. Two ancestors is enough to name a region and short enough to
 * print. */
function selectorish(el) {
  const own = el.classes.length ? el.tag + "." + el.classes.join(".") : el.tag;
  const up = [];
  let cur = el.parent;
  while (cur && up.length < 2) {
    if (cur.classes.length) up.unshift("." + cur.classes[0]);
    cur = cur.parent;
  }
  return [...up, own].join(" ");
}

/* ================================================================= 7. run ===================== */

const THEMES = ["light", "dark"];
const perTheme = {};
for (const theme of THEMES) {
  pairs.clear();
  for (const hash of routes) {
    const tree = renderTree(hash);
    // `:root` custom properties seed the whole document.
    const rootProps = {};
    for (const r of allRules) {
      if (r.selector !== ":root") continue;
      if (r.media === "dark" && theme !== "dark") continue;
      for (const [prop, value] of r.decls) if (prop.startsWith("--")) rootProps[prop] = value;
    }
    const bodyBg = (() => {
      for (const r of allRules) {
        if (r.selector !== "body") continue;
        if (r.media === "dark" && theme !== "dark") continue;
        const c = colorFromShorthand(r.decls.map(([p, v]) => (p === "background" || p === "background-color" ? v : "")).join(" "), rootProps);
        if (c) return c;
      }
      return null;
    })();
    walk(tree, theme, null, rootProps, bodyBg ? [{ rgb: bodyBg.rgb, token: bodyBg.token }] : []);
  }
  perTheme[theme] = [...pairs.values()];
}

/* ---- the discovery must be real -------------------------------------------------------------- */

for (const theme of THEMES) {
  if (!perTheme[theme].length) failures.push(`${theme}: discovered no colour pairs at all`);
}
const total = perTheme.light.length + perTheme.dark.length;
if (total < 80) {
  failures.push(`discovered only ${total} pairs across both themes — that is too few to be a real sweep`);
}
for (const cls of SENTINELS) {
  if (!seenClasses.has(cls)) {
    failures.push(`the rendered screens no longer contain ".${cls}" — this gate would be checking a UI that is gone`);
  }
}
if (perTheme.light.map((p) => p.bg.hex).join() === perTheme.dark.map((p) => p.bg.hex).join()) {
  failures.push("light and dark resolved to identical colours — the dark theme is not being applied");
}

/* The tenant's own accent must actually be what got checked on the console, or the whole
 * accent / accent-ink split is untested. */
const tenantAccent = (block.tenant.accent || "").toLowerCase();
/* `--accent-edge` is the tenant hex pushed 80% toward black in light and toward white in dark, so
 * the raw hex is never what gets drawn. Recompute both corrections here and require each to turn
 * up in a checked pair: if the inline `--accent` override ever stops reaching an element, these
 * fall back to the default accent and this fails. */
const mix80 = (hex, towardHex) => {
  const a = hexToRgb(hex), b = hexToRgb(towardHex);
  return rgbToHex(a.map((v, k) => v * 0.8 + b[k] * 0.2));
};
if (tenantAccent) {
  for (const [theme, expect] of [
    ["light", mix80(tenantAccent, "#000000")],
    ["dark", mix80(tenantAccent, "#ffffff")],
  ]) {
    const hit = perTheme[theme].some(
      (p) => p.fg.label === "--c-seam" && p.fg.hex.toLowerCase() === expect.toLowerCase()
    );
    if (!hit) {
      failures.push(
        `${theme}: the tenant accent ${tenantAccent} never reached a --c-seam pair as ${expect} — ` +
          `the inline per-deployment override is not getting through to this gate`
      );
    }
  }
}

/* ---- the ledger is never dimmed --------------------------------------------------------------- */

/* THE LEDGER IS NEVER DIMMED — the one product rule this gate enforces beyond WCAG.
 *
 * A sub-threshold row is tinted (`--bad` at 6%) because it is worth marking, and it is otherwise
 * identical to any other row: same ink, same weight, same size. Dimming it would draw the exact
 * incumbent behaviour this entry inverts (D-030) — an evidence row below the cut is retained, and
 * it still counts.
 *
 * The reference is discovered, not declared: the panel's PRIMARY ink is whichever ink reaches the
 * highest contrast on `--c-panel` anywhere in the run. A tinted ledger cell has to be inked with
 * that one. Holding it back a step — the natural way someone would "de-emphasise a secondary row"
 * — changes the token and fails here, even though the weaker ink would still clear 4.5:1 on its
 * own. Whether a case with a sub-threshold row is open is a property of the fixture, so the
 * absence of one is a failure too: this check does not get to pass by finding nothing.
 */
for (const theme of THEMES) {
  const onPanel = perTheme[theme].filter((p) => p.role === "text" && p.bg.label === "--c-panel");
  const primary = onPanel.reduce((best, p) => (!best || p.ratio > best.ratio ? p : best), null);
  const tinted = perTheme[theme].filter(
    (p) => p.role === "text" && p.tag === "td" && p.bg.label.indexOf("--bad@6%") === 0
  );
  if (!primary) {
    failures.push(`${theme}: no text was found on --c-panel, so there is no primary ink to compare against`);
    continue;
  }
  if (!tinted.length) {
    failures.push(
      `${theme}: no sub-threshold ledger cell was rendered anywhere in ${routes.length} routes — ` +
        `either the ledger stopped marking retained evidence, or this check has gone vacuous`
    );
    continue;
  }
  for (const p of tinted) {
    if (p.fg.label !== primary.fg.label) {
      failures.push(
        `${theme}: a sub-threshold ledger cell is inked ${p.fg.label} where this panel's primary ` +
          `ink is ${primary.fg.label} — retained evidence renders at full strength (D-030)`
      );
    }
    if (p.ratio < 4.5) {
      failures.push(`${theme}: a sub-threshold ledger cell renders at ${p.ratio.toFixed(2)}:1`);
    }
    if (p.ratio < primary.ratio * 0.85) {
      failures.push(
        `${theme}: the tint on a sub-threshold ledger cell costs it too much — ${p.ratio.toFixed(2)}:1 ` +
          `against a primary ${primary.ratio.toFixed(2)}:1`
      );
    }
  }
}

/* ---- gate ------------------------------------------------------------------------------------- */

const FLOOR = { text: 4.5, large: 3.0, ui: 3.0, decor: 0 };
const ROLE_ORDER = { text: 0, large: 1, ui: 2, decor: 3 };

/* One line per distinct token pair, at its WORST occurrence, with a count and an example of where
 * it happens. Every occurrence is still gated — this is how the table is printed, not what is
 * checked — but 634 rows that differ only in which cell they were seen in is a wall, not a report.
 * `--all` adds the decorative rules. */
function report(theme) {
  const groups = new Map();
  for (const r of perTheme[theme]) {
    const key = `${r.role}|${r.fg.label}|${r.bg.label}`;
    const g = groups.get(key);
    if (!g || r.ratio < g.ratio) groups.set(key, { ...r, seen: (g ? g.seen : 0) + r.count });
    else g.seen += r.count;
    const floor = FLOOR[r.role];
    if (floor > 0 && r.ratio < floor) {
      failures.push(
        `${theme} ${r.role} ${r.ratio.toFixed(2)}:1 (needs ${floor}) — ${r.fg.label} on ` +
          `${r.bg.label} at ${r.where}`
      );
    }
  }
  const rows = [...groups.values()].sort(
    (a, b) => ROLE_ORDER[a.role] - ROLE_ORDER[b.role] || a.ratio - b.ratio
  );
  const shown = rows.filter((r) => SHOW_ALL || r.role !== "decor" || r.ratio < FLOOR[r.role]);
  console.log(`
  ${theme.toUpperCase()}  —  ${perTheme[theme].length} pairs on screen, ${rows.length} distinct token pairs`);
  console.log(
    "  " + "role".padEnd(6) + "ratio".padStart(7) + "  n".padEnd(6) + "  " +
      "foreground".padEnd(23) + "background".padEnd(32) + "worst case"
  );
  console.log("  " + "-".repeat(116));
  for (const r of shown) {
    const floor = FLOOR[r.role];
    const flag = floor > 0 && r.ratio < floor ? "  FAIL" : "";
    console.log(
      "  " + r.role.padEnd(6) + r.ratio.toFixed(2).padStart(7) + String(r.seen).padStart(5) + "   " +
        `${r.fg.label} ${r.fg.hex}`.padEnd(23) +
        `${r.bg.label} ${r.bg.hex}`.padEnd(32) +
        `${r.where}${r.extra ? " [" + r.extra + "]" : ""}${flag}`
    );
  }
}

console.log("Contrast gate — every foreground/background pair the rendered UI actually uses.");
console.log(`  ${routes.length} routes · ${allRules.length} rules from ${SHEETS.join(", ")}`);
console.log("  text >= 4.5:1 · large (>=24px, or >=18.66px bold) >= 3:1 · ui border >= 3:1");
console.log("  decor = a rule between rows of one surface: reported, not gated (--all shows them)");
for (const theme of THEMES) report(theme);

if (notes.length) {
  console.log("\n  notes");
  for (const n of notes) console.log("   - " + n);
}

if (failures.length) {
  console.error("\ncontrast FAILED:");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  `\ncontrast OK: ${total} pairs across 2 themes, ${routes.length} routes, ` +
    `${SENTINELS.length} sentinels present, tenant accent ${tenantAccent} checked.`
);
