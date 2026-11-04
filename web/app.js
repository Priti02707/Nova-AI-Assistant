import { interpret } from "./commands.mjs";

const form = document.querySelector("#message-form");
const input = document.querySelector("#message");
const log = document.querySelector("#conversation");
const status = document.querySelector("#request-status");
const service = document.querySelector("#service-status");
const send = document.querySelector("#send");
const clear = document.querySelector("#clear");
const speak = document.querySelector("#speak");
const mic = document.querySelector("#microphone");
const voiceStatus = document.querySelector("#voice-status");
const history = [];
let latestReply = "";

function appendMessage(role, text, links = []) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  const heading = document.createElement("h2");
  heading.textContent = role === "user" ? "You" : "Nova";
  const content = document.createElement("p");
  content.textContent = text;
  message.append(heading, content);
  for (const { url, label } of links) {
    if (typeof url !== "string" || !url.startsWith("https://") || typeof label !== "string") continue;
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.textContent = label;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    message.append(anchor);
  }
  log.append(message);
  log.scrollTop = log.scrollHeight;
}

async function requestReply(message) {
  const local = interpret(message);
  if (local) {
    return { text: local.text, links: local.url ? [{ url: local.url, label: local.label }] : [] };
  }
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
    signal: AbortSignal.timeout(28_000),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Nova could not complete this request.");
  }
  if (typeof data.text !== "string" || !data.text.trim()) throw new Error("Nova returned an empty reply.");
  return data;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || send.disabled) return;
  send.disabled = true;
  clear.disabled = true;
  status.textContent = "Nova is responding…";
  input.value = "";
  if (!log.querySelector("article")) log.replaceChildren();
  appendMessage("user", message);
  try {
    const { text, links } = await requestReply(message);
    const sources = Array.isArray(links) ? links : [];
    appendMessage("assistant", text, sources);
    history.push({ role: "user", content: message }, { role: "assistant", content: text.slice(0, 3500) });
    if (history.length > 8) history.splice(0, 2);
    latestReply = [text, ...sources.map(({ label }) => label)].join("\n");
    speak.hidden = !("speechSynthesis" in window);
    status.textContent = "";
  } catch (error) {
    status.textContent = error instanceof SyntaxError || error instanceof TypeError || error.name === "TimeoutError"
      ? "Nova's online service could not be reached. Try again or use an offline command."
      : error.message;
    if (!input.value) input.value = message;
  } finally {
    send.disabled = false;
    clear.disabled = false;
  }
});

document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => {
    if (send.disabled) return;
    input.value = button.dataset.message;
    form.requestSubmit();
  });
});
clear.addEventListener("click", () => {
  history.length = 0;
  latestReply = "";
  log.replaceChildren();
  status.textContent = "New conversation started.";
  speak.hidden = true;
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  input.value = "";
  input.focus();
});
speak.addEventListener("click", () => {
  speechSynthesis.cancel();
  speechSynthesis.speak(new SpeechSynthesisUtterance(latestReply));
});

fetch("/api/chat", { signal: AbortSignal.timeout(5000) })
  .then((response) => {
    if (!response.ok) throw new Error("Service unavailable");
    return response.json();
  })
  .then(({ conversation_enabled: enabled }) => {
    service.textContent = enabled
      ? "AI chat is online. Send a message to start."
      : "AI chat is disabled. Everyday commands, weather, and tech headlines are available.";
  })
  .catch(() => {
    service.textContent = "Online service is unavailable. Offline commands still work.";
  });

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (Recognition && window.isSecureContext) {
  const recognition = new Recognition();
  recognition.lang = navigator.language || "en-US";
  mic.hidden = false;
  mic.addEventListener("click", () => {
    mic.disabled = true;
    voiceStatus.textContent = "Starting microphone…";
    try {
      recognition.start();
    } catch {
      mic.disabled = false;
      voiceStatus.textContent = "Could not start voice input. You can type a message.";
    }
  });
  recognition.onstart = () => { voiceStatus.textContent = "Listening…"; };
  recognition.onresult = (event) => {
    input.value = event.results[0][0].transcript.trim().slice(0, input.maxLength);
    voiceStatus.textContent = "Transcript ready. Review it and select Send.";
  };
  recognition.onnomatch = () => {
    voiceStatus.textContent = "No speech was recognized. Try again or type a message.";
  };
  recognition.onerror = () => {
    voiceStatus.textContent = "Voice input did not complete. Check permission or type a message.";
  };
  recognition.onend = () => {
    mic.disabled = false;
    if (["Listening…", "Starting microphone…"].includes(voiceStatus.textContent)) {
      voiceStatus.textContent = "No transcript received. Try again or type a message.";
    }
  };
} else {
  voiceStatus.textContent = "Voice input is unavailable here. You can type a message.";
}
