from bleach import clean, linkify
from bleach.callbacks import nofollow, target_blank
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown_del_ins import DelInsExtension


def prevent_py(attrs, new=False):
    if not new:
        return attrs
    text = attrs['_text']
    if text.endswith('.py') and not text.startswith(('http:', 'https:')):
        return None
    return attrs


def prevent_md(attrs, new=False):
    if not new:
        return attrs
    text = attrs['_text']
    if text.endswith('.md') and not text.startswith(('http:', 'https:')):
        return None
    return attrs


def clean_this(html, sc=False):
    callbacks = [nofollow, target_blank, prevent_py, prevent_md]
    if sc:
        del callbacks[0]
    tags = ['a', 'blockquote', 'br', 'code', 'del', 'div',
            'em', 'iframe', 'img', 'ins', 'h2', 'hr',
            'li', 'ol', 'pre', 'span', 'strong', 'ul', 'p']
    attrs = {'*': ['class'],
             'a': ['href', 'title'],
             'abbr': ['title'],
             'iframe': ['src'],
             'img': ['src', 'alt', 'data-link']}
    return linkify(
        clean(html, tags=tags, attributes=attrs),
        callbacks=callbacks, skip_tags=['pre', 'code', 'iframe'])


def html_this(md_text, sc=False):
    html = markdown(
        md_text,
        extensions=['markdown.extensions.fenced_code',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.md_in_html',
                    CodeHiliteExtension(use_pytgments=True),
                    DelInsExtension()],
        output_format='html5')
    return clean_this(html, sc=sc)


def parse_md(query, sc=False):
    md = '\n\n'.join([par.get('mdtext') for par in query])
    return html_this(md, sc=sc).replace('&amp;', '&')
