from urllib.parse import urlparse

import boto3

_session = boto3.session.Session()


def new_service_client(service_name: str, region_name: str = None, **kwargs):
    return _session.client(service_name, region_name, **kwargs)


class S3Url(object):
    # copied from https://stackoverflow.com/a/42641363/1700467
    def __init__(self, url):
        self._parsed = urlparse(url, allow_fragments=False)

    @property
    def bucket(self):
        return self._parsed.netloc

    @property
    def key(self):
        if self._parsed.query:
            return self._parsed.path.lstrip('/') + '?' + self._parsed.query
        else:
            return self._parsed.path.lstrip('/')

    @property
    def url(self):
        return self._parsed.geturl()
