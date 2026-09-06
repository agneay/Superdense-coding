/*
 * app.js
 *
 * Frontend for the superdense coding web demo. Talks to the Flask API
 * in webapp/app.py, which calls the exact same simulation/superdense_coding.py
 * functions as the terminal demo (simulation/demo_cli.py) and the physical
 * rig (hardware/pi_superdense_demo.py) -- this file only owns presentation.
 *
 * Mirrors two terminal features:
 *   - demo_cli.py: "Send" runs one message, "Run all 4" runs every
 *     combination and prints the same summary table.
 *   - pi_superdense_demo.py's keyboard mock: "Cycle" steps through
 *     00/01/10/11 like the 'c' key, "Send" like the 's' key, and the
 *     LED/LCD panel re-creates the same idle/sending/decoded states.
 */

const GATE_LED_IDS = { I: "ledGateI", X: "ledGateX", Z: "ledGateZ", ZX: "ledGateZX" };
const ALL_LED_IDS = ["ledEntangled", "ledSent", "ledMatch", ...Object.values(GATE_LED_IDS)];

const state = {
  combinations: ["00", "01", "10", "11"],
  sendAnimationSeconds: 1.2,
  selectedIndex: 0,
};

const el = (id) => document.getElementById(id);

function setLcd(id, line1, line2 = "") {
  const lines = el(id).querySelectorAll(".lcd-line");
  lines[0].textContent = line1;
  lines[1].textContent = line2;
}

function setLed(id, on) {
  el(id).classList.toggle("on", Boolean(on));
}

function allLedsOff() {
  ALL_LED_IDS.forEach((id) => setLed(id, false));
}

function highlightSelected() {
  document.querySelectorAll(".msg-btn").forEach((btn, i) => {
    btn.classList.toggle("selected", i === state.selectedIndex);
  });
}

function renderMessageButtons() {
  const container = el("messageButtons");
  container.innerHTML = "";
  state.combinations.forEach((msg, i) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = msg;
    btn.className = "msg-btn";
    btn.addEventListener("click", () => {
      state.selectedIndex = i;
      showIdleState();
    });
    container.appendChild(btn);
  });
  highlightSelected();
}

function showIdleState() {
  highlightSelected();
  const msg = state.combinations[state.selectedIndex];
  setLcd("lcdAlice", `Select: ${msg}`, "Press SEND ->");
  setLcd("lcdBob", "Waiting for", "Alice...");
  allLedsOff();
  el("resultPanel").hidden = true;
}

function renderResult(r) {
  const panel = el("resultPanel");
  panel.hidden = false;
  panel.querySelector("tbody").innerHTML = `
    <tr><th>Alice's classical bits</th><td>b1=${r.bit1} b0=${r.bit0}</td></tr>
    <tr><th>Gate Alice applies</th><td>${r.gate_name}</td></tr>
    <tr><th>Resulting Bell state</th><td>${r.bell_state_name}</td></tr>
    <tr><th>Bob decodes</th><td>b1=${r.decoded_bit1} b0=${r.decoded_bit0}</td></tr>
    <tr><th>Match</th><td class="${r.success ? "yes" : "no"}">${r.success ? "YES" : "NO (unexpected!)"}</td></tr>
  `;
}

function sleep(seconds) {
  return new Promise((resolve) => setTimeout(resolve, seconds * 1000));
}

async function send() {
  const msg = state.combinations[state.selectedIndex];
  const sendBtn = el("sendBtn");
  sendBtn.disabled = true;

  try {
    // "Entangled" + "in transit" stages, same order as pi_superdense_demo.py's on_send().
    setLed("ledEntangled", true);
    setLcd("lcdAlice", `Alice: ${msg}`, "Sending...");
    setLed("ledSent", true);
    el("ledSent").classList.add("blinking");

    await sleep(state.sendAnimationSeconds);

    el("ledSent").classList.remove("blinking");
    setLed("ledSent", false);

    const res = await fetch(`/api/run?bits=${msg}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Request failed (${res.status})`);
    }
    const result = await res.json();

    Object.entries(GATE_LED_IDS).forEach(([gate, id]) => setLed(id, gate === result.gate_name));
    setLcd("lcdAlice", `Alice: ${msg}`, `Gate: ${result.gate_name}`);
    setLcd("lcdBob", `Bob decoded: ${result.decoded_message}`, result.success ? "MATCH!" : "MISMATCH");
    setLed("ledMatch", result.success);

    renderResult(result);
    el("circuitImg").src = `/api/circuit.png?bits=${msg}&t=${Date.now()}`;
  } catch (err) {
    setLcd("lcdBob", "Error", String(err.message || err).slice(0, 16));
  } finally {
    sendBtn.disabled = false;
  }
}

async function runAll() {
  const runAllBtn = el("runAllBtn");
  runAllBtn.disabled = true;
  try {
    const res = await fetch("/api/run_all");
    const results = await res.json();
    const tbody = document.querySelector("#allResultsTable tbody");
    tbody.innerHTML = results
      .map(
        (r) => `
      <tr>
        <td>${r.message}</td>
        <td>${r.gate_name}</td>
        <td>${r.bell_state_name}</td>
        <td>${r.decoded_message}</td>
        <td class="${r.success ? "yes" : "no"}">${r.success ? "YES" : "NO"}</td>
      </tr>
    `
      )
      .join("");
    el("allResultsPanel").hidden = false;
  } finally {
    runAllBtn.disabled = false;
  }
}

async function loadConfig() {
  const res = await fetch("/api/config");
  const data = await res.json();
  state.combinations = data.combinations;
  state.sendAnimationSeconds = data.send_animation_seconds;
  renderMessageButtons();
  showIdleState();
}

el("cycleBtn").addEventListener("click", () => {
  state.selectedIndex = (state.selectedIndex + 1) % state.combinations.length;
  showIdleState();
});
el("sendBtn").addEventListener("click", send);
el("runAllBtn").addEventListener("click", runAll);

loadConfig();
