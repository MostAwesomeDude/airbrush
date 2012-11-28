from __future__ import division

from collections import defaultdict
import random
from urllib import urlopen

from lxml.html.soupparser import fromstring

def make_chains():
    page = urlopen("http://timecube.com/")
    tree = fromstring(page.read())
    chains = defaultdict(list)

    l = []

    for span in tree.xpath("//span"):
        contents = span.text_content().strip()
        for word in contents.split():
            # There will be a couple "words" that are either NBSPs or
            # punctuation-based HRs/BRs. Discard them with a length-based
            # heuristic.
            word = word.strip()
            if word and len(word) < 25:
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
