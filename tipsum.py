from __future__ import division

from collections import defaultdict
import random
from urllib import urlopen

from lxml.html.soupparser import fromstring

EOS = object()

def is_eos(word):
    """
    Classify a word as being at the end of a sentence.
    """

    if word.endswith("?"):
        return True
    if word.endswith(".\""):
        return True

    dots = "dr.", "b."
    return word.endswith(".") and word.lower() not in dots

def make_chains():
    page = urlopen("http://timecube.com/")
    tree = fromstring(page.read())
    chains = defaultdict(list)

    l = []

    for span in tree.xpath("//span"):
        contents = span.text_content().strip()
        for word in contents.split():
            # Discard double-spaces and NBSPs.
            word = word.strip()
            if not word:
                continue

            # There will be a couple "words" that are punctuation-based
            # HRs/BRs. Discard them with a length-based heuristic.
            if len(word) >= 25:
                continue

            # Save this word.
            l.append(unicode(word.strip()))

            if is_eos(word):
                # This ends a sentence; push a marker onto the stream.
                l.append(EOS)

    heads = []
    iterator = enumerate(l[:-3])

    for i, word in iterator:
        if word is EOS:
            # Set up a head and append a partial chain.
            heads.append(l[i + 1])
            chains[l[i + 1], l[i + 2]].append(l[i + 3])
            chains[l[i + 1],].append(l[i + 2])
        elif EOS in l[i + 1:i + 3]:
            # Just pump it away.
            continue
        else:
            chain = word, l[i + 1], l[i + 2]
            chains[chain].append(l[i + 3])

    return heads, dict(chains)

def make_text(heads, chains):
    l = [random.choice(heads)]
    while True:
        t = tuple(l[-3:])
        choice = random.choice(chains[t])
        if choice is EOS:
            break
        else:
            l.append(choice)
    return l
