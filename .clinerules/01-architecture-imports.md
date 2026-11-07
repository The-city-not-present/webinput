# Architecture & imports (library & pinliner constraints)

`webinput` is a small Python **library**, consumed in two ways:

1. as an imported module, and
2. as a git submodule of a bigger project (e.g. `gitgui`), where the outer
   project bundles everything with `pinliner` into a single self-contained
   `.py` file.

Everything here exists so both ways keep working unchanged.

## Imports

- Use **only relative imports** in `.py` files.
- Do **not** import from the top/outer level; there is no launcher or global
  config object here. Each module imports exactly what it needs, relatively.
- Every imported-module path **must** contain `__init__.py` at each level
  (pinliner requires this even though modern Python does not). When adding a
  package or submodule, ensure `__init__.py` exists.

## Runtime files

- The library must **not** depend on separate local files at runtime: no
  `.env`, no standalone JS/CSS/HTML assets, no `help.md`/`version.md`.
- Anything required at runtime must be **importable as a Python module**. The
  frontend skin lives as embedded module strings
  (`src/endpoints/html_templates/default/assets/*.py`) and is served from
  memory.
- This does **not** forbid reading *user-provided* files at runtime.

## Bundling & submodules

- `webinput` itself is **not** bundled here: the outer project's `build.sh`
  (via `pinliner`) produces the one-file bundle. This repo's own `build.sh` is
  a temporary dev-environment helper only.
- Reusable code is deliberately extracted into git submodules:
  `src/lib/webserve` (self-written webserver) and `src/lib/qre` (the data
  model, which in turn vendors `translatable`). Prefer submodules for
  separable pieces.
- Stick to a policy of **minimal dependencies**.
