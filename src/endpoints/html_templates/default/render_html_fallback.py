
import html


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

