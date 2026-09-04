

from datetime import datetime, timezone
from copy import deepcopy

from .questions.to_schema import question_to_schema
from .questions.question_types import QuestionTypeRoot


from .lib.webserve.src.webserver import Webserver # a wrapper around python http.server - no flask or django
from .lib.webserve.src.webserver import HTTP403, HTTP404, WebResponse
from .lib.webserve.src.find_free_port import find_free_port
from .lib.webserve.src.launch_browser import launch_browser

from .endpoints.make_handlers import make_handlers as make_root_handler


CONFIG_WEBSERVER_MULTITHREADED = True
PORT_START_WITH = 5279
script_version = '0.000.000'

# STDOUT_COLOR_RED = "\033[91m"
STDOUT_COLOR_RED = "\033[31m"
STDOUT_COLOR_RESET = "\033[0m"
STDOUT_COLOR_GREEN = "\033[32m"



# Getting a warning "shadows name input" but that's exactly the intent: conceptually it replaces "input"
# If you still need both, just import input as webinput
def input(form_fields: QuestionTypeRoot, config: dict | None = None) -> QuestionTypeRoot:

    time_start = datetime.now(timezone.utc)
    script_name = 'gitgui script'
    _form_fields = deepcopy(form_fields)
    if not config:
        config = {}

    _config = {
        **config,
        'time_start': time_start,
        'script_name': script_name,
        'script_version': script_version,
        # 'credentials:year': f'{datetime.now().year}',
        # 'credentials:name': credentials_str,
        # 'credentials:version': script_version,

        # 'help_pages': help_md,

        'http_host': None,
        'http_port': None,
        'http_address': None,

        'iface': {
            **config.get('iface', {}),
            'WebResponse': WebResponse,
            'HTTP403': HTTP403,
            'HTTP404': HTTP404,
        },
    }

    json_schema = question_to_schema(_form_fields)

    print('\npreparing webserver...\n')
    if not _config.get('http_host'):
        _config['http_host'] = 'localhost'
    if not _config.get('http_port'):
        _config['http_port'] = find_free_port(_config['http_host'], start=PORT_START_WITH)
    if not _config.get('http_protocol'):
        _config['http_protocol'] = 'http'
    if not _config.get('http_address'):
        _config['http_address'] = (
            f'{_config["http_protocol"]}://'
            f'{_config["http_host"]}:{_config["http_port"]}'
        )

    endpoints = {
        **_config.get('endpoints', {}),
        '/': make_root_handler(_form_fields, json_schema),
        '/quit': lambda handler, *args, **argv: handler.server.shutdown() if handler.command=='POST' else None,
    }

    print(f'{STDOUT_COLOR_GREEN}starting {script_name} at {time_start}{STDOUT_COLOR_RESET}')

    print('\n')
    server = Webserver(_config, is_threading=CONFIG_WEBSERVER_MULTITHREADED) # a wrapper around python http.server - no flask or django
    server.assign_handlers(endpoints)
    # print(f'{STDOUT_COLOR_GREEN}starting webserver at {config.get("http_address")}{STDOUT_COLOR_RESET}')

    launch_browser(f'{_config.get("http_address")}/')
    server.run()

    return _form_fields
