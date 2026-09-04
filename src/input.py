

from datetime import datetime, timezone

from .questions.to_schema import question_to_schema
from .questions.question_types import Question


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




def inp(form_fields: Question) -> Question:

    time_start = datetime.now(timezone.utc)
    script_name = 'gitgui script'

    config = {
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
            'WebResponse': WebResponse,
            'HTTP403': HTTP403,
            'HTTP404': HTTP404,
        },
    }

    json_schema = question_to_schema(form_fields)

    print('\npreparing webserver...\n')
    config['http_host'] = 'localhost'
    config['http_port'] = find_free_port(config['http_host'], start=PORT_START_WITH)
    config['http_protocol'] = 'http'
    config['http_address'] = (
        f'{config["http_protocol"]}://'
        f'{config["http_host"]}:{config["http_port"]}'
    )

    endpoints = {
        '/': make_root_handler(form_fields, json_schema),
        '/quit': lambda handler, *args, **argv: handler.server.shutdown() if handler.command=='POST' else None,
    }

    print(f'{STDOUT_COLOR_GREEN}starting {script_name} at {time_start}{STDOUT_COLOR_RESET}')

    print('\n')
    server = Webserver(config,is_threading=CONFIG_WEBSERVER_MULTITHREADED) # a wrapper around python http.server - no flask or django
    server.assign_handlers(endpoints)
    # print(f'{STDOUT_COLOR_GREEN}starting webserver at {config.get("http_address")}{STDOUT_COLOR_RESET}')

    launch_browser(f'{config.get("http_address")}/')
    server.run()

    # form_fields is now enriched with responses
