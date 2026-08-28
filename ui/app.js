/* The router and the three reviewer screens, over one case shape.
 *
 * Vanilla, no build, no dependencies. It reads `window.EARSHOT_DATA` (written by
 * tools/ui_fixture.py from an `earshot investigate` artifact) and renders the same objects the
 * deployed API returns from `GET /cases`, `GET /cases/{id}` and
 * `GET /customers/{id}/conversations/{id}` -- both come from `case_record()`, so there is one code
 * path here rather than an offline one and a live one.
 *
 * **The same three screens serve two data sources.** A case from the recorded `investigate` run
 * and a case from a streamed run (`window.EARSHOT_STREAM`, one block per tenant) are the same
 * object -- `case_record()` builds both -- so `renderCase`, `renderRetro` and `renderConversation`
 * take a *source* rather than reaching for a global. Adding the stream demo therefore added
 * routes, not renderers. A second copy of the evidence chain is exactly how two screens end up
 * disagreeing about what a case says.
 *
 * It computes nothing. Every score, contribution, delta and load-bearing flag is read straight off
 * the data; `memory.py` is the only scorer in this system and a browser is not going to become the
 * second one.
 *
 * All customer speech goes through `EARSHOT_UI.esc()` before it reaches innerHTML. It is untrusted
 * text by definition -- it is whatever someone said on a call.
 */

(function () {
  "use strict";

  var U = window.EARSHOT_UI;
  var LIVE = window.EARSHOT_LIVE || null;
  var CONSOLE = window.EARSHOT_CONSOLE || null;
  var DATA = window.EARSHOT_DATA || null;
  var view = document.getElementById("view");
  var crumbs = document.getElementById("crumbs");

  /* ---- data sources ------------------------------------------------------------------------
   *
   * A source is the four things a reviewer screen needs and nothing else: the cases, the
   * transcripts behind their citations, the provenance to print, and where "back" goes. The
   * recorded investigate run is one; each streamed tenant is another.
   */
  function recordedSource() {
    if (!DATA) return null;
    return {
      key: "",
      cases: DATA.cases,
      conversations: DATA.conversations,
      manifest: DATA.manifest,
      backHref: "#/queue",
      backLabel: "Reviewer queue",
    };
  }

  function caseHref(src, caseId, suffix) {
    var base = src.key ? "#/stream/" + src.key + "/case/" : "#/case/";
    return base + encodeURIComponent(caseId) + (suffix || "");
  }

  function conversationHref(src, conversationId, caseId, turn) {
    var base = src.key ? "#/stream/" + src.key + "/conversation/" : "#/conversation/";
    return (
      base + encodeURIComponent(conversationId) +
      "?case=" + encodeURIComponent(caseId) + "&turn=" + turn
    );
  }

  // ---- chrome --------------------------------------------------------------------

  function renderProvenance(src) {
    var el = document.getElementById("provenance");
    var m = src && src.manifest;
    if (!m) {
      el.innerHTML =
        "<strong>No data loaded.</strong> Run <code>uv run python tools/ui_fixture.py</code> " +
        "to build <code>ui/data.js</code> from an investigate artifact.";
      return;
    }
    var live = m.provider && m.provider !== "offline-rules";
    el.innerHTML =
      "<strong>Recorded run, not live data.</strong> provider=" + U.esc(m.provider) +
      "  seed=" + U.esc(m.seed) +
      "  config=" + U.esc(m.config_hash) +
      "  git=" + U.esc(m.git_sha) +
      "  threshold=" + U.esc(m.threshold) +
      (m.budget === undefined ? "" : "  budget=" + U.esc(m.budget)) +
      (m.asr ? "  asr=" + U.esc(m.asr) : "") +
      (live
        ? ""
        : "  — <strong>offline-rules is a rule engine, not a model. These verdicts are a floor, " +
          "not a result.</strong>");
  }

  function renderNav(active) {
    var el = document.getElementById("mainnav");
    if (!el) return;
    // Two halves, named as such. The console is what a bank sees; the explanatory screens are
    // why it is true. Keeping them apart in the nav is the whole framing of the demo.
    var items = [
      { href: "#/desk", label: "Reviewer desk", key: "desk", group: "In use" },
      { href: "#/desk/call", label: "During a call", key: "call", group: "In use" },
      { href: "#/stream", label: "The stream", key: "stream", group: "How it works" },
      { href: "#/deployment", label: "Where it plugs in", key: "deployment", group: "How it works" },
    ];
    var group = "";
    el.innerHTML = items
      .map(function (item) {
        if (!LIVE || !LIVE.hasData()) return "";
        var lead = item.group === group ? "" :
          '<span class="navgroup">' + U.esc(item.group) + "</span>";
        group = item.group;
        return (
          lead +
          '<a class="navlink' + (item.key === active ? " on" : "") + '" href="' +
          U.esc(item.href) + '">' + U.esc(item.label) + "</a>"
        );
      })
      .join("");
  }

  // ---- screen 1: the ranked queue --------------------------------------------------

  function renderQueue() {
    U.setCrumbs(crumbs, [{ label: "Reviewer queue" }]);
    var q = DATA.queue;
    var rows = q.cases
      .map(function (c) {
        return (
          '<tr tabindex="0" data-case="' + U.esc(c.case_id) + '">' +
          "<td>" + U.esc(c.customer_id) + "</td>" +
          "<td>" + U.esc(U.words(c.signal_type)) + "</td>" +
          '<td class="right"><div class="score"><span class="num">' + U.n3(c.score) + "</span>" +
          '<span class="bar"><i style="width:' + U.pct(c.score) + '%"></i></span></div></td>' +
          '<td class="right num">' + U.n3(c.score_at_open) + "</td>" +
          '<td><span class="badge ' + U.verdictClass(c.verdict) + '">' +
          U.esc(U.words(c.verdict || "—")) + "</span></td>" +
          "<td>" + U.esc(c.owning_team || "—") + "</td>" +
          '<td class="right num">' + U.n2(c.confidence) + "</td>" +
          '<td class="right num">' + U.esc(c.n_evidence) + "</td>" +
          '<td class="right num">' + U.esc(c.opened_on_day) + " → " + U.esc(c.as_of_day) + "</td>" +
          "</tr>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>Ranked queue</h2>" +
      '<p class="lede">Ordered by the score <em>today</em>, which is the question a review team ' +
      "actually asks. A case that has faded since it opened ranks below one that is still live, " +
      "so the two scores are shown side by side.</p>" +
      '<div class="panel"><div class="table-wrap"><table>' +
      "<thead><tr>" +
      "<th>Customer</th><th>Signal</th>" +
      '<th class="right">Score now</th><th class="right">At open</th>' +
      "<th>Verdict</th><th>Owning team</th>" +
      '<th class="right">Conf.</th><th class="right">Quotes</th>' +
      '<th class="right">Day opened → now</th>' +
      "</tr></thead><tbody>" + rows + "</tbody></table></div>" +
      '<p class="note">' + U.esc(q.count) + " case" + (q.count === 1 ? "" : "s") +
      (q.truncated ? ", and the list is truncated at the page limit." : ", the whole queue.") +
      " Threshold " + U.esc(DATA.manifest.threshold) + " at a " +
      U.esc(Math.round((DATA.manifest.budget || 0) * 100)) + "% review budget." +
      " <strong>This threshold is the budget-derived one</strong> — the top 10% of a known " +
      "population. The live stream uses a fixed cut instead, because a streaming consumer has no " +
      "population to rank against. The two disagree about who crossed, and that is a property of " +
      "streaming rather than a bug.</p></div>";

    Array.prototype.forEach.call(view.querySelectorAll("tr[data-case]"), function (tr) {
      // Encoded for the same reason as every other case link: a case id contains "#".
      function open() {
        location.hash = "#/case/" + encodeURIComponent(tr.getAttribute("data-case"));
      }
      tr.addEventListener("click", open);
      tr.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
      });
    });
  }

  // ---- screen 2: one case, and its evidence chain -------------------------------------

  function renderCase(src, caseId) {
    var c = src.cases[caseId];
    if (!c) return renderMissing(src, "No case " + caseId);
    U.setCrumbs(crumbs, [
      { label: src.backLabel, href: src.backHref },
      { label: c.customer_id },
    ]);

    var d = c.decision || {};
    var t = c.trace || {};
    var cited = (d.evidence || [])
      .map(function (ref) {
        return (
          '<blockquote class="quote">' + U.esc(ref.quote) +
          "<cite>" +
          '<a class="plain" href="' +
          U.esc(conversationHref(src, ref.conversation_id, caseId, ref.turn_index)) + '">' +
          U.esc(ref.conversation_id) + " turn " + U.esc(ref.turn_index) +
          " — read in context</a>" +
          "</cite></blockquote>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>" + U.esc(c.customer_id) + " — " + U.esc(U.words(c.signal_type)) + "</h2>" +
      '<p class="lede">Opened on day ' + U.esc(c.opened_on_day) + " by " +
      U.esc(c.opened_by_conversation) + ", scored as of day " + U.esc(c.as_of_day) + "." +
      (c.team_label
        ? " Routed to <strong>" + U.esc(c.team_label) + "</strong>, this deployment's name for " +
          "the <code>" + U.esc(d.owning_team) + "</code> slot."
        : "") +
      "</p>" +

      '<div class="grid">' +
        '<section class="panel"><h3>Standing score</h3><dl class="kv">' +
          "<dt>Score now</dt><dd>" + U.n3(c.score) + "</dd>" +
          "<dt>Score at open</dt><dd>" + U.n3(c.score_at_open) + "</dd>" +
          "<dt>Threshold</dt><dd>" + U.n3(c.threshold) + "</dd>" +
          "<dt>Quotes on file</dt><dd>" + U.esc((c.evidence || []).length) + "</dd>" +
          "<dt>Status</dt><dd>" + U.esc(c.status) + "</dd>" +
        "</dl></section>" +

        '<section class="panel"><h3>Verdict</h3><dl class="kv">' +
          "<dt>Verdict</dt><dd><span class=\"badge " + U.verdictClass(d.verdict) + '">' +
            U.esc(U.words(d.verdict || "—")) + "</span></dd>" +
          "<dt>Confidence</dt><dd>" + U.n2(d.confidence) + "</dd>" +
          "<dt>Owning team</dt><dd>" + U.esc(c.team_label || d.owning_team || "—") + "</dd>" +
          "<dt>Recommended</dt><dd>" + U.esc(d.recommended_action || "—") + "</dd>" +
        "</dl></section>" +

        '<section class="panel"><h3>Run</h3><dl class="kv">' +
          "<dt>Provider</dt><dd>" + U.esc(t.provider || "—") + "</dd>" +
          "<dt>Model</dt><dd>" + U.esc(t.model || "—") + "</dd>" +
          "<dt>Model calls</dt><dd>" + U.esc(t.model_calls) + "</dd>" +
          "<dt>Tool calls</dt><dd>" + U.esc(t.tool_calls) + "</dd>" +
          "<dt>Cost</dt><dd>" + U.usd(t.cost_usd) + "</dd>" +
          "<dt>Stopped</dt><dd>" + U.esc(t.stopped_because || "—") + "</dd>" +
          "<dt>Evidence repairs</dt><dd>" + U.esc(t.evidence_repairs) + "</dd>" +
          "<dt>Account data</dt><dd>" +
            (t.account_data
              ? '<span class="badge warn">' + U.esc(t.account_data) + "</span>"
              : '<span class="badge mute">not recorded</span>') +
          "</dd>" +
        "</dl></section>" +
      "</div>" +

      '<section class="panel"><h3>Why</h3><p>' + U.esc(d.rationale || "—") + "</p>" +
        "<h3 style=\"margin-top:16px\">What would change my mind</h3><p>" +
        U.esc(d.what_would_change_my_mind || "—") + "</p></section>" +

      '<section class="panel"><h3>Evidence cited</h3>' +
        (cited || '<p class="empty">No citations on this decision.</p>') + "</section>" +

      '<section class="panel"><h3>Evidence chain — everything ever heard</h3>' +
        renderChain(src, c) +
        '<p class="note">Every row is retained, including the ones that never mattered on their ' +
        "own. Never discarding a sub-threshold signal is the inversion this system is built on: " +
        "incumbents reconcile to current truth, this accumulates.</p>" +
        '<p style="margin-top:14px"><a class="plain" href="' +
        U.esc(caseHref(src, caseId, "/retro")) + '">See how these re-scored →</a></p>' +
      "</section>" +

      (Array.isArray(t.steps) && t.steps.length
        ? '<section class="panel"><h3>Agent trace</h3><ol class="steps">' +
          t.steps
            .map(function (s) {
              return "<li><span>" + U.esc(s.index) + '.</span><span class="kind">' +
                U.esc(s.kind) + "</span><span>" + U.esc(s.name) + " — " +
                U.esc(s.detail) + "</span></li>";
            })
            .join("") +
          "</ol></section>"
        : "");
  }

  function renderChain(src, c) {
    var rows = (c.evidence || [])
      .map(function (e) {
        return (
          "<li>" +
          '<div class="head">' +
            '<span class="day">day ' + U.esc(e.day) + " · " + U.esc(e.channel) + " · " +
            U.esc(e.conversation_id) + " turn " + U.esc(e.turn_index) + "</span>" +
            (e.load_bearing
              ? '<span class="badge bad">load-bearing</span>'
              : '<span class="badge mute">not load-bearing</span>') +
            '<span class="badge mute">confidence ' + U.n3(e.confidence) + "</span>" +
          "</div>" +
          '<blockquote class="quote">' + U.esc(e.evidence_quote) +
            '<cite><a class="plain" href="' +
            U.esc(conversationHref(src, e.conversation_id, c.case_id, e.turn_index)) +
            '">read in context</a></cite></blockquote>' +
          "</li>"
        );
      })
      .join("");
    return rows ? '<ul class="chain">' + rows + "</ul>" : '<p class="empty">No evidence.</p>';
  }

  // ---- screen 3: the retro re-score ---------------------------------------------------

  function renderRetro(src, caseId) {
    var c = src.cases[caseId];
    if (!c) return renderMissing(src, "No case " + caseId);
    U.setCrumbs(crumbs, [
      { label: src.backLabel, href: src.backHref },
      { label: c.customer_id, href: caseHref(src, caseId) },
      { label: "Retro re-score" },
    ]);

    var cut = c.threshold;
    var rows = (c.evidence || [])
      .map(function (e) {
        var then = U.pct(e.score_at_write);
        var now = U.pct(e.score_now);
        var lo = Math.min(then, now);
        var span = Math.abs(now - then);
        var delta = e.retro_delta;
        return (
          "<li>" +
          '<div class="head">' +
            '<span class="day">day ' + U.esc(e.day) + " · " + U.esc(e.conversation_id) + "</span>" +
            (e.load_bearing ? '<span class="badge bad">load-bearing</span>' : "") +
          "</div>" +
          '<blockquote class="quote">' + U.esc(e.evidence_quote) + "</blockquote>" +
          '<div class="track">' +
            '<span class="span" style="left:' + lo + "%;width:" + span + '%"></span>' +
            '<span class="then-mark" style="left:' + then + '%"></span>' +
            '<span class="now-mark" style="left:' + now + '%"></span>' +
            '<span class="cut" style="left:' + U.pct(cut) + '%"></span>' +
          "</div>" +
          '<div class="retro">' +
            '<span class="then">supported ' + U.n3(e.score_at_write) + " when it arrived</span>" +
            '<span class="arrow">→</span>' +
            '<span class="now">supports ' + U.n3(e.score_now) + " now</span>" +
            '<span class="delta ' + (delta > 0.0005 ? "up" : "flat") + '">(' +
            U.signed(delta) + ")</span>" +
          "</div>" +
          "</li>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>Retro re-score — " + U.esc(c.customer_id) + "</h2>" +
      '<p class="lede">The same earlier conversations, re-read in light of the last one. The grey ' +
      "mark is what the customer's total score was when that quote landed; the blue mark is what " +
      "it is today; the red line is the threshold.</p>" +
      '<div class="panel"><ul class="chain">' + rows + "</ul>" +
      '<p class="note"><strong>Marginal value per quote falls as evidence accumulates</strong> — ' +
      "the score function is concave, so “this quote is worth more points now” would be " +
      "mathematically false. What moves is the conclusion the evidence supports, and whether the " +
      "case would collapse without it. That second question is the load-bearing flag, and it is " +
      "the one a compliance officer asks.</p></div>";
  }

  // ---- the transcript behind a quote ----------------------------------------------------

  function renderConversation(src, conversationId, params) {
    var conversation = (src.conversations || {})[conversationId];
    if (!conversation) return renderMissing(src, "No transcript for " + conversationId);
    var caseId = params.get("case");
    var citedTurn = params.get("turn");
    var back = caseId && src.cases[caseId] ? src.cases[caseId] : null;

    U.setCrumbs(
      crumbs,
      [{ label: src.backLabel, href: src.backHref }]
        .concat(back ? [{ label: back.customer_id, href: caseHref(src, caseId) }] : [])
        .concat([{ label: conversationId }])
    );

    var turns = (conversation.turns || [])
      .map(function (turn) {
        var isCited = String(turn.index) === String(citedTurn);
        return (
          '<li class="' + (isCited ? "cited" : "") + '">' +
          '<span class="who">' + U.esc(turn.speaker) + " · " + U.esc(turn.index) + "</span>" +
          "<span>" + U.esc(turn.text) + "</span></li>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>" + U.esc(conversationId) + "</h2>" +
      '<p class="lede">' + U.esc(conversation.customer_id) + " · " + U.esc(conversation.channel) +
      " · day " + U.esc(conversation.day) +
      ". The highlighted turn is the one the case cites.</p>" +
      '<div class="panel"><ul class="turns">' + turns + "</ul></div>";
  }

  // ---- routing ---------------------------------------------------------------------------

  function renderMissing(src, message) {
    var home = src || { backHref: "#/queue", backLabel: "Reviewer queue" };
    U.setCrumbs(crumbs, [
      { label: home.backLabel, href: home.backHref },
      { label: "Not found" },
    ]);
    view.innerHTML =
      '<div class="panel"><h2>Not found</h2><p class="lede">' + U.esc(message) +
      '</p><p><a class="plain" href="' + U.esc(home.backHref) + '">Back to ' +
      U.esc(home.backLabel) + "</a></p></div>";
  }

  function noRecordedData() {
    U.setCrumbs(crumbs, [{ label: "No data" }]);
    view.innerHTML =
      '<div class="panel"><h2>No data</h2><p class="lede">This page renders a recorded ' +
      "<code>earshot investigate</code> run. Build one:</p>" +
      "<pre class=\"quote\">uv run earshot investigate --customers 400 --limit 8\n" +
      "uv run python tools/ui_fixture.py</pre></div>";
  }

  function route() {
    // Every route change stops the stream player. A timer left running behind a different screen
    // keeps painting into detached nodes and, in live mode, keeps an EventSource open.
    if (LIVE) LIVE.teardown();

    var hash = location.hash.replace(/^#\/?/, "");
    var query = "";
    var q = hash.indexOf("?");
    if (q >= 0) { query = hash.slice(q + 1); hash = hash.slice(0, q); }
    var parts = hash.split("/").filter(Boolean).map(decodeURIComponent);
    var params = new URLSearchParams(query);
    var recorded = recordedSource();

    // -- the demo screens ------------------------------------------------------------------
    //
    // The portfolio is the front door when there is a demo to show, and the queue is the front
    // door when there is not. Rendered directly rather than redirected: a `location.replace` here
    // would put a second entry in the router's own history and make Back leave the page.
    // -- the console: our panel inside the client's desktop ---------------------------------
    if (parts[0] === "desk" && CONSOLE && CONSOLE.hasData()) {
      renderNav(parts[1] === "call" ? "call" : "desk");
      document.getElementById("provenance").innerHTML =
        "<strong>This is the product surface.</strong> The desktop chrome is a stand-in for the " +
        "client's own case-management console; only the outlined panel is ours. Customer data " +
        "is synthetic and there is no speech recognition anywhere in this system.";
      // `#/desk/team/<slot>` and `#/desk/team/<slot>/case/<id>`: a team view is a link someone
      // sends a colleague, so the filter lives in the route rather than in a variable, and it
      // survives a reload. The slot is the model's canonical `OwningTeam` value — stable, and the
      // only part of the mapping that belongs in a URL; the label a reviewer reads comes from the
      // tenant profile (D-029).
      var deskHome = { backHref: "#/desk", backLabel: "Reviewer desk" };
      if (parts[1] === "team") {
        var slot = parts[2] || null;
        if (!slot || !CONSOLE.hasTeam(slot)) {
          return renderMissing(
            deskHome,
            'No team view for "' + (slot || "") + '". This deployment routes to: ' +
              CONSOLE.teamSlots().join(", ") + "."
          );
        }
        var teamOk = parts[3] === "case"
          ? CONSOLE.renderCase(view, crumbs, parts[4] || null, slot)
          : CONSOLE.renderQueue(view, crumbs, slot);
        if (teamOk) return;
        return renderMissing(deskHome, "The console has no recorded run to show.");
      }
      var ok = parts[1] === "call"
        ? CONSOLE.renderCall(view, crumbs, parts[2] || null)
        : parts[1] === "case"
          ? CONSOLE.renderCase(view, crumbs, parts[2] || null)
          : CONSOLE.renderQueue(view, crumbs);
      if (ok) return;
      return renderMissing(deskHome, "The console has no recorded run to show.");
    }

    if (!parts.length && CONSOLE && CONSOLE.hasData()) {
      // The front door is the product in use, not an explanation of it.
      renderNav("desk");
      document.getElementById("provenance").innerHTML =
        "<strong>This is the product surface.</strong> The desktop chrome is a stand-in for the " +
        "client's own case-management console; only the outlined panel is ours. Customer data " +
        "is synthetic and there is no speech recognition anywhere in this system.";
      if (CONSOLE.renderQueue(view, crumbs)) return;
    }

    var wantsDeployment =
      parts[0] === "deployment" ||
      parts[0] === "portfolio" ||  // the old name; bookmarks from before the rename still land
      (!parts.length && LIVE && LIVE.hasData());
    if (wantsDeployment && LIVE) {
      renderNav("deployment");
      document.getElementById("provenance").innerHTML =
        "<strong>One synthetic deployment.</strong> This system is a layer that goes into a " +
        "client's existing stack — their contact centre, their transcripts, their case " +
        "management, their reviewers. Every conversation here was generated as text: there is " +
        "no speech recognition anywhere in this system.";
      return LIVE.renderIntegration(view, crumbs);
    }
    if (parts[0] === "stream" && LIVE) {
      // parts[1] is a tenant id when present. With one deployment shipping it usually is not, so
      // it falls back rather than 404ing on the route a person actually types.
      var tenantId = parts[1] && parts[1] !== "case" && parts[1] !== "conversation"
        ? parts[1]
        : LIVE.defaultTenantId();
      var streamSource = LIVE.sourceFor(tenantId);
      if (streamSource) streamSource.key = tenantId;

      if (parts[2] === "case" && parts[3] && streamSource) {
        renderNav("stream");
        renderProvenance(streamSource);
        return parts[4] === "retro"
          ? renderRetro(streamSource, parts[3])
          : renderCase(streamSource, parts[3]);
      }
      if (parts[2] === "conversation" && parts[3] && streamSource) {
        renderNav("stream");
        renderProvenance(streamSource);
        return renderConversation(streamSource, parts[3], params);
      }
      renderNav("stream");
      document.getElementById("provenance").innerHTML =
        "<strong>A recorded run, replayed on a wall clock.</strong> Provenance for this " +
        "deployment is printed on the stream itself, including the reader, the agent provider " +
        "and the threshold kind.";
      return LIVE.renderStream(view, crumbs, tenantId);
    }

    // -- the reviewer screens over the recorded investigate run -----------------------------
    renderNav("queue");
    renderProvenance(recorded);
    if (!recorded) return noRecordedData();

    if (parts[0] === "case" && parts[1] && parts[2] === "retro") {
      return renderRetro(recorded, parts[1]);
    }
    if (parts[0] === "case" && parts[1]) return renderCase(recorded, parts[1]);
    if (parts[0] === "conversation" && parts[1]) {
      return renderConversation(recorded, parts[1], params);
    }
    if (parts[0] === "queue" || !parts.length) return renderQueue();
    return renderMissing(recorded, "No screen at #/" + parts.join("/"));
  }

  window.addEventListener("hashchange", function () {
    route();
    view.focus();
    window.scrollTo(0, 0);
  });

  route();
})();
