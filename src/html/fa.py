#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from zlib import adler32

from src.commons import Response


CSS = open('src/html/fa.css', 'rb').read()
CSS_HEADERS = [
    ('Content-Type', 'text/css; charset=UTF-8'),
    ('Content-Length', str(len(CSS))),
    ('Cache-Control', 'max-age=31536000'),
]

HTML_SUBST = Template(
    open('src/html/fa.html', encoding='utf8').read().replace(
        # Invalidate css cache after any change in css file.
        '"stylesheet" href="./static/fa',
        '"stylesheet" href="./static/fa' + str(adler32(CSS)),
    )
).substitute

# Predefined responses
DEFAULT_RESPONSE = Response(
    sfn='یادکرد ساخته‌شده اینجا نمایان خواهد شد...',
    cite='',
    ref='',
)
HTTPERROR_RESPONSE = Response(
    sfn='خطای اچ‌تی‌تی‌پی:',
    cite='یک یا چند مورد از منابع اینترنتی مورد '
    'نیاز برای ساخت این یادکرد در این لحظه '
    'در دسترس نیستند و یا ورودی نامعتبر است.',
    ref='',
)
OTHER_EXCEPTION_RESPONSE = Response(
    sfn='خطای ناشناخته‌ای رخ داد..',
    cite='اطلاعات خطا در سیاهه ثبت شد.',
    ref='',
)
UNDEFINED_INPUT_RESPONSE = Response(
    sfn='ورودی تجزیه‌ناپذیر',
    cite='پوزش، ورودی قابل پردازش نبود. خطا در سیاهه ثبت شد.',
    ref='',
)


def response_to_html(response: Response, date_format: str):
    """Insert the response into the HTML template and return response_body."""
    return HTML_SUBST(**response._asdict())
