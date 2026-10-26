"use strict";

const state = {
  options: null,
  uploadId: null,
  lastFile: null,
};

const $ = (id) => document.getElementById(id);

async function init() {
  const res = await fetch("/api/options");
  state.options = await res.json();
  buildTaskSelect();
  buildLanguageSelect();
  buildTags();
  setDefaults();
  refreshStatus();
  setInterval(refreshStatus, 5000);

  $("task").addEventListener("change", renderDynamicControls);
  $("loadTxt").addEventListener("click", loadTxtFile);
  $("uploadPrompt").addEventListener("click", uploadPrompt);
  $("speak").addEventListener("click", speak);
  $("download").addEventListener("click", download);
  document.querySelectorAll(".presets button").forEach((b) =>
    b.addEventListener("click", () => applyPreset(b.dataset.preset))
  );
  renderDynamicControls();
}

function buildTaskSelect() {
  const sel = $("task");
  sel.innerHTML = "";
  state.options.tasks.forEach((t) => {
    const o = document.createElement("option");
    o.value = t.value;
    o.textContent = t.label;
    sel.appendChild(o);
  });
}

function buildLanguageSelect() {
  const sel = $("language");
  sel.innerHTML = "";
  state.options.languages.forEach((l) => {
    const o = document.createElement("option");
    o.value = l.value;
    o.textContent = l.label;
    sel.appendChild(o);
  });
  sel.value = "en";
}

function buildTags() {
  const box = $("tags");
  box.innerHTML = "";
  state.options.paralinguistic_tags.forEach((tag) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = tag;
    b.addEventListener("click", () => insertAtCursor($("text"), tag));
    box.appendChild(b);
  });
}

function setDefaults() {
  const d = state.options.defaults;
  setRange("cfg", d.cfg, "cfgVal");
  setRange("sigma", d.sigma, "sigmaVal");
  setRange("temperature", d.temperature, "tempVal");
  setRange("maxLength", d.max_length, "maxLenVal");
}

function setRange(id, val, labelId) {
  $(id).value = val;
  if (labelId) $(labelId).textContent = val;
  $(id).addEventListener("input", () => { $(labelId).textContent = $(id).value; });
}

function renderDynamicControls() {
  const task = $("task").value;
  const taskDef = state.options.tasks.find((t) => t.value === task);
  const box = $("dynamicControls");
  box.innerHTML = "";

  const add = (labelText, el) => {
    const wrap = document.createElement("label");
    wrap.className = "field";
    const span = document.createElement("span");
    span.textContent = labelText;
    wrap.appendChild(span);
    wrap.appendChild(el);
    box.appendChild(wrap);
  };

  const controls = taskDef ? taskDef.controls : [];
  if (controls.includes("speed")) {
    add("Speed", selectFrom("speed", state.options.speed));
  }
  if (controls.includes("pitch")) {
    add("Pitch", selectFrom("pitch", state.options.pitch));
  }
  if (controls.includes("volume")) {
    add("Volume", selectFrom("volume", state.options.volume));
  }
  if (controls.includes("emotion")) {
    add("Emotion", selectFrom("emotion", state.options.emotions));
  }
  if (controls.includes("dialect")) {
    add("Dialect", selectFrom("dialect", state.options.dialects));
  }
  if (controls.includes("style")) {
    const ta = document.createElement("textarea");
    ta.id = "style"; ta.rows = 3;
    ta.placeholder = "Describe the voice, e.g. 'A mature, steady male documentary narrator with clear enunciation and a relaxed pace.'";
    add("Voice design style", ta);
  }
  if (controls.includes("instruction")) {
    const ta = document.createElement("textarea");
    ta.id = "instruction"; ta.rows = 3;
    ta.placeholder = "Natural-language delivery instruction, e.g. 'Speak in a warm, intimate storytelling voice.'";
    add("Free-form instruction", ta);
  }
  if (controls.includes("ip")) {
    add("Built-in voice", selectFrom("ip", state.options.builtin_voices.map((v) => v.value),
      state.options.builtin_voices.map((v) => v.label)));
  }
}

function selectFrom(id, items, labels) {
  const sel = document.createElement("select");
  sel.id = id;
  // ``items`` may be a list of strings or {value,label} dicts. When dicts are
  // passed, ``labels`` is ignored and the dict label is used for display while
  // the dict value is sent to the model.
  const useDicts = items.length && typeof items[0] === "object";
  items.forEach((it, i) => {
    const o = document.createElement("option");
    if (useDicts) {
      o.value = it.value;
      o.textContent = it.label;
    } else {
      o.value = it;
      o.textContent = labels ? labels[i] : it;
    }
    sel.appendChild(o);
  });
  return sel;
}

function insertAtCursor(el, text) {
  const start = el.selectionStart, end = el.selectionEnd;
  el.value = el.value.slice(0, start) + text + el.value.slice(end);
  el.focus();
  el.selectionStart = el.selectionEnd = start + text.length;
}

function loadTxtFile() {
  const f = $("txtFile").files[0];
  if (!f) return;
  const reader = new FileReader();
  reader.onload = () => { $("text").value = reader.result; };
  reader.readAsText(f);
}

async function uploadPrompt() {
  const f = $("promptAudio").files[0];
  if (!f) { $("promptStatus").textContent = "Choose an audio file first."; return; }
  const fd = new FormData();
  fd.append("file", f);
  $("promptStatus").textContent = "Uploading…";
  const res = await fetch("/api/upload_prompt", { method: "POST", body: fd });
  const data = await res.json();
  if (res.ok) {
    state.uploadId = data.upload_id;
    $("promptStatus").textContent = `Uploaded: ${data.filename} (id ${data.upload_id})`;
  } else {
    $("promptStatus").textContent = `Upload failed: ${data.error}`;
  }
}

function collectParams() {
  const task = $("task").value;
  const p = {
    task,
    text: $("text").value.trim(),
    language_id: $("language").value,
    // Speaker embedding only makes sense when a reference clip was uploaded.
    // Without one, sending use_spk_emb=true makes MingTTS reject the request.
    use_spk_emb: state.uploadId ? $("useSpkEmb").checked : false,
    use_zero_spk_emb: false,
    cfg: parseFloat($("cfg").value),
    sigma: parseFloat($("sigma").value),
    temperature: parseFloat($("temperature").value),
    max_length: parseInt($("maxLength").value, 10),
    no_trim_silence: $("noTrim").checked,
    raw_text: $("rawText").checked,
  };
  if (state.uploadId) { p.upload_id = state.uploadId; }
  if ($("promptText").value.trim()) p.prompt_text = $("promptText").value.trim();

  const taskDef = state.options.tasks.find((t) => t.value === task);
  const controls = taskDef ? taskDef.controls : [];
  controls.forEach((c) => {
    const el = $(c);
    if (el && el.value) p[c] = el.value;
  });
  return p;
}

async function speak() {
  const errBox = $("error");
  errBox.classList.add("hidden");
  if (!$("text").value.trim()) {
    return showError("Please enter some text to speak.");
  }
  const params = collectParams();
  $("progress").classList.remove("hidden");
  $("speak").disabled = true;
  $("download").disabled = true;
  try {
    const res = await fetch("/api/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    const data = await res.json();
    if (!res.ok) { showError(data.error || "Synthesis failed."); return; }
    $("player").src = data.audio_url;
    $("player").play().catch(() => {});
    $("download").disabled = false;
    state.lastFile = data.filename;
    $("meta").innerHTML =
      `sample_rate: ${data.sample_rate} Hz<br>duration: ${data.duration_seconds} s<br>file: ${data.filename}`;
  } catch (e) {
    showError("Network error: " + e.message);
  } finally {
    $("progress").classList.add("hidden");
    $("speak").disabled = false;
  }
}

function download() {
  if (state.lastFile) window.location.href = `/api/download/${state.lastFile}`;
}

function showError(msg) {
  const errBox = $("error");
  errBox.textContent = msg;
  errBox.classList.remove("hidden");
}

async function refreshStatus() {
  try {
    const res = await fetch("/api/status");
    const s = await res.json();
    const el = $("status");
    if (s.loaded) {
      el.className = "status ok";
      el.textContent = `model loaded · ${s.sample_rate} Hz`;
    } else {
      el.className = "status bad";
      el.textContent = "model not loaded (loads on first speak)";
    }
  } catch {
    $("status").textContent = "server offline";
  }
}

function applyPreset(name) {
  const set = (id, val) => { const e = $(id); if (e) e.value = val; };
  if (name === "clone") { set("task", "TTS"); }
  if (name === "design") { set("task", "VOICE_DESIGN"); }
  if (name === "freeform") { set("task", "FREEFORM"); }
  if (name === "builtin") { set("task", "IP"); }
  if (name === "emotion") { set("task", "EMOTION"); }
  if (name === "multilingual") { set("task", "MULTILINGUAL"); set("language", "ja"); }
  renderDynamicControls();
}

init();
