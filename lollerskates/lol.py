#!/usr/bin/env python

from collections import defaultdict
import re
from string import ascii_letters

from lxml.html import fromstring
import requests


def retrieve(name):
    print "Retrieving", name, "..."
    url = "http://leagueoflegends.wikia.com/wiki/%s" % name
    request = requests.get(url)
    html = request.content
    print "Parsing", name, "..."
    document = fromstring(html)
    return document


def get_champ_stats():
    document = retrieve("Base_champion_statistics")

    table = document.xpath("//table")[0]
# In the future, if you ever need the magic incantation to get the table
# headers, try this: [i[0].text if i else i.text for i in table[0]]
    headers = [
        "health", "healthg",
        "hregen", "hregeng",
        "mana", "manag",
        "mregen", "mregeng",
        "ad", "adg",
        "as", "asg",
        "armor", "armorg",
        "mr", "mrg",
        "ms",
        "range",
    ]

    champions = {}

    for row in table[1:]:
        d = {}
        # Champ name rule: Remove spaces and punctuation, and capitalize by hand.
        champ = row[0][0].text.strip()
        champ = champ.replace(" ", "").replace(".", "").replace("'", "")
        champ = champ[0].upper() + champ[1:]
        for label, cell in zip(headers, row[1:]):
            data = cell.text.strip()
            # AS per level is measured in percents.
            if data.endswith("%"):
                data = float(data[:-1]) / 100.0
            else:
                data = float(data)
            d[label] = data
        champions[champ] = d

    return champions


def clauses_for_champs(champions):
# Prolog doesn't like discontiguous clauses. Sort before printing.
    champions.sort(key=lambda d: d["champ"])

    clauses = defaultdict(list)

    for i, champion in enumerate(champions):
        name = champion["champ"].lower()
        clauses["champ_name"].append("champ(%d, %s)." % (i, name))
        for stat in champion:
            if stat == "champ":
                continue
            clauses[stat].append("champ_%s(%d, %f)." % (stat, i, champion[stat]))

    return clauses


def clauses_for_items():
    document = retrieve("Template:Items")

    trs = document.xpath("//table/tr")[1:-3]
    l = [x.text for tr in trs for x in tr.xpath("td/span/a/span")]
    l.sort()

    res = {
        "item_ad": "\+(\d+) attack damage",
        "item_ap": "\+(\d+) ability power",
        "item_armor": "\+(\d+) armor",
        "item_as": "\+(\d+)% attack speed",
        "item_cc": "\+(\d+)% critial strike chance",
        "item_health": "\+(\d+) health(?! regeneration)",
        "item_hregen": "\+(\d+) health regeneration",
        "item_lifesteal": "\+(\d+)% life steal",
        "item_mana": "\+(\d+) mana(?! regeneration)",
        "item_mr": "\+(\d+) magic resistance",
        "item_mregen": "\+(\d+(\.\d+)?) mana regeneration",
        "item_spellvamp": "\+(\d+)% spell vamp",
    }

    clauses = defaultdict(list)

    for i, item in enumerate(l):
        name = "".join(c.lower() for c in item if c in ascii_letters)
        clauses["item_name"].append("item(%d, %s)." % (i, name))
        document = retrieve(item)
        for tr in document.xpath("//table/tr"):
            text = tr.text_content()
            if "Effect" not in text:
                continue
            for clause, regex in res.iteritems():
                m = re.search(regex, text, re.M)
                if m:
                    clauses[clause].append("%s(%d, %s)."
                        % (clause, i, m.groups()[0]))

    return clauses


def print_clauses(clauses, champions):
    handle = open("data.pl", "wb")

    handle.write("""/* set filetype=prolog syntax=prolog */
    /* This module is autogenerated by champs.py in the top-level directory.
     * To regenerate, be online, then $ python data.py
     * If you hand-edit this, be sure to explain your reasoning.
     * All of the champion quirks are tracked in champs.py, not in this file.
     * ~ C. */

    """)

    for clause in sorted(clauses):
        for datum in clauses[clause]:
            handle.write(datum)
            handle.write("\n")
        handle.write("\n")

    handle.write("champ_max(%d).\n\n" % (len(champions) - 1))
