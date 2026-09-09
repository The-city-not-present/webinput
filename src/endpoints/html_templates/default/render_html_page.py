from .widgets.common_funcs import (
    sanitize_html,
)
from .assets import (
    common_js,
    common_css,
    normalize_css,
    projectspecific_css,
)
from .widgets import Widget







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
    result_txt += f'<title>{sanitize_html(root.get("title"))}</title>'
    result_txt += """
</head>
<body class="mdmreportpage webinput page-webinput page-webinput-home mdmreportpage-page-webinput mdmreportpage-page-webinput-home">
<div class="container">
<div class="error error-banner" id="errorbanner"></div>
"""
    result_txt += f'<h1>{sanitize_html(root.get("title"))}</h1>'
    result_txt += f'<form method="POST" action="/" class="mdm-webinput-page">'
    if root.get("x-type")!='block':
        result_txt += f'<div class="error">{sanitize_html("Root element is not of type `block`")}</div>'
    elif ':helperfields' in root['properties'] and len(root['properties'][':helperfields'])>0:
        result_txt += f'<div class="error">{sanitize_html("helper_fields are not allowed on root element")}</div>'
    else:
        # good to process
        result_txt += '\n<!-- root -->\n'
        # result_txt += f'<label>{sanitize_html(root.get("title"))}</label>'
        result_txt += f'<div class="error validation-error"><span data-role="validation-error" data-for=""></span></div>'
        for name, group in root['properties'].items():
            result_txt += Widget(name,group,parent_path='').to_html()
    result_txt += '\n<!-- end of root -->\n'
    result_txt += f'<button type="submit" class="mdmreport-control webinput-control webinput-control-submit webinput-button-submit">Confirm selection!</button>'
    result_txt += f'</form>'
    result_txt += """
</div></body></html>
"""
    return result_txt


