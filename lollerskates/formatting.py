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
def canonical(haystack, needle, nicknames):
    """
    Attempt to canonicalize a name based on an iterable of acceptable names
    and a mapping of nicknames.
    """

    if needle in haystack:
        return needle

    lneedle = needle.lower()

    candidates = []
    for candidate in haystack:
        if candidate.lower() == lneedle:
            return candidate
        elif candidate.lower().startswith(lneedle):
            candidates.append(candidate)

    if len(candidates) == 1:
        return candidates[0]

    if lneedle in nicknames:
        return nicknames[lneedle]

    return None


def canonical_champ(champs, needle):
    """
    Get the actual champ name, or None.
    """

    nicknames = {
        "bird":   "Anivia",
        "bull":   "Alistar",
        "cassie": "Cassiopeia",
        "cat":    "Nidalee",
        "cow":    "Alistar",
        "dog":    "Nasus",
        "heimy":  "Heimerdinger",
        "lion":   "Rengar",
        "mf":     "MissFortune",
        "missy":  "MissFortune",
        "monk":   "LeeSin",
        "mu":     "Amumu",
        "mundo":  "DrMundo",
        "niv":    "Anivia",
        "pig":    "Sejuani",
        "pony":   "Hecarim",
        "raka":   "Soraka",
        "relly":  "Irelia",
        "snake":  "Cassiopeia",
        "tf":     "TwistedFate",
        "wick":   "Warwick",
        "wolf":   "Warwick",
        "ww":     "Warwick",
        "yeti":   "Nunu",
    }

    return canonical(champs, needle, nicknames)


def canonical_item(items, needle):

    nicknames = {
    }

    return canonical(items, needle, nicknames)
