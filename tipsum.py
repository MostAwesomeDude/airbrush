from __future__ import division

from collections import defaultdict
import random

import requests
from lxml.html.soupparser import fromstring

def make_chains():
    page = requests.get("http://timecube.com/")
    tree = fromstring(page.text)
    chains = defaultdict(list)

    l = []

    for span in tree.xpath("//span"):
        contents = span.text_content().strip()
        for word in contents.split():
            if word:
                l.append(unicode(word.strip()))

    for i, word in enumerate(l[:-3]):
        chain = word, l[i + 1], l[i + 2]
        chains[chain].append(l[i + 3])

    return dict(chains)

def make_text(chains, length):
    l = list(random.choice(list(chains)))
    while len(l) < length:
        t = tuple(l[-3:])
        l.append(random.choice(chains[t]))
    return l
