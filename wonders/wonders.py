#!/usr/bin/python2
import sys
import random
from flask import Flask, render_template, abort

class Wonders(object):

    def __init__(self, path):
        self.load_wonders(path)

    def load_wonders(self, path):
        self.wonders = []
        with open(path) as wonders_file:
            self.wonders = [s.strip() for s in wonders_file]

    def get(self, n):
        effect = self.wonders[n-1]
        if effect[-1] not in ['.', '!', '?']:
            effect = effect + '.'
        return effect

    def random(self):
        r = random.randint(1, len(self.wonders) + 1)
        return self.get(r)

    def serve(self):
        app = Flask(__name__)

        @app.route('/')
        def index():
            number, effect = self.random().split(' ', 1)
            return render_template('effect.html', effect=effect, number=number)

        @app.route('/<int:n>')
        def particular(n):
            if n <= 0 or n >= len(self.wonders):
                abort(404)
            number, effect = self.get(n).split(' ', 1)
            return render_template('effect.html', effect=effect, number=number)

        @app.errorhandler(404)
        def error(error):
            return render_template('effect.html', effect='Wonder not found.',
                    number=404)

        app.run(debug=True)


def main():
    w = Wonders()
    return w.random()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        w = Wonders()
        print {
            'random': w.random,
            'serve': w.serve,
        }[sys.argv[1]](*sys.argv[2:])
    else:
        print('Usage: {0} command'.format(sys.argv[0]))
        sys.exit(1)
