# Maintenance log

> Cross-project maintenance notes. Entries here capture **structural** changes
> that apply to any project sharing this repo's shape — a self-contained library
> vendored as a git submodule, bundled upstream via `pinliner`, using relative
> imports and Python-module-embedded assets.
>
> Repo-specific changes do **not** belong here; they stay in the commit history
> and `docs/project-context.md`. Anything recorded here is meant to be repeatable
> in other projects of the same structure.
>
> Entries are ordered **newest first**.

## How to read an entry

Each entry is a section whose heading reads like a commit subject: it states the
**intent** of the change and **where** the change happens (component/module).
Inside, answer the questions needed to repeat the same update elsewhere:

- **When** — date/time requested and implemented.
- **What & why** — the request and the reasoning behind the chosen approach.
- **Input** — a sample of the code/file **before** the change.
- **Output** — a sample of the code/file **after** the change.
- **Repeat** — a checklist of the exact steps to apply the same convention in
  another project.

---

## Webinput: serve static assets from a generated `GENERATED/` module

- **Requested:** 2026-11-07
- **Implemented:** 2026-11-07
- **Where:** `src/endpoints/` (handler + registration), `build_assets.py`, `build.sh`.

### What & why

`webinput` needed to serve static, non-importable files (e.g. `.txt`) over its
self-written webserver without depending on separate files at runtime (which
would clash with pinliner's single-file bundle). The parent project's pattern is
reused: static sources live in a `assets_static/` folder (no `__init__.py` — not
importable), a build-time script turns them into an importable
`GENERATED/ASSETS.py` Python module, and a handler imports that module and serves
it. `GENERATED/` is gitignored and recreated on every build.

### Repeat

1. Put static files under `<pkg>/assets_static/` (no `__init__.py`).
2. Add a stdlib-only build script that scans `assets_static/` and writes
   `<pkg>/GENERATED/ASSETS.py` with `ASSETS = {relpath: content}` plus an empty
   `__init__.py` (so `GENERATED/` is a package pinliner will bundle).
3. Add a handler module that does `from .GENERATED.ASSETS import ASSETS` and
   serves a matching path (raise `HTTP404` for unknown names).
4. Register it in the `endpoints` dict with a `re.compile(r'/assets/.+')` key
   (the webserver's endpoint matcher supports regex keys).
5. Call the build script from `build.sh` — both the library's own `build.sh`
   and the outer bundler's `build.sh` (before pinliner runs).

---

## Project bootstrap: adopt `.clinerules/`, `docs/` and a stub `build.sh`

- **Requested:** 2026-11-07
- **Implemented:** 2026-11-07
- **Where:** repo root (`webinput/`).

### What & why

`webinput` previously carried no machine rules, no context docs, and no build
entry point. To match the parent project's shape, the same overall patterns are
adopted: a `.clinerules/` directory with the *relevant* subset of the parent's
rules (adapted to a library/submodule rather than a standalone app), a `docs/`
folder with `project-context.md`, `roadmap.md` and `maintenance-log.md`, and a
temporary `build.sh` that only prepares the dev environment.

### Input (before)

```
webinput/
  __init__.py
  README.md
  requirements.txt
  src/
  tests/           # empty
  # no .clinerules/, no docs/, no build.sh
```

### Output (after)

```
webinput/
  __init__.py
  README.md
  requirements.txt
  build.sh                 # temporary dev-env helper
  .clinerules/             # adapted subset of the parent's rules
  docs/
    project-context.md
    roadmap.md
    maintenance-log.md
  src/
  tests/
```

### Repeat

1. Copy the parent project's `.clinerules/` files that apply; adapt any that
   reference parent-specific paths (entry points, bundle names, asset locations).
2. Seed `docs/project-context.md` from the actual source tree (layout, decisions,
   gotchas), `docs/roadmap.md` from the "Exact plans / Things to consider"
   template, and `docs/maintenance-log.md` from this header + guide.
3. Add a `build.sh` that is a minimal dev-environment helper (venv + deps +
   submodules) until real bundling is needed.
