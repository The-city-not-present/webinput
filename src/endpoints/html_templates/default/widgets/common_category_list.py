
from .common_funcs import make_tag, sanitize_html, sanitize_html_attr_name


_ids = {'counter': 0}


def make_category_inputs(question, full_name, input_type):
    """Render the categories of a single-/multi-punch question in definition
    order, with group headings when grouping is present."""
    x_categories = question.get('x-categories') or {}
    groups = question.get('x-category-groups') or []

    input_type_attr = 'radio' if input_type == 'singlepunch' else 'checkbox'


    def make_one(cat_name):
        cat = x_categories.get(cat_name, {})
        id = f'{input_type}_id_{sanitize_html_attr_name(cat_name)}_{sanitize_html_attr_name(full_name)}_{_ids["counter"]}'
        _ids['counter'] += 1
        tag_control = make_tag(
            'input',
            {
                'type': input_type_attr,
                'class': 'mdmreport-control webinput-control',
                'name': full_name,
                'value': cat_name,
                'id': id,
            },
            '',
        )
        tag_label = make_tag(
            'label',
            {'for': id},
            sanitize_html(cat.get('title', cat_name)),
        )
        return make_tag(
            'div',
            {'class': 'webinput-control-singlepunch-category-container'},
            [tag_control, tag_label],
        )

    cat_group_label = {}
    for group in groups:
        for cat_name in group.get('categories', []):
            cat_group_label.setdefault(cat_name, group.get('label'))

    tags = []
    seen_group_labels = set()
    for cat_name in x_categories:
        group_label = cat_group_label.get(cat_name)
        if group_label and group_label not in seen_group_labels:
            seen_group_labels.add(group_label)
            tags.append(make_tag(
                'div',
                {'class': 'webinput-control-category-group'},
                sanitize_html(group_label),
            ))
        tags.append(make_one(cat_name))
    return tags
