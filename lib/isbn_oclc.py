from collections import defaultdict
from json import loads
from logging import getLogger
from threading import Thread
from typing import Any, Optional

from isbnlib import info as isbn_info
from langid import classify
from regex import search

from config import LANG
from lib.commons import (
    FOUR_DIGIT_NUM,
    ISBN10_SEARCH,
    ISBN13_SEARCH,
    ReturnError,
    request,
)
from lib.ketabir import (
    isbn_to_url as ketabir_isbn2url,
    url_to_dict as ketabir_url_to_dict,
)
from lib.urls import url_to_dict

RM_DASH_SPACE = str.maketrans('', '', '- ')


class IsbnError(Exception):

    """Raise when bibliographic information is not available."""

    pass


def isbn_to_dict(
    isbn_container_str: str,
    pure: bool = False,
    date_format: str = '%Y-%m-%d',
) -> dict:
    if pure:
        isbn = isbn_container_str
    else:
        # search for isbn13
        if (m := ISBN13_SEARCH(isbn_container_str)) is not None:
            isbn = m[0]
        else:
            # search for isbn10
            isbn = ISBN10_SEARCH(isbn_container_str)[0]

    if (iranian_isbn := isbn_info(isbn) == 'Iran') is True:
        ketabir_result_list = []
        ketabir_thread = Thread(
            target=ketabir_thread_target, args=(isbn, ketabir_result_list)
        )
        ketabir_thread.start()

    google_books_result = []
    google_books_thread = Thread(
        target=google_books,
        args=(isbn, google_books_result),
    )
    google_books_thread.start()

    citoid_result_list = []
    citoid_thread = Thread(
        target=citoid_thread_target, args=(isbn, citoid_result_list)
    )
    citoid_thread.start()

    if iranian_isbn is True:
        # noinspection PyUnboundLocalVariable
        ketabir_thread.join()
        # noinspection PyUnboundLocalVariable
        if ketabir_result_list:
            # noinspection PyUnboundLocalVariable
            ketabir_dict = ketabir_result_list[0]
        else:
            ketabir_dict = None
    else:
        ketabir_dict = None

    citoid_thread.join()
    if citoid_result_list:
        citoid_dict = citoid_result_list[0]
    else:
        citoid_dict = defaultdict(lambda: None)

    google_books_thread.join()
    if google_books_result:
        citoid_dict.update(google_books_result[0])

    dictionary = combine_dicts(ketabir_dict, citoid_dict)

    dictionary['date_format'] = date_format
    if 'language' not in dictionary:
        dictionary['language'] = classify(dictionary['title'])[0]
    return dictionary


def ketabir_thread_target(isbn: str, result: list) -> None:
    # noinspection PyBroadException
    try:
        if (url := ketabir_isbn2url(isbn)) is None:
            return  # ketab.ir does not have any entries for this isbn
        if d := ketabir_url_to_dict(url):
            result.append(d)
    except Exception:
        logger.exception('isbn: %s', isbn)
        return


def combine_dicts(ketabir: dict, citoid: dict) -> dict:
    if not ketabir and not citoid:
        raise IsbnError('Bibliographic information not found.')

    if not ketabir:
        return citoid
    elif not citoid:
        return ketabir

    # both ketabid and citoid are available
    if LANG == 'fa':
        result = ketabir
        if (oclc := citoid['oclc']) is not None:
            result['oclc'] = oclc
        return result
    return citoid


def isbn2int(isbn):
    return int(isbn.translate(RM_DASH_SPACE))


def get_citoid_dict(isbn) -> Optional[dict]:
    # https://www.mediawiki.org/wiki/Citoid/API
    r = request(
        'https://en.wikipedia.org/api/rest_v1/data/citation/mediawiki/' + isbn
    )
    if r.status_code != 200:
        return

    j0 = r.json()[0]
    get = j0.get

    d = defaultdict(lambda: None)

    d['cite_type'] = j0['itemType']
    d['isbn'] = j0['ISBN'][0]
    # worldcat url is not needed since OCLC param will create it
    # d['url'] = j0['url']
    if (oclc := j0.get('oclc')) is not None:
        d['oclc'] = oclc
    d['title'] = j0['title']

    authors = get('author')
    contributors = get('contributor')

    if authors is not None and contributors is not None:
        d['authors'] = authors + contributors
    elif authors is not None:
        d['authors'] = authors
    elif contributors is not None:
        d['authors'] = contributors

    if (publisher := get('publisher')) is not None:
        d['publisher'] = publisher

    if (place := get('place')) is not None:
        d['publisher-location'] = place

    if (date := get('date')) is not None:
        d['date'] = date

    return d


def google_books(isbn: str, result: list):
    try:
        j = request(
            f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn.replace("-", "")}'
        ).json()
        d = j['items'][0]
        d.update(d['volumeInfo'])
    except Exception:  # noqa
        return
    if authors := d['authors']:
        d['authors'] = [a.rsplit(' ', 1) for a in authors]
    if date := d.get('publishedDate'):
        d['date'] = date
    d['isbn'] = isbn
    d['cite_type'] = 'book'
    result.append(d)


def citoid_thread_target(isbn: str, result: list) -> None:
    if citoid_dict := get_citoid_dict(isbn):
        result.append(citoid_dict)


def worldcat_url_to_dict(url: str, date_format: str = '%Y-%m-%d', /) -> dict:
    try:
        oclc = search('(?i)worldcat.org/(?:title|oclc)/(\d+)', url)[1]
    except TypeError:  # 'NoneType' object is not subscriptable
        # e.g. on https://www.worldcat.org/formats-editions/22239204
        return url_to_dict(url, date_format)
    return oclc_dict(oclc, date_format)


def oclc_dict(oclc: str, date_format: str = '%Y-%m-%d', /) -> dict:
    content = request('https://www.worldcat.org/title/' + oclc).content
    j = loads(
        content[
            (s := (f := content.find)(b' type="application/json">') + 25) : f(
                b'</script>', s
            )
        ]
    )
    record = j['props']['pageProps']['record']
    if record is None:  # invalid OCLC number
        raise ReturnError(
            'Error processing OCLC number: ' + oclc,
            'Make sure the OCLC identifier is valid.',
            '',
        )
    d: defaultdict[str, Any] = defaultdict(lambda: None)
    d['cite_type'] = record['generalFormat'].lower()
    d['title'] = record['title']
    d['authors'] = [
        ('', c['nonPersonName']['text'])
        if 'nonPersonName' in c
        else (c["firstName"]['text'], c["secondName"]['text'])
        for c in record["contributors"]
    ]
    if (publisher := record['publisher']) != '[publisher not identified]':
        d['publisher'] = publisher
    if (
        place := record['publicationPlace']
    ) != '[Place of publication not identified]':
        d['publisher-location'] = place
    if m := FOUR_DIGIT_NUM(record['publicationDate']):
        d['year'] = m[0]
    d['language'] = record['catalogingLanguage']
    if isbn := record['isbn13']:
        d['isbn'] = isbn
    if issns := record['issns']:
        d['issn'] = issns[0]
    d['oclc'] = oclc
    d['date_format'] = date_format
    return d


logger = getLogger(__name__)
