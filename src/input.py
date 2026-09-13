

from datetime import datetime, timezone
from copy import deepcopy
from threading import Thread
# import time

from .lib.qre.src.to_schema import question_to_schema
from .lib.qre.src.question_types import QuestionTypeRoot


from .lib.webserve.src.webserver import Webserver # a wrapper around python http.server - no flask or django
from .lib.webserve.src.webserver import HTTP403, HTTP404, WebResponse
from .lib.webserve.src.find_free_port import find_free_port

from .browser import WebBrowser

from .endpoints.make_handlers import (
    make_handlers as make_root_handler,
    handle_isup_net_request,
    handle_quit_net_request,
)


CONFIG_WEBSERVER_MULTITHREADED = True
PORT_START_WITH = 5279
script_version = '0.000.000'

# STDOUT_COLOR_RED    = "\033[91m"
STDOUT_COLOR_RED    = "\033[31m"
STDOUT_COLOR_RESET  = "\033[0m"
STDOUT_COLOR_GREEN  = "\033[32m"



# Getting a warning "shadows name input" but that's exactly the intent: conceptually it replaces "input"
# If you still need both, just import input as webinput
def webinput(form_fields: QuestionTypeRoot, config: dict | None = None) -> QuestionTypeRoot | None:

    time_start = datetime.now(timezone.utc)
    script_name = 'gitgui script'
    _form_fields = deepcopy(form_fields)
    if not config:
        config = {}

    config = {
        **config,
        'time_start': time_start,
        'script_name': script_name,
        'script_version': script_version,
        # 'credentials:year': f'{datetime.now().year}',
        # 'credentials:name': credentials_str,
        # 'credentials:version': script_version,

        # 'help_pages': help_md,

        'http_host': config.get('http_host'),
        'http_port': config.get('http_port'),
        'http_address': config.get('http_address'),

        'iface': {
            **config.get('iface', {}),
            'WebResponse': WebResponse,
            'HTTP403': HTTP403,
            'HTTP404': HTTP404,
        },
    }

    json_schema = question_to_schema(_form_fields)

    print('\npreparing webserver...\n')
    if not config.get('http_host'):
        config['http_host'] = 'localhost'
    if not config.get('http_port'):
        config['http_port'] = find_free_port(config['http_host'], start=PORT_START_WITH)
    if not config.get('http_protocol'):
        config['http_protocol'] = 'http'
    if not config.get('http_address'):
        config['http_address'] = (
            f'{config["http_protocol"]}://'
            f'{config["http_host"]}:{config["http_port"]}'
        )

    endpoints = {
        **config.get('endpoints', {}),
        '/': make_root_handler(_form_fields, json_schema, config),
        '/quit': handle_quit_net_request,
        '/functionality/isup.txt': handle_isup_net_request, 
    }

    print(f'{STDOUT_COLOR_GREEN}starting {script_name} at {time_start}{STDOUT_COLOR_RESET}')

    print('\n')
    server = Webserver(config, is_threading=CONFIG_WEBSERVER_MULTITHREADED) # a wrapper around python http.server - no flask or django
    server.assign_handlers(endpoints)
    # print(f'{STDOUT_COLOR_GREEN}starting webserver at {config.get("http_address")}{STDOUT_COLOR_RESET}')

    with WebBrowser(url=f'{config.get("http_address")}/',window_title=str(form_fields.label)) as wb:
        def worker():
            server.run()
        thread = Thread(target=worker, daemon=True)
        thread.start()
        def term_worker():
            thread.join()
            wb.close()
        term_thread = Thread(target=term_worker, daemon=True)
        term_thread.start()
        wb.open()
        term_thread.join()

    return _form_fields
