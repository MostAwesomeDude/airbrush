from __future__ import division


def ukey(n):
    return n.nums, n.denoms


def balance(nums, denoms):
    """
    Cancel terms on a single fraction.
    """

    sn = sorted(nums)
    sd = sorted(denoms)

    i = 0

    while i < len(sn):
        if sn[i] in sd:
            sd.remove(sn[i])
            sn.remove(sn[i])
        else:
            i += 1

    return tuple(sn), tuple(sd)


class Unit(object):
    """
    The base type of all wrapped units.
    """

    def __init__(self, n):
        self.n = n

    def __repr__(self):
        nums = "*".join(self.nums)
        denoms = "*".join(self.denoms)

        if not denoms:
            label = nums
        elif not nums:
            label = "1/" + denoms
        else:
            label = "/".join([nums, denoms])

        return "%r (%s)" % (self.n, label)

    def __nonzero__(self):
        return bool(self.n)

    def __int__(self):
        return int(self.n)

    def __float__(self):
        return float(self.n)

    def __add__(self, other):
        if ukey(self) != ukey(other):
            raise TypeError("Unit mismatch")

        return self.__class__(self.n + other.n)

    def __sub__(self, other):
        if ukey(self) != ukey(other):
            raise TypeError("Unit mismatch")

        return self.__class__(self.n - other.n)

    def __mul__(self, other):
        nums = self.nums + other.nums
        denoms = self.denoms + other.denoms

        cls = unit("Generated", nums=nums, denoms=denoms)

        return cls(self.n * other.n)

    def __truediv__(self, other):
        # Division is just multiplication inverted.
        nums = self.nums + other.denoms
        denoms = self.denoms + other.nums

        cls = unit("Generated", nums=nums, denoms=denoms)

        return cls(self.n / other.n)

    __div__ = __truediv__


def unit(name, nums=(), denoms=()):

    if not nums:
        nums = name,

    nums, denoms = balance(nums, denoms)

    members = {
        "nums": nums,
        "denoms": denoms,
    }

    return type(name, (Unit,), members)
