/* Timeline explorer for /pseudo_resume.

   The entries arrive as JSON in #resume-data (built by pseudo_resume.py). Each
   one becomes a row: its title on the left and a bar on a shared time axis on
   the right. Filters, sorting, grouping, and the zoomed date range all feed one
   apply() pass; picking a row fills the detail panel.

   Months are counted from year 0 (year * 12 + month), matching the server. */

(function () {
  "use strict";

  var dataEl = document.getElementById("resume-data");
  if (!dataEl) return;

  var DATA = JSON.parse(dataEl.textContent);
  var ENTRIES = DATA.entries;
  var CATS = DATA.categories;
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var today = new Date();
  var NOW = today.getFullYear() * 12 + today.getMonth();
  var REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var byId = {};
  var catLabel = {};
  CATS.forEach(function (c) { catLabel[c.id] = c.label; });
  ENTRIES.forEach(function (e) {
    byId[e.id] = e;
    e.dated = e.start !== null;
    e.until = e.ongoing ? NOW : e.end;
    e.months = e.dated ? e.until - e.start + 1 : 0;
  });

  var $ = function (id) { return document.getElementById(id); };
  var q = $("q");
  var sortSel = $("sort");
  var groupSel = $("group");
  var chips = [].slice.call(document.querySelectorAll("#chips .chip"));
  var statusBtns = [].slice.call(document.querySelectorAll("#status button"));
  var countEl = $("count");
  var resetBtn = $("reset");
  var rowsEl = $("rows");
  var emptyEl = $("empty");
  var axisTrack = $("axis-track");
  var axisHint = $("axis-hint");
  var erasEl = $("eras");
  var detail = $("detail");
  var toolbar = $("toolbar");

  $("explorer").hidden = false;

  var state = {
    terms: [],
    cats: [],
    status: "any",
    range: null,      // [firstMonth, lastMonth] or null for everything
    sort: "recent",
    group: "none",
    sel: null
  };

  var visible = [];   // entries currently listed, in display order
  var scale = null;   // current axis scale, see makeScale()

  /* --- small helpers ------------------------------------------------------ */

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function monthLabel(m) { return MONTHS[m % 12] + " " + Math.floor(m / 12); }

  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }

  function duration(e) {
    if (!e.dated) return "";
    if (e.points && e.points.length > 1) return plural(e.points.length, "time");
    if (e.points) return "";
    var n = e.months;
    var text = n < 12
      ? plural(n, "month")
      : plural(Math.floor(n / 12), "year") + (n % 12 ? ", " + plural(n % 12, "month") : "");
    if (e.approxStart || e.approxEnd) text = "about " + text;
    return e.ongoing ? text + " so far" : text;
  }

  // Wrap every search term found in plain `text` with <mark>, escaping the rest.
  function markText(text, terms) {
    if (!terms.length) return esc(text);
    var lower = text.toLowerCase();
    var spans = [];
    terms.forEach(function (t) {
      var at = 0, found;
      while ((found = lower.indexOf(t, at)) !== -1) {
        spans.push([found, found + t.length]);
        at = found + t.length;
      }
    });
    if (!spans.length) return esc(text);
    spans.sort(function (a, b) { return a[0] - b[0]; });
    var out = "", pos = 0;
    spans.forEach(function (s) {
      if (s[1] <= pos) return;
      var from = Math.max(s[0], pos);
      out += esc(text.slice(pos, from)) + "<mark>" + esc(text.slice(from, s[1])) + "</mark>";
      pos = s[1];
    });
    return out + esc(text.slice(pos));
  }

  // Same, but inside an element that already holds markup.
  function markIn(root, terms) {
    if (!terms.length) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [], node;
    while ((node = walker.nextNode())) nodes.push(node);
    nodes.forEach(function (text) {
      var html = markText(text.nodeValue, terms);
      if (html.indexOf("<mark>") === -1) return;
      var holder = document.createElement("span");
      holder.innerHTML = html;
      var frag = document.createDocumentFragment();
      while (holder.firstChild) frag.appendChild(holder.firstChild);
      text.parentNode.replaceChild(frag, text);
    });
  }

  function snippet(e, terms) {
    var lower = e.body.toLowerCase();
    var at = -1;
    terms.some(function (t) { at = lower.indexOf(t); return at !== -1; });
    if (at === -1) return "";
    var from = Math.max(0, at - 40);
    var to = Math.min(e.body.length, at + 80);
    return (from ? "…" : "") + markText(e.body.slice(from, to), terms) + (to < e.body.length ? "…" : "");
  }

  /* --- filtering, sorting, grouping --------------------------------------- */

  function overlapsRange(e, r) {
    if (!e.dated) return false;
    if (e.points) return e.points.some(function (p) { return p[1] >= r[0] && p[0] <= r[1]; });
    return e.until >= r[0] && e.start <= r[1];
  }

  // `skip` leaves one filter out, so a chip can count what it would add.
  function passes(e, skip) {
    if (skip !== "cats" && state.cats.length &&
        !e.cats.some(function (c) { return state.cats.indexOf(c) !== -1; })) return false;
    if (state.status === "ongoing" && !e.ongoing) return false;
    if (state.status === "done" && (!e.dated || e.ongoing)) return false;
    if (state.range && !overlapsRange(e, state.range)) return false;
    for (var i = 0; i < state.terms.length; i++) {
      if (e.text.indexOf(state.terms[i]) === -1) return false;
    }
    return true;
  }

  var SORTS = {
    recent: function (a, b) { return b.until - a.until || b.start - a.start; },
    newest: function (a, b) { return b.start - a.start || b.until - a.until; },
    oldest: function (a, b) { return a.start - b.start || a.until - b.until; },
    longest: function (a, b) { return b.months - a.months || b.start - a.start; },
    alpha: function (a, b) { return a.title.localeCompare(b.title); }
  };

  function sortList(list) {
    var fn = SORTS[state.sort] || SORTS.recent;
    if (state.sort === "alpha") return list.slice().sort(fn);
    // Undated things have nowhere to go on a date sort, so they trail.
    var dated = list.filter(function (e) { return e.dated; }).sort(fn);
    var undated = list.filter(function (e) { return !e.dated; }).sort(SORTS.alpha);
    return dated.concat(undated);
  }

  function groupList(list) {
    if (state.group === "category") {
      return CATS.map(function (c) {
        return { label: c.label, cat: c.id, items: list.filter(function (e) { return e.cats[0] === c.id; }) };
      });
    }
    if (state.group === "status") {
      return [
        { label: "Ongoing", items: list.filter(function (e) { return e.ongoing; }) },
        { label: "Finished", items: list.filter(function (e) { return e.dated && !e.ongoing; }) },
        { label: "Undated", items: list.filter(function (e) { return !e.dated; }) }
      ];
    }
    if (state.group === "year") {
      var years = {};
      list.forEach(function (e) {
        var key = e.dated ? String(Math.floor(e.start / 12)) : "Undated";
        (years[key] = years[key] || []).push(e);
      });
      var keys = Object.keys(years).filter(function (k) { return k !== "Undated"; });
      keys.sort(state.sort === "oldest" ? undefined : function (a, b) { return b - a; });
      if (years.Undated) keys.push("Undated");
      return keys.map(function (k) { return { label: k, items: years[k] }; });
    }
    return [{ label: null, items: list }];
  }

  /* --- the time scale ----------------------------------------------------- */

  // Piecewise-linear month -> percent. Without a zoom, a long sparse lead-in
  // (Aikido since 2014, years before anything else) is squeezed into a narrow
  // strip so the dense recent years get the room.
  var KNEE_PCT = 14;

  function makeScale(list) {
    var dated = list.filter(function (e) { return e.dated; });
    if (!dated.length) dated = ENTRIES.filter(function (e) { return e.dated; });
    var d0, d1, knots;

    if (state.range) {
      d0 = state.range[0];
      d1 = state.range[1] + 1;
      knots = [[d0, 0], [d1, 100]];
    } else {
      var starts = dated.map(function (e) { return e.start; }).sort(function (a, b) { return a - b; });
      var lastEnd = Math.max.apply(null, dated.map(function (e) { return e.until; }));
      d0 = Math.floor(starts[0] / 12) * 12;
      d1 = Math.max(lastEnd, NOW) + 3;
      knots = [[d0, 0], [d1, 100]];
      // Find the last big gap in the earliest third of start dates.
      var knee = null;
      for (var i = 1; i < Math.ceil(starts.length / 3); i++) {
        if (starts[i] - starts[i - 1] >= 36) knee = Math.floor(starts[i] / 12) * 12;
      }
      if (knee !== null && knee - d0 >= 36 && d1 - knee >= 24) {
        knots = [[d0, 0], [knee, KNEE_PCT], [d1, 100]];
      }
    }

    function x(m) {
      if (m <= d0) return 0;
      if (m >= d1) return 100;
      for (var i = 1; i < knots.length; i++) {
        var a = knots[i - 1], b = knots[i];
        if (m <= b[0]) return a[1] + (m - a[0]) / (b[0] - a[0]) * (b[1] - a[1]);
      }
      return 100;
    }

    function inv(p) {
      p = Math.max(0, Math.min(100, p));
      for (var i = 1; i < knots.length; i++) {
        var a = knots[i - 1], b = knots[i];
        if (p <= b[1]) return a[0] + (p - a[1]) / (b[1] - a[1]) * (b[0] - a[0]);
      }
      return d1;
    }

    return { d0: d0, d1: d1, x: x, inv: inv, knee: knots.length === 3 ? knots[1][0] : null };
  }

  function setVar(el, name, value) { el.style.setProperty(name, value); }

  function renderAxis() {
    var width = axisTrack.getBoundingClientRect().width || 600;
    axisTrack.textContent = "";
    var span = scale.d1 - scale.d0;
    var lastLabel = null, lastLabelPx = -Infinity, yearShown = false;
    gridEl.textContent = "";

    function gridLine(cls, m) {
      var l = document.createElement("span");
      l.className = cls;
      setVar(l, "--x", scale.x(m) + "%");
      gridEl.appendChild(l);
    }

    function tick(m, label, cls) {
      var t = document.createElement("span");
      t.className = "tick " + cls;
      setVar(t, "--x", scale.x(m) + "%");
      var px = scale.x(m) / 100 * width;
      var isYear = cls === "tick-year";
      // A year label beats a month label that is crowding it.
      if (label && isYear && px - lastLabelPx < 40 && lastLabel && lastLabel.classList.contains("tick-month")) {
        lastLabel.textContent = "";
        lastLabel.classList.remove("has-label");
        lastLabelPx = -Infinity;
      }
      if (label && px - lastLabelPx >= (isYear ? 40 : 30) && px <= width - 30) {
        // Months before the first year label need their year spelled out.
        if (!isYear && !yearShown) label += " \u2019" + String(Math.floor(m / 12)).slice(2);
        if (isYear) yearShown = true;
        t.textContent = label;
        t.classList.add("has-label");
        lastLabel = t;
        lastLabelPx = px;
      }
      axisTrack.appendChild(t);
    }

    var firstYear = Math.ceil(scale.d0 / 12);
    var lastYear = Math.floor(scale.d1 / 12);
    for (var y = firstYear; y <= lastYear; y++) {
      var m = y * 12;
      if (span <= 36) {
        for (var k = 0; k < 12; k++) {
          var mm = m - 12 + k;
          if (k && mm > scale.d0 && mm < scale.d1) tick(mm, k % 3 === 0 ? MONTHS[k] : "", "tick-month");
        }
      }
      // In the squeezed lead-in only the edges get labels.
      var squeezed = scale.knee !== null && m > scale.d0 && m < scale.knee;
      tick(m, squeezed ? "" : String(y), "tick-year");
      if (m > scale.d0 && m < scale.d1) gridLine("gl", m);
    }
    if (span <= 36) {
      for (var k2 = 1; k2 < 12; k2++) {
        var tail = lastYear * 12 + k2;
        if (tail < scale.d1) tick(tail, k2 % 3 === 0 ? MONTHS[k2] : "", "tick-month");
      }
    }

    if (scale.knee !== null) {
      var brk = document.createElement("span");
      brk.className = "axis-break";
      brk.title = "Earlier years are squeezed together";
      setVar(brk, "--x", scale.x(scale.knee) + "%");
      axisTrack.appendChild(brk);
      gridLine("gl-squeeze", scale.knee);
    }

    if (NOW >= scale.d0 && NOW <= scale.d1) {
      var now = document.createElement("span");
      now.className = "axis-now";
      now.textContent = "now";
      setVar(now, "--x", scale.x(NOW + 0.5) + "%");
      axisTrack.appendChild(now);
      gridLine("gl-now", NOW + 0.5);
    }

    brushEl = document.createElement("span");
    brushEl.className = "brush";
    brushEl.hidden = true;
    axisTrack.appendChild(brushEl);

  }

  /* --- rows --------------------------------------------------------------- */

  var rowEls = {};

  // Year lines, the "now" line, and the squeezed lead-in, drawn once behind
  // all of the rows' tracks.
  var gridEl = document.createElement("div");
  gridEl.className = "grid";
  gridEl.setAttribute("aria-hidden", "true");

  function buildRow(e) {
    var row = document.createElement("button");
    row.type = "button";
    row.className = "row cat-" + e.cats[0];
    row.dataset.id = e.id;
    row.innerHTML =
      '<span class="row-main">' +
        '<span class="row-title"></span>' +
        '<span class="row-meta"><span class="row-period">' + esc(e.period) + "</span>" +
          '<span class="row-dots">' + e.cats.map(function (c) {
            return '<span class="swatch swatch-' + c + '" title="' + esc(catLabel[c]) + '"></span>';
          }).join("") + "</span></span>" +
        '<span class="row-snippet"></span>' +
      "</span>" +
      '<span class="track"></span>';

    var track = row.querySelector(".track");
    if (!e.dated) {
      track.innerHTML = '<span class="undated">' + esc(e.period.toLowerCase()) + "</span>";
    } else if (e.points) {
      if (e.points.length > 1) {
        var link = document.createElement("span");
        link.className = "points-link";
        track.appendChild(link);
      }
      e.points.forEach(function () {
        var p = document.createElement("span");
        p.className = "point" + (e.approxStart ? " approx" : "");
        track.appendChild(p);
      });
    } else {
      var bar = document.createElement("span");
      bar.className = "bar" +
        (e.ongoing ? " ongoing" : "") +
        (e.approxStart ? " approx-start" : "") +
        (e.approxEnd ? " approx-end" : "");
      track.appendChild(bar);
    }

    row.addEventListener("click", function () { select(e.id === state.sel ? null : e.id); });
    row.addEventListener("mouseenter", function () { showTip(e, row); });
    row.addEventListener("mouseleave", hideTip);
    return row;
  }

  function placeRow(e, row) {
    row.querySelector(".row-title").innerHTML = markText(e.title, state.terms);

    var snip = row.querySelector(".row-snippet");
    var titleHasAll = state.terms.every(function (t) { return e.title.toLowerCase().indexOf(t) !== -1; });
    snip.innerHTML = state.terms.length && !titleHasAll ? snippet(e, state.terms) : "";

    if (!e.dated) return;
    var track = row.querySelector(".track");
    if (e.points) {
      var dots = track.querySelectorAll(".point");
      e.points.forEach(function (p, i) {
        var left = scale.x(p[0]);
        setVar(dots[i], "--l", left + "%");
        setVar(dots[i], "--w", (scale.x(p[1] + 1) - left) + "%");
        dots[i].classList.toggle("out", p[1] < scale.d0 || p[0] >= scale.d1);
      });
      var link = track.querySelector(".points-link");
      if (link) {
        var a = scale.x(e.points[0][0]);
        setVar(link, "--l", a + "%");
        setVar(link, "--w", (scale.x(e.points[e.points.length - 1][0]) - a) + "%");
      }
    } else {
      var bar = track.querySelector(".bar");
      var l = scale.x(e.start);
      setVar(bar, "--l", l + "%");
      setVar(bar, "--w", (scale.x(e.until + 1) - l) + "%");
      bar.classList.toggle("clip-left", e.start < scale.d0);
      bar.classList.toggle("clip-right", e.until + 1 > scale.d1);
    }
  }

  ENTRIES.forEach(function (e) { rowEls[e.id] = buildRow(e); });

  /* --- hover tooltip on the timeline ------------------------------------- */

  var tip = document.createElement("div");
  tip.className = "tip";
  tip.hidden = true;
  document.body.appendChild(tip);

  function showTip(e, row) {
    if (!e.dated || window.matchMedia("(hover: none)").matches) return;
    var track = row.querySelector(".track").getBoundingClientRect();
    var d = duration(e);
    tip.innerHTML = "<b>" + esc(e.period) + "</b>" + (d ? " &middot; " + esc(d) : "");
    tip.hidden = false;
    var x = track.left + track.width * (scale.x(e.start) / 100);
    tip.style.left = Math.min(window.innerWidth - tip.offsetWidth - 8, Math.max(8, x)) + "px";
    tip.style.top = (track.top + window.scrollY - tip.offsetHeight - 4) + "px";
  }

  function hideTip() { tip.hidden = true; }

  /* --- apply: the one place the list is redrawn -------------------------- */

  function apply() {
    hideTip();
    var list = ENTRIES.filter(function (e) { return passes(e); });
    var groups = groupList(sortList(list));
    scale = makeScale(list);
    renderAxis();

    rowsEl.textContent = "";
    rowsEl.appendChild(gridEl);
    visible = [];
    groups.forEach(function (g) {
      if (!g.items.length) return;
      if (g.label !== null) {
        var head = document.createElement("div");
        head.className = "group-head" + (g.cat ? " cat-" + g.cat : "");
        head.innerHTML = (g.cat ? '<span class="swatch swatch-' + g.cat + '"></span>' : "") +
          esc(g.label) + ' <span class="group-count">' + g.items.length + "</span>";
        rowsEl.appendChild(head);
      }
      g.items.forEach(function (e) {
        var row = rowEls[e.id];
        placeRow(e, row);
        row.classList.toggle("is-sel", e.id === state.sel);
        row.setAttribute("aria-pressed", e.id === state.sel ? "true" : "false");
        rowsEl.appendChild(row);
        visible.push(e);
      });
    });

    emptyEl.hidden = visible.length !== 0;
    countEl.textContent = visible.length === ENTRIES.length
      ? "All " + ENTRIES.length + " entries"
      : "Showing " + visible.length + " of " + ENTRIES.length;
    resetBtn.hidden = !filtersActive();

    paintControls();
    renderDetail();
    syncUrl();
  }

  function filtersActive() {
    return state.terms.length || state.cats.length || state.status !== "any" || state.range;
  }

  function paintControls() {
    chips.forEach(function (chip) {
      var cat = chip.dataset.cat;
      var on = state.cats.indexOf(cat) !== -1;
      chip.setAttribute("aria-pressed", on ? "true" : "false");
      var n = ENTRIES.filter(function (e) { return e.cats.indexOf(cat) !== -1 && passes(e, "cats"); }).length;
      chip.querySelector(".chip-count").textContent = n;
      chip.classList.toggle("is-empty", n === 0 && !on);
    });
    statusBtns.forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.status === state.status ? "true" : "false");
    });
    sortSel.value = state.sort;
    groupSel.value = state.group;

    [].forEach.call(erasEl.querySelectorAll("button"), function (b) {
      var r = eraRange(b.dataset.era);
      var on = r === null ? state.range === null
        : state.range !== null && r[0] === state.range[0] && r[1] === state.range[1];
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });

    if (state.range) {
      axisHint.innerHTML = esc(monthLabel(state.range[0])) +
        (state.range[1] !== state.range[0] ? " &ndash; " + esc(monthLabel(state.range[1])) : "") +
        ' <button type="button" class="linkish" id="clear-range">zoom out</button>';
      $("clear-range").addEventListener("click", function () { setRange(null); });
    } else {
      axisHint.textContent = "Drag across the years to zoom";
    }
  }

  /* --- detail panel ------------------------------------------------------- */

  function entryButton(e) {
    return '<li><button type="button" class="mini" data-goto="' + e.id + '">' +
      '<span class="swatch swatch-' + e.cats[0] + '"></span>' +
      '<span class="mini-title">' + esc(e.title) + "</span>" +
      '<span class="mini-when">' + esc(e.period) + "</span></button></li>";
  }

  function aroundTheSameTime(e) {
    if (!e.dated) return [];
    var near = function (win) {
      return ENTRIES.filter(function (o) {
        return o !== e && o.dated && Math.abs(o.start - e.start) <= win;
      });
    };
    var list = near(6);
    if (list.length < 2) list = near(12);
    return list.sort(function (a, b) {
      return Math.abs(a.start - e.start) - Math.abs(b.start - e.start);
    }).slice(0, 6);
  }

  function similar(e, exclude) {
    return ENTRIES.filter(function (o) { return o !== e && exclude.indexOf(o) === -1; })
      .map(function (o) {
        var shared = o.cats.filter(function (c) { return e.cats.indexOf(c) !== -1; }).length;
        var primary = o.cats[0] === e.cats[0] ? 1 : 0;
        var gap = e.dated && o.dated ? Math.abs(o.start - e.start) : 999;
        return { o: o, score: shared + primary, gap: gap };
      })
      .filter(function (r) { return r.score >= 2; })
      .sort(function (a, b) { return b.score - a.score || a.gap - b.gap; })
      .slice(0, 4)
      .map(function (r) { return r.o; });
  }

  function renderDetail() {
    var e = state.sel ? byId[state.sel] : null;
    document.body.classList.toggle("sheet-open", !!e);
    detail.classList.toggle("is-open", !!e);
    detail.innerHTML = e ? entryDetail(e) : overview();
    if (e) markIn(detail.querySelector(".detail-body"), state.terms);
    else sizeOverviewBars();
    detail.scrollTop = 0;
  }

  function entryDetail(e) {
    var at = visible.indexOf(e);
    var nav = at === -1
      ? '<span class="detail-pos">Hidden by your filters</span>'
      : '<button type="button" class="nav-btn" data-step="-1" aria-label="Previous"' + (at === 0 ? " disabled" : "") + ">&larr;</button>" +
        '<span class="detail-pos">' + (at + 1) + " of " + visible.length + "</span>" +
        '<button type="button" class="nav-btn" data-step="1" aria-label="Next"' + (at === visible.length - 1 ? " disabled" : "") + ">&rarr;</button>";

    var html =
      '<div class="detail-top cat-' + e.cats[0] + '">' +
        '<div class="detail-nav">' + nav + "</div>" +
        '<button type="button" class="detail-close" aria-label="Close">&times;</button>' +
      "</div>" +
      '<p class="detail-when">' + esc(e.period) + (duration(e) ? ' <span>&middot; ' + esc(duration(e)) + "</span>" : "") + "</p>" +
      '<h2 class="detail-title">' + esc(e.title) + "</h2>" +
      '<div class="detail-tags">' + e.cats.map(function (c) {
        return '<button type="button" class="tag" data-filter-cat="' + c + '" title="Show only ' + esc(catLabel[c]) + '">' +
          '<span class="swatch swatch-' + c + '"></span>' + esc(catLabel[c]) + "</button>";
      }).join("") + "</div>" +
      '<div class="detail-body">' +
        (e.summary ? '<p class="detail-summary">' + esc(e.summary) + "</p>" : "") +
        e.details.map(function (d) { return "<p>" + d + "</p>"; }).join("") +
        (e.children.length ? "<ul>" + e.children.map(function (c) { return "<li>" + c + "</li>"; }).join("") + "</ul>" : "") +
        (e.links.length ? '<p class="detail-links">' + e.links.map(function (l) {
          return '<a href="' + esc(l.url) + '">' + esc(l.label) + " &rarr;</a>";
        }).join("") + "</p>" : "") +
      "</div>";

    var around = aroundTheSameTime(e);
    var alike = similar(e, around);
    if (around.length) {
      html += '<h3 class="detail-h">Around the same time</h3><ul class="mini-list">' + around.map(entryButton).join("") + "</ul>";
    }
    if (alike.length) {
      html += '<h3 class="detail-h">Similar</h3><ul class="mini-list">' + alike.map(entryButton).join("") + "</ul>";
    }
    return html;
  }

  function overview() {
    var list = visible;
    var dated = list.filter(function (o) { return o.dated; });
    var html = '<p class="detail-kicker">Overview</p>';

    if (!list.length) return html + "<p>Nothing to summarise yet &mdash; loosen the filters a little.</p>";

    var first = dated.length ? Math.floor(Math.min.apply(null, dated.map(function (o) { return o.start; })) / 12) : null;
    var lastYear = Math.floor(NOW / 12);
    var when = first !== null ? ", " + first + " to now" : "";
    if (state.range) {
      // Zoomed in: describe and chart only the zoomed stretch.
      first = Math.floor(state.range[0] / 12);
      lastYear = Math.floor(state.range[1] / 12);
      when = ", " + monthLabel(state.range[0]) +
        (state.range[1] !== state.range[0] ? " – " + monthLabel(state.range[1]) : "");
    }
    var ongoing = list.filter(function (o) { return o.ongoing; }).length;
    html += '<h2 class="detail-title">' + plural(list.length, "thing") + esc(when) + "</h2>" +
      '<p class="detail-summary">' + ongoing + " still going. Pick anything on the left for the full story, " +
      "or use these to narrow things down.</p>";

    // Categories, counted on what is listed right now.
    var counts = CATS.map(function (c) {
      return { c: c, n: list.filter(function (o) { return o.cats.indexOf(c.id) !== -1; }).length };
    }).filter(function (r) { return r.n; });
    var max = Math.max.apply(null, counts.map(function (r) { return r.n; }));
    html += '<h3 class="detail-h">By category</h3><ul class="cat-bars">' + counts.map(function (r) {
      return '<li><button type="button" data-filter-cat="' + r.c.id + '">' +
        '<span class="cat-bar-label">' + esc(r.c.label) + "</span>" +
        '<span class="cat-bar"><span class="cat-bar-fill swatch-' + r.c.id + '" data-pct="' + (r.n / max * 100) + '"></span></span>' +
        '<span class="cat-bar-n">' + r.n + "</span></button></li>";
    }).join("") + "</ul>";

    // How many things were on the go in each year.
    if (dated.length) {
      var years = [];
      for (var y = first; y <= lastYear; y++) {
        var r = [y * 12, y * 12 + 11];
        years.push({ y: y, n: dated.filter(function (o) { return overlapsRange(o, r); }).length });
      }
      var top = Math.max.apply(null, years.map(function (v) { return v.n; }));
      html += '<h3 class="detail-h">Going on each year</h3><div class="year-cols">' + years.map(function (v) {
        return '<button type="button" class="year-col" data-year="' + v.y + '" title="' + v.y + ": " + plural(v.n, "thing") + '">' +
          '<span class="year-n">' + (v.n || "") + "</span>" +
          '<span class="year-fill" data-pct="' + (v.n / top * 100) + '"></span>' +
          '<span class="year-label">' + "&rsquo;" + String(v.y).slice(2) + "</span></button>";
      }).join("") + "</div>";
    }
    return html;
  }

  // Bar lengths in the overview go through the CSSOM: the page's CSP forbids
  // inline style attributes.
  function sizeOverviewBars() {
    [].forEach.call(detail.querySelectorAll("[data-pct]"), function (el) {
      setVar(el, "--pct", el.dataset.pct + "%");
    });
  }

  detail.addEventListener("click", function (ev) {
    var t = ev.target.closest("button");
    if (!t) return;
    if (t.dataset.goto) select(t.dataset.goto, true);
    else if (t.dataset.step) step(+t.dataset.step);
    else if (t.classList.contains("detail-close")) select(null);
    else if (t.dataset.filterCat) { state.cats = [t.dataset.filterCat]; apply(); }
    else if (t.dataset.year) { var y = +t.dataset.year; setRange([y * 12, y * 12 + 11]); }
  });

  /* --- selection ---------------------------------------------------------- */

  function select(id, scroll) {
    state.sel = id && byId[id] ? id : null;
    ENTRIES.forEach(function (e) {
      var on = e.id === state.sel;
      rowEls[e.id].classList.toggle("is-sel", on);
      rowEls[e.id].setAttribute("aria-pressed", on ? "true" : "false");
    });
    renderDetail();
    syncUrl();
    if (scroll && state.sel && rowEls[state.sel].isConnected) {
      rowEls[state.sel].scrollIntoView({ block: "nearest", behavior: REDUCED ? "auto" : "smooth" });
    }
  }

  function step(delta) {
    if (!visible.length) return;
    var at = visible.indexOf(byId[state.sel]);
    var next = at === -1 ? (delta > 0 ? 0 : visible.length - 1)
      : Math.max(0, Math.min(visible.length - 1, at + delta));
    select(visible[next].id, true);
    rowEls[visible[next].id].focus({ preventScroll: true });
  }

  /* --- zooming the timeline ---------------------------------------------- */

  DATA.eras.forEach(function (era, i) {
    var b = document.createElement("button");
    b.type = "button";
    b.dataset.era = String(i);
    b.textContent = era.label;
    erasEl.appendChild(b);
  });
  var lastYearBtn = document.createElement("button");
  lastYearBtn.type = "button";
  lastYearBtn.dataset.era = "year";
  lastYearBtn.textContent = "Past year";
  erasEl.appendChild(lastYearBtn);

  function eraRange(key) {
    if (key === "all") return null;
    if (key === "year") return [NOW - 11, NOW];
    var era = DATA.eras[+key];
    return [era.start, era.end === null ? NOW : era.end];
  }

  erasEl.addEventListener("click", function (ev) {
    var b = ev.target.closest("button");
    if (b) setRange(eraRange(b.dataset.era));
  });

  function setRange(r) {
    state.range = r;
    apply();
  }

  var brushEl = null;
  var drag = null;

  function pctAt(clientX) {
    var rect = axisTrack.getBoundingClientRect();
    return (clientX - rect.left) / rect.width * 100;
  }

  axisTrack.addEventListener("pointerdown", function (ev) {
    if (ev.button !== 0) return;
    drag = { x0: ev.clientX, p0: pctAt(ev.clientX) };
    axisTrack.setPointerCapture(ev.pointerId);
    ev.preventDefault();
  });

  axisTrack.addEventListener("pointermove", function (ev) {
    if (!drag) return;
    var p = pctAt(ev.clientX);
    brushEl.hidden = Math.abs(ev.clientX - drag.x0) < 4;
    setVar(brushEl, "--l", Math.max(0, Math.min(p, drag.p0)) + "%");
    setVar(brushEl, "--w", (Math.min(100, Math.max(p, drag.p0)) - Math.max(0, Math.min(p, drag.p0))) + "%");
  });

  axisTrack.addEventListener("pointerup", function (ev) {
    if (!drag) return;
    var moved = Math.abs(ev.clientX - drag.x0) >= 4;
    var a = Math.floor(scale.inv(drag.p0));
    var b = Math.floor(scale.inv(pctAt(ev.clientX)));
    drag = null;
    if (!moved) {
      // A click picks the whole year under the pointer.
      var y = Math.floor(a / 12);
      setRange([y * 12, y * 12 + 11]);
    } else {
      setRange([Math.min(a, b), Math.max(a, b, Math.min(a, b) + 1)]);
    }
  });

  axisTrack.addEventListener("pointercancel", function () {
    drag = null;
    if (brushEl) brushEl.hidden = true;
  });

  /* --- controls ----------------------------------------------------------- */

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var cat = chip.dataset.cat;
      var at = state.cats.indexOf(cat);
      if (at === -1) state.cats.push(cat);
      else state.cats.splice(at, 1);
      apply();
    });
  });

  statusBtns.forEach(function (b) {
    b.addEventListener("click", function () { state.status = b.dataset.status; apply(); });
  });

  sortSel.addEventListener("change", function () { state.sort = sortSel.value; apply(); });
  groupSel.addEventListener("change", function () { state.group = groupSel.value; apply(); });

  var typing;
  q.addEventListener("input", function () {
    clearTimeout(typing);
    typing = setTimeout(function () {
      state.terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      apply();
    }, 80);
  });

  function resetAll() {
    q.value = "";
    state.terms = [];
    state.cats = [];
    state.status = "any";
    state.range = null;
    apply();
  }
  resetBtn.addEventListener("click", resetAll);
  $("empty-reset").addEventListener("click", resetAll);

  [].forEach.call(document.querySelectorAll(".stat"), function (s) {
    s.addEventListener("click", function () {
      if (s.dataset.entry) {
        if (visible.indexOf(byId[s.dataset.entry]) === -1) resetAll();
        select(s.dataset.entry, true);
      } else {
        state.cats = [s.dataset.cat];
        apply();
        $("explorer").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth" });
      }
    });
  });

  /* --- keyboard ----------------------------------------------------------- */

  document.addEventListener("keydown", function (ev) {
    var tag = document.activeElement && document.activeElement.tagName;
    var inField = tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA";
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;

    if (ev.key === "/" && !inField) {
      ev.preventDefault();
      q.focus();
      q.select();
    } else if (ev.key === "Escape") {
      if (document.activeElement === q && q.value) {
        q.value = "";
        state.terms = [];
        apply();
      } else if (state.sel) {
        select(null);
      }
      if (inField) document.activeElement.blur();
    } else if ((ev.key === "ArrowDown" || ev.key === "j") && (!inField || (document.activeElement === q && ev.key === "ArrowDown"))) {
      ev.preventDefault();
      step(1);
    } else if ((ev.key === "ArrowUp" || ev.key === "k") && !inField) {
      ev.preventDefault();
      step(-1);
    }
  });

  /* --- layout ------------------------------------------------------------- */

  // The axis sticks just under the toolbar, wherever the toolbar ends.
  function measureToolbar() {
    var sticky = getComputedStyle(toolbar).position === "sticky";
    setVar(document.documentElement, "--toolbar-h", (sticky ? toolbar.offsetHeight : 0) + "px");
  }

  if (window.ResizeObserver) {
    new ResizeObserver(measureToolbar).observe(toolbar);
    var lastWidth = 0;
    new ResizeObserver(function () {
      var w = axisTrack.getBoundingClientRect().width;
      if (scale && Math.abs(w - lastWidth) > 1) { lastWidth = w; renderAxis(); }
    }).observe(axisTrack);
  }
  window.addEventListener("resize", measureToolbar);
  window.addEventListener("scroll", hideTip, { passive: true });

  /* --- shareable state ---------------------------------------------------- */

  function monthParam(m) { return Math.floor(m / 12) + "-" + ("0" + (m % 12 + 1)).slice(-2); }

  function parseMonth(s) {
    var m = /^(\d{4})-(\d{2})$/.exec(s || "");
    return m ? +m[1] * 12 + (+m[2] - 1) : null;
  }

  function syncUrl() {
    var p = new URLSearchParams();
    if (state.terms.length) p.set("q", q.value.trim());
    if (state.cats.length) p.set("cat", state.cats.join(","));
    if (state.status !== "any") p.set("status", state.status);
    if (state.range) { p.set("from", monthParam(state.range[0])); p.set("to", monthParam(state.range[1])); }
    if (state.sort !== "recent") p.set("sort", state.sort);
    if (state.group !== "none") p.set("group", state.group);
    if (state.sel) p.set("sel", state.sel);
    var qs = p.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : ""));
  }

  function readUrl() {
    var p = new URLSearchParams(location.search);
    if (p.get("q")) {
      q.value = p.get("q");
      state.terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
    }
    if (p.get("cat")) {
      state.cats = p.get("cat").split(",").filter(function (c) { return catLabel[c]; });
    }
    if (["ongoing", "done"].indexOf(p.get("status")) !== -1) state.status = p.get("status");
    var from = parseMonth(p.get("from")), to = parseMonth(p.get("to"));
    if (from !== null && to !== null && from <= to) state.range = [from, to];
    if (SORTS[p.get("sort")]) state.sort = p.get("sort");
    if (["category", "year", "status"].indexOf(p.get("group")) !== -1) state.group = p.get("group");
    if (byId[p.get("sel")]) state.sel = p.get("sel");
  }

  readUrl();
  measureToolbar();
  apply();
  if (state.sel) rowEls[state.sel].scrollIntoView({ block: "center" });
})();
