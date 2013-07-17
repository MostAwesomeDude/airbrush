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
