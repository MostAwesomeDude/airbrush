#!/usr/bin/python3
import random

class Wonders(object):

    def __init__(self):
        self.load_wonders('./wonders.txt')

    def load_wonders(self, path):
        self.wonders = []
        with open(path) as wonders_file:
            self.wonders = [s.strip() for s in wonders_file]

    def get(self, n):
        return self.wonders[n-1]

    def random(self):
        return random.choice(self.wonders)


def main():
    w = Wonders()
    return w.random()


if __name__ == '__main__':
    print(main())
