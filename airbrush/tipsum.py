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
from __future__ import division

from collections import defaultdict
import random

from airbrush.get import retrieve


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


def make_stream():
    tree = retrieve("http://timecube.com/")

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

    return l


def parse_chains(l):

    chains = defaultdict(list)
    heads = []
    iterator = enumerate(l[:-2])

    for i, word in iterator:
        if word is EOS:
            # Set up a head and append a partial chain.
            heads.append(l[i + 1])
            chains[l[i + 1],].append(l[i + 2])
        elif EOS in l[i + 1:i + 2]:
            # Just pump it away.
            continue
        else:
            chain = word, l[i + 1]
            chains[chain].append(l[i + 2])

    return heads, dict(chains)


def make_chains():
    l = make_stream()
    return parse_chains(l)


def make_text(heads, chains):
    l = [random.choice(heads)]
    while True:
        t = tuple(l[-2:])
        choice = random.choice(chains[t])
        if choice is EOS:
            break
        else:
            l.append(choice)
    return l
