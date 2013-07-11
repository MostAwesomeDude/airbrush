from __future__ import division

from collections import defaultdict
from math import floor, sqrt

from werkzeug.contrib.cache import SimpleCache
from werkzeug.routing import BaseConverter, ValidationError
from flask import Blueprint, abort

from flask.ext.holster.main import init_holster, with_template

from lollerskates.analyze import champ_stat_at, is_manaless
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
        if is_manaless(c) and stat in ("mana", "mregen"):
            # Manaless champion.
            continue

        starting = champ_stat_at(champ, stat, 1)
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
            if is_manaless(champ) and stat in ("mana", "mregen"):
                # Manaless champion.
                continue

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


class SVGMaker(object):

    template = """
    <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <!-- Offset for X is -300, Y is flipped by 100 -->

        <path stroke="blue" stroke-width="5" fill="none"
              d="M 0,149
                 C 100,168 200,72 300,50
                 C 400,72 500,168 600,149" />

        %s

        <line x1="0" y1="150" x2="600" y2="150"
              style="stroke:black; stroke-width: 5" />
        <line x1="300" y1="0" x2="300" y2="150"
              style="stroke:black; stroke-width: 5" />
    </svg>
    """

    rect = """<rect %s
    style="fill:blue;stroke:green;stroke-width:5;fill-opacity:0.5" />
    """

    def _make_rect(self, **kwargs):
        l = []
        for k, v in kwargs.iteritems():
            l.append('%s="%s"' % (k, v))

        return self.rect % " ".join(l)

    def format(self, d):
        buckets = d["Level 1 Stats"]["buckets"]
        rects = []
        total = sum(len(bucket) for bucket in buckets.iteritems())
        for label, bucket in buckets.iteritems():
            size = len(bucket)
            # Height is 100, scaled by 1/sqrt(2pi) ~= 2.5066...
            # 100 for now.
            height = 100 * size // total
            # The labels are half-stddev-sized. Multiply by 100 to get the
            # width, and then adjust by moving them over to the offset mark.
            x = int(label * 100) + 300
            # And finally, remember that Y descends from above, so we need to
            # flip on the Y-axis for positioning.
            y = 150 - height
            rects.append(self._make_rect(x=x, y=y, width=50, height=height))
        return self.template % "\n".join(rects)


@lol.holster("/stats/<stat>")
@with_template("svg", SVGMaker())
def lol_stats(stat):
    champions = get_champions()

    level1 = {}
    level18 = {}

    for champ in champions:
        if is_manaless(champ) and stat in ("mana", "mregen"):
            # Manaless champion.
            continue

        level1[champ] = champ_stat_at(champions[champ], stat, 1)
        level18[champ] = champ_stat_at(champions[champ], stat, 18)

    d = {
        "Level 1 Stats": calculate(level1.values()),
        "Level 18 Stats": calculate(level18.values()),
    }
    return d


@lol.holster("/stats/<stat>/<champ:selected>")
def lol_stats_champ(stat, selected):
    if is_manaless(selected) and stat in ("mana", "mregen"):
        # Manaless champion.
        return {selected: "<Manaless>"}

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
