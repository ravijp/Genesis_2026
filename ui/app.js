/* The reviewer SPA: three screens over one case shape.
 *
 * Vanilla, no build, no dependencies. It reads `window.EARSHOT_DATA` (written by
 * tools/ui_fixture.py from an `earshot investigate` artifact) and renders the same objects the
 * deployed API returns from `GET /cases`, `GET /cases/{id}` and
 * `GET /customers/{id}/conversations/{id}` -- both come from `case_record()`, so there is one code
 * path here rather than an offline one and a live one.
 *
 * It computes nothing. Every score, contribution, delta and load-bearing flag is read straight off
 * the data; `memory.py` is the only scorer in this system and a browser is not going to become the
 * second one.
 *
 * All customer speech goes through `esc()` before it reaches innerHTML. It is untrusted text by
 * definition -- it is whatever someone said on a call.
 */

(function () {
  "use strict";

  var DATA = window.EARSHOT_DATA || null;
  var view = document.getElementById("view");
  var crumbs = document.getElementById("crumbs");

  // ---- helpers -------------------------------------------------------------------

  function esc(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function n3(value) {
    return typeof value === "number" ? value.toFixed(3) : "—";
  }

  function signed(value) {
    if (typeof value !== "number") return "—";
    return (value >= 0 ? "+" : "") + value.toFixed(3);
  }

  function pct(value) {
    return Math.max(0, Math.min(100, (Number(value) || 0) * 100));
  }

  function verdictClass(verdict) {
    if (verdict === "genuine") return "bad";       // a real risk signal is bad news, not a success
    if (verdict === "false_positive") return "ok";
    return "warn";
  }

  // ---- chrome --------------------------------------------------------------------

  function renderProvenance() {
    var el = document.getElementById("provenance");
    if (!DATA) {
      el.innerHTML =
        "<strong>No data loaded.</strong> Run <code>uv run python tools/ui_fixture.py</code> " +
        "to build <code>ui/data.js</code> from an investigate artifact.";
      return;
    }
    var m = DATA.manifest || {};
    var live = m.provider && m.provider !== "offline-rules";
    el.innerHTML =
      "<strong>Recorded run, not live data.</strong> provider=" + esc(m.provider) +
      "  seed=" + esc(m.seed) +
      "  config=" + esc(m.config_hash) +
      "  git=" + esc(m.git_sha) +
      "  threshold=" + esc(m.threshold) +
      "  budget=" + esc(m.budget) +
      (live
        ? ""
        : "  — <strong>offline-rules is a rule engine, not a model. These verdicts are a floor, " +
          "not a result.</strong>");
  }

  function setCrumbs(parts) {
    crumbs.innerHTML = parts
      .map(function (p, i) {
        var text = i === parts.length - 1
          ? "<span>" + esc(p.label) + "</span>"
          : '<a href="' + esc(p.href) + '">' + esc(p.label) + "</a>";
        return text;
      })
      .join(' <span aria-hidden="true">/</span> ');
  }

  // ---- screen 1: the ranked queue --------------------------------------------------

  function renderQueue() {
    setCrumbs([{ label: "Reviewer queue" }]);
    var q = DATA.queue;
    var rows = q.cases
      .map(function (c) {
        return (
          '<tr tabindex="0" data-case="' + esc(c.case_id) + '">' +
          "<td>" + esc(c.customer_id) + "</td>" +
          "<td>" + esc(String(c.signal_type).replace(/_/g, " ")) + "</td>" +
          '<td class="right"><div class="score"><span class="num">' + n3(c.score) + "</span>" +
          '<span class="bar"><i style="width:' + pct(c.score) + '%"></i></span></div></td>' +
          '<td class="right num">' + n3(c.score_at_open) + "</td>" +
          '<td><span class="badge ' + verdictClass(c.verdict) + '">' +
          esc(String(c.verdict || "—").replace(/_/g, " ")) + "</span></td>" +
          "<td>" + esc(c.owning_team || "—") + "</td>" +
          '<td class="right num">' + (typeof c.confidence === "number" ? c.confidence.toFixed(2) : "—") + "</td>" +
          '<td class="right num">' + esc(c.n_evidence) + "</td>" +
          '<td class="right num">' + esc(c.opened_on_day) + " → " + esc(c.as_of_day) + "</td>" +
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
      '<p class="note">' + esc(q.count) + " case" + (q.count === 1 ? "" : "s") +
      (q.truncated ? ", and the list is truncated at the page limit." : ", the whole queue.") +
      " Threshold " + esc(DATA.manifest.threshold) + " at a " +
      esc(Math.round((DATA.manifest.budget || 0) * 100)) + "% review budget.</p></div>";

    Array.prototype.forEach.call(view.querySelectorAll("tr[data-case]"), function (tr) {
      function open() { location.hash = "#/case/" + tr.getAttribute("data-case"); }
      tr.addEventListener("click", open);
      tr.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
      });
    });
  }

  // ---- screen 2: one case, and its evidence chain -------------------------------------

  function renderCase(caseId) {
    var c = DATA.cases[caseId];
    if (!c) return renderMissing("No case " + caseId);
    setCrumbs([{ label: "Reviewer queue", href: "#/queue" }, { label: c.customer_id }]);

    var d = c.decision || {};
    var t = c.trace || {};
    var cited = (d.evidence || [])
      .map(function (ref) {
        return (
          '<blockquote class="quote">' + esc(ref.quote) +
          "<cite>" +
          '<a class="plain" href="#/conversation/' + esc(ref.conversation_id) +
          "?case=" + esc(caseId) + "&turn=" + esc(ref.turn_index) + '">' +
          esc(ref.conversation_id) + " turn " + esc(ref.turn_index) + " — read in context</a>" +
          "</cite></blockquote>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>" + esc(c.customer_id) + " — " + esc(String(c.signal_type).replace(/_/g, " ")) + "</h2>" +
      '<p class="lede">Opened on day ' + esc(c.opened_on_day) + " by " +
      esc(c.opened_by_conversation) + ", scored as of day " + esc(c.as_of_day) + ".</p>" +

      '<div class="grid">' +
        '<section class="panel"><h3>Standing score</h3><dl class="kv">' +
          "<dt>Score now</dt><dd>" + n3(c.score) + "</dd>" +
          "<dt>Score at open</dt><dd>" + n3(c.score_at_open) + "</dd>" +
          "<dt>Threshold</dt><dd>" + n3(c.threshold) + "</dd>" +
          "<dt>Quotes on file</dt><dd>" + esc((c.evidence || []).length) + "</dd>" +
          "<dt>Status</dt><dd>" + esc(c.status) + "</dd>" +
        "</dl></section>" +

        '<section class="panel"><h3>Verdict</h3><dl class="kv">' +
          "<dt>Verdict</dt><dd><span class=\"badge " + verdictClass(d.verdict) + '">' +
            esc(String(d.verdict || "—").replace(/_/g, " ")) + "</span></dd>" +
          "<dt>Confidence</dt><dd>" + (typeof d.confidence === "number" ? d.confidence.toFixed(2) : "—") + "</dd>" +
          "<dt>Owning team</dt><dd>" + esc(d.owning_team || "—") + "</dd>" +
          "<dt>Recommended</dt><dd>" + esc(d.recommended_action || "—") + "</dd>" +
        "</dl></section>" +

        '<section class="panel"><h3>Run</h3><dl class="kv">' +
          "<dt>Provider</dt><dd>" + esc(t.provider || "—") + "</dd>" +
          "<dt>Model</dt><dd>" + esc(t.model || "—") + "</dd>" +
          "<dt>Model calls</dt><dd>" + esc(t.model_calls) + "</dd>" +
          "<dt>Tool calls</dt><dd>" + esc(t.tool_calls) + "</dd>" +
          "<dt>Cost</dt><dd>$" + (typeof t.cost_usd === "number" ? t.cost_usd.toFixed(4) : "—") + "</dd>" +
          "<dt>Stopped</dt><dd>" + esc(t.stopped_because || "—") + "</dd>" +
          "<dt>Evidence repairs</dt><dd>" + esc(t.evidence_repairs) + "</dd>" +
          "<dt>Account data</dt><dd>" +
            (t.account_data
              ? '<span class="badge warn">' + esc(t.account_data) + "</span>"
              : '<span class="badge mute">not recorded</span>') +
          "</dd>" +
        "</dl></section>" +
      "</div>" +

      '<section class="panel"><h3>Why</h3><p>' + esc(d.rationale || "—") + "</p>" +
        "<h3 style=\"margin-top:16px\">What would change my mind</h3><p>" +
        esc(d.what_would_change_my_mind || "—") + "</p></section>" +

      '<section class="panel"><h3>Evidence cited</h3>' +
        (cited || '<p class="empty">No citations on this decision.</p>') + "</section>" +

      '<section class="panel"><h3>Evidence chain — everything ever heard</h3>' +
        renderChain(c) +
        '<p class="note">Every row is retained, including the ones that never mattered on their ' +
        "own. Never discarding a sub-threshold signal is the inversion this system is built on: " +
        "incumbents reconcile to current truth, this accumulates.</p>" +
        '<p style="margin-top:14px"><a class="plain" href="#/case/' + esc(caseId) +
        '/retro">See how these re-scored →</a></p>' +
      "</section>" +

      (Array.isArray(t.steps) && t.steps.length
        ? '<section class="panel"><h3>Agent trace</h3><ol class="steps">' +
          t.steps
            .map(function (s) {
              return "<li><span>" + esc(s.index) + '.</span><span class="kind">' +
                esc(s.kind) + "</span><span>" + esc(s.name) + " — " + esc(s.detail) + "</span></li>";
            })
            .join("") +
          "</ol></section>"
        : "");
  }

  function renderChain(c) {
    var rows = (c.evidence || [])
      .map(function (e) {
        return (
          "<li>" +
          '<div class="head">' +
            '<span class="day">day ' + esc(e.day) + " · " + esc(e.channel) + " · " +
            esc(e.conversation_id) + " turn " + esc(e.turn_index) + "</span>" +
            (e.load_bearing
              ? '<span class="badge bad">load-bearing</span>'
              : '<span class="badge mute">not load-bearing</span>') +
            '<span class="badge mute">confidence ' + n3(e.confidence) + "</span>" +
          "</div>" +
          '<blockquote class="quote">' + esc(e.evidence_quote) +
            '<cite><a class="plain" href="#/conversation/' + esc(e.conversation_id) +
            "?case=" + esc(c.case_id) + "&turn=" + esc(e.turn_index) +
            '">read in context</a></cite></blockquote>' +
          "</li>"
        );
      })
      .join("");
    return rows ? '<ul class="chain">' + rows + "</ul>" : '<p class="empty">No evidence.</p>';
  }

  // ---- screen 3: the retro re-score ---------------------------------------------------

  function renderRetro(caseId) {
    var c = DATA.cases[caseId];
    if (!c) return renderMissing("No case " + caseId);
    setCrumbs([
      { label: "Reviewer queue", href: "#/queue" },
      { label: c.customer_id, href: "#/case/" + caseId },
      { label: "Retro re-score" },
    ]);

    var cut = c.threshold;
    var rows = (c.evidence || [])
      .map(function (e) {
        var then = pct(e.score_at_write);
        var now = pct(e.score_now);
        var lo = Math.min(then, now);
        var span = Math.abs(now - then);
        var delta = e.retro_delta;
        return (
          "<li>" +
          '<div class="head">' +
            '<span class="day">day ' + esc(e.day) + " · " + esc(e.conversation_id) + "</span>" +
            (e.load_bearing ? '<span class="badge bad">load-bearing</span>' : "") +
          "</div>" +
          '<blockquote class="quote">' + esc(e.evidence_quote) + "</blockquote>" +
          '<div class="track">' +
            '<span class="span" style="left:' + lo + "%;width:" + span + '%"></span>' +
            '<span class="then-mark" style="left:' + then + '%"></span>' +
            '<span class="now-mark" style="left:' + now + '%"></span>' +
            '<span class="cut" style="left:' + pct(cut) + '%"></span>' +
          "</div>" +
          '<div class="retro">' +
            '<span class="then">supported ' + n3(e.score_at_write) + " when it arrived</span>" +
            '<span class="arrow">→</span>' +
            '<span class="now">supports ' + n3(e.score_now) + " now</span>" +
            '<span class="delta ' + (delta > 0.0005 ? "up" : "flat") + '">(' + signed(delta) + ")</span>" +
          "</div>" +
          "</li>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>Retro re-score — " + esc(c.customer_id) + "</h2>" +
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

  function renderConversation(conversationId, params) {
    var conversation = (DATA.conversations || {})[conversationId];
    if (!conversation) return renderMissing("No transcript for " + conversationId);
    var caseId = params.get("case");
    var citedTurn = params.get("turn");
    var back = caseId && DATA.cases[caseId] ? DATA.cases[caseId] : null;

    setCrumbs(
      [{ label: "Reviewer queue", href: "#/queue" }]
        .concat(back ? [{ label: back.customer_id, href: "#/case/" + caseId }] : [])
        .concat([{ label: conversationId }])
    );

    var turns = (conversation.turns || [])
      .map(function (turn) {
        var isCited = String(turn.index) === String(citedTurn);
        return (
          '<li class="' + (isCited ? "cited" : "") + '">' +
          '<span class="who">' + esc(turn.speaker) + " · " + esc(turn.index) + "</span>" +
          "<span>" + esc(turn.text) + "</span></li>"
        );
      })
      .join("");

    view.innerHTML =
      "<h2>" + esc(conversationId) + "</h2>" +
      '<p class="lede">' + esc(conversation.customer_id) + " · " + esc(conversation.channel) +
      " · day " + esc(conversation.day) +
      ". The highlighted turn is the one the case cites.</p>" +
      '<div class="panel"><ul class="turns">' + turns + "</ul></div>";
  }

  // ---- routing ---------------------------------------------------------------------------

  function renderMissing(message) {
    setCrumbs([{ label: "Reviewer queue", href: "#/queue" }, { label: "Not found" }]);
    view.innerHTML =
      '<div class="panel"><h2>Not found</h2><p class="lede">' + esc(message) +
      '</p><p><a class="plain" href="#/queue">Back to the queue</a></p></div>';
  }

  function route() {
    if (!DATA) {
      view.innerHTML =
        '<div class="panel"><h2>No data</h2><p class="lede">This page renders a recorded ' +
        "<code>earshot investigate</code> run. Build one:</p>" +
        "<pre class=\"quote\">uv run earshot investigate --customers 400 --limit 8\n" +
        "uv run python tools/ui_fixture.py</pre></div>";
      return;
    }
    var hash = location.hash.replace(/^#\/?/, "");
    var query = "";
    var q = hash.indexOf("?");
    if (q >= 0) { query = hash.slice(q + 1); hash = hash.slice(0, q); }
    var parts = hash.split("/").filter(Boolean).map(decodeURIComponent);
    var params = new URLSearchParams(query);

    if (parts[0] === "case" && parts[1] && parts[2] === "retro") return renderRetro(parts[1]);
    if (parts[0] === "case" && parts[1]) return renderCase(parts[1]);
    if (parts[0] === "conversation" && parts[1]) return renderConversation(parts[1], params);
    return renderQueue();
  }

  window.addEventListener("hashchange", function () {
    route();
    view.focus();
    window.scrollTo(0, 0);
  });

  renderProvenance();
  route();
})();
