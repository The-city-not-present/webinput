# Frontend & build

- The webserver is self-written (`src/lib/webserve`, submodule) — **no Flask/Django**.
- The webserver handles **all HTTP methods** (POST, etc.), even if it looks GET-only at first glance.
- The frontend may use **only `.js` and `.css`** — **no `.vue` and no `.ts`**.
- The rendering layer is pluggable **skins** under `src/endpoints/html_templates/`
  (see the registry in its `__init__.py`): `html` (server-rendered, embedded Python
  module strings under `html_templates/default/assets/`) and `vue` (a thin shell +
  a client app in `src/frontend/app_js/`). `config['skin']` selects one; callers
  may also pass their own skin object.
- Shared base assets (normalize + common CSS) live under
  `src/endpoints/html_templates/assets/`; skin-specific assets live inside each skin.
- Non-importable static files (e.g. `.txt`, the vendored `vue.esm-browser.js`) live
  under `src/endpoints/assets_static/`; `build.sh` (via `build_assets.py`) turns them
  into the importable, gitignored `src/endpoints/GENERATED/ASSETS.py`, served by the
  `/assets/<name>` endpoint. `build_assets.py` also bundles the Vue app
  (`src/frontend/app_js/src/app.js` → `app.js`) via `py_js_bundler`.
- The build must be possible **without Node installed** (py_js_bundler is stdlib-only).
  Node/Vite may be used only to speed up Vue development (`npm run dev` in
  `src/frontend/app_js/`, proxying to `dev_webinput.py` on :5279).
- `build.sh` is the single build entry point and must work after a fresh clone.
