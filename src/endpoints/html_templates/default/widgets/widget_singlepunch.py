



from .widget_base import Widget

from .common_funcs import make_tag, sanitize_html

global_ids_stupid_dict = {
    'counter': 0,
}


@Widget.register('singlepunch')
class WidgetSinglePunch(Widget):
    def make_input_element(self):
        tags_categories = []
        for cat_name, cat in self.question.get('x-categories').items() or []:
            id = f'singlepunch_stupid_id_{cat_name}_{self.name}_{global_ids_stupid_dict.get("counter")}'
            global_ids_stupid_dict['counter'] += 1
            tag_control = make_tag(
                'input',
                {
                    'type': 'radio',
                    'class': 'mdmreport-control webinput-control',
                    'name': self.full_name,
                    'value': cat_name,
                    'id': id,
                },
                '',
            )
            tag_label = make_tag(
                'label',
                {
                    'for': id,
                },
                sanitize_html(cat.get('title',cat_name)),
            )
            tag_cat = make_tag(
                'div',
                { 'class': 'webinput-control-singlepunch-category-container', },
                [
                    tag_control,
                    tag_label,
                ],
            )
            tags_categories.append(tag_cat)
        return make_tag(
            'div',
            { 'class': 'webinput-control-singlepunch-outer', },
            tags_categories,
        )
