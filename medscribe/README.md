# MedScribe

A 100%-local clinical scribe for Australian general practitioners.

Records a GP-patient consultation, transcribes it on-device with Whisper,
and generates a structured SOAP note (with MBS item suggestion, AU drug
names, RACGP-style red-flag surfacing, and an optional draft patient
message) using a local LLM. No audio or transcript ever leaves the box.

## Why

Existing scribes (Heidi, Lyrebird, Augmedix) send audio to the cloud.
AHPRA, RACGP, and the AU Privacy Act make that a hard sell to many
clinics. MedScribe runs entirely on the GP's hardware — or a clinic
appliance running on the same LAN.

## Hardware target

Optimised for the dev box:
- NVIDIA RTX 5090 (32 GB VRAM)
- 64 GB system RAM
- Linux (tested on kernel 6.x)

A 4090 / 4080 will also work for v1 (Qwen 2.5 32B in 4-bit). For
70B-class models you want the 5090 or a 4090 + 64+ GB RAM with CPU
offload.

## Stack

| Layer       | Choice                       | Why                                                  |
|-------------|------------------------------|------------------------------------------------------|
| UI          | Browser HTML/JS              | Beta GPs install nothing; opens in any browser       |
| Audio       | Browser `MediaRecorder`      | Native, works on Chrome/Firefox/Safari               |
| Backend     | FastAPI                      | Async, fast, simple                                  |
| ASR         | `faster-whisper` large-v3    | ~3-5× real-time on a 5090, very accurate on AU AusE  |
| LLM         | Ollama + Qwen 2.5 32B (v1)   | Fits in 32 GB VRAM at 4-bit, strong med knowledge    |
| Prompt      | `prompts/soap_au_gp.txt`     | AU-GP-specific format, MBS-aware, this is the moat   |

## Quick install

```bash
cd medscribe
./setup.sh           # installs system deps, python deps, pulls models
./run.sh             # starts the server on http://localhost:8080
```

Then open `http://localhost:8080` in any browser, hit **Record**, talk
through a fake consult, hit **Stop**, and watch the SOAP note appear.

## What works in v1

- Browser audio capture (WebM/Opus)
- Whisper large-v3 transcription (English, AU accent OK)
- AU-GP SOAP note generation with MBS item suggestion
- Copy-to-clipboard for paste into Best Practice / MedicalDirector
- Single GP, single workstation, no auth

## What's deferred to v2

- Speaker diarisation (WhisperX + pyannote — uses the doctor/patient
  speaker labels for better attribution)
- Best Practice / MedicalDirector clinical-software integration
- Multi-GP / multi-clinic auth + roles
- Audit-grade logging for medico-legal use
- TGA software-as-medical-device registration (only needed if MedScribe
  starts giving clinical decision support — scribing alone is admin
  software and exempt)
- Mental health care plan & GPMP/TCA template variants
- ICD-10-AM / SNOMED-AU coding output

## Beta plan (90 days)

1. **Week 1-4:** Use yourself, daily. Track time-per-consult vs. typing.
2. **Week 5-6:** Recruit 3-5 GP friends. Ship them the Docker image
   (`docker-compose up`). Get one signed off as the "champion" reviewer.
3. **Week 7-10:** Fix what they hate. Add the 2-3 features they ask for
   most.
4. **Week 11-12:** Set up Stripe + simple landing page. Launch at
   AU$99/mo per GP, first 50 GPs lifetime AU$79/mo.

## Files

```
medscribe/
├── README.md                       this
├── requirements.txt
├── setup.sh                        installs system deps + Python deps + models
├── run.sh                          starts the FastAPI server
├── server/
│   ├── main.py                     FastAPI app
│   ├── transcribe.py               faster-whisper wrapper
│   ├── soap.py                     Ollama LLM call
│   └── prompts/
│       └── soap_au_gp.txt          the AU-GP-specific SOAP prompt
└── ui/
    ├── index.html
    ├── app.js
    └── styles.css
```
