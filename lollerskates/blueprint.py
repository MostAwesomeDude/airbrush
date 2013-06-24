from __future__ import division

from collections import defaultdict
from math import floor, sqrt

from werkzeug.contrib.cache import SimpleCache
from werkzeug.routing import BaseConverter, ValidationError
from flask import Blueprint, abort

from flask.ext.holster.main import init_holster

from lollerskates.analyze import champ_stat_at
from lollerskates.formatting import canonical_champ
from lollerskates.lol import get_champ_stats


lol = Blueprint("lol", __name__)
init_holster(lol)

cache = SimpleCache()


def get_champions():
    champs = cache.get("champions")
    if not champs:
        champs = get_champ_stats()
        cache.set("champions", champs)
    return champs


@lol.holster("/raw")
def lol_raw():
    champions = get_champions()
    return champions


@lol.holster("/raw/<champ:c>")
def lol_raw_champ(c):
    champions = get_champions()
    return champions.get(c, abort(400))


@lol.holster("/cooked/<champ:c>")
def lol_cooked_champ(c):
    champions = get_champions()

    champ = champions.get(c, abort(400))

    d = {
        "Champion": champ,
        "Range": champ["range"],
        "Movement Speed": champ["ms"],
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
        starting = champ_stat_at(champ, stat, 1)
        if starting == 0 and stat in ("mana", "mregen"):
            # Manaless champion.
            continue
        ending = champ_stat_at(champ, stat, 18)

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

    buckets = defaultdict(list)
    for value in values:
        k = floor(value_to_stddev(mean, stddev, value) * 2) / 2
        buckets[k].append(value)

    rv = {
        "mean": mean,
        "variance": variance,
        "stddev": stddev,
        "buckets": dict(buckets),
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


@lol.holster("/stats/<stat>/<champ:selected>")
def lol_stats_champ(stat, selected):
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


def add_champ_converter(app):
    class ChampConverter(BaseConverter):
        def to_python(self, value):
            cs = get_champions().keys()
            champ = canonical_champ(cs, value)
            if champ is None:
                raise ValidationError()
            return champ

        def to_url(self, value):
            return value

    app.url_map.converters["champ"] = ChampConverter
