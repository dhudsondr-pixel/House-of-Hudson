# MedScribe

A clinical scribe for Australian general practitioners that records a
consult on a dedicated desk microphone, transcribes it locally with
Whisper, and generates a structured SOAP note using a local LLM. Audio
never leaves the GP's network.

## Architecture

```
┌─ Consult-room workstation (Windows, runs Best Practice) ─────────────┐
│                                                                       │
│   [Yealink CP700 / Jabra Speak]──USB──►  MedScribe agent (tray)       │
│                                                |                      │
│                                                | F8 starts/stops      │
│                                                | clipboard auto-fill  │
│                                                ▼                      │
│   Best Practice consult notes ◄──Ctrl+V── (note ready notification)   │
└──────────────────────────────────────────────|────────────────────────┘
                                               │ HTTP (LAN / VPN)
                                               │ audio → transcript → SOAP
                                               ▼
┌─ Inference server (Linux, RTX 5090) ─────────────────────────────────┐
│                                                                       │
│   FastAPI :8080                                                       │
│       ├── faster-whisper large-v3   (3-5× real-time)                  │
│       └── Ollama + Qwen 2.5 32B     (~30 tok/s, 18 GB VRAM)           │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

Two components, run on (usually) two machines:

1. **Inference server** — Python FastAPI process that owns the GPU. Lives
   on the dev box for the beta; ships as a clinic appliance for prod.
2. **Desktop agent** — Python tray app that captures audio from the
   USB mic, talks to the server over the LAN, and drops the SOAP note
   into the workstation's clipboard.

## Hardware

### Inference server

- NVIDIA RTX 5090 (32 GB VRAM) or 4090 (24 GB) — recommended
- 64 GB system RAM (allows future Llama 3.3 70B with CPU offload)
- Linux (kernel 6.x), Ubuntu / Debian / Fedora

### Workstation microphone

Lyrebird ships with the **Yealink CP700**. That's still the best default.

| Mic                        | ~AU$   | Notes                                       |
|----------------------------|--------|---------------------------------------------|
| **Yealink CP700**          | 200    | What Lyrebird uses. Omnidirectional, USB-C  |
| Jabra Speak 510            | 180    | Widely stocked, USB + Bluetooth             |
| Anker PowerConf S330       | 120    | Budget pick. Fine for desk use.             |
| Movo M1 USB                | 80     | Cheapest, OK for testing only               |

Avoid laptop built-in mics. Pickup of the patient across the desk is too
patchy for reliable transcription.

## Install — inference server

```bash
cd medscribe
./setup.sh           # ffmpeg + python deps + ollama + qwen2.5:32b (~18 GB)
./run.sh             # serves on http://0.0.0.0:8080
```

Make sure port 8080 is reachable from your beta GPs' workstations
(LAN, or expose via Tailscale / WireGuard for off-site GPs).

## Install — workstation agent

### Linux dev box (your own dogfooding)

```bash
cd medscribe
./run_agent.sh                       # first run installs deps in .venv_agent
./run_agent.sh --list-devices        # prints all audio inputs; pick yours
```

Then edit `~/.medscribe.json`:

```json
{
  "server_url": "http://localhost:8080",
  "mic_device": "Yealink",
  "hotkey": "<f8>",
  "auto_copy": true,
  "show_notification": true
}
```

### Windows beta-GP workstation

```cmd
cd medscribe
run_agent.bat                        REM first run installs deps
run_agent.bat --list-devices         REM lists Yealink etc.
```

Then edit `%USERPROFILE%\.medscribe.json`:

```json
{
  "server_url": "http://YOUR-HOME-IP:8080",
  "mic_device": "Yealink",
  "hotkey": "<f8>"
}
```

A shortcut to `run_agent.bat` in the **Startup** folder
(`Win+R` → `shell:startup`) makes the agent auto-launch on login.

## Consult workflow

1. Patient walks in. GP greets and gets verbal consent:
   > "I'm using a local AI tool to help me write your notes. The audio
   > stays on our practice server and is deleted after the note is
   > generated. Are you OK with that?"
2. GP taps **F8** → tray icon turns red, recording starts.
3. Consult proceeds normally. The GP doesn't touch the keyboard.
4. End of consult: GP taps **F8** → tray icon turns amber (processing).
5. ~30s later: desktop notification "SOAP note copied to clipboard."
6. GP clicks into Best Practice consult notes → **Ctrl+V** → review,
   edit, save.

## What's in v0.2

- ✓ Browser UI (still works, useful for testing without a USB mic)
- ✓ Tray-based desktop agent with global hotkey
- ✓ Configurable USB mic (Yealink / Jabra / etc. by name fragment)
- ✓ Clipboard auto-fill on note ready
- ✓ Desktop notification
- ✓ Persistent config at `~/.medscribe.json`
- ✓ AU-GP SOAP prompt with MBS item suggestion, AU drug names,
  RACGP-style red flags, draft patient portal message

## What's deferred to v0.3

- Speaker diarisation (WhisperX + pyannote — needs HuggingFace ToS
  acceptance, defer to keep beta install simple)
- Best Practice "Word Processor" template auto-load (clipboard works
  fine for v0.2)
- Settings GUI (currently edit `~/.medscribe.json` by hand)
- Foot-pedal support (start/stop via VEC Infinity / Olympus pedal)
- Audit-grade local logging for medico-legal use
- Mental health care plan + GPMP/TCA template variants of the prompt

## Beta plan (90 days)

| Week  | Goal                                                              |
|-------|-------------------------------------------------------------------|
| 1-2   | Dr Hudson uses agent daily. Track time saved vs typing.            |
| 3-4   | Iterate on `soap_au_gp.txt` prompt — fix every wrong output.       |
| 5-6   | Recruit 3-5 GP friends. Each gets Yealink + agent installer.       |
| 7-8   | Weekly feedback. Track must-fix vs. nice-to-have.                  |
| 9-10  | Add the top 2-3 most-requested features. Ship v0.3.                |
| 11-12 | Stripe + landing page. Launch at AU$99/mo (first 50 GPs AU$79).    |

## Files

```
medscribe/
├── README.md                         this
├── requirements.txt                  server deps
├── requirements_agent.txt            agent deps
├── setup.sh                          install inference server
├── run.sh                            start inference server
├── run_agent.sh                      start agent (Linux)
├── run_agent.bat                     start agent (Windows)
├── server/
│   ├── main.py                       FastAPI app (3 endpoints)
│   ├── transcribe.py                 faster-whisper large-v3 wrapper
│   ├── soap.py                       Ollama call
│   └── prompts/soap_au_gp.txt        AU-GP-specific SOAP prompt
├── agent/
│   ├── main.py                       CLI entrypoint
│   ├── config.py                     persistent agent config
│   ├── recorder.py                   sounddevice mic capture
│   ├── hotkey.py                     pynput global hotkey
│   ├── tray.py                       pystray system tray icon
│   ├── notify.py                     plyer desktop notification + clipboard
│   └── client.py                     HTTP client for the server
└── ui/                               legacy browser UI (still works)
    ├── index.html
    ├── app.js
    └── styles.css
```
