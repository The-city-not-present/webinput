
from dataclasses import dataclass
from typing import BinaryIO # , Callable
from collections.abc import Iterable, Callable # for type annotations

from urllib.parse import urlparse, parse_qs # to detect path within endpoints
import json # for responding, obviously


from .common_functions import JSONEncoder, delay_term, print_stacktrace

from .render_html_page import render as render_home, render_fallback







@dataclass
class WebResponse:
    status_code: int
    content_type: str
    body: str | bytes | bytearray | BinaryIO | Iterable[bytes|bytearray]
    headers: list[tuple[str,str]]
    # cookies # can be passed in headers, no need for separate field
    is_binary: bool = False
    is_done: bool = False
    is_stream: bool = False
    options: dict | None = None



def make_handlers(form_fields, json_schema) -> Callable[..., WebResponse]:

    job_status = {
        "response_received": False,
    }

    def handle_root_path(net_request_handler, config: dict, added_data=None) -> WebResponse:
        method = net_request_handler.command
        path_with_query = net_request_handler.path
        path_parsed = f'{urlparse(path_with_query).path}'
        path_parts = path_parsed.split('/')
        params = parse_qs(urlparse(path_with_query).query)
        params_flattened = {key: values[-1] for key, values in params.items()}

        if path_parsed == '/':
            if method == 'HEAD':
                return WebResponse(
                    status_code=200,
                    content_type='text/plain',
                    body = b'',
                    headers=[],
                )
            elif method == 'GET':

                try:
                    html_page = render_home(json_schema)
                    return WebResponse(
                        status_code=200,
                        content_type='text/html',
                        body = html_page,
                        is_binary = False,
                        headers=[],
                    )
                except Exception as e:
                    print_stacktrace(e)
                    html_page = render_fallback(e)
                    return WebResponse(
                        status_code=503,
                        content_type='text/html',
                        body = html_page,
                        is_binary = False,
                        headers=[],
                    )

            elif method == 'POST':

                if job_status["response_received"]:
                    net_request_handler.server.shutdown()
                    delay_term()
                    return WebResponse(
                        status_code = 400,
                        content_type='application/json',
                        body=json.dumps({'status': 'error', 'error': 'response already received, not accepting anymore'}, cls=JSONEncoder),
                        is_binary=False,
                        headers=[],
                    )

                # Read payload
                # Read Content-Length header
                length = int(net_request_handler.headers.get("Content-Length",0))
                content_type = str(net_request_handler.headers.get("Content-Type", ""))
                # Read exactly that many bytes
                body = net_request_handler.rfile.read(length)
                payload = {}
                if content_type.lower().startswith('application/json'.lower()):
                    # Convert bytes -> str -> Python object
                    payload = json.loads(body) # expect dict with name: value pairs for all inputs
                elif content_type.lower().startswith('application/x-www-form-urlencoded'.lower()):
                    response_parsed = parse_qs(body.decode("utf-8"))
                    if any(len(values) > 1 for values in response_parsed.values()):
                        # Bad request
                        return WebResponse(
                            status_code=415,
                            content_type='application/json',
                            body=json.dumps({'status': 'error', 'error': f'Duplicates in fields: {repr([values for values in response_parsed.values() if len(values) > 1])}'}, cls=JSONEncoder),
                            headers=[],
                        )
                    payload = {
                        key: values[0]
                        for key, values in response_parsed.items()
                    }
                else:
                    return WebResponse(
                        status_code=400,
                        content_type='application/json',
                        body=json.dumps({'status': 'error', 'error': 'Unkown network request type: Content-type == {content_type}'}, cls=JSONEncoder),
                        headers=[],
                    )

                try:
                    form_fields.assign(payload)
                except form_fields.ValidationError as e:
                    return WebResponse(
                        status_code = 415,
                        content_type = 'application/json',
                        body = json.dumps({
                            'status': 'error',
                            'error': f'{e}',
                            'path': f'{e.path}',
                        }, cls=JSONEncoder),
                        headers = [],
                    )

                job_status["response_received"] = True
                delay_term(net_request_handler)

                return WebResponse(
                    status_code = 202,
                    content_type = 'application/json',
                    body = json.dumps({'status': 'done', 'message': f'accepted'},
                                    cls=JSONEncoder),
                    headers = [],
                )

            else:
                return WebResponse(
                    status_code=405,
                    content_type='application/json',
                    body=json.dumps({'status': 'error', 'error': f'handler for {method} {path_parsed} is not recognized'},
                                    cls=JSONEncoder),
                    headers=[],
                )
        else:
            return WebResponse(
                status_code=404,
                content_type='application/json',
                body=json.dumps({'status': 'error', 'error': f'not found'},
                                cls=JSONEncoder),
                headers=[],
            )

    return handle_root_path
