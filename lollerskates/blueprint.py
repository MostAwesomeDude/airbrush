# Copyright (C) 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import division

from collections import defaultdict
from functools import wraps
from math import floor, sqrt

from werkzeug.contrib.cache import SimpleCache
from werkzeug.routing import BaseConverter, ValidationError
from flask import Blueprint, abort

from flask.ext.holster.main import init_holster, with_template
from flask.ext.holster.simple import html

from lollerskates.analyze import champ_stat_at, is_manaless
from lollerskates.formatting import canonical_champ, canonical_item
from lollerskates.lol import get_champ_stats, get_item_names, single_item
from lollerskates.statistics import cdf


lol = Blueprint("lol", __name__, template_folder="templates")
init_holster(lol)

cache = SimpleCache()


def caching(label):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            data = cache.get(label)
            if data is None:
                data = f(*args, **kwargs)
                cache.set(label, data)
            return data
        return inner
    return outer


@caching("champions")
def get_champions():
    return get_champ_stats()


@caching("item_names")
def item_names():
    return get_item_names()


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
    x = cdf(stddev)
    return int(x * 100)


class SVGMaker(object):

    template = """
    <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
        <!-- Offset for X is -300, Y is flipped by 100 -->

        <g transform="scale(1, -1) translate(0, -150)">
            <path stroke="blue" stroke-width="5" fill="none"
                  d="M 0,1
                     C 67,2    133,15  200,61
                     C 267,112 333,112 400,61
                     C 467,15  533,2   600,1" />

            <g fill="blue" stroke="green" stroke-width="5" fill-opacity="0.5">
                %s
            </g>

            <g stroke="black" stroke-width="5">
                <line x1="0"   y1="0" x2="600" y2="0"   />
                <line x1="300" y1="0" x2="300" y2="150" />
            </g>
        </g>
    </svg>
    """

    rect = "<rect %s />"

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
            rects.append(self._make_rect(x=x, y=0, width=50, height=height))
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


@lol.holster("/items")
@html("items.html")
def items():
    return {"items": get_item_names()}


@lol.holster("/items/<item:i>")
def item(i):
    item, effects = single_item(i)
    return {
        "item": item,
        "effects": effects,
    }


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


def add_item_converter(app):
    class ItemConverter(BaseConverter):
        def to_python(self, value):
            items = get_item_names()
            item = canonical_item(items, value)
            if item is None:
                raise ValidationError()
            return item

        def to_url(self, value):
            return value

    app.url_map.converters["item"] = ItemConverter
