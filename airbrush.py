from __future__ import with_statement

from collections import defaultdict
from math import sqrt

from werkzeug.contrib.cache import SimpleCache

from flask import Blueprint, Flask, abort, redirect, request, url_for
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

lol = Blueprint("lol", __name__)
init_holster(lol)

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


@lol.holster("/raw")
def lol_raw():
    champions = get_champions()
    return champions


@lol.holster("/raw/<champ>")
def lol_raw_champ(champ):
    champions = get_champions()
    if champ not in champions:
        abort(404)
    return champions[champ]


@lol.holster("/cooked/<champ>")
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
        if starting == 0 and stat in ("mana", "mregen"):
            # Manaless champion.
            continue
        ending = champ_stat_at(c, stat, 18)

        skey = "%s at Level 1" % stats[stat]
        ekey = "%s at Level 18" % stats[stat]

        d[skey] = starting
        d[ekey] = ending

    return d


@lol.holster("/height-chart/<stat>")
def lol_height_chart(stat):
    champions = get_champions()

    total_healths = defaultdict(int)

    for level in range(1, 19):
        healths = {}
        for champ in champions:
            health = champ_stat_at(champions[champ], stat, level)
            healths[champ] = health

        for standing, champ in enumerate(sorted(healths,
                                                key=lambda k: healths[k])):
            total_healths[champ] += standing

    d = sorted(total_healths, key=lambda k: total_healths[k])

    return d


def calculate(values):
    mean = sum(values) / len(values)

    variance = (sum((mean - value) ** 2 for value in values)
                / (len(values) - 1))
    stddev = sqrt(variance)

    rv = {
        "mean": mean,
        "variance": variance,
        "stddev": stddev,
    }
    return rv


def value_to_stddev(mean, stddev, value):
    return (value - mean) / stddev


def stddev_to_percentile(stddev):
    if stddev < -1.29:
        return 0
    elif stddev < -0.85:
        return 10
    elif stddev < -0.53:
        return 20
    elif stddev < -0.26:
        return 30
    elif stddev < 0:
        return 40
    elif stddev < 0.26:
        return 50
    elif stddev < 0.53:
        return 60
    elif stddev < 0.85:
        return 70
    elif stddev < 1.29:
        return 80
    else:
        return 90


@lol.holster("/stats/<stat>")
def lol_stats(stat):
    champions = get_champions()

    level1 = {}
    level18 = {}

    for champ in champions:
        level1[champ] = champ_stat_at(champions[champ], stat, 1)
        level18[champ] = champ_stat_at(champions[champ], stat, 18)

    d = {
        "Level 1 Stats": calculate(level1.values()),
        "Level 18 Stats": calculate(level18.values()),
    }
    return d


@lol.holster("/stats/<stat>/<champ>")
def lol_stats_champ(stat, champ):
    selected = champ
    champions = get_champions()

    level1 = {}
    level18 = {}

    for champ in champions:
        level1[champ] = champ_stat_at(champions[champ], stat, 1)
        level18[champ] = champ_stat_at(champions[champ], stat, 18)

    l1stats = calculate(level1.values())
    l18stats = calculate(level18.values())

    champ1value = champ_stat_at(champions[selected], stat, 1)
    champ18value = champ_stat_at(champions[selected], stat, 18)

    champ1stddev = value_to_stddev(l1stats["mean"], l1stats["stddev"],
                                   champ1value)
    champ18stddev = value_to_stddev(l18stats["mean"], l18stats["stddev"],
                                    champ18value)

    champ1stats = {
        "Value": champ1value,
        "Stddev": champ1stddev,
        "Percentile": stddev_to_percentile(champ1stddev),
    }

    champ18stats = {
        "Value": champ18value,
        "Stddev": champ18stddev,
        "Percentile": stddev_to_percentile(champ18stddev),
    }

    d = {
        "Level 1 Stats": l1stats,
        "Level 18 Stats": l18stats,
        selected: {
            "Level 1 Stats": champ1stats,
            "Level 18 Stats": champ18stats,
        },
    }
    return d


# And finally hook up the blueprints.
app.register_blueprint(lol, url_prefix="/lol")
