# Dev backend tooling

- The webinput dev backend runs on `localhost:5279`; the Vite dev server for the
  Vue skin proxies `/schema`, `/submit`, `/health`, `/assets` to it.
- Manage the dev backend **only** via `python dev_webinput.py` (`status` / `start` /
  `stop` / `restart` / `health` / `logs`) from the webinput root — see the
  `webinput-backend` skill.
- Never use `lsof` / `kill` / `sudo` / `taskkill` to find or kill the backend process.
- If the backend isn't running, start it headlessly with `python dev_webinput.py start`
  before working on the Vue frontend.
