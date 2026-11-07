# Global CSS (`common_css.py`)

`src/endpoints/html_templates/default/assets/common_css.py` is the shared global
"skin" (embedded as a Python module string). Its rules are broad and reach all
rendered markup, so it must stay predictable and low-surprise.

- Before assuming a layout bug lives in `common_css.py`, check the widget or
  project-specific styles first (`projectspecific_css.py`, and the `widget_*`
  renderers). Most per-widget spacing/layout issues belong there, not in the
  global skin.
- Only modify `common_css.py` when a change is genuinely global (a shared token,
  a shared utility, or a rule that should apply everywhere).
- **Every change to the shared skin (`common_css.py`, and its companions
  `normalize_css.py` / `projectspecific_css.py`) must be recorded** in
  `src/endpoints/html_templates/default/assets/common_css.changelog.md` (the
  file lives alongside the assets). Log entries are reverse-chronological and
  include the date and a short reason for each change.
