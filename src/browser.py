import queue
from typing import Any
import threading
import time

from .lib.webserve.src.launch_browser import launch_browser



import_pywebview_error = None
try:
    import webview
except ImportError as e:
    import_pywebview_error = e


DEFAULT_WINDOW_TITLE = 'WebInput'



class WebBrowserBase:
    def __init__(self, url, window_title: str|None = None):
        self._url = url
        pass

    def open(self):
        pass

    def close(self):
        pass

    def destroy(self):
        pass

    # unlink document if some error happened, or if we are done processing it
    def __del__(self):
        pass

    # methods required by python so that I can use "with"
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None



class WebBrowserPywebview(WebBrowserBase):
    def __init__(self, url, window_title: str|None = None):
        # print('    WEBBROWSER: __init__(): begin')
        super().__init__(url)
        assert not not webview and not import_pywebview_error
        self._window_title = window_title or DEFAULT_WINDOW_TITLE
        # print('    WEBBROWSER: __init__(): calling webview.create_window()')
        self._window = webview.create_window(self._window_title, self._url)
        def thread_func(window):
            # print('      WEBBROWSER: __init__(): thread_func(): begin')
            # window.something
            # wait for server to finish...
            self._done.wait()
            # print('      WEBBROWSER: __init__(): thread_func(): the end')
        self._thread_func = thread_func
        self._err_queue = queue.Queue()
        event_done = threading.Event()
        event_done.clear()
        self._done = event_done
        # print('    WEBBROWSER: __init__(): the end')

    def _create_window(self,_:Any,window,thread_func):
        # print('    WEBBROWSER: self._create_window(): begin')
        start_args = {}
        thread_param = []
        destroy_event = self._destroy_window(webview, window, 0.1)
        def thread():
            # print('      WEBBROWSER: self._create_window(): thread(): begin')
            try:
                window.events.loaded.wait()
                if thread_func:
                    thread_func(window, *thread_param)
                destroy_event.set()
            except Exception as e:
                # print('      WEBBROWSER: self._create_window(): thread(): fail')
                self._err_queue.put(e)
                destroy_event.set()
                raise
            # print('      WEBBROWSER: self._create_window(): thread(): the end')
        t = threading.Thread(target=thread)
        t.start()
        # print('    WEBBROWSER: calling webview.start()')
        webview.start(**start_args)
        # print('    WEBBROWSER: self._create_window(): the end')

    def _destroy_window(self,_: Any, window: Any, delay: float) -> threading.Event:
        # print('    WEBBROWSER: self._destroy_window(): begin')
        def stop():
            # print('      WEBBROWSER: self._destroy_window(): stop(): begin')
            try:
                event.wait()
                time.sleep(delay)
                # print('    WEBBROWSER: calling window.destroy()')
                window.destroy()
                time.sleep(delay)
            except Exception as e:
                # print('      WEBBROWSER: self._destroy_window(): stop(): fail')
                self._err_queue.put(e)
                raise
            # print('      WEBBROWSER: self._destroy_window(): stop(): the end')
        event = threading.Event()
        event.clear()
        t = threading.Thread(target=stop)
        t.start()
        # print('    WEBBROWSER: self._destroy_window(): the end')
        return event

    def open(self):
        # print('    WEBBROWSER: open(): begin')
        # print('    WEBBROWSER: calling webview.start()')
        # webview.start()
        time.sleep(.1)
        self._create_window(webview, self._window, self._thread_func)
        pass
        # print('    WEBBROWSER: after webview.start()')
        # print('    WEBBROWSER: open(): the end')

    def close(self):
        # print('    WEBBROWSER: close(): begin')
        # print('    WEBBROWSER: close(): done.set()')
        self._done.set()
        # print('    WEBBROWSER: close(): the end')

    def __del__(self):
        self._done.set()
        return super().__del__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._done.set()
        return super().__exit__(exc_type, exc_val, exc_tb)



class WebBrowserSystemDefault(WebBrowserBase):
    def open(self):
        launch_browser(self._url )





if import_pywebview_error:
    WebBrowser = WebBrowserSystemDefault
else:
    WebBrowser = WebBrowserPywebview
