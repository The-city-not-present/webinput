"""Page-template ("skin") registry.

The rendering layer is pluggable: a *skin* turns the questionnaire's JSON schema
into the HTML page shown to the user. The core HTTP contract is skin-agnostic:

* ``GET /``       -> ``skin.render(json_schema, config)``
* ``POST /``      -> parse payload, ``form_fields.assign(...)``, validate, done
  (also exposed as ``POST /submit`` so a client-rendered skin can post from a
  Vite dev page without colliding with the page itself)
* ``/quit``, ``/health``, ``/assets/<name>`` -> core lifecycle/asset endpoints

Each skin may contribute extra HTTP endpoints via its ``endpoints`` mapping; the
core merges them *below* its own endpoints and below any caller-provided
``config['endpoints']``. The built-in client-rendered skin uses this to expose
``/schema`` (the questionnaire as JSON data); server-rendered skins need no
extra endpoints because they build the form directly from the schema.

``config['skin']`` selects the skin: a built-in name (``'html'``, ``'vue'``) or
an object supplied by the caller exposing ``render(json_schema, config) -> str``
and optionally ``endpoints`` — the escape hatch that lets an outer project
provide its own look without touching webinput (see README, "no way to provide
a skin").
"""

from .default.render_html_page import render as _render_html
from .vue import render as _render_vue, endpoints as _vue_endpoints


_SKINS = {
    # `default` is the original server-rendered basic-HTML form (no client
    # framework) and stays the safe fallback.
    'html': {'render': _render_html, 'endpoints': {}},
    # Thin shell; a Vue app fetches /schema and renders the form client-side.
    'vue': {'render': _render_vue, 'endpoints': _vue_endpoints},
}

DEFAULT_SKIN = 'html'


def get_skin(skin=None):
    """Resolve ``config['skin']`` into a dict with ``render`` and ``endpoints``."""
    if skin is None:
        skin = DEFAULT_SKIN
    if isinstance(skin, str):
        try:
            return _SKINS[skin]
        except KeyError:
            raise ValueError(
                f"unknown skin {skin!r}; available: {', '.join(sorted(_SKINS))}"
            ) from None

    render = getattr(skin, 'render', None)
    if not callable(render):
        raise ValueError(
            "config['skin'] must be a built-in skin name or an object exposing "
            "render(json_schema, config) -> str"
        )
    endpoints = getattr(skin, 'endpoints', {})
    return {
        'render': render,
        'endpoints': endpoints if isinstance(endpoints, dict) else {},
    }

