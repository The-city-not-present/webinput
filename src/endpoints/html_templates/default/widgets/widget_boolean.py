


from .widget_base import Widget


@Widget.register('boolean')
class WidgetBoolean(Widget):
    def make_input_element(self):
        return '<span class="error" style="color: #900; font-weight: 500;">Boolean widget: not implemented</span>'

