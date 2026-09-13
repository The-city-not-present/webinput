

from datetime import datetime, timezone
from copy import deepcopy
from threading import Thread
# import time

from .lib.qre.src.to_schema import question_to_schema
from .lib.qre.src.question_types import (
    QuestionTypeRoot,
    QuestionTypeBlock,
    QuestionTypeBool,
)


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




def enrich_form_fields_with_datacollection_field(form_fields: QuestionTypeBlock):
    """Mutates"""
    if not isinstance(form_fields,QuestionTypeRoot):
        raise Exception('webinput: make_handlers: form_fields passed must be a root element, instance of QuestionTypeRoot')
    if '_data_collection' not in [ f.name for f in form_fields.fields ]:
        form_fields.fields.insert(0,QuestionTypeBlock(
            name = '_data_collection',
            label = '_data_collection, hidden system field',
            fields = [],
            is_hidden = True,
            is_system = True,
            is_required = False,
        ))
    datacollection_form_field: QuestionTypeBlock = next(iter([ f for f in form_fields.fields if f.name=='_data_collection' ]))
    if 'response_received' not in [ f.name for f in datacollection_form_field.fields ]:
        datacollection_form_field.fields.append(QuestionTypeBool(
            name = 'response_received',
            label = '_data_collection.response_received, hidden system field',
            is_required = False,
        ))
    datacollection_responsereceived_form_field: QuestionTypeBool = next(iter([ f for f in datacollection_form_field.fields if f.name=='response_received' ]))
    datacollection_responsereceived_form_field.assign(False,{})





# Getting a warning "shadows name input" but that's exactly the intent: conceptually it replaces "input"
# If you still need both, just import input as webinput
def webinput(form_fields: QuestionTypeRoot, config: dict | None = None) -> QuestionTypeRoot | None:

    time_start = datetime.now(timezone.utc)
    script_name = 'webinput'

    # print(f'{STDOUT_COLOR_GREEN}starting {script_name} at {time_start}{STDOUT_COLOR_RESET}')

    form_fields = deepcopy(form_fields)
    enrich_form_fields_with_datacollection_field(form_fields) # mutates

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

    json_schema = question_to_schema(form_fields)

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
        '/': make_root_handler(form_fields, json_schema, config),
        '/quit': handle_quit_net_request,
        '/functionality/isup.txt': handle_isup_net_request, 
    }

    print('\n')
    server = Webserver(config, is_threading=CONFIG_WEBSERVER_MULTITHREADED) # a wrapper around python http.server - no flask or django
    server.assign_handlers(endpoints)
    # print(f'{STDOUT_COLOR_GREEN}starting webserver at {config.get("http_address")}{STDOUT_COLOR_RESET}')

    with WebBrowser(url=f'{config.get("http_address")}/',window_title=str(form_fields.label)) as wb:
        def worker():
            server.run()
        def webbrowser_window_closed():
            server_httpserver_obj = server.server
            if server_httpserver_obj:
                server_httpserver_obj.shutdown()
        def reject_watcher():
            wb.events.close.wait()
            webbrowser_window_closed()
        thread_reject_watcher = Thread(target=reject_watcher, daemon=True)
        thread_reject_watcher.start()
        thread = Thread(target=worker, daemon=True)
        thread.start()
        def term_worker():
            thread.join()
            wb.close()
        term_thread = Thread(target=term_worker, daemon=True)
        term_thread.start()
        wb.open()
        term_thread.join()

    return form_fields if next(iter([ f for f in next(iter([ f for f in form_fields.fields if f.name=='_data_collection' ])).fields if f.name=='response_received' ])).response else None
