# Project context

> Living document. Updated after every task. Read this first at the start of every task.

## What this is

`webinput` is a small, self-contained Python library that renders a
questionnaire as a local web page and returns the user's answers. The conceptual
API is `answer = webinput.ask(...)`:

```
application
    │  ask(...)
    ▼
┌───────────────┐
│ webinput      │
│ start server  │
│ generate HTML │
│ open browser  │
│ wait          │
│ receive POST  │
│ validate      │
│ stop server   │
└───────┬───────┘
        ▼
     answer
```

It is consumed two ways: as an imported module, or as a git submodule of a bigger
project (`gitgui`) that bundles everything with `pinliner` into one self-contained
`.py` file. Both ways must keep working unchanged, so the code obeys strict
portability constraints (relative imports, `__init__.py` at every level, no
standalone assets at runtime).

## Layout

```
webinput/
  __init__.py                  # public API: question types + webinput()
  README.md
  requirements.txt             # beautifulsoup4, pytest, pytest-html (pywebview optional)
  build.sh                     # venv + deps + build_assets.py (Vue bundle via py_js_bundler)
  build_assets.py              # build-time: assets_static/ -> GENERATED/ASSETS.py + bundle app.js
  dev_webinput.py              # dev backend: headless keep-alive on :5279 (status/start/…/logs)
  .clinerules/                 # AI-agent rules (+ skills/webinput-backend)
  docs/
    project-context.md         # this file
    roadmap.md
    maintenance-log.md
  src/
    input.py                   # webinput() entry point (skin selection, keep_alive)
    browser.py                 # WebBrowser: pywebview vs system-default fallback
    helper_webserve_logging.py # subscribes to webserve events, prints to console
    endpoints/                 # HTTP handlers + rendering
      make_handlers.py         # GET / (skin dispatch) + POST / and /submit + /quit + /health
      common_functions.py
      render_error.py          # generic error page (used when a skin's render() raises)
      handle_assets.py         # /assets/<name> handler (serves GENERATED/ASSETS.py)
      assets_static/           # static non-importable files (vue.esm-browser.js); source for GENERATED/
      GENERATED/               # gitignored; ASSETS.py produced by build_assets.py
      html_templates/          # skin registry (get_skin); see its __init__.py
        assets/                # shared base CSS (common_css.py, normalize_css.py)
        default/               # skin 'html': server-rendered (widgets/ + assets/)
        vue/                   # skin 'vue': render_vue.py shell + /schema endpoint
    frontend/app_js/           # Vue client app source (Vite dev + py_js_bundler entry)
      src/app.js, src/app.css, vite.config.js, package.json, index.html, jsconfig.json
    lib/
      webserve/                # submodule: self-written webserver (no Flask/Django)
      qre/                     # submodule: questionnaire data model (+ translatable)
      py_js_bundler/           # submodule: stdlib-only JS bundler (build-time only)
      json_shema.py            # empty placeholder (typo; see gotchas)
  tests/                       # development tests
```

## Key decisions

- **Rendering is pluggable "skins".** `src/endpoints/html_templates/` is a skin
  registry; `config['skin']` picks `'html'` (server-rendered) or `'vue'`
  (client-rendered, fetches `/schema`), or a caller-supplied skin object (the
  "no way to provide a skin" escape hatch). Core owns only the skin-agnostic
  contract: `GET /` (dispatch to skin), `POST /` and `POST /submit`
  (parse/validate/assign), `/quit`, `/health`, `/assets/<name>`. `/schema` is a
  *skin* endpoint contributed by the Vue skin, not core.
- **Model comes from `qre`.** The questionnaire tree (`QuestionTypeRoot`,
  `QuestionTypeBlock`, scalar/compound types, validation) lives in the `src/lib/qre`
  submodule. `webinput` only converts it to JSON Schema (`question_to_schema`),
  renders it, and writes the answer back via `form_fields.assign(payload)`.
- **The server is `webserve`**, a self-written wrapper around `http.server` — no
  Flask/Django. Handlers are callables assigned per path.
- **"Reject" is a hidden system field.** `enrich_form_fields_with_datacollection_field`
  injects a hidden `_data_collection` block with a `response_received` boolean.
  On a valid POST it is set to `True`; `webinput()` returns the populated form or
  `None` (window closed / `/quit`). This is how "user cancelled" is told apart
  from "answered" without an exception.
- **Browser is pluggable.** `src/browser.py` prefers `pywebview` (guarded import)
  and falls back to the system default browser (`launch_browser`). A missing
  `webview` package must not break the module (see `10-optional-dependencies.md`).
- **Vue is served as the unminified development ESM build.** The `/assets/`
  endpoint ships `vue.esm-browser.js` (Vue 3.5.x), vendored from the parent
  project's `assets_vendor_libs/vue/`. It is the **development** ES-module
  browser build (full dev warnings — not a `*.prod.js` build) and is **not
  minified**: webinput serves it raw because its build must work without Node,
  whereas the parent repo minifies it with `minify_js`. Swap in a `*.prod.js`
  build and/or add minification if production size/warnings matter.
- **Categories are ordered and groupable.** The `qre` model stores
  single-/multi-punch `categories` and loop `iterations` as an ordered
  `CategoryList` (optionally grouped via `CategoryGroup`); `question_to_schema`
  emits `x-categories` (ordered dict) plus a new `x-category-groups` list.
  `widget_singlepunch`/`widget_multipunch` render categories in order with group
  headings; `make_handlers` collects repeated form fields into a list so
  multi-punch checkboxes submit correctly.

## Conventions

- `.clinerules/` holds the machine rules: terminal commands, project-context,
  architecture/imports, frontend/build, testing, code style & errors, JS, CSS,
  dates & time, commit messages, GitHub issues in commits, the `common.css`
  changelog rule, optional dependencies, and submodule-commit constraints.
- `docs/maintenance-log.md` holds cross-project structural notes (import style,
  bundling/call conventions) shared with sibling projects of the same shape;
  repo-specific notes stay here.

## Last state

- **Skins registry + Vue serving path (2026-11-19).** `src/endpoints/html_templates/`
  is now a skin registry (`get_skin`); built-ins are `html` (server-rendered,
  the fallback) and `vue` (client-rendered shell + `/schema` endpoint).
  `config['skin']` selects one, or a caller-supplied skin object. Shared base
  CSS (normalize + common) hoisted to `html_templates/assets/`; the generic
  error page moved to `src/endpoints/render_error.py`.
- **Dual-run Vue dev loop (2026-11-19).** Added `py_js_bundler` submodule,
  `src/frontend/app_js/` (Vue + Vite, `npm run dev`), `dev_webinput.py`
  (headless keep-alive dev backend on :5279, verbs status/start/stop/restart/
  health/logs), `config['keep_alive']`, and the `POST /submit` alias.
  `build_assets.py` bundles `app.js` via py_js_bundler (no Node). POST body is
  now read via `request_body` (fixed a latent block in webserve's body-reader
  cleanup).
- Ordered + groupable categories: `qre`'s `categories`/`iterations` are now an
  ordered `CategoryList` (with `CategoryGroup` for grouping); the schema emits
  ordered `x-categories` and a new `x-category-groups`, and the single-/multi-punch
  widgets render groups in order. `make_handlers` now collects repeated form
  fields into a list so multi-punch checkboxes submit.
- Removed `git submodule update --init --recursive` from `build.sh` (submodule
  initialization is no longer part of the dev-env prep).
- Adopted `.clinerules/09-github-issues.md` (scan open GitHub issues and match
  them against pending changes when writing commit messages) from the sibling
  MDM-Diff-py project.
- webserve logging is now caller-side: the vendored `webserve` submodule was
  updated to a version that emits events instead of printing, and
  `src/input.py` creates the server with `logging_enabled=False` and subscribes
  `src/helper_webserve_logging.py`'s `WebserveLogger` (print-only — no in-memory
  log) to `server.events`.

## Known gotchas

- `src/lib/json_shema.py` is an empty file with a typo in its name ("shema").
  The real schema converter is `qre`'s `src/to_schema.py` (`question_to_schema`).
- CSS naming is a mix of three domains: `mdm-*` (brand), `webinput-*` (this
  library's feature domain), and the legacy `mdmreport-*` carried over from the
  parent project. See `.clinerules/06-css-guidelines.md` refinements.
- `src/browser.py`'s `WebBrowserPywebview` is half-wired (a threaded
  `webview.start` path); the system-default fallback is used whenever `webview`
  is missing.

## Build & test

- `build.sh` prepares a venv, installs deps, then runs `build_assets.py`, which
  (a) turns `assets_static/` into `GENERATED/ASSETS.py` and (b) bundles the Vue
  app (`frontend/app_js/src/app.js` → `app.js`) via `py_js_bundler` — no Node.
- `GENERATED/` is gitignored and must be (re)built before importing
  `src.endpoints.handle_assets`.
- Dev loop for the Vue skin: `python dev_webinput.py start` (headless keep-alive
  on :5279), then `npm run dev` inside `src/frontend/app_js/` (Vite proxies to
  :5279). See `.clinerules/skills/webinput-backend`.
- Development tests live in `tests/`; `tests-real-sensitive-data/` is gitignored.
  Note: `pytest` also collects the `py_js_bundler` submodule's tests.

## Open questions / next steps

See `docs/roadmap.md`.
