
from .common_funcs import make_tag, sanitize_html





class WidgetWrapErr:
    def __init__(self,widget,err):
        self._widget = widget
        self._err = err

    def to_html(self):
        source_widget = self._widget.to_html()
        err_banner = make_tag('div',{'style':'font-weight: 500; color: #900;','class':'error'},sanitize_html(self._err),)
        return make_tag('div',{'class':'webinput-widget-err',},[err_banner,source_widget,])

    def __str__(self):
        return self.to_html()

