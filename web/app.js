import { interpret } from "./commands.mjs";

const form = document.querySelector("#command-form");
const input = document.querySelector("#command");
const reply = document.querySelector("#reply");
const link = document.querySelector("#result-link");
const speak = document.querySelector("#speak");
const mic = document.querySelector("#microphone");
const voiceStatus = document.querySelector("#voice-status");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const result = interpret(input.value);
  reply.textContent = result.text;
  link.hidden = !result.url;
  if (result.url) {
    link.href = result.url;
    link.textContent = result.label;
  } else {
    link.removeAttribute("href");
  }
  speak.hidden = !("speechSynthesis" in window);
});
document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.command;
    form.requestSubmit();
  });
});
speak.addEventListener("click", () => {
  speechSynthesis.cancel();
  speechSynthesis.speak(new SpeechSynthesisUtterance(reply.textContent));
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
      voiceStatus.textContent = "Could not start voice input. You can type a command.";
    }
  });
  recognition.onstart = () => { voiceStatus.textContent = "Listening…"; };
  recognition.onresult = (event) => {
    input.value = event.results[0][0].transcript.trim().slice(0, input.maxLength);
    voiceStatus.textContent = "Transcript ready. Review it and select Run command.";
  };
  recognition.onnomatch = () => {
    voiceStatus.textContent = "No speech was recognized. Try again or type a command.";
  };
  recognition.onerror = () => {
    voiceStatus.textContent = "Voice input did not complete. Check permission or type a command.";
  };
  recognition.onend = () => {
    mic.disabled = false;
    if (["Listening…", "Starting microphone…"].includes(voiceStatus.textContent)) {
      voiceStatus.textContent = "No transcript received. Try again or type a command.";
    }
  };
} else {
  voiceStatus.textContent = "Voice input is unavailable here. You can type a command.";
}
