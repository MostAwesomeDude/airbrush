from lxml.html import fromstring

import requests

from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache(default_timeout=60 * 15)


def retrieve(url):
    html = cache.get(url)
    if html is None:
        print "retrieve:", url, "cache miss"
        request = requests.get(url)
        html = request.content
        cache.set(url, html)
    else:
        print "retrieve:", url, "cache hit"

    document = fromstring(html)
    return document
