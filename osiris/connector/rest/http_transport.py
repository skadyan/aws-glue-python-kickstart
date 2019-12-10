import codecs
import io

import urllib3
from urllib3 import HTTPResponse

from osiris.base.generalutils import parse_charset_from_content_type, remove_entry_if_none
from osiris.base.logutils import get_logger

_log = get_logger(__name__)


class HTTPTransport:
    def __init__(self, default_headers: dict = None, timeout: int = 300):
        self.default_headers = default_headers
        self.timeout = timeout
        self._http = urllib3.PoolManager(maxsize=5, block=True, headers=default_headers)

    def post(self, url, data=None, fields=None, headers: dict = None, timeout: int = -1, sink=None) -> HTTPResponse:
        return self._request("POST", url, headers=headers, body=data, fields=fields, timeout=timeout, sink=sink)

    def get(self, url, headers: dict = None, timeout: int = -1, sink=None) -> HTTPResponse:
        return self._request("GET", url, headers=headers, timeout=timeout, sink=sink)

    def _request(self, method: str, url: str, sink=None, **kwargs) -> HTTPResponse:
        if kwargs.get("timeout") == -1:
            kwargs["timeout"] = self.timeout
        if 'preload_content' not in kwargs and sink:
            kwargs['preload_content'] = False

        remove_entry_if_none(kwargs, 'body')
        remove_entry_if_none(kwargs, 'fields')

        response: HTTPResponse = self._http.request(method, url=url, **kwargs)

        if sink is not None:
            if response.status == 200:
                self._download_in_chunks(response, sink)
            else:
                _log.warning(f"Download was requested but response code is :{response.status}")

        return response

    def download_chunks(self, url, sink, headers: dict = None, timeout: int = -1) -> HTTPResponse:
        response: urllib3.HTTPResponse = self._request("GET", url,
                                                       headers=headers,
                                                       timeout=timeout,
                                                       preload_content=False)
        self._download_in_chunks(response, sink)

    def _download_in_chunks(self, response: HTTPResponse, sink):
        if response.status != 200:
            raise urllib3.exceptions.HTTPError(f"Bad HTTP Response: {response.status}")
        text_content = isinstance(sink, io.TextIOBase)
        total_size = 0
        if text_content:
            encoding = parse_charset_from_content_type(response.getheader('Content-Type'), 'utf-8')
            reader = codecs.getreader(encoding)(response)
            while True:
                chunk = reader.read(chars=2 ** 16)
                if chunk:
                    sink.write(chunk)
                    total_size += len(chunk)
                else:
                    break

        else:
            for chunk in response.stream(2 ** 16, True):
                sink.write(chunk)
                total_size += len(chunk)

        sink.flush()
        _log.info(f"Downloaded Content's length ({'in chars' if text_content else 'in bytes'}: ({total_size}")
