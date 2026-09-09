


from .widget_base import Widget


@Widget.register('block')
class WidgetBlock(Widget):
    def make_input_element(self):
        return ''

