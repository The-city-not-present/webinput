

from .widget_base import Widget


@Widget.register('multipunch')
class WidgetMultiPunch(Widget):
    def make_input_element(self):
        return '<span class="error" style="color: #900; font-weight: 500;">Multi-punch widget: not implemented</span>'
