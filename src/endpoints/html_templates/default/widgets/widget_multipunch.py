

from .widget_base import Widget

from .common_funcs import make_tag

from .common_category_list import make_category_inputs


@Widget.register('multipunch')
class WidgetMultiPunch(Widget):
    def make_input_element(self):
        tags_categories = make_category_inputs(self.question, self.full_name, 'multipunch')
        return make_tag(
            'div',
            { 'class': 'webinput-control-multipunch-outer', },
            tags_categories,
        )
