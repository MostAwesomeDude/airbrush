from __future__ import division, with_statement

from math import cos, pi, sin
from time import time

from flask import Flask, abort, redirect, request, url_for
from flask.ext.holster.helpers import lift
from flask.ext.holster.main import init_holster, with_template
from flask.ext.holster.simple import html

from lollerskates.blueprint import add_champ_converter, lol

from airbrush.elements import match_word
from airbrush.tipsum import make_chains, make_text
from airbrush.wonders import Wonders, prettify

app = Flask(__name__)
app.debug = True
init_holster(app)

w = Wonders()
f = app.open_resource("wonders.txt")
w.load_wonders(f)

def no_cache(response):
    response.cache_control.no_cache = True
    return response

@app.bare_holster("/wonders")
@app.bare_holster("/wonders/<int:n>")
@lift(no_cache)
@app.holsterize
@html("wonders.html")
def wonders(n=None):
    if n is None:
        n, effect = w.random()
    else:
        # Switch from zero-indexed to one-indexed.
        n -= 1

        if 0 <= n < len(w.wonders):
            effect = w.wonders[n]
        else:
            abort(404)

    # And back to one-indexed.
    n += 1

    return {
        "effect": prettify(effect),
        "number": n,
    }

@app.holster("/elements", methods=["GET", "POST"])
@html("elements.html")
def elements():
    if request.method == "POST":
        s = request.form["word"].strip().lower()
        return redirect(url_for("show_element", word=s))

    return {}

@app.holster("/elements/<word>")
@html("show_element.html")
def show_element(word):
    matches = match_word(word)
    matches = [[x.capitalize() for x in match] for match in matches]
    return {"matches": matches}

@app.bare_holster("/tipsum")
@app.bare_holster("/tipsum/<int:length>")
@lift(no_cache)
@app.holsterize
@html("tipsum.html")
def tipsum(length=3):
    heads, chains = make_chains()
    sentences = []
    for i in range(length):
        words = make_text(heads, chains)
        sentences.append(u" ".join(words))
    return {"tipsum": sentences}


class SVGMaker(object):

    template = """
    <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <circle cx="50" cy="50" r="50" stroke="black" stroke-width="1"
                fill="white" />

        %s
    </svg>
    """

    @staticmethod
    def _aim(theta):
        theta -= pi / 2
        return cos(theta), sin(theta)

    def _hand(self, amount, length):
        theta = pi * amount / 50
        x, y = self._aim(theta)
        line = '<line x1="50" y1="50" x2="%d" y2="%d" stroke="black" />'
        return line % (x * length + 50, y * length + 50)

    def format(self, d):
        hands = []
        hands.append(self._hand(d["hour"], 30))
        hands.append(self._hand(d["minute"], 40))
        return self.template % "\n".join(hands)


@app.bare_holster("/nr")
@lift(no_cache)
@app.holsterize
@html("nr.html")
@with_template("svg", SVGMaker())
def nr():
    offset = 6906 * 100000000 + 92 * 1000000 + 3 * 10000 + 33 * 100 + 33

    milliseconds = int(time() * 1000)

    # Newrem time is actually delightful. It is metric time, with centiseconds
    # that tick at 1/90 the speed of Earth milliseconds.
    result = milliseconds // 90 + offset
    result, nr_seconds = divmod(result, 100)
    result, nr_minutes = divmod(result, 100)
    result, nr_hours = divmod(result, 100)
    nr_years, nr_days = divmod(result, 100)

    seasons = ["JA", "SA", "KA", "RA"]

    if nr_days == 0:
        date = "Frista"
    elif nr_days == 99:
        date = "Lanos"
    else:
        date = "%s%d" % (seasons[nr_days // 25], nr_days)

    return {
        "second": nr_seconds,
        "minute": nr_minutes,
        "hour": nr_hours,
        "day": nr_days,
        "date": date,
        "year": nr_years,
    }


@app.holster("/")
@html("index.html")
def index():
    return {
        "stuff": {
            "dnd": {
                "wonders": url_for("wonders", _external=True),
            },
            "words": {
                "elements": url_for("elements", _external=True),
                "tipsum": url_for("tipsum", _external=True),
            },
        },
    }


# And finally hook up the blueprints.
add_champ_converter(app)
app.register_blueprint(lol, url_prefix="/lol")
