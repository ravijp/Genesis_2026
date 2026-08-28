/* Formatting and escaping, shared by every screen. Loaded first; owns no state.
 *
 * This file exists because `app.js` and `live.js` both render scores, verdicts and customer
 * speech, and two copies of `esc()` is one copy too many: the day they diverge is the day one
 * screen escapes a quote and the other does not. There is one `esc()` in this UI.
 *
 * It computes nothing about the product. `n3` and `pct` are display transforms of numbers that
 * arrived already computed -- `memory.py` is the only scorer in this system and a browser is not
 * going to become the second one.
 */

window.EARSHOT_UI = (function () {
  "use strict";

  /* Everything a customer said is untrusted text by definition: it is whatever someone said on a
   * call. It goes through here before it reaches innerHTML, without exception. */
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

  function n2(value) {
    return typeof value === "number" ? value.toFixed(2) : "—";
  }

  function signed(value) {
    if (typeof value !== "number") return "—";
    return (value >= 0 ? "+" : "") + value.toFixed(3);
  }

  /* Clamped, because a score bar is a rectangle and a rectangle cannot be 140% wide. The clamp is
   * presentation only: the number printed beside the bar is never clamped, so a value out of
   * range stays visible as a number rather than being quietly hidden by its own chart. */
  function pct(value) {
    return Math.max(0, Math.min(100, (Number(value) || 0) * 100));
  }

  function usd(value, places) {
    return typeof value === "number" ? "$" + value.toFixed(places === undefined ? 4 : places) : "—";
  }

  function words(value) {
    return String(value === undefined || value === null ? "" : value).replace(/_/g, " ");
  }

  /* A real risk signal is bad news, not a success. Green means "we can stand this one down". */
  function verdictClass(verdict) {
    if (verdict === "genuine") return "bad";
    if (verdict === "false_alarm" || verdict === "false_positive") return "ok";
    return "warn";
  }

  function setCrumbs(crumbs, parts) {
    crumbs.innerHTML = parts
      .map(function (p, i) {
        return i === parts.length - 1
          ? "<span>" + esc(p.label) + "</span>"
          : '<a href="' + esc(p.href) + '">' + esc(p.label) + "</a>";
      })
      .join(' <span aria-hidden="true">/</span> ');
  }

  return {
    esc: esc,
    n3: n3,
    n2: n2,
    signed: signed,
    pct: pct,
    usd: usd,
    words: words,
    verdictClass: verdictClass,
    setCrumbs: setCrumbs,
  };
})();
