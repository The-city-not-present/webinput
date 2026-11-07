# Frontend & build

- The webserver is self-written (`src/lib/webserve`, submodule) — **no Flask/Django**.
- The webserver handles **all HTTP methods** (POST, etc.), even if it looks GET-only at first glance.
- The frontend may use **only `.js` and `.css`** — **no `.vue` and no `.ts`**. Assets are embedded as Python module strings under `src/endpoints/html_templates/default/assets/` and served from memory.
- The build must be possible **without Node installed**.
- `build.sh` is the single build entry point and must work after a fresh clone (it runs `git submodule update --init --recursive`).
