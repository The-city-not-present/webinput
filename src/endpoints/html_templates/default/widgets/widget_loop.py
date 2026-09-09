


from .widget_base import Widget


@Widget.register('loop')
@Widget.register(('loop','',))
class WidgetLoop(Widget):
    def make_input_element(self):
        return '<span class="error" style="color: #900; font-weight: 500;">Loop widget: not implemented</span>'

@Widget.register(('grid','forcetable',))
class WidgetGridForceTable(Widget):
    def make_input_element(self):
        return '<span class="error" style="color: #900; font-weight: 500;">Loop widget: not implemented</span>'

@Widget.register('grid')
@Widget.register(('grid','',))
@Widget.register(('grid','rollablesections',))
class WidgetGridRollableSections(Widget):
    def make_input_element(self):
        return '<span class="error" style="color: #900; font-weight: 500;">Loop widget: not implemented</span>'

WidgetGrid = WidgetGridRollableSections
