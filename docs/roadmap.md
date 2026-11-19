# Roadmap

## Exact plans

- Migrate the widget renderers (`html_templates/default/widgets/`) to Vue
  components in `src/frontend/app_js/` — single-punch first (project selector),
  then text/number/boolean/datetime/multipunch. `boolean`/`loop`/`grid` are
  currently "not implemented" stubs to build in Vue. Keep the `html` skin as the
  fallback throughout.
- Flip the default skin to `'vue'` once parity + tests land; keep `'html'`
  config-gated.
- Add development tests under `tests/` for `webinput()`, the skin registry,
  `/schema`, keep-alive, and the POST/validation flow.
- Finish or remove the half-wired `WebBrowserPywebview` path in `src/browser.py`.

## Things to consider, reminders, random thoughts

- Serve the shared base CSS (normalize/common) via `/assets/*.css` (from
  `assets_static/`) so the Vite dev `index.html` gets the same base skin as the
  bundle, instead of inlining it only in the server shells.
- `pytest` currently also collects the `py_js_bundler` submodule's tests; add
  `testpaths` scoping if that becomes noisy.
- Delete or rename the empty `src/lib/json_shema.py` placeholder (typo "shema").
- Decide whether `webinput-*` classes should be normalized under the `mdm-`
  brand, or kept as this library's feature domain (see
  `.clinerules/06-css-guidelines.md`).
- Consider extracting the HTML/widget rendering into its own submodule if it
  grows further (kept behind the `render(...)` seam so it can be lifted later).
