def canonical_champ(champs, needle):
    """
    Get the actual champ name, or None.
    """

    if needle in champs:
        return needle

    candidates = []
    for champ in champs:
        if champ.lower() == needle:
            return champ
        elif champ.lower().startswith(needle):
            candidates.append(champ)

    if len(candidates) == 1:
        return candidates[0]

    nicknames = {
        "bird": "Anivia",
        "bull": "Alistar",
        "cassie": "Cassiopeia",
        "cat": "Nidalee",
        "cow": "Alistar",
        "dog": "Nasus",
        "heimy": "Heimerdinger",
        "lion": "Rengar",
        "mf": "MissFortune",
        "missy": "MissFortune",
        "monk": "LeeSin",
        "mu": "Amumu",
        "mundo": "DrMundo",
        "niv": "Anivia",
        "pig": "Sejuani",
        "raka": "Soraka",
        "relly": "Irelia",
        "snake": "Cassiopeia",
        "tf": "TwistedFate",
        "wick": "Warwick",
        "wolf": "Warwick",
        "ww": "Warwick",
        "yeti": "Nunu",
    }

    if needle.lower() in nicknames:
        return nicknames[needle.lower()]
