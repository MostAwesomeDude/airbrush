#!/usr/bin/python2
import random

def prettify(s):
    if s[-1] not in (".", "!", "?"):
        s += "."

    return s

class Wonders(object):

    def __init__(self):
        self.wonders = []

    def load_wonders(self, path):
        with open(path) as f:
            for line in f:
                digits, rest = line.split(" ", 1)
                self.wonders.append(rest.strip())

    def random(self):
        r = random.randint(0, len(self.wonders))
        return r, self.wonders[r]
