# Optional dependencies

- The global `requirements.txt` lists only app-wide requirements
  (`beautifulsoup4`, `pytest`, `pytest-html`).
- Optional extras must **not** be required to import the module. The canonical
  example here is `webview` (pywebview), used only by `WebBrowserPywebview`:
  `src/browser.py` guards its import (`try/except`, storing the error) and falls
  back to `WebBrowserSystemDefault`. A missing `webview` must never break the
  module or the library.
- Each module that needs an optional package guards its own import
  (`try/except`, storing the error) so the module always loads and reports a
  readable error (or degrades gracefully) at its start. No global import-error
  machinery.
- When the outer project bundles `webinput`, optional deps are installed
  best-effort by the outer build; a missing one is normal and must not break
  discovery/registration.
