# Frontend & build

- The webserver is self-written (`src/lib/webserve`, submodule) — **no Flask/Django**.
- The webserver handles **all HTTP methods** (POST, etc.), even if it looks GET-only at first glance.
- The frontend may use **only `.js` and `.css`** — **no `.vue` and no `.ts`**. Assets are embedded as Python module strings under `src/endpoints/html_templates/default/assets/` and served from memory.
- Non-importable static files (e.g. `.txt`) live under `src/endpoints/assets_static/`; `build.sh` (via `build_assets.py`) turns them into the importable, gitignored `src/endpoints/GENERATED/ASSETS.py`, served by the `/assets/<name>` endpoint.
- The build must be possible **without Node installed**.
- `build.sh` is the single build entry point and must work after a fresh clone (it runs `git submodule update --init --recursive`).
