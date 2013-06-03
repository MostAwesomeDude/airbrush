from __future__ import with_statement

from werkzeug.contrib.cache import SimpleCache

from flask import Flask, abort, redirect, request, url_for
from flask.ext.holster.helpers import lift
from flask.ext.holster.main import init_holster
from flask.ext.holster.simple import html

from analyze import champ_stat_at
from lol import get_champ_stats
from tipsum import make_chains, make_text
from wonders.wonders import Wonders, prettify

app = Flask(__name__)
app.debug = True
init_holster(app)

cache = SimpleCache()

def get_champions():
    champs = cache.get("champions")
    if not champs:
        champs = get_champ_stats()
        cache.set("champions", champs)
    return champs

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


@app.holster("/lol/raw")
def lol_raw():
    champions = get_champions()
    return champions


@app.holster("/lol/raw/<champ>")
def lol_raw_champ(champ):
    champions = get_champions()
    if champ not in champions:
        abort(404)
    return champions[champ]


@app.holster("/lol/cooked/<champ>")
def lol_cooked_champ(champ):
    champions = get_champions()
    if champ not in champions:
        abort(404)

    c = champions[champ]

    d = {
        "Champion": champ,
        "Range": c["range"],
        "Movement Speed": c["ms"],
    }
    stats = {
        "ad": "Attack Damage",
        "as": "Attack Speed",
        "armor": "Armor",
        "mr": "Magic Resistance",
        "health": "Health",
        "mana": "Mana",
        "hregen": "Health Regeneration",
        "mregen": "Mana Regeneration",
    }

    for stat in stats:
        starting = champ_stat_at(c, stat, 1)
        ending = champ_stat_at(c, stat, 18)
        skey = "%s at Level 1" % stats[stat]
        ekey = "%s at Level 18" % stats[stat]
        d[skey] = starting
        d[ekey] = ending

    return d


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
