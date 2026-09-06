import html
import re


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

def render_field(name,question,parent_path='') -> str:
    result_txt = ''
    full_name = parent_path + ('' if parent_path=='' else '.') + name
    result_txt += f'\n<!-- {full_name} -->\n'
    result_txt += f'<div class="control-group">'
    result_txt += f'<label>{html_escape(question.get("title"))}</label>'
    result_txt += f'<div class="error validation-error"><span data-role="validation-error" data-for="{full_name}"></span></div>'
    if question.get('type')!='object':
        result_txt += f'<input type="{question.get("type")}" name="{full_name}" value="{question.get("response")}"></input>'
    for name, group in question['properties'].items():
        result_txt += render_field(name,group,parent_path=full_name)
    result_txt += f'</div>'
    result_txt += f'\n<!-- end of {full_name}  -->\n'
    return result_txt


def render_fallback(msg):
    msg = f'{msg}'
    msg = html.escape(msg)
    return f'''
<!doctype html>
<html lang="">
<head>
      <meta charset="UTF-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width">
      <title>Error</title>
      <style> * {{ box-sizing: border-box; }} .error {{ font-weight: 500; color: #900; }} .container {{ margin: 20px; width: 100%; }} @media all and (min-width: 800px) {{ .container {{ margin: 20px auto 20px; width: 600px; }} }}</style>
</head>
<body style="margin: 0; padding: 0;"><div class="container"><h1>Error</h1><div class="error">{msg}</div></div></body></html>
'''

js_scripts = '''
document.addEventListener("DOMContentLoaded", function() {
    const errorBannerElement = document.querySelector('#errorbanner');
    const logError = e => {
        console.error(e);
        const p = document.createElement('p');
        p.classList.add('error');
        p.innerText = `${e}`;
        errorBannerElement.appendChild(p);
    };
    async function makeFetchResponseErrorMessage(response) {
        // const checkIfFormValidationError = async response => {
        //   if( response.status===415 ) {
        //     try {
        //       const data = await response.json();
        //       const errorMsg = data?.error;
        //       if( errorMsg )
        //         return `Validation failed: ${errorMsg}`;
        //     } catch(e) {
        //       // ok to ignore, if response is not json, or anything else - validation should anyway be caught earlier
        //     }
        //   }
        //   return null;
        // }
        if( response instanceof Promise )
          return makeFetchResponseErrorMessage(await response);
        else if( response instanceof Response ) {
          // const possibleFormValidationError = await checkIfFormValidationError(response);
          // if( possibleFormValidationError )
          //   return possibleFormValidationError;
          const prefix = `HTTP ${ response.status }`;
          try {
            const contentType = response.headers.get( 'content-type' ) || '';
            if( contentType.includes( 'application/json' ) ) {
              const body = await response.json();
              // Prefer a non-empty `error` field.
              if( body && !!body.error ) {
                return `${ prefix }: ${ body.error }`;
              }
              // Fall back to the whole JSON response.
              const details = JSON.stringify( body );
              return details ? `${ prefix }: ${ details }` : prefix;
            }
            // For text/plain and other non-JSON responses, use the response text.
            const text = await response.text();
            return text.trim() ? `${ prefix }: ${ text }` : prefix;
          } catch( e ) {
            // If the response body cannot be read/parsed, at least return the status.
            return prefix;
          }
        } else if( response instanceof Error ) {
          return `${response}`;
        } else {
          return `${response}`;
        }
    };
    const handleFormSubmit = async formElement=>{
        try {
            const url = formElement.getAttribute('action');
            const method = formElement.getAttribute('method');
            const body = new URLSearchParams(new FormData(formElement));
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body,
            });
            Array.from(formElement.querySelectorAll('[data-role="validation-error"]')).forEach(errBannerEl=>{errBannerEl.innerText = '';});
            if( response.status===415 ) {
                const data = await response.json()
                const errorMsg = data?.error;
                const errorPath = data?.path;
                if( errorMsg ) {
                    // <span data-role="validation-error" data-for="
                    const targetErrorPlaceholders = Array.from(formElement.querySelectorAll('[data-role="validation-error"][data-for="'+errorPath+'"]'));
                    if( targetErrorPlaceholders.length>0 ) {
                        targetErrorPlaceholders.forEach(errBannerEl=>{errBannerEl.innerText = errorMsg;});
                        return;
                    }
                }
            }
            if( !response.ok ) {
                const err_msg = new Error(await makeFetchResponseErrorMessage(response));
                throw err_msg;
            }
            const result = await response.text();
            const p = document.createElement('p');
            p.innerText = 'Response received. You can close this window now.';
            formElement.innerHTML = '<div class="done"></div>';
            formElement.appendChild(p);
            (new Promise(r=>setTimeout(5000,r))).then(()=>{ window.close(); });
        } catch(e) {
            logError(e);
            throw e;
        }
    };
    Array.from(document.querySelectorAll('form')).forEach(formElement=>Promise.resolve(formElement).then(formElement=>formElement.addEventListener('submit',function(event){
        event.preventDefault();
        handleFormSubmit(formElement);
        return false;
    })));
})
'''


def render(json_schema: dict) -> str:
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
    result_txt += f'<script>{js_scripts}</script>'
    result_txt += f'<title>{html_escape(root.get("title"))}</title>'
    result_txt += """
</head>
<body class="mdmreportpage webinput webinput-home">
<div class="error" id="errorbanner"></div>
"""
    result_txt += f'<h1>{html_escape("WebInput")}</h1>'
    result_txt += f'<form method="POST" action="/">'
    if root.get("x-type")!='block':
        result_txt += f'<div class="error">{html_escape("Root element is not of type `block`")}</div>'
    elif ':helperfields' in root['properties'] and len(root['properties'][':helperfields'])>0:
        result_txt += f'<div class="error">{html_escape("helper_fields are not allowed on root element")}</div>'
    else:
        # good to process
        result_txt += '\n<!-- root -->\n'
        result_txt += f'<label>{html_escape(root.get("title"))}</label>'
        result_txt += f'<div class="error validation-error"><span data-role="validation-error" data-for=""></span></div>'
        for name, group in root['properties'].items():
            result_txt += render_field(name,group,parent_path='')
    result_txt += '\n<!-- end of root -->\n'
    result_txt += f'<button type="submit">Confirm selection!</button>'
    result_txt += f'</form>'
    result_txt += """
</body></html>
"""
    return result_txt


