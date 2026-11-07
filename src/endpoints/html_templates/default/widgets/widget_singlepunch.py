



from .widget_base import Widget

from .common_funcs import make_tag

from .common_category_list import make_category_inputs


@Widget.register('singlepunch')
class WidgetSinglePunch(Widget):
    def make_input_element(self):
        tags_categories = make_category_inputs(self.question, self.full_name, 'singlepunch')
        return make_tag(
            'div',
            { 'class': 'webinput-control-singlepunch-outer', },
            tags_categories,
        )
