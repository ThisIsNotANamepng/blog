/* Filtering, view switching, and search highlighting for /pseudo_resume.
   Everything is rendered server side; this only ever hides, opens, or
   re-orders what is already on the page. */

(function () {
  "use strict";

  var page = document.getElementById("page");
  if (!page) return;

  var q = document.getElementById("q");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var viewBtns = Array.prototype.slice.call(document.querySelectorAll(".view-btn"));
  var entries = Array.prototype.slice.call(document.querySelectorAll(".entry"));
  var bands = Array.prototype.slice.call(document.querySelectorAll(".band"));
  var panes = { timeline: document.getElementById("timeline"), groups: document.getElementById("groups") };
  var countEl = document.getElementById("count");
  var emptyEl = document.getElementById("empty");

  var state = { query: "", cats: [], view: "timeline" };

  // Keep a pristine copy of each card header so highlighting can be undone.
  var pristine = new WeakMap();
  entries.forEach(function (e) {
    pristine.set(e, e.querySelector(".entry-head").innerHTML);
  });

  /* --- filtering --------------------------------------------------------- */

  function matches(entry) {
    if (state.cats.length) {
      var cats = entry.dataset.cats.split(" ");
      var hit = state.cats.some(function (c) { return cats.indexOf(c) !== -1; });
      if (!hit) return false;
    }
    if (state.query && entry.dataset.text.indexOf(state.query) === -1) return false;
    return true;
  }

  function apply() {
    var seen = {};
    var shown = 0;

    entries.forEach(function (entry) {
      var ok = matches(entry);
      entry.hidden = !ok;
      if (ok && !seen[entry.dataset.id]) {
        seen[entry.dataset.id] = true;
        shown++;
      }
      // A search deep enough to be deliberate opens its hits, so the matching
      // text is actually on screen rather than folded away.
      if (ok && state.query.length >= 2) entry.open = true;
    });

    bands.forEach(function (band) {
      var any = band.querySelector(".entry:not([hidden])");
      band.hidden = !any;
    });

    highlight();

    var total = entries.filter(function (e) { return e.closest("#timeline"); }).length;
    countEl.textContent = shown === total
      ? "All " + total + " entries"
      : "Showing " + shown + " of " + total;

    emptyEl.hidden = shown !== 0;
    syncUrl();
  }

  /* --- search highlighting ----------------------------------------------- */

  function highlight() {
    entries.forEach(function (entry) {
      var head = entry.querySelector(".entry-head");
      if (!state.query || entry.hidden) {
        if (head.dataset.marked) {
          head.innerHTML = pristine.get(entry);
          delete head.dataset.marked;
        }
        return;
      }
      head.innerHTML = pristine.get(entry);
      head.dataset.marked = "1";
      markIn(head, state.query);
    });
  }

  function markIn(root, needle) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var targets = [];
    var node;
    while ((node = walker.nextNode())) {
      if (node.nodeValue.toLowerCase().indexOf(needle) !== -1) targets.push(node);
    }
    targets.forEach(function (text) {
      var value = text.nodeValue;
      var lower = value.toLowerCase();
      var frag = document.createDocumentFragment();
      var at = 0;
      var found;
      while ((found = lower.indexOf(needle, at)) !== -1) {
        frag.appendChild(document.createTextNode(value.slice(at, found)));
        var mark = document.createElement("mark");
        mark.textContent = value.slice(found, found + needle.length);
        frag.appendChild(mark);
        at = found + needle.length;
      }
      frag.appendChild(document.createTextNode(value.slice(at)));
      text.parentNode.replaceChild(frag, text);
    });
  }

  /* --- views -------------------------------------------------------------- */

  function setView(view) {
    state.view = view;
    page.className = "view-" + view;
    panes.timeline.hidden = view === "groups";
    panes.groups.hidden = view !== "groups";
    viewBtns.forEach(function (b) {
      var on = b.dataset.view === view;
      b.classList.toggle("is-on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  /* --- chips -------------------------------------------------------------- */

  function paintChips() {
    chips.forEach(function (chip) {
      var on = chip.dataset.cat === "all"
        ? state.cats.length === 0
        : state.cats.indexOf(chip.dataset.cat) !== -1;
      chip.classList.toggle("is-on", on);
      chip.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var cat = chip.dataset.cat;
      if (cat === "all") {
        state.cats = [];
      } else {
        var at = state.cats.indexOf(cat);
        if (at === -1) state.cats.push(cat);
        else state.cats.splice(at, 1);
      }
      paintChips();
      apply();
    });
  });

  viewBtns.forEach(function (b) {
    b.addEventListener("click", function () { setView(b.dataset.view); syncUrl(); });
  });

  var typing;
  q.addEventListener("input", function () {
    clearTimeout(typing);
    typing = setTimeout(function () {
      state.query = q.value.trim().toLowerCase();
      apply();
    }, 90);
  });

  document.getElementById("expand-all").addEventListener("click", function () {
    visibleEntries().forEach(function (e) { e.open = true; });
  });

  document.getElementById("collapse-all").addEventListener("click", function () {
    visibleEntries().forEach(function (e) { e.open = false; });
  });

  document.getElementById("reset").addEventListener("click", function () {
    q.value = "";
    state.query = "";
    state.cats = [];
    paintChips();
    apply();
  });

  function visibleEntries() {
    var pane = state.view === "groups" ? panes.groups : panes.timeline;
    return Array.prototype.slice.call(pane.querySelectorAll(".entry:not([hidden])"));
  }

  /* --- keyboard ----------------------------------------------------------- */

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "/" && document.activeElement !== q) {
      ev.preventDefault();
      q.focus();
      q.select();
    } else if (ev.key === "Escape") {
      if (q.value) {
        q.value = "";
        state.query = "";
        apply();
      }
      q.blur();
    }
  });

  /* --- shareable state ---------------------------------------------------- */

  function syncUrl() {
    var parts = [];
    if (state.view !== "timeline") parts.push("view=" + state.view);
    if (state.cats.length) parts.push("cat=" + state.cats.join(","));
    if (state.query) parts.push("q=" + encodeURIComponent(state.query));
    var url = location.pathname + (parts.length ? "?" + parts.join("&") : "");
    history.replaceState(null, "", url);
  }

  function readUrl() {
    var params = new URLSearchParams(location.search);
    var view = params.get("view");
    var known_views = ["timeline", "groups", "list"];
    setView(known_views.indexOf(view) !== -1 ? view : "timeline");

    var cat = params.get("cat");
    if (cat) {
      var known = chips.map(function (c) { return c.dataset.cat; });
      state.cats = cat.split(",").filter(function (c) { return known.indexOf(c) !== -1; });
    }
    var query = params.get("q");
    if (query) {
      q.value = query;
      state.query = query.trim().toLowerCase();
    }
  }

  /* --- stat count-up ------------------------------------------------------ */

  function countUp() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var stats = document.querySelectorAll(".stat-value");
    Array.prototype.forEach.call(stats, function (el) {
      var target = parseFloat(el.dataset.value);
      var prefix = el.dataset.prefix || "";
      var suffix = el.dataset.suffix || "";
      var decimals = String(el.dataset.value).indexOf(".") !== -1 ? 1 : 0;
      var started = performance.now();
      var duration = 700;

      function step(now) {
        var t = Math.min(1, (now - started) / duration);
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = prefix + (target * eased).toFixed(decimals) + suffix;
        if (t < 1) requestAnimationFrame(step);
        else el.textContent = prefix + target.toFixed(decimals) + suffix;
      }
      requestAnimationFrame(step);
    });
  }

  readUrl();
  paintChips();
  apply();
  countUp();
})();
