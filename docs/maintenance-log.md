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
