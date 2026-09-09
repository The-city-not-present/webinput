
from abc import abstractmethod
from collections.abc import Iterable

from .common_funcs import (
    sanitize_html,
    sanitize_html_attr,
    sanitize_html_attr_name,
    make_tag,
)
from .widget_wrap_err import WidgetWrapErr




class Widget:
    def __new__(cls, name,question,parent_path=''):
        def detect_widget_cls(widgets,question_type,widget_spec):
            if question_type in widgets:
                widget_spec = widget_spec or ''
                return widgets.get(question_type).get(widget_spec,WidgetWrapErr(widgets.get(question_type).get(''),f'Widget not found: {widget_spec}'))
            else:
                assert isinstance(widgets.get('text'),dict)
                return WidgetWrapErr(widgets.get('text').get(''),f'Widget not found: {question_type}')
        if cls is Widget:
            question_type = question.get('x-type')
            widget_spec = question.get('x-widget')
            WidgetCls = detect_widget_cls(cls._registry,question_type,widget_spec)
            return WidgetCls(name,question,parent_path)
        return super().__new__(cls)

    _registry = {}

    @classmethod
    def register(cls, name):
        def set_at_path(d, path, value=None):
            for key in path[:-1]:
                d = d.setdefault(key, {})
            d[path[-1]] = value
        def decorator(widget_cls):
            path = name
            if isinstance(path,str) or not isinstance(path,Iterable):
                path = (path,)
            path = (*path,*['' * max(0, 2 - len(path))])
            set_at_path(cls._registry,path,widget_cls)
            return widget_cls
        return decorator
    
    def __init__(self,name: str,question, parent_path=''):
        self.name = name
        self.question = question
        self.parent_path = parent_path
        self.question_type = question.get('x-question_type')
        self.is_helper_field = self.name.startswith(':helperfields.')
        self.full_name = parent_path + ('' if parent_path=='' else '.') + name
        self.is_compound = self.question_type in ('block','loop','grid',)
        self.x_ui_properties = { f'x-ui-{prop}': value for prop, value in question.get('x-ui',{}).items() if True }

    def make_outer(self,children):
        full_name = self.full_name
        is_compound = self.is_compound
        x_ui_properties = self.x_ui_properties
        html_added_attrs = { f'data-{sanitize_html_attr_name(prop)}': sanitize_html_attr(value) for prop, value in x_ui_properties.items() }
        return make_tag(
            'div',
            {
                'class': f'control-group mdmreport-banner webinput-controls-thumb {"webinput-controls-question_type-compound" if is_compound else "webinput-controls-question_type-plain"} mdmreport-controls',
                **html_added_attrs,
            },
            make_tag('--',f'\n<!-- {full_name} -->\n',None) \
                + make_tag(
                    'div',
                    { 'class': 'mdmreport-controls-group', },
                    children,
                ) \
                + make_tag('--',f'\n<!-- end of {full_name} -->\n',None),
        )

    def make_label(self):
        question = self.question
        return make_tag(
            'label',
            {},
            sanitize_html(question.get("title")),
        )

    def make_err_banner(self):
        full_name = self.full_name
        return make_tag(
            'div',
            { 'class': 'error validation-error', },
            make_tag(
                'span',
                {
                    'data-role': 'validation-error',
                    'data-for': full_name,
                },
                '',
            ),
        )

    @abstractmethod
    def make_input_element(self):
        return NotImplementedError('make_input_element: this method must be overloaded')
    
    def make_children(self):
        return ''.join(
            Widget(name,group,parent_path=self.full_name).to_html() for name, group in self.question['properties'].items()
        )

    def to_html(self)-> str:

        return self.make_outer(
            [
                self.make_label(),
                self.make_err_banner(),
                self.make_input_element(),
                self.make_children(),
            ]
        )

    def __str__(self) -> str:
        return self.to_html()

