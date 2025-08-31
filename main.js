const isProd =
  typeof window !== "undefined" &&
  window.location.hostname.endsWith(".vercel.app");

const API = isProd
  ? "https://email-classifier-ysyc.onrender.com"
  : "http://127.0.0.1:8000";

const $ = (sel) => document.querySelector(sel);
const btn = $("#btnProcess");
const loader = $("#loading");
const toast = $("#toast");
const resultCard = $("#resultCard");
const categoryBadge = $("#categoryBadge");
const confidence = $("#confidence");
const confBar = $("#confBar");
const replyBox = $("#replyBox");
const debugJson = $("#debugJson");
const envLabel = $("#envLabel");
const fileInput = $("#fileInput");
const fileList = $("#fileList");
const btnCopy = $("#btnCopy");
const textInput = $("#textInput");

const batchSection = $("#batchResults");
const batchContainer = $("#batchContainer");

let currentFiles = [];

function renderFileList() {
  fileList.innerHTML = "";
  currentFiles.forEach((file, idx) => {
    const li = document.createElement("li");
    li.className = "file-chip";
    li.innerHTML = `
      <span>${file.name}</span>
      <button title="Remover" data-idx="${idx}">✕</button>
    `;
    fileList.appendChild(li);
  });
}

fileList.addEventListener("click", (e) => {
  if (e.target.tagName.toLowerCase() === "button") {
    const idx = Number(e.target.getAttribute("data-idx"));
    currentFiles = currentFiles.filter((_, i) => i !== idx);
    renderFileList();
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files?.length) {
    if (textInput.value.trim()) {
      textInput.value = "";
      showToast("Texto limpo: usando arquivos para processamento.");
    }
    currentFiles.push(...Array.from(fileInput.files));
    renderFileList();
    fileInput.value = "";
  }
});

textInput.addEventListener("input", () => {
  if (textInput.value.trim() && currentFiles.length) {
    currentFiles = [];
    renderFileList();
    showToast("Arquivos removidos: usando o texto para processamento.");
  }
});

async function fetchJSON(url, options) {
  const resp = await fetch(url, options);
  const raw = await resp.text();
  let data = {};
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    console.warn("Resposta não-JSON:", raw);
  }
  if (!resp.ok) {
    throw new Error(data?.detail || raw || `HTTP ${resp.status}`);
  }
  return data;
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const j = await fetchJSON(`${API}/health`);
    envLabel && (envLabel.textContent = j.app_env || j.env || "local");
  } catch (_) {
    envLabel && (envLabel.textContent = "offline");
  }
});

function showToast(msg, isError = false) {
  toast.textContent = msg;
  toast.classList.toggle("error", isError);
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

function setLoading(on) {
  btn.disabled = on;
  loader.classList.toggle("hidden", !on);
}

function renderFileList() {
  fileList.innerHTML = "";
  currentFiles.forEach((file, idx) => {
    const li = document.createElement("li");
    li.className = "file-chip";
    li.innerHTML = `
      <span>${file.name}</span>
      <button title="Remover" data-idx="${idx}">✕</button>
    `;
    fileList.appendChild(li);
  });
}

fileList.addEventListener("click", (e) => {
  if (e.target.tagName.toLowerCase() === "button") {
    const idx = Number(e.target.getAttribute("data-idx"));
    currentFiles = currentFiles.filter((_, i) => i !== idx);
    renderFileList();
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files?.length) {
    currentFiles.push(...Array.from(fileInput.files));
    renderFileList();
    fileInput.value = "";
  }
});

function setSingleResult({ category, confidence: conf, suggestedReply }, raw) {
  resultCard.classList.remove("hidden");
  batchSection.classList.add("hidden");

  categoryBadge.textContent = category || "—";
  categoryBadge.classList.remove("ok", "warn");
  if ((category || "").toLowerCase().startsWith("produt")) {
    categoryBadge.classList.add("ok");
  } else {
    categoryBadge.classList.add("warn");
  }

  if (typeof conf === "number") {
    const pct = Math.max(0, Math.min(100, conf * 100));
    confidence.textContent = `${pct.toFixed(1)}%`;
    confBar.style.width = `${pct}%`;
  } else {
    confidence.textContent = "—";
    confBar.style.width = "0%";
  }

  replyBox.textContent = suggestedReply || "—";
  debugJson.textContent = JSON.stringify(raw, null, 2);
}

function setBatchResults(items) {
  batchSection.classList.remove("hidden");
  resultCard.classList.add("hidden");
  batchContainer.innerHTML = "";

  items.forEach((it) => {
    const div = document.createElement("div");
    div.className = "batch-item";
    if (it.error) {
      div.innerHTML = `
        <div class="name">${it.filename}</div>
        <div class="err">Erro: ${it.error}</div>
      `;
    } else {
      const pct =
        typeof it.confidence === "number"
          ? (it.confidence * 100).toFixed(1)
          : "—";
      div.innerHTML = `
        <div class="name">${it.filename}</div>
        <div>Categoria: <strong>${it.category}</strong> (${pct}%)</div>
        <div class="bar" style="margin:8px 0 6px;"><div class="bar-fill" style="width:${pct}%"></div></div>
        <div style="font-size: 13px; opacity:.9;">${
          it.suggestedReply || "—"
        }</div>
      `;
    }
    batchContainer.appendChild(div);
  });
}

if (btnCopy) {
  btnCopy.addEventListener("click", async () => {
    const text = replyBox.textContent || "";
    if (!text.trim()) return;
    try {
      await navigator.clipboard.writeText(text);
      showToast("Resposta copiada ✔");
    } catch {
      showToast("Falha ao copiar.", true);
    }
  });
}

btn.addEventListener("click", async () => {
  const text = $("#textInput").value.trim();

  if (!currentFiles.length && !text) {
    showToast("Envie arquivos .txt/.pdf ou cole o texto do email.", true);
    return;
  }

  setLoading(true);
  try {
    if (currentFiles.length) {
      const fd = new FormData();
      currentFiles.forEach((f) => fd.append("files", f, f.name));
      const raw = await fetchJSON(`${API}/classify/uploads`, {
        method: "POST",
        body: fd,
      });
      setBatchResults(raw);
      showToast("Arquivos processados ✔");
      return;
    }

    const raw = await fetchJSON(`${API}/classify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    setSingleResult(raw, raw);
    showToast("Texto processado ✔");
  } catch (err) {
    console.error(err);
    showToast(err.message || "Erro de rede ou CORS.", true);
  } finally {
    setLoading(false);
  }
});
