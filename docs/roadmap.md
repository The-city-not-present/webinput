# Roadmap

## Exact plans

- Fill in `build.sh` so it does real work (pinliner bundling for the outer
  project, running tests) — currently a temporary stub. Asset generation is now
  implemented: `build.sh` runs `build_assets.py` to turn
  `src/endpoints/assets_static/` into `src/endpoints/GENERATED/ASSETS.py`.
- Add development tests under `tests/` covering `webinput()`, the endpoint
  handlers, and widget rendering.
- Finish or remove the half-wired `WebBrowserPywebview` path in `src/browser.py`.

## Things to consider, reminders, random thoughts

- Delete or rename the empty `src/lib/json_shema.py` placeholder (typo "shema").
- Decide whether `webinput-*` classes should be normalized under the `mdm-`
  brand, or kept as this library's feature domain (see
  `.clinerules/06-css-guidelines.md`).
- Consider extracting the HTML/widget rendering into its own submodule if it
  grows further.
