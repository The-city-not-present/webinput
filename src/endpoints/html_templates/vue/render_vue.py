"""Vue skin: serve a thin HTML shell; a Vue app fetches /schema and renders.

The shell inlines the shared base CSS (normalize + common) and loads the
bundled ``/assets/app.js`` as an ES module. The bundle leaves ``import ... from
'vue'`` bare, so the import map resolves it to the vendored browser build at
``/assets/vue.esm-browser.js``.
"""

import html as _html

from ..assets import common_css, normalize_css


_IMPORTMAP = (
    '<script type="importmap">'
    '{ "imports": { "vue": "./assets/vue.esm-browser.js" } }'
    '</script>'
)


def render(json_schema: dict, config: dict | None = None) -> str:
    title = _html.escape(f'{json_schema.get("title") or "WebInput"}')
    return f'''<!doctype html>
<html lang="">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>{normalize_css}</style>
  <style>{common_css}</style>
  <title>{title}</title>
  {_IMPORTMAP}
  <script type="module" src="/assets/app.js"></script>
</head>
<body class="mdmreportpage webinput page-webinput page-webinput-home mdmreportpage-page-webinput mdmreportpage-page-webinput-home">
<div class="container">
  <h1>{title}</h1>
  <div class="error error-banner" id="errorbanner"></div>
  <div id="webinput_app"></div>
</div>
</body>
</html>
'''
