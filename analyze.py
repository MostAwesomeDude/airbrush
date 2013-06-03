def champ_stat_at(champion, stat, level):
    """
    Calculate the base statistic for a champion at a given level.

    Levels are not range-checked.

    The `champion` should be a dict of base statistics for the champion.
    """

    gains = champion[stat + "g"] * level
    return champion[stat] + gains
