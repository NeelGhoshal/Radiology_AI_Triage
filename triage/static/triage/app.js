"use strict";

const MODALITY = { XR: "X-ray", CT: "CT", MR: "MRI" };
const VERDICT = { confirmed: "Confirmed", rejected: "Rejected" };
const $ = (id) => document.getElementById(id);

const state = { findings: [], selected: null, modality: "", busy: false, loaded: false };

/* Builds an element. Text is always added as text nodes, so API data can't inject markup. */
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "onclick") node.onclick = value;
    else node.setAttribute(key, value);
  }
  node.append(...children);
  return node;
}

const percent = (n) => `${Math.round(n * 100)}%`;
const examName = (f) => `${MODALITY[f.modality] || f.modality}, ${f.body_part.toLowerCase()}`;

async function api(path, options) {
  let response;
  try {
    response = await fetch(path, { headers: { Accept: "application/json" }, ...options });
  } catch {
    throw new Error("The server didn't respond. Check your connection, then try again.");
  }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.error || body.detail || `The server answered with status ${response.status}.`);
    error.status = response.status;
    throw error;
  }
  return body;
}

function csrfToken() {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

let toastTimer;
function toast(message) {
  const node = $("toast");
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove("show"), 4500);
}

const visible = () => state.findings.filter((f) => !state.modality || f.modality === state.modality);

function keepOrPickSelection() {
  const findings = visible();
  if (!findings.some((f) => f.id === state.selected)) {
    state.selected = findings.length ? findings[0].id : null;
  }
}

/* ---- Film ---- */

function drawVertebrae() {
  for (let i = 0; i < 13; i++) {
    const width = 8 + i * 0.5;
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    const attrs = { x: 100 - width / 2, y: 91 + i * 10.4, width, height: 8, rx: 2 };
    for (const [key, value] of Object.entries(attrs)) rect.setAttribute(key, value);
    $("vertebrae").append(rect);
  }
}

function highlightRegion(bodyPart) {
  const map = $("body-map");
  let matched = false;
  for (const group of map.querySelectorAll("[data-region]")) {
    const on = group.dataset.region === bodyPart;
    group.classList.toggle("on", on);
    matched = matched || on;
  }
  map.setAttribute("aria-label", matched
    ? `Diagram of the body with the ${bodyPart.toLowerCase()} highlighted`
    : "Diagram of the body");
  $("region-caption").textContent = matched ? "Diagram of the scanned area" : "";
}

function filmMessage(title, note, actionLabel, action) {
  for (const id of ["film-id", "film-exam", "film-urgency"]) $(id).textContent = "";
  $("film-title").textContent = title;
  $("film-note").textContent = note;
  $("film-confidence").hidden = true;
  $("verdict").hidden = true;
  $("film-action").hidden = false;
  $("film-action").textContent = actionLabel;
  $("film-action").onclick = action;
  highlightRegion(null);
}

function renderFilm(animate) {
  const finding = state.findings.find((f) => f.id === state.selected);
  if (!finding) {
    if (state.modality && state.findings.length) {
      filmMessage(`No ${MODALITY[state.modality]} findings waiting`, "Other scan types still have findings to review.",
        "Show all scan types", () => setModality(""));
    } else {
      filmMessage("Worklist clear", "Every AI finding has been reviewed.", "Check for new findings", load);
    }
    return;
  }
  $("film-id").textContent = finding.accession_id;
  $("film-exam").textContent = examName(finding);
  $("film-urgency").textContent = finding.critical ? "Critical finding" : "Routine finding";
  $("film-urgency").classList.toggle("critical", finding.critical);
  $("film-title").textContent = finding.label;
  $("film-percent").textContent = percent(finding.confidence);
  $("film-confidence").querySelector(".wedge").style.setProperty("--value", `${finding.confidence * 100}%`);
  $("film-note").textContent = "";
  $("film-confidence").hidden = false;
  $("verdict").hidden = false;
  $("film-action").hidden = true;
  highlightRegion(finding.body_part);

  if (animate) {
    const film = $("film");
    film.classList.remove("next");
    void film.offsetWidth; // restart the animation
    film.classList.add("next");
  }
}

/* ---- Queue ---- */

function row(finding) {
  const wedge = el("div", { class: "wedge wedge-row", "aria-hidden": "true" }, el("i"));
  wedge.style.setProperty("--value", `${finding.confidence * 100}%`);
  const button = el("button",
    { type: "button", class: "row", "data-id": finding.id, onclick: () => select(finding.id) },
    el("b", {}, finding.label),
    el("small", {}, `${examName(finding)}, ${finding.accession_id}`),
    el("span", { class: "score" }, wedge, el("span", {}, percent(finding.confidence))));
  if (finding.id === state.selected) button.setAttribute("aria-current", "true");
  return el("li", {}, button);
}

function renderQueue() {
  const findings = visible();
  $("queue-title").textContent = `${findings.length} waiting for review`;
  const groups = [
    ["critical", "Critical", findings.filter((f) => f.critical)],
    ["routine", "Routine", findings.filter((f) => !f.critical)],
  ].filter(([, , items]) => items.length);

  $("queue").replaceChildren(...(groups.length
    ? groups.map(([kind, name, items]) => el("div", { class: `group ${kind}` },
        el("h3", { class: kind }, `${name} (${items.length})`),
        el("ul", {}, ...items.map(row))))
    : [el("p", { class: "empty" }, "Nothing waiting.")]));
}

function select(id) {
  state.selected = id;
  renderFilm(true);
  for (const button of document.querySelectorAll(".row")) {
    if (Number(button.dataset.id) === id) button.setAttribute("aria-current", "true");
    else button.removeAttribute("aria-current");
  }
  if (matchMedia("(max-width: 60rem)").matches) {
    const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
    $("film").scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "start" });
  }
}

function setModality(modality) {
  state.modality = modality;
  for (const button of document.querySelectorAll("[data-modality]")) {
    button.setAttribute("aria-pressed", String(button.dataset.modality === modality));
  }
  if (!state.loaded) return;
  keepOrPickSelection();
  renderQueue();
  renderFilm(false);
}

/* ---- Track record ---- */

async function loadRecord() {
  const keys = ["", "XR", "CT", "MR"];
  try {
    const stats = await Promise.all(keys.map((key) => api(`/findings/stats/${key ? `?modality=${key}` : ""}`)));
    $("record").replaceChildren(...stats.map((s, i) => {
      const rate = s.confirmation_rate;
      const fill = el("i");
      fill.style.width = rate === null ? "0" : `${rate * 100}%`;
      return el("div", { class: "rate" },
        el("span", { class: "name" }, keys[i] ? MODALITY[keys[i]] : "All scans"),
        el("div", { class: "bar", "aria-hidden": "true" }, fill),
        el("b", {}, rate === null ? "" : percent(rate)),
        el("small", {}, rate === null ? "No reviews yet" : `${s.confirmed} of ${s.reviewed} confirmed`));
    }));
  } catch {
    $("record").replaceChildren(el("p", { class: "empty" }, "Couldn't load the review totals. Reload the page to try again."));
  }
}

/* ---- Actions ---- */

async function load() {
  loadRecord();
  try {
    state.findings = await api("/findings/worklist/");
    state.loaded = true;
    keepOrPickSelection();
    renderQueue();
    renderFilm(false);
  } catch (error) {
    filmMessage("Couldn't load the worklist", error.message, "Try again", load);
  }
}

function setBusy(busy) {
  state.busy = busy;
  for (const b of document.querySelectorAll("[data-verdict], .row, [data-modality]")) b.disabled = busy;
}

async function review(verdict) {
  const finding = state.findings.find((f) => f.id === state.selected);
  if (!finding || state.busy) return;
  setBusy(true);
  try {
    await api(`/findings/${finding.id}/review/`, {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
      body: JSON.stringify({ status: verdict }),
    });
    toast(`${VERDICT[verdict]}: ${finding.label}, ${finding.accession_id}`);
    const index = visible().findIndex((f) => f.id === finding.id);
    state.findings = state.findings.filter((f) => f.id !== finding.id);
    const rest = visible();
    const next = rest[index] || rest[rest.length - 1];
    state.selected = next ? next.id : null;
    renderQueue();
    renderFilm(true);
    $("film-title").focus({ preventScroll: true });
    loadRecord();
  } catch (error) {
    if (error.status === 400 || error.status === 404) {
      toast(`${finding.label}, ${finding.accession_id}: ${error.message}`);
      await load(); // someone else reviewed it, so this list is out of date
    } else {
      toast(`Review not saved. ${error.message}`);
    }
  } finally {
    setBusy(false);
  }
}

drawVertebrae();
for (const b of document.querySelectorAll("[data-verdict]")) b.addEventListener("click", () => review(b.dataset.verdict));
for (const b of document.querySelectorAll("[data-modality]")) b.addEventListener("click", () => setModality(b.dataset.modality));
load();
