


from .common_funcs import make_tag, as_text

from .widget_base import Widget


@Widget.register('int')
@Widget.register('float')
class WidgetNumber(Widget):
    def make_input_element(self):
        return make_tag(
            'input',
            {
                'type': 'number', # self.question.get("question_type"),
                'class': 'mdmreport-control webinput-control',
                'name': self.full_name,
                'value': as_text(self.question.get("response")),
            },
            '',
        )
    

