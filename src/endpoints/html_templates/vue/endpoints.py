"""Extra endpoints contributed by the Vue skin.

``/schema`` serves the questionnaire as JSON data for client-side rendering.
It is a *skin* concern, not core: server-rendered skins build the form directly
from the schema and never need it over HTTP. The core computes the schema and
passes it via ``config['json_schema']``; this handler just serializes it.
"""

import json

from ....lib.webserve.src.webserver import WebResponse


def handle_schema(net_request_handler, config: dict | None = None, added_data=None) -> WebResponse:
    method = net_request_handler.command
    if method != 'GET':
        return WebResponse(
            status_code=405,
            content_type='application/json',
            body=json.dumps({
                'status': 'error',
                'error': f'HTTP {method} method not supported',
            }),
            headers=[],
        )
    config = config or {}
    return WebResponse(
        status_code=200,
        content_type='application/json',
        body=json.dumps(config.get('json_schema', {})),
        headers=[],
    )


endpoints = {
    '/schema': handle_schema,
}
