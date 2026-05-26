# House of Hudson — Utilities

Two unrelated tools live in this repo:

1. [WhatsApp Group Message Scheduler](#whatsapp-group-message-scheduler)
2. [3D Print Optimizer](#3d-print-optimizer)

---

# WhatsApp Group Message Scheduler

Schedules a WhatsApp message to a group for tomorrow morning. Uses
[`pywhatkit`](https://pypi.org/project/pywhatkit/), which drives WhatsApp Web
on your computer using your S26 Ultra's linked-device session.

## How it works

`pywhatkit.sendwhatmsg_to_group` waits until the configured hour/minute,
then opens `https://web.whatsapp.com/accept?code=<GROUP_ID>` in your default
browser, pastes the message, and presses Enter. You stay logged in via the
QR code you scanned with WhatsApp on your phone.

## Setup

1. **Install Python deps**
   ```bash
   pip install -r requirements.txt
   ```
2. **Link WhatsApp Web** to your S26 Ultra
   - On the phone: `WhatsApp → Settings → Linked Devices → Link a Device`
   - On the laptop: visit https://web.whatsapp.com and scan the QR.
3. **Get the group ID**
   - On the phone, open the group → `Group info → Invite via link → Copy link`
   - The ID is the suffix after `https://chat.whatsapp.com/`
     (e.g. `Abc123XyZ...`).
4. **Edit `schedule_whatsapp.py`**
   - Set `GROUP_ID`, `MESSAGE`, `SEND_HOUR`, `SEND_MINUTE`.
5. **Run it**
   ```bash
   python schedule_whatsapp.py
   ```
   Leave the laptop awake and online until the send time.

## Caveats

- WhatsApp Web sessions expire if the phone is offline for ~14 days.
- Don't touch the mouse/keyboard while the script is sending.
- Group invite link must be enabled in the group's settings.
- For headless/server use, swap `pywhatkit` for a Selenium script with a
  persistent profile — happy to add that variant if you need it.

## Alternative (no code)

If you'd rather not run a laptop overnight, use **MacroDroid** or
**Tasker** on the S26: create a task that fires at the target time, opens
WhatsApp with the group, and uses the Accessibility service to tap Send.

---

# 3D Print Optimizer

Upload an STL / 3MF / OBJ / PLY and get:

- The **best print orientation** (rotation matrix + how the model should sit on the bed)
- **Scored alternative orientations** so you can override the pick
- A **recommended slicer settings** profile (layer height, walls, infill, speed, supports, brim)
- A **downloadable oriented STL** ready to drop into PrusaSlicer / Cura / OrcaSlicer

## How it works

The orientation algorithm is a simplified
[Tweaker-3](https://github.com/ChristophSchranz/Tweaker-3):
for each candidate "down" direction (six axis directions plus the dominant
face normals of the mesh), it rotates the model, then scores it on:

- **Bed contact area** (more is better — adhesion, less risk of tipping)
- **Overhang area** (less is better — supports cost time + waste filament)
- **Z-height** (shorter is better — print time scales with layer count)

Settings come from heuristics on bounding box, volume, smallest dimension,
and the overhang fraction of the chosen orientation. Honest caveat: the
only way to know *true* print time is to actually slice — this tool gets
you to the slicer faster with sane defaults already picked.

## Run

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:8000
```

Or with uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Use as a library

```python
import trimesh
from print_optimizer import analyze

mesh = trimesh.load("my_model.stl", force="mesh")
report = analyze(mesh)
print(report["best_orientation"])
print(report["recommended_settings"])
oriented = report["_oriented_mesh"]
oriented.export("my_model_oriented.stl")
```

## Tests

```bash
python -m pytest -q
```
