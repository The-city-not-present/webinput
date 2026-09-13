import queue
from typing import Any
import threading
import time
from dataclasses import dataclass, field

from .lib.webserve.src.launch_browser import launch_browser



import_pywebview_error = None
try:
    import webview
except ImportError as e:
    import_pywebview_error = e


DEFAULT_WINDOW_TITLE = 'WebInput'


@dataclass
class WebBrowserEvents:
    constructor: threading.Event = field(default_factory=threading.Event,init=False)
    open: threading.Event = field(default_factory=threading.Event,init=False)
    close: threading.Event = field(default_factory=threading.Event,init=False)
    destroy: threading.Event = field(default_factory=threading.Event,init=False)
    destructor: threading.Event = field(default_factory=threading.Event,init=False)
    enter: threading.Event = field(default_factory=threading.Event,init=False)
    exit: threading.Event = field(default_factory=threading.Event,init=False)

class WebBrowserBase:
    def __init__(self, url, window_title: str|None = None):
        self._url = url
        self._events = WebBrowserEvents()
        self._events.constructor.set()

    def open(self):
        self._events.open.set()
        pass

    def close(self):
        self._events.close.set()
        pass

    def destroy(self):
        self._events.destroy.set()
        pass

    @property
    def events(self):
        return self._events

    # unlink document if some error happened, or if we are done processing it
    def __del__(self):
        self._events.destructor.set()
        pass

    # methods required by python so that I can use "with"
    def __enter__(self):
        self._events.enter.set()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._events.exit.set()
        return None



class WebBrowserPywebview(WebBrowserBase):
    def __init__(self, url, window_title: str|None = None):
        super().__init__(url)
        assert not not webview and not import_pywebview_error
        self._window_title = window_title or DEFAULT_WINDOW_TITLE
        self._window = webview.create_window(self._window_title, self._url)
        def thread_func(window):
            # window.something
            # wait for server to finish...
            self._done.wait()
        self._thread_func = thread_func
        self._err_queue = queue.Queue()
        event_done = threading.Event()
        event_done.clear()
        self._done = event_done

    def _create_window(self,_:Any,window,thread_func):
        start_args = {
            # 'gui': 'qt',
        }
        thread_param = []
        destroy_event = self._destroy_window(webview, window, 0.1)
        def thread():
            try:
                window.events.loaded.wait()
                if thread_func:
                    thread_func(window, *thread_param)
                destroy_event.set()
            except Exception as e:
                self._err_queue.put(e)
                destroy_event.set()
                raise
        t = threading.Thread(target=thread)
        t.start()
        webview.start(**start_args)

    def _destroy_window(self,_: Any, window: Any, delay: float) -> threading.Event:
        def stop():
            try:
                event.wait()
                time.sleep(delay)
                window.destroy()
                time.sleep(delay)
            except Exception as e:
                self._err_queue.put(e)
                raise
        event = threading.Event()
        event.clear()
        t = threading.Thread(target=stop)
        t.start()
        return event

    def open(self):
        super().open()
        # webview.start()
        time.sleep(.1)
        self._create_window(webview, self._window, self._thread_func)
        self._events.close.set()

    def close(self):
        super().close()
        self._done.set()

    def __del__(self):
        self._done.set()
        return super().__del__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._done.set()
        return super().__exit__(exc_type, exc_val, exc_tb)



class WebBrowserSystemDefault(WebBrowserBase):
    def open(self):
        super().open()
        launch_browser(self._url )





if import_pywebview_error:
    WebBrowser = WebBrowserSystemDefault
else:
    WebBrowser = WebBrowserPywebview
