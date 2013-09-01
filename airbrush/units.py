def ukey(n):
    cls = n.__class__
    return cls.name, cls.abbreviation


def add(self, other):
    if ukey(self) != ukey(other):
        raise TypeError("Unit mismatch")

    return self.__class__(self.n + other.n)


def sub(self, other):
    if ukey(self) != ukey(other):
        raise TypeError("Unit mismatch")

    return self.__class__(self.n - other.n)


def init(self, n):
    self.n = n


def rep(self):
    return "%r (%s)" % (self.n, self.abbreviation)


def unit(name, abbreviation=None):

    members = {
        "name": name,
        "abbreviation": abbreviation or name,
        "__init__": init,
        "__repr__": rep,
        "__nonzero__": lambda self: bool(self.n),
        "__int__": lambda self: int(self.n),
        "__float__": lambda self: float(self.n),
        "__add__": add,
        "__sub__": sub,
    }

    return type(name, (object,), members)
