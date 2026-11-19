---
name: webinput-backend
description: Manage the webinput dev backend on localhost:5279 — status, start, stop, restart, health, logs via dev_webinput.py (never lsof/kill/sudo).
---

# Manage the webinput dev backend

webinput is a one-shot library (`answer = webinput(...)`), so it has no
naturally-running backend. The Vite dev server for its Vue skin needs a stable
headless backend to proxy to — `dev_webinput.py` is that backend's single
source of truth.

## Always

- Run from the webinput root (`src/lib/webinput`).
- Use `python dev_webinput.py <verb>` (the venv is resolved by the script itself).
- Never use `lsof`, `kill`, `sudo`, or `taskkill` directly.

## Verbs

- `status`  — is it running and healthy? (exit 0 = running/healthy)
- `start`   — start headless keep-alive on 5279 if not already running
- `stop`    — stop it (idempotent)
- `restart` — stop + start + wait for health
- `health`  — HTTP HEAD probe of `http://localhost:5279/health` (exit 0 = HTTP 200)
- `logs`    — tail the log `.webinput-dev-backend.log`

## Dev loop (Vue skin)

1. `python dev_webinput.py start`
2. `cd src/frontend/app_js && npm install && npm run dev`
3. The Vite page proxies `/schema`, `/submit`, `/health`, `/assets` to :5279.

If `start`/`restart` reports the backend did not become healthy, read
`python dev_webinput.py logs` before changing anything else.
