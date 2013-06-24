from collections import defaultdict
from math import sqrt

from werkzeug.contrib.cache import SimpleCache
from flask import Blueprint, abort

from flask.ext.holster.main import init_holster

from lollerskates.analyze import champ_stat_at
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
