from lxml.html import fromstring

import requests

from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()


def retrieve(url):
    cached = cache.get(url)
    if cached is not None:
        print "retrieve:", url, "cache hit"
        return cached

    print "retrieve:", url, "cache miss"
    request = requests.get(url)
    html = request.content
    document = fromstring(html)

    cache.set(url, document)
    return document
