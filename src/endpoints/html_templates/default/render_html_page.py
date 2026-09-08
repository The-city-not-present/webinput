import html
import re


from .assets import (
    common_js,
    common_css,
    normalize_css,
    projectspecific_css,
)


def html_escape(val):
    def is_nonempty(val):
        if isinstance(val, bool):
            return False
        if isinstance(val, int) or isinstance(val, float):
            return True
        elif isinstance(val, str):
            return not re.match(r'^\s*$', val)
        else:
            return not not val
    def as_text(val):
        if is_nonempty(val):
            return f'{val}'
        else:
            return ''
    return html.escape(as_text(val))

def sanitize_html_attr(s):
    def is_nonempty(val):
        if isinstance(val, bool):
            return False
        if isinstance(val, int) or isinstance(val, float):
            return True
        elif isinstance(val, str):
            return not re.match(r'^\s*$', val)
        else:
            return not not val
    def as_text(val):
        if is_nonempty(val):
            return f'{val}'
        else:
            return ''
    s = as_text(s)
    s = re.sub(r'["\'\n\r]','',s)

def sanitize_html_attr_name(s):
    def is_nonempty(val):
        if isinstance(val, bool):
            return False
        if isinstance(val, int) or isinstance(val, float):
            return True
        elif isinstance(val, str):
            return not re.match(r'^\s*$', val)
        else:
            return not not val
    def as_text(val):
        if is_nonempty(val):
            return f'{val}'
        else:
            return ''
    s = as_text(s)
    s = re.sub(r'[^\w]','',s)


def render_field(name,question,parent_path='') -> str:
    result_txt = ''
    full_name = parent_path + ('' if parent_path=='' else '.') + name
    type = question.get('x-type')
    is_compound = type in ('block','compound','array','loop','grid','object',)
    x_ui_properties = { prop: value for prop, value in question.items() if prop.startswith('x-ui') }
    html_added_attrs = ' '.join(f'data-{sanitize_html_attr_name(prop)}="{sanitize_html_attr(value)}"' for prop, value in x_ui_properties.items())
    result_txt += f'\n<!-- {full_name} -->\n'
    result_txt += f'<div class="control-group mdmreport-banner webinput-controls-thumb {"webinput-controls-type-compound" if is_compound else "webinput-controls-type-plain"} mdmreport-controls" data-variable-path="{full_name}" {html_added_attrs}>'
    result_txt += f'<div class="mdmreport-controls-group">'
    result_txt += f'<label>{html_escape(question.get("title"))}</label>'
    result_txt += f'<div class="error validation-error"><span data-role="validation-error" data-for="{full_name}"></span></div>'
    if question.get('type')!='object':
        result_txt += f'<input type="{question.get("type")}" class="mdmreport-control webinput-control" name="{full_name}" value="{question.get("response")}"></input>'
    for name, group in question['properties'].items():
        result_txt += render_field(name,group,parent_path=full_name)
    result_txt += f'</div></div>'
    result_txt += f'\n<!-- end of {full_name}  -->\n'
    return result_txt





def render(json_schema: dict, config: dict|None = None) -> str:

    if not config:
        config = {}

    root = json_schema
    
    if 'properties' not in root:
        root['properties'] = {}
    result_txt = ""
    result_txt += """
<!doctype html>
<html lang="">
<head>
      <meta charset="UTF-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width">
      <style> .error { font-weight: 500; color: #900; } </style>
"""
    result_txt += f'<style>{normalize_css}</style>'
    result_txt += f'<style>{common_css}</style>'
    result_txt += f'<style>{projectspecific_css}</style>'
    result_txt += f'<script>{common_js}</script>'
    result_txt += f'<title>{html_escape(root.get("title"))}</title>'
    result_txt += """
</head>
<body class="mdmreportpage webinput page-webinput page-webinput-home mdmreportpage-page-webinput mdmreportpage-page-webinput-home">
<div class="container">
<div class="error error-banner" id="errorbanner"></div>
"""
    result_txt += f'<h1>{html_escape(root.get("title"))}</h1>'
    result_txt += f'<form method="POST" action="/" class="mdm-webinput-page">'
    if root.get("x-type")!='block':
        result_txt += f'<div class="error">{html_escape("Root element is not of type `block`")}</div>'
    elif ':helperfields' in root['properties'] and len(root['properties'][':helperfields'])>0:
        result_txt += f'<div class="error">{html_escape("helper_fields are not allowed on root element")}</div>'
    else:
        # good to process
        result_txt += '\n<!-- root -->\n'
        # result_txt += f'<label>{html_escape(root.get("title"))}</label>'
        result_txt += f'<div class="error validation-error"><span data-role="validation-error" data-for=""></span></div>'
        for name, group in root['properties'].items():
            result_txt += render_field(name,group,parent_path='')
    result_txt += '\n<!-- end of root -->\n'
    result_txt += f'<button type="submit" class="mdmreport-control webinput-control webinput-control-submit webinput-button-submit">Confirm selection!</button>'
    result_txt += f'</form>'
    result_txt += """
</div></body></html>
"""
    return result_txt


