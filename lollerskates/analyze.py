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
def is_manaless(champ):
    """
    Classify a champion as "manaless".

    Manaless champions do not have a mana pool. Their raw numerical data may
    reuse the mana-related fields for champion-specific concepts, or be zeroed
    out. Because of this, manaless champions should be avoidable in certain
    situations.
    """

    s = set([
        "Aatrox",
        "Akali",
        "DrMundo",
        "Garen",
        "Katarina",
        "Kennen",
        "LeeSin",
        "Mordekaiser",
        "Renekton",
        "Rengar",
        "Riven",
        "Rumble",
        "Shen",
        "Shyvana",
        "Tryndamere",
        "Vladimir",
        "Zac",
        "Zed",
    ])

    return champ in s


def champ_stat_at(champion, stat, level):
    """
    Calculate the base statistic for a champion at a given level.

    Levels are not range-checked.

    The `champion` should be a dict of base statistics for the champion.
    """

    if stat == "ms":
        # Movement speed doesn't vary with level.
        return champion["ms"]

    if stat == "as":
        # Attack speed is *so* weird.
        level -= 1
        gains = champion["asg"] * level
        return champion["as"] * (gains + 1)

    gains = champion[stat + "g"] * level
    return champion[stat] + gains
