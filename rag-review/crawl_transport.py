"""Pinned public-only transport for the upstream crawler's urllib opener contract."""

import urllib.error
from urllib.parse import quote, urljoin, urlunsplit

from ingestion import _public_target, _resolve_public, _pinned_connection, decode_source_body


class CrawlTransport:
    def __init__(self, owner):
        self.owner = owner

    def open(self, request, timeout=15):
        url = request.full_url
        for _ in range(6):
            parsed, host, port = _public_target(url)
            connection = _pinned_connection(
                parsed, host, port, _resolve_public(host, port), timeout
            )
            try:
                target = urlunsplit(
                    (
                        "",
                        "",
                        quote(parsed.path or "/", safe="/%:@!$&'()*+,;=-._~"),
                        quote(parsed.query, safe="/%?:@!$&'()*+,;=-._~"),
                        "",
                    )
                )
                connection.request(
                    "GET",
                    target,
                    headers={
                        **dict(request.header_items()),
                        "Accept-Encoding": "identity",
                        "Connection": "close",
                    },
                )
                response = connection.getresponse()
                if response.status in (301, 302, 303, 307, 308):
                    location = response.getheader("Location")
                    if not location:
                        raise ValueError("Redirect missing location")
                    url = urljoin(url, location)
                    # Preserve upstream robots checks for each redirect target.
                    if not url.endswith("/robots.txt"):
                        self.owner.ensure_robots(url)
                    continue
                if response.status != 200:
                    raise urllib.error.HTTPError(
                        url, response.status, "Source HTTP failure", response.headers, None
                    )
                raw = response.read(self.owner.max_bytes + 1)
                encoding = response.getheader("Content-Encoding")
                raw = decode_source_body(raw, encoding, self.owner.max_bytes)
                if encoding and encoding.strip().lower() != "identity":
                    # The buffered response now contains decoded representation bytes.
                    del response.headers["Content-Encoding"]
                    del response.headers["Content-Length"]
                    response.headers["Content-Length"] = str(len(raw))
                return BufferedResponse(raw, response.headers, url, response.status)
            finally:
                connection.close()
        raise ValueError("Too many redirects")


class BufferedResponse:
    def __init__(self, body, headers, url, status):
        self.body, self.headers, self.url, self.status = body, headers, url, status

    def read(self, limit):
        return self.body[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False
