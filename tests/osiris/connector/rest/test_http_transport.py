import io

from osiris.connector.rest.http_transport import HTTPTransport

t = HTTPTransport()


def test_download_chunks():
    with io.StringIO() as out:
        t.get("http://httpbin.org/encoding/utf8", sink=out)
        out.seek(0)
        text = out.read()
    assert text


def test_post_action():
    with io.StringIO() as out:
        t.post("https://httpbin.org/post", sink=out)
        out.seek(0)
        text = out.read()
    assert text


def test_post_action_expecting_binary():
    with io.BytesIO() as out:
        t.post("https://httpbin.org/post", sink=out)
        out.seek(0)
        data = out.read()
    assert data


def test_post_action_without_sink():
    response = t.post("https://httpbin.org/post")
    data = response.data
    assert data


def test_get_action_without_sink():
    response = t.get("https://httpbin.org/get")
    data = response.data
    assert data
