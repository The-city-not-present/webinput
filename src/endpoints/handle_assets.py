
import json
from urllib.parse import urlparse

from ..lib.webserve.src.webserver import WebResponse, HTTP404

from .GENERATED.ASSETS import ASSETS


_ASSET_PREFIX = '/assets/'


# Content types for the common text/web asset types; everything else is served
# as a generic binary stream. Keep this small — extend only when a real asset
# needs a specific type.
_CONTENT_TYPES = {
    '.txt': 'text/plain',
    '.html': 'text/html',
    '.htm': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.mjs': 'text/javascript',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
}


def _content_type_for(filename: str) -> str:
    suffix = filename[filename.rfind('.'):].lower() if '.' in filename else ''
    return _CONTENT_TYPES.get(suffix, 'application/octet-stream')


def handle_assets(net_request_handler, config: dict | None = None, added_data=None) -> WebResponse:
    """Serve a static asset bundled into GENERATED/ASSETS.py.

    Path is `/assets/<filename>`; `filename` is looked up in the generated
    `ASSETS` mapping. Unknown or missing assets raise HTTP404.
    """
    method = net_request_handler.command

    if method not in ('GET', 'HEAD'):
        return WebResponse(
            status_code=405,
            content_type='application/json',
            body=json.dumps({'status': 'error', 'error': f'HTTP {method} method not supported'}),
            headers=[],
        )

    path = urlparse(net_request_handler.path).path
    if not path.startswith(_ASSET_PREFIX):
        raise HTTP404(f'Asset not found: {path}')

    filename = path[len(_ASSET_PREFIX):]
    if not filename or filename not in ASSETS:
        raise HTTP404(f'Asset not found: {filename}')

    return WebResponse(
        status_code=200,
        content_type=_content_type_for(filename),
        body=ASSETS[filename],
        headers=[],
        is_binary=False,
    )
