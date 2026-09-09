


from .common_funcs import make_tag, as_text

from .widget_base import Widget


@Widget.register('text')
class WidgetText(Widget):
    def make_input_element(self):
        return make_tag(
            'input',
            {
                'type': 'text', # self.question.get("question_type"),
                'class': 'mdmreport-control webinput-control',
                'name': self.full_name,
                'value': as_text(self.question.get("response")),
            },
            '',
        )
    

