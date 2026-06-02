// MedScribe UI: record audio in the browser, send to backend, render note.

const recordBtn = document.getElementById("record-btn");
const timerEl = document.getElementById("timer");
const statusEl = document.getElementById("status");
const fileInput = document.getElementById("file-input");
const output = document.getElementById("output");
const noteContent = document.getElementById("note-content");
const transcriptContent = document.getElementById("transcript-content");
const noteTiming = document.getElementById("note-timing");
const transcriptTiming = document.getElementById("transcript-timing");

let mediaRecorder = null;
let chunks = [];
let startedAt = 0;
let timerHandle = null;

function fmtTime(secs) {
    const m = Math.floor(secs / 60).toString().padStart(2, "0");
    const s = Math.floor(secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
}

function setStatus(text) {
    statusEl.textContent = text || "";
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        chunks = [];
        mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };
        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach((t) => t.stop());
            const blob = new Blob(chunks, { type: "audio/webm" });
            await submitAudio(blob);
        };
        mediaRecorder.start();
        startedAt = Date.now();
        timerHandle = setInterval(() => {
            timerEl.textContent = fmtTime((Date.now() - startedAt) / 1000);
        }, 250);
        recordBtn.textContent = "■ Stop & generate note";
        recordBtn.classList.add("recording");
        setStatus("Recording…");
    } catch (err) {
        setStatus(`Mic error: ${err.message}`);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
    }
    clearInterval(timerHandle);
    recordBtn.textContent = "● Start recording";
    recordBtn.classList.remove("recording");
}

async function submitAudio(blob) {
    setStatus("Transcribing & generating note… (this can take 30-90s)");
    output.classList.remove("hidden");
    noteContent.textContent = "Working…";
    transcriptContent.textContent = "Working…";

    const fd = new FormData();
    fd.append("audio", blob, "consult.webm");
    try {
        const r = await fetch("/api/scribe", { method: "POST", body: fd });
        if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
        const data = await r.json();
        noteContent.textContent = data.note;
        transcriptContent.textContent = data.transcript;
        transcriptTiming.textContent = `transcribed in ${data.timings.transcribe_s}s`;
        noteTiming.textContent = `note generated in ${data.timings.soap_s}s`;
        setStatus("Done.");
    } catch (err) {
        noteContent.textContent = `Error: ${err.message}`;
        setStatus("");
    }
}

recordBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
    } else {
        startRecording();
    }
});

fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    setStatus(`Uploading ${file.name}…`);
    await submitAudio(file);
});

// Tabs
document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
});

// Copy buttons
document.getElementById("copy-note").addEventListener("click", async () => {
    await navigator.clipboard.writeText(noteContent.textContent);
    setStatus("Note copied to clipboard.");
});
document.getElementById("copy-transcript").addEventListener("click", async () => {
    await navigator.clipboard.writeText(transcriptContent.textContent);
    setStatus("Transcript copied to clipboard.");
});
