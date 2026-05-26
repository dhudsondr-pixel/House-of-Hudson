"""Upload an STL/3MF/OBJ; get the best orientation and slicer settings."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import trimesh
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from print_optimizer import analyze


ALLOWED_EXTENSIONS = {".stl", ".3mf", ".obj", ".ply"}
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


app = FastAPI(title="3D Print Optimizer")


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>3D Print Optimizer</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
  h1 { margin-bottom: 0.25rem; }
  p.lead { color: #555; margin-top: 0; }
  form { border: 1px solid #ccc; border-radius: 8px; padding: 1.5rem; background: #fafafa; }
  input[type=file] { display: block; margin: 1rem 0; }
  button { background: #2b6cb0; color: white; border: 0; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; }
  pre { background: #111; color: #eee; padding: 1rem; border-radius: 6px; overflow: auto; max-height: 480px; }
  .actions a { display: inline-block; margin-right: 1rem; }
  .err { color: #b00; }
</style>
</head>
<body>
  <h1>3D Print Optimizer</h1>
  <p class="lead">Upload an STL / 3MF / OBJ / PLY. Get the best orientation, scored alternatives, and recommended slicer settings.</p>
  <form id="f" enctype="multipart/form-data">
    <label>Model file:<input type="file" name="file" accept=".stl,.3mf,.obj,.ply" required /></label>
    <button type="submit">Analyze</button>
  </form>
  <div class="actions" id="actions"></div>
  <pre id="out"></pre>
<script>
const form = document.getElementById('f');
const out = document.getElementById('out');
const actions = document.getElementById('actions');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  out.textContent = 'Analyzing...';
  actions.innerHTML = '';
  const fd = new FormData(form);
  const r = await fetch('/analyze', { method: 'POST', body: fd });
  if (!r.ok) {
    const t = await r.text();
    out.innerHTML = '<span class="err">' + t + '</span>';
    return;
  }
  const data = await r.json();
  out.textContent = JSON.stringify(data, null, 2);
  const file = fd.get('file');
  const dl = document.createElement('a');
  dl.href = '/oriented?' + new URLSearchParams({ name: file.name });
  dl.textContent = 'Download oriented STL';
  dl.id = 'dl';
  actions.appendChild(dl);
  window._lastFile = file;
});
document.addEventListener('click', async (e) => {
  if (e.target && e.target.id === 'dl') {
    e.preventDefault();
    const fd = new FormData();
    fd.append('file', window._lastFile);
    const r = await fetch('/oriented', { method: 'POST', body: fd });
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = window._lastFile.name.replace(/\\.[^.]+$/, '') + '_oriented.stl';
    a.click();
    URL.revokeObjectURL(url);
  }
});
</script>
</body>
</html>
"""


def _load_mesh(upload: UploadFile, data: bytes) -> trimesh.Trimesh:
    suffix = Path(upload.filename or "model.stl").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {suffix}")
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    loaded = trimesh.load(tmp_path, force="mesh")
    if isinstance(loaded, trimesh.Scene):
        loaded = loaded.dump(concatenate=True)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise HTTPException(400, "Could not load a mesh from the uploaded file.")
    return loaded


async def _read_upload(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File exceeds 100 MB limit.")
    if not data:
        raise HTTPException(400, "Empty upload.")
    return data


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return INDEX_HTML


@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    data = await _read_upload(file)
    mesh = _load_mesh(file, data)
    report = analyze(mesh)
    report.pop("_oriented_mesh", None)
    return JSONResponse(report)


@app.post("/oriented")
async def oriented_endpoint(file: UploadFile = File(...)) -> StreamingResponse:
    data = await _read_upload(file)
    mesh = _load_mesh(file, data)
    report = analyze(mesh)
    oriented = report["_oriented_mesh"]
    buf = io.BytesIO()
    oriented.export(buf, file_type="stl")
    buf.seek(0)
    base = Path(file.filename or "model").stem
    return StreamingResponse(
        buf,
        media_type="model/stl",
        headers={"Content-Disposition": f'attachment; filename="{base}_oriented.stl"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
