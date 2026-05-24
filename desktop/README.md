# Desktop App (Tauri)

Wraps the web UI in a native window and can auto-start the Python API.

## Prerequisites

- [Rust](https://rustup.rs/) (for Tauri build)
- Node.js
- Python venv with package installed (`pip install -e .` from project root)
- Web dependencies (`cd ../web && npm install`)

## Development

1. Start Ollama (optional): `ollama serve`
2. From project root, ensure API can run: `uvicorn api.main:app --port 8000`
3. From this folder:

```powershell
npm install
npm run tauri dev
```

`tauri dev` runs the Next.js dev server (port 3000) and opens the desktop window. Start the API separately in another terminal:

```powershell
..\scripts\start-api.ps1
```

## Production build

```powershell
npm run tauri build
```

Requires `../web` production build (`npm run build` in web folder).

## Alternative: use start-all script

From project root:

```powershell
.\scripts\start-all.ps1
```

Then open http://localhost:3000 in your browser — same UI without Tauri.
