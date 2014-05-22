# Copyright (C) 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from lxml.html import fromstring

import requests

from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache(default_timeout=60 * 60)


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
