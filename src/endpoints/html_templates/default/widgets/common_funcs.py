from bs4 import BeautifulSoup, Comment, Tag, NavigableString
import html
import re
from collections.abc import Iterable



def make_tag(tagname,attrs: dict|None,children) -> str:
    if tagname == '--':
        return str(BeautifulSoup(Comment(as_text(children)), "html.parser"))
    soup = BeautifulSoup("", "html.parser")
    tag = soup.new_tag(tagname)
    if not attrs:
        attrs = {}
    for attr_name, attr_value in attrs.items():
        tag[attr_name] = attr_value
    if children:
        children_array = None
        if isinstance(children,str):
            fragment = BeautifulSoup(children, "html.parser")
            # IMPORTANT: iterate over a copy
            children_array = list(fragment.contents)
        elif isinstance(children,Iterable):
            children_array = []
            for child in children:
                if isinstance(child,str):
                    fragment = BeautifulSoup(child, "html.parser")
                    children_array.extend(fragment.contents)
                elif isinstance(child,(Tag, Comment, NavigableString)):
                    children_array.append(child)
                else:
                    raise ValueError(child)
        else:
            raise ValueError(f'make_tag: cildren param is not of recognized format')
        for child in children_array:
            tag.append(child)
    return str(tag)




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

def sanitize_html(val):
    return html.escape(as_text(val))

def sanitize_html_attr(s):
    s = as_text(s)
    s = re.sub(r'["\'\n\r]','',s)
    return s

def sanitize_html_attr_name(s):
    s = as_text(s)
    s = re.sub(r'[^\w-]','',s)
    return s

