from datetime import datetime
from pathlib import Path
import json
import threading # for delayed shutdown
import time # for delayed shutdown
import traceback, sys # for error reporting


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return f'{obj}'
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Exception):
            return f'{obj}'
        return super().default(obj)



def delay_term(net_request_handler):
    def worker():
        time.sleep(1)
        net_request_handler.server.shutdown()

    threading.Thread(target=worker, daemon=True).start()


def print_stacktrace(e):
    # STDOUT_COLOR_RED = "\033[91m"
    STDOUT_COLOR_RED = "\033[31m"
    STDOUT_COLOR_RESET = "\033[0m"
    STDOUT_COLOR_GREEN = "\033[32m"
    print('', file=sys.stderr)
    print('Stack trace:', file=sys.stderr)
    print('', file=sys.stderr)
    traceback.print_exception(e, limit=20)
    print('', file=sys.stderr)
    print('', file=sys.stderr)
    print('', file=sys.stderr)
    print(f'{STDOUT_COLOR_RED}Error:{STDOUT_COLOR_RESET}', file=sys.stderr)
    print('', file=sys.stderr)
    print(f'{STDOUT_COLOR_RED}{e}{STDOUT_COLOR_RESET}', file=sys.stderr)
    print('', file=sys.stderr)
