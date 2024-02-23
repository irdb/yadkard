from datetime import date
from threading import Thread
from urllib.parse import urlparse

from curl_cffi import CurlError

from lib import logger
from lib.commons import rc
from lib.urls import (
    ContentLengthError,
    ContentTypeError,
    url_data,
)

ARCHIVE_ORG_URL_MATCH = rc(
    r'https?+://web(?:-beta)?+\.archive\.org/(?:web/)?+'
    r'(\d{4})(\d{2})(\d{2})\d{6}(?>cs_|i(?>d_|m_)|js_)?+/(http.*)'
).match


def archive_org_data(archive_url: str) -> dict:
    if (m := ARCHIVE_ORG_URL_MATCH(archive_url)) is None:
        # Could not parse the archive_url. Treat as an ordinary URL.
        return url_data(archive_url)
    archive_year, archive_month, archive_day, original_url = m.groups()
    og_d = {}
    og_thread = Thread(target=og_url_data_tt, args=(original_url, og_d))
    og_thread.start()
    d = url_data(archive_url, check_home=False)
    d['url'] = original_url
    d['archive-url'] = archive_url
    d['archive-date'] = date(
        int(archive_year), int(archive_month), int(archive_day)
    )
    og_thread.join()
    if og_d:
        # The original_process has been successful
        if (
            og_d['title'] == d['title']
            or og_d['html_title'] == d['html_title']
        ):
            d |= og_d
            d['url-status'] = 'live'
        else:
            # and original title is the same as archive title. Otherwise it
            # means that the content probably has changed and the original data
            # cannot be trusted.
            d['url-status'] = 'unfit'
    else:
        d['website'] = urlparse(original_url).hostname.removeprefix('www.')
        d['url-status'] = 'dead'
    return d


def og_url_data_tt(og_url: str, og_d: dict, /) -> None:
    """Fill the dictionary with the information found in ogurl."""
    # noinspection PyBroadException
    try:
        og_d |= url_data(og_url, this_domain_only=True)
    except (
        ContentTypeError,
        ContentLengthError,
        CurlError,
    ):
        pass
    except Exception:
        logger.exception(
            'There was an unexpected error in waybackmechine thread'
        )
