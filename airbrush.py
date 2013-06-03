from __future__ import with_statement

from werkzeug.contrib.cache import SimpleCache

from flask import Flask, abort, redirect, request, url_for
from flask.ext.holster.helpers import lift
from flask.ext.holster.main import init_holster
from flask.ext.holster.simple import html

from lol import get_champ_stats
from tipsum import make_chains, make_text
from wonders.wonders import Wonders, prettify

app = Flask(__name__)
app.debug = True
init_holster(app)

cache = SimpleCache()

w = Wonders()
f = app.open_resource("wonders/wonders.txt")
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
    from elements import match_word
    matches = match_word(word)
    matches = [[x.capitalize() for x in match] for match in matches]
    return {"matches": matches}

heads, chains = make_chains()

@app.bare_holster("/tipsum")
@app.bare_holster("/tipsum/<int:length>")
@lift(no_cache)
@app.holsterize
@html("tipsum.html")
def tipsum(length=3):
    sentences = []
    for i in range(length):
        words = make_text(heads, chains)
        sentences.append(u" ".join(words))
    return {"tipsum": sentences}

@app.holster("/lol")
def lol():
    champions = cache.get("champions")
    if not champions:
        champions = get_champ_stats()
        cache.set("champions", champions)
    return champions

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
