/* The demo screens: a multi-enterprise portfolio, and the arrival stream replayed on a clock.
 *
 * `app.js` owns the router and the three reviewer screens. This file owns the two demo screens
 * and is loaded before it. Split because they are different jobs: the reviewer screens are the
 * product a bank's staff use, and these two are how the product is *shown* -- one has to keep
 * working when the other is being rebuilt the night before a gate.
 *
 * **It computes nothing.** Every score, delta, board position, crossing and cost in a frame was
 * computed by `memory.py` inside `earshot stream` and written to `ui/stream.js`. This file steps
 * an index through an array and paints. It does not add, decay, rank or threshold. The moment a
 * browser starts scoring there are two scorers in this system and they will disagree on stage.
 *
 * **There is no speech recognition anywhere in this product**, and this screen says so rather
 * than implying otherwise by animating a waveform. What the replay reproduces faithfully is the
 * *arrival pattern* -- order across the whole book, day spacing, channel mix -- and, at 1x, the
 * reader's own measured per-call latency. The transcripts were generated as text.
 *
 * **Two sources, one player.** Over `file://` it plays the recorded run, which is what survives a
 * judging room with no wifi (D-004). Served from `earshot stream --serve` it can instead attach
 * an EventSource to localhost and paint frames as a live Bedrock call produces each one. Same
 * `paint()` either way, because the server emits the identical frame objects `run_stream` writes.
 */

window.EARSHOT_LIVE = (function () {
  "use strict";

  var U = window.EARSHOT_UI;
  var STREAM = window.EARSHOT_STREAM || null;

  // Height of one live-board row, in px. Rows are absolutely positioned and moved by transform so
  // a re-rank is a visible slide rather than a repaint -- re-ranking IS the thing being shown, and
  // an innerHTML swap makes it invisible. Must match `.boardrow` height in styles.css.
  var ROW = 40;

  // 1x is the reader's own measured latency for that conversation, so "real time" is a fact from
  // the run rather than a chosen animation speed. The floor stops a cached 0 ms read from making
  // the stream unwatchable; the fallback covers the keyless lexicon, which costs no time at all.
  var SPEEDS = [
    { label: "1× real time", k: 1 },
    { label: "4×", k: 4 },
    { label: "12×", k: 12 },
    { label: "40×", k: 40 },
  ];
  var FALLBACK_MS = 900;
  var FLOOR_MS = 90;

  var player = null;

  function blocks() {
    return STREAM && STREAM.tenants ? STREAM.tenants : [];
  }

  function blockFor(tenantId) {
    var all = blocks();
    if (!all.length) return null;
    if (!tenantId) return all[0];
    for (var i = 0; i < all.length; i++) {
      if (all[i].tenant.tenant_id === tenantId) return all[i];
    }
    return null;
  }

  function noData(view, what) {
    view.innerHTML =
      '<div class="panel"><h2>No stream data</h2><p class="lede">' +
      U.esc(what) +
      " This screen replays a recorded <code>earshot stream</code> run. Build one:</p>" +
      '<pre class="quote">uv run earshot stream --tenant all --extractor model --provider bedrock\n' +
      "uv run python tools/stream_fixture.py</pre>" +
      '<p><a class="plain" href="#/queue">Back to the reviewer queue</a></p></div>';
  }

  /* ---- the honesty banner ---------------------------------------------------------------
   *
   * On the screen, not in a caption someone remembers to say out loud. A screenshot of this page
   * has to carry its own caveats, because a screenshot is what ends up in someone else's deck.
   */
  function provenanceLine(block) {
    var m = block.manifest || {};
    var live = m.provider && m.provider !== "offline-rules";
    return (
      '<div class="prov-inline">' +
      "<strong>" +
      (m.live ? "Live run." : "Recorded run, replayed on a wall clock.") +
      "</strong> " +
      "reader=" + U.esc(m.reader) +
      "  agent=" + U.esc(m.provider) +
      "  threshold=" + U.esc(m.threshold) + " (fixed cut, as the deployed ingest handler uses — " +
      "not the budget-derived one <code>earshot investigate</code> reports)" +
      "  seed=" + U.esc(m.seed) +
      "  git=" + U.esc(m.git_sha) +
      "  data=" + U.esc(m.data) +
      '<br><strong>No speech recognition.</strong> ' + U.esc(m.asr_note || "") +
      (live
        ? ""
        : "  <strong>The agent here is offline-rules — a rule engine, not a model. Its verdicts " +
          "are a floor, not a result.</strong>") +
      "</div>"
    );
  }

  function tenantPills(activeId, hrefFor) {
    return (
      '<nav class="pills" aria-label="Enterprise">' +
      blocks()
        .map(function (b) {
          var t = b.tenant;
          var on = t.tenant_id === activeId;
          return (
            '<a class="pill' + (on ? " on" : "") + '" href="' + U.esc(hrefFor(t.tenant_id)) + '"' +
            ' style="--accent:' + U.esc(t.accent) + '">' +
            "<span class=\"dot\"></span><span>" + U.esc(t.name) + "</span>" +
            '<span class="pill-sub">' + U.esc(t.industry) + "</span></a>"
          );
        })
        .join("") +
      "</nav>"
    );
  }

  /* ---- screen: the portfolio -------------------------------------------------------------- */

  function renderPortfolio(view, crumbs) {
    U.setCrumbs(crumbs, [{ label: "Deployments" }]);
    var all = blocks();
    if (!all.length) return noData(view, "No tenants found in ui/stream.js.");

    var cards = all
      .map(function (b) {
        var t = b.tenant;
        var n = b.totals;
        var teams = (b.teams || [])
          .map(function (row) {
            return (
              '<li><span class="team-name">' + U.esc(row.label) + "</span>" +
              '<span class="team-bar"><i style="width:' +
              (n.investigated ? (100 * row.cases) / n.investigated : 0) +
              '%"></i></span>' +
              '<span class="num">' + U.esc(row.cases) + "</span></li>"
            );
          })
          .join("");
        return (
          '<section class="panel tenant-card" style="--accent:' + U.esc(t.accent) + '">' +
          '<div class="tenant-head"><span class="dot"></span><div>' +
          "<h3>" + U.esc(t.name) + "</h3>" +
          '<p class="muted">' + U.esc(t.industry) + " · synthetic book</p></div></div>" +
          '<p class="book">' + U.esc(t.book) + "</p>" +
          '<dl class="kv tight">' +
          "<dt>Conversations read</dt><dd>" + U.esc(n.conversations) + "</dd>" +
          "<dt>Customers</dt><dd>" + U.esc(n.customers) + "</dd>" +
          "<dt>Signals kept</dt><dd>" + U.esc(n.signals) + "</dd>" +
          "<dt>Alert threshold</dt><dd>" + U.n2(t.threshold) + " (fixed)</dd>" +
          "<dt>Crossings</dt><dd>" + U.esc(n.crossings) + "</dd>" +
          "<dt>Investigated</dt><dd>" + U.esc(n.investigated) + " of " + U.esc(n.crossings) +
          "</dd>" +
          "<dt>Reader spend</dt><dd>" + U.usd(n.reader_cost_usd) + "</dd>" +
          "<dt>Agent spend</dt><dd>" + U.usd(n.investigation_cost_usd) + "</dd>" +
          "</dl>" +
          '<h4 class="mini">Where cases were routed</h4>' +
          '<ul class="teams">' + teams + "</ul>" +
          '<p><a class="plain" href="#/stream/' + U.esc(t.tenant_id) + '">' +
          "Watch this book stream →</a></p>" +
          "</section>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>Three deployments, one engine</h2>" +
      '<p class="lede">Each of these is the same code on its own book of business: its own ' +
      "conversations, its own decay half-lives, its own alert threshold, and its own names for " +
      "the four routing teams. There is no per-tenant scorer and no per-tenant prompt. What " +
      "differs is configuration, and the numbers below differ because of it.</p>" +
      '<div class="cards">' + cards + "</div>" +
      '<section class="panel"><h3>What actually differs between them</h3>' +
      '<div class="table-wrap"><table><thead><tr>' +
      "<th>Deployment</th><th>Book</th><th class=\"right\">Threshold</th>" +
      '<th class="right">Customers</th><th class="right">Conversations</th>' +
      "<th>Reader</th><th>Agent</th>" +
      "</tr></thead><tbody>" +
      all
        .map(function (b) {
          return (
            "<tr><td>" + U.esc(b.tenant.name) + "</td>" +
            "<td>" + U.esc(b.tenant.industry) + "</td>" +
            '<td class="right num">' + U.n2(b.tenant.threshold) + "</td>" +
            '<td class="right num">' + U.esc(b.totals.customers) + "</td>" +
            '<td class="right num">' + U.esc(b.totals.conversations) + "</td>" +
            "<td>" + U.esc(b.manifest.reader) + "</td>" +
            "<td>" + U.esc(b.manifest.provider) + "</td></tr>"
          );
        })
        .join("") +
      "</tbody></table></div>" +
      '<p class="note"><strong>The thresholds differ because the review capacity differs</strong>' +
      " — a servicer with four reviewers on a book of 38 cannot accept a card issuer's alert " +
      "rate. Every one of these books is synthetic and every enterprise here is invented; the " +
      "names exist so three deployments are distinguishable on screen. Costs are shown per " +
      "deployment and never summed, because each is a separate customer of this system.</p>" +
      "</section>";
  }

  /* ---- screen: the stream ------------------------------------------------------------------
   *
   * The player is a plain index into `block.frames`. `paint(i)` is a pure function of the frame
   * at `i` plus the frames before it (for the counters and the decided-cases list), so a scrub
   * backwards lands on exactly the state the forward pass would have shown. That property is
   * what makes the scrubber safe to use in front of an audience.
   */

  function teardown() {
    if (player) {
      if (player.timer) clearTimeout(player.timer);
      if (player.source) player.source.close();
      player = null;
    }
  }

  function renderStream(view, crumbs, tenantId) {
    teardown();
    var block = blockFor(tenantId);
    if (!block) {
      return noData(
        view,
        tenantId ? "No stream recorded for " + tenantId + "." : "ui/stream.js is missing."
      );
    }
    var t = block.tenant;
    U.setCrumbs(crumbs, [
      { label: "Deployments", href: "#/portfolio" },
      { label: t.name },
    ]);

    view.innerHTML =
      '<div class="stream" style="--accent:' + U.esc(t.accent) + '">' +
      tenantPills(t.tenant_id, function (id) { return "#/stream/" + id; }) +
      '<div class="stream-head">' +
        "<h2>" + U.esc(t.name) + " — conversations arriving</h2>" +
        '<p class="lede">' + U.esc(t.book) + "</p>" +
      "</div>" +
      provenanceLine(block) +
      '<div class="transport" id="transport"></div>' +
      '<div class="stage">' +
        '<section class="panel call" id="call"></section>' +
        '<section class="panel ledgerpane" id="ledgerpane"></section>' +
        '<section class="panel boardpane">' +
          "<h3>Live queue — who a reviewer should look at right now</h3>" +
          '<p class="muted small">Ranked on the score today. Every customer heard so far is ' +
          "re-scored on each arrival, including the ones who said nothing: under decay their " +
          "scores move when the calendar does.</p>" +
          '<div class="boardrows" id="boardrows"></div>' +
        "</section>" +
      "</div>" +
      '<div class="ticker" id="ticker"></div>' +
      '<section class="panel" id="decided"></section>' +
      "</div>";

    player = {
      block: block,
      frames: block.frames.slice(),
      i: 0,
      playing: true,
      speed: 0,
      timer: null,
      source: null,
      live: false,
      rows: {},
      nodes: {
        transport: document.getElementById("transport"),
        call: document.getElementById("call"),
        ledger: document.getElementById("ledgerpane"),
        board: document.getElementById("boardrows"),
        ticker: document.getElementById("ticker"),
        decided: document.getElementById("decided"),
      },
    };

    paintTransport();
    paint(0);
    schedule();
    offerLive();
  }

  function frameDuration(frame) {
    var measured = frame && frame.reader ? Number(frame.reader.latency_ms) : 0;
    var base = measured > 0 ? measured : FALLBACK_MS;
    return Math.max(FLOOR_MS, base / SPEEDS[player.speed].k);
  }

  function schedule() {
    if (!player || !player.playing || player.live) return;
    if (player.i >= player.frames.length - 1) {
      player.playing = false;
      paintTransport();
      return;
    }
    player.timer = setTimeout(function () {
      if (!player) return;
      player.i += 1;
      paint(player.i);
      paintTransport();
      schedule();
    }, frameDuration(player.frames[player.i]));
  }

  function jump(index) {
    if (!player) return;
    if (player.timer) clearTimeout(player.timer);
    player.i = Math.max(0, Math.min(player.frames.length - 1, index));
    paint(player.i);
    paintTransport();
    schedule();
  }

  function nextCrossing() {
    for (var k = player.i + 1; k < player.frames.length; k++) {
      if (player.frames[k].crossed) return k;
    }
    return player.frames.length - 1;
  }

  function paintTransport() {
    var n = player.frames.length;
    var frame = player.frames[player.i] || {};
    player.nodes.transport.innerHTML =
      '<button class="tbtn" id="playpause">' +
      (player.playing ? "❙❙ Pause" : "▶ Play") +
      "</button>" +
      '<button class="tbtn" id="stepback" title="Back one conversation">◀</button>' +
      '<button class="tbtn" id="stepfwd" title="Forward one conversation">▶</button>' +
      '<button class="tbtn" id="tocross">Next threshold crossing ⤳</button>' +
      '<button class="tbtn" id="restart">↺ Restart</button>' +
      '<span class="speeds">' +
      SPEEDS.map(function (s, k) {
        return (
          '<button class="tbtn small' + (k === player.speed ? " on" : "") +
          '" data-speed="' + k + '">' + U.esc(s.label) + "</button>"
        );
      }).join("") +
      "</span>" +
      '<input class="scrub" id="scrub" type="range" min="0" max="' + (n - 1) +
      '" value="' + player.i + '" aria-label="Position in the stream">' +
      '<span class="pos">conversation ' + (player.i + 1) + " / " + n +
      "  ·  day " + U.esc(frame.day) + "</span>" +
      // The badge names the cache mode rather than saying "LIVE" over a replay. Once the reader
      // cache is warm a live run serves recorded completions in seconds, and a badge that hid
      // that would be the one dishonest pixel on the page.
      (player.live
        ? '<span class="badge bad live">LIVE — ' +
          U.esc((player.liveMeta || {}).live_kind || "running now") + "</span>"
        : "");

    document.getElementById("playpause").onclick = function () {
      player.playing = !player.playing;
      paintTransport();
      if (player.playing) schedule();
      else if (player.timer) clearTimeout(player.timer);
    };
    document.getElementById("stepback").onclick = function () {
      player.playing = false;
      jump(player.i - 1);
    };
    document.getElementById("stepfwd").onclick = function () {
      player.playing = false;
      jump(player.i + 1);
    };
    document.getElementById("tocross").onclick = function () {
      player.playing = false;
      jump(nextCrossing());
    };
    document.getElementById("restart").onclick = function () {
      player.playing = true;
      player.rows = {};
      player.nodes.board.innerHTML = "";
      jump(0);
    };
    document.getElementById("scrub").oninput = function (e) {
      player.playing = false;
      jump(Number(e.target.value));
    };
    Array.prototype.forEach.call(
      player.nodes.transport.querySelectorAll("[data-speed]"),
      function (btn) {
        btn.onclick = function () {
          player.speed = Number(btn.getAttribute("data-speed"));
          paintTransport();
          if (player.timer) clearTimeout(player.timer);
          schedule();
        };
      }
    );
  }

  /* ---- the three panels -------------------------------------------------------------------- */

  function paintCall(frame) {
    var block = player.block;
    var conversation = (block.conversations || {})[frame.conversation_id] || {};
    var cited = {};
    (frame.signals || []).forEach(function (s) {
      cited[s.turn_index] = s;
    });

    // Turns reveal on a CSS delay rather than a JS timer: it restarts cleanly on every frame,
    // survives a scrub, and cannot leave a stray interval running when the route changes.
    var turns = (conversation.turns || [])
      .map(function (turn, k) {
        var hit = cited[turn.index === undefined ? k : turn.index];
        return (
          '<li class="turn' + (hit ? " hit" : "") + '" style="--k:' + k + '">' +
          '<span class="who">' + U.esc(turn.speaker) + "</span>" +
          "<span>" + U.esc(turn.text) + "</span>" +
          (hit
            ? '<span class="flag">' + U.esc(U.words(hit.signal_type)) +
              "  conf " + U.n2(hit.confidence) + "</span>"
            : "") +
          "</li>"
        );
      })
      .join("");

    var read = frame.reader || {};
    player.nodes.call.innerHTML =
      "<h3>On the line — " + U.esc(frame.conversation_id) + "</h3>" +
      '<p class="muted small">' + U.esc(frame.customer_id) + " · " + U.esc(frame.channel) +
      " · day " + U.esc(frame.day) + " · " + U.esc(frame.n_turns) + " turns</p>" +
      '<ul class="turns live">' + turns + "</ul>" +
      '<div class="readbar">' +
      (read.model_calls
        ? "<span>read by the model: " + U.esc(read.latency_ms) + " ms · " +
          U.usd(read.cost_usd, 5) + "</span>"
        : "<span>read by the keyless lexicon: no model call, no cost</span>") +
      "<span>" +
      ((frame.signals || []).length
        ? U.esc(frame.signals.length) + " signal(s) kept"
        : "nothing kept from this conversation") +
      "</span></div>";
  }

  function paintLedger(frame) {
    var t = player.block.tenant;
    var before = frame.score_before || 0;
    var after = frame.score_after || 0;
    var delta = after - before;
    var crossedNow = frame.crossed;

    player.nodes.ledger.innerHTML =
      "<h3>" + U.esc(frame.customer_id) + " — standing ledger</h3>" +
      '<p class="muted small">' +
      (frame.signal_type
        ? "Strongest signal family: " + U.esc(U.words(frame.signal_type))
        : "No signal on file yet") +
      " · " + U.esc(frame.n_entries) + " quote(s) retained</p>" +
      '<div class="scoremeter">' +
        '<div class="meter">' +
          '<span class="fill" style="width:' + U.pct(after) + '%"></span>' +
          '<span class="was" style="width:' + U.pct(before) + '%"></span>' +
          '<span class="cut" style="left:' + U.pct(t.threshold) + '%"></span>' +
        "</div>" +
        '<div class="meterlabels">' +
          "<span>was " + U.n3(before) + "</span>" +
          '<span class="big">' + U.n3(after) + "</span>" +
          '<span class="delta ' + (delta > 0.0005 ? "up" : "flat") + '">' +
          U.signed(delta) + "</span>" +
          "<span>cut " + U.n2(t.threshold) + "</span>" +
        "</div>" +
      "</div>" +
      (crossedNow
        ? '<div class="crossbanner">THRESHOLD CROSSED — case opened for ' +
          U.esc(frame.customer_id) + " on day " + U.esc(frame.day) +
          '<span class="sub">Opened by this conversation. The agent works it against the ' +
          "evidence known at this moment, not the whole book.</span></div>"
        : "") +
      '<p class="note small">Nothing here is ever deleted or superseded. A quote that mattered ' +
      "to nobody in month one is still summable in month six — that inversion is the point: " +
      "incumbents reconcile to current truth, this accumulates.</p>";
  }

  function paintBoard(frame) {
    var container = player.nodes.board;
    var board = frame.board || [];
    var live = {};
    var t = player.block.tenant;

    board.forEach(function (row, k) {
      live[row.customer_id] = true;
      var node = player.rows[row.customer_id];
      if (!node) {
        node = document.createElement("div");
        node.className = "boardrow";
        container.appendChild(node);
        player.rows[row.customer_id] = node;
      }
      node.style.transform = "translateY(" + k * ROW + "px)";
      node.className =
        "boardrow" +
        (row.state === "case" ? " open" : row.state === "over" ? " over" : "") +
        (row.customer_id === frame.customer_id ? " touched" : "");
      node.innerHTML =
        '<span class="cid">' + U.esc(row.customer_id) + "</span>" +
        '<span class="sig">' + U.esc(U.words(row.signal_type)) + "</span>" +
        '<span class="bar"><i style="width:' + U.pct(row.score) + '%"></i>' +
        '<b class="cut" style="left:' + U.pct(t.threshold) + '%"></b></span>' +
        '<span class="num">' + U.n3(row.score) + "</span>" +
        '<span class="state">' +
        (row.state === "case" ? "case open" : row.state === "over" ? "over cut" : "watch") +
        "</span>";
    });

    Object.keys(player.rows).forEach(function (cid) {
      if (!live[cid]) {
        container.removeChild(player.rows[cid]);
        delete player.rows[cid];
      }
    });
    container.style.height = board.length * ROW + "px";
  }

  function paintTicker(frame) {
    var frames = player.frames;
    var read = 0;
    var kept = 0;
    var spend = 0;
    var crossings = 0;
    for (var k = 0; k <= player.i && k < frames.length; k++) {
      read += 1;
      kept += (frames[k].signals || []).length;
      spend += (frames[k].reader && frames[k].reader.cost_usd) || 0;
      if (frames[k].crossed) crossings += 1;
    }
    player.nodes.ticker.innerHTML =
      '<span><b>' + read + "</b> conversations read</span>" +
      '<span><b>' + kept + "</b> signals kept</span>" +
      '<span><b>' + U.esc(frame.customers_seen) + "</b> customers on the ledger</span>" +
      '<span><b>' + U.esc(frame.ledger_size) + "</b> quotes retained, none discarded</span>" +
      '<span><b>' + crossings + "</b> threshold crossings</span>" +
      '<span><b>' + U.usd(spend, 4) + "</b> reader spend so far</span>";
  }

  /* Cases appear only once the stream has reached the frame that opened them. Showing all of them
   * from the first frame would answer the question the demo is asking before it is asked. */
  function paintDecided() {
    var block = player.block;
    var cases = Object.keys(block.cases || {})
      .map(function (id) { return block.cases[id]; })
      .filter(function (c) { return (c.frame_index || 0) <= player.i; })
      .sort(function (a, b) { return (b.frame_index || 0) - (a.frame_index || 0); });

    var unworked = (block.unworked || []).filter(function (row) {
      for (var k = 0; k <= player.i; k++) {
        if (player.frames[k].crossed && player.frames[k].customer_id === row.customer_id) {
          return true;
        }
      }
      return false;
    });

    var rows = cases
      .map(function (c) {
        var d = c.decision || {};
        return (
          // encodeURIComponent, because `make_case_id` joins its triple with "#" and a raw one
          // inside a hash route is legal-but-browser-dependent. `app.js` decodes every path part,
          // so an encoded id round-trips exactly and the question stops being interesting.
          '<li><a class="plain" href="#/stream/' + U.esc(block.tenant.tenant_id) +
          "/case/" + U.esc(encodeURIComponent(c.case_id)) + '">' +
          '<span class="badge ' + U.verdictClass(d.verdict) + '">' +
          U.esc(U.words(d.verdict)) + "</span>" +
          '<span class="cid">' + U.esc(c.customer_id) + "</span>" +
          '<span class="team">→ ' + U.esc(c.team_label) + "</span>" +
          '<span class="muted">conf ' + U.n2(d.confidence) +
          " · " + U.usd((c.trace || {}).cost_usd) +
          " · " + U.esc((c.trace || {}).tool_calls) + " tool calls</span>" +
          "</a></li>"
        );
      })
      .join("");

    player.nodes.decided.innerHTML =
      "<h3>Cases opened and worked</h3>" +
      (rows
        ? '<ul class="decided">' + rows + "</ul>"
        : '<p class="empty">No case has opened yet in this run.</p>') +
      (unworked.length
        ? '<p class="note"><strong>' + unworked.length + " crossing(s) opened but were not " +
          "investigated</strong> — " + U.esc(unworked[0].reason || "no reason recorded") +
          ". They are listed in the artifact rather than dropped, because a demo that shows " +
          "four worked cases from nine crossings and does not say so is claiming a precision it " +
          "did not measure.</p>"
        : "");
  }

  function paint(i) {
    var frame = player.frames[i];
    if (!frame) return;
    paintCall(frame);
    paintLedger(frame);
    paintBoard(frame);
    paintTicker(frame);
    paintDecided();
  }

  /* ---- live mode ---------------------------------------------------------------------------
   *
   * Only offered when the page is being served, because `file://` has no server to attach to.
   * The browser never holds a credential: it opens an EventSource to 127.0.0.1 and `earshot
   * stream --serve` makes the Bedrock calls in its own process.
   */
  function offerLive() {
    if (!/^https?:$/.test(window.location.protocol)) return;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/live/meta", true);
    xhr.onload = function () {
      if (xhr.status !== 200 || !player) return;
      var btn = document.createElement("button");
      btn.className = "tbtn live-btn";
      btn.textContent = "⚡ Go live — call Bedrock now";
      btn.onclick = function () { goLive(); };
      player.nodes.transport.appendChild(btn);
    };
    xhr.onerror = function () {};
    try { xhr.send(); } catch (e) { /* file:// or no server; the recorded replay stands */ }
  }

  function goLive() {
    if (!player || player.live) return;
    if (player.timer) clearTimeout(player.timer);
    player.live = true;
    player.playing = false;
    player.frames = [];
    player.rows = {};
    player.i = 0;
    player.nodes.board.innerHTML = "";
    player.nodes.decided.innerHTML =
      '<h3>Cases opened and worked</h3><p class="empty">Waiting for the first crossing. The ' +
      "agent runs after the book has been read, so this fills in at the end.</p>";

    var source = new EventSource("/live/stream");
    player.source = source;
    // The live manifest is kept apart from the recorded block's: the transcripts on screen still
    // come from the recorded fixture (same tenant, same seed, so the same book), but the
    // provenance printed over them must describe the run that is happening now.
    source.addEventListener("meta", function (e) {
      if (!player) return;
      player.liveMeta = JSON.parse(e.data);
      paintTransport();
    });
    source.addEventListener("frame", function (e) {
      if (!player) return;
      player.frames.push(JSON.parse(e.data));
      player.i = player.frames.length - 1;
      paint(player.i);
      paintTransport();
    });
    source.addEventListener("verdict", function (e) {
      if (!player) return;
      var v = JSON.parse(e.data);
      var li = document.createElement("li");
      li.className = "livecase";
      li.innerHTML = v.skipped
        ? '<span class="badge mute">not worked</span><span class="cid">' +
          U.esc(v.customer_id) + '</span><span class="muted">' + U.esc(v.skipped) + "</span>"
        : '<span class="badge ' + U.verdictClass(v.verdict) + '">' + U.esc(U.words(v.verdict)) +
          '</span><span class="cid">' + U.esc(v.customer_id) + "</span>" +
          '<span class="team">→ ' + U.esc(v.team_label) + "</span>" +
          '<span class="muted">conf ' + U.n2(v.confidence) + " · " + U.usd(v.cost_usd) + "</span>";
      var list = player.nodes.decided.querySelector("ul.decided");
      if (!list) {
        list = document.createElement("ul");
        list.className = "decided";
        player.nodes.decided.appendChild(list);
      }
      list.insertBefore(li, list.firstChild);
    });
    source.addEventListener("done", function (e) {
      if (!player) return;
      // The server sends the identical payload the recorded artifact carries, so the case and
      // retro screens work off a live run exactly as they do off a replay.
      player.block = JSON.parse(e.data);
      player.frames = player.block.frames;
      paintDecided();
      source.close();
      player.source = null;
    });
    source.addEventListener("failed", function (e) {
      player.nodes.decided.innerHTML =
        '<h3>The live run stopped</h3><p class="empty">' + U.esc(JSON.parse(e.data).error) +
        " The recorded replay is still on this page — reload to return to it.</p>";
      source.close();
      player.source = null;
    });
    paintTransport();
  }

  /* The stream's own cases, exposed so `app.js` can render them with the same three reviewer
   * screens the recorded investigate run uses. One renderer, two data sources. */
  function sourceFor(tenantId) {
    var block = blockFor(tenantId);
    if (!block) return null;
    return {
      cases: block.cases,
      conversations: block.conversations,
      manifest: block.manifest,
      tenant: block.tenant,
      backHref: "#/stream/" + block.tenant.tenant_id,
      backLabel: block.tenant.name,
    };
  }

  return {
    renderPortfolio: renderPortfolio,
    renderStream: renderStream,
    sourceFor: sourceFor,
    teardown: teardown,
    hasData: function () { return blocks().length > 0; },
  };
})();
