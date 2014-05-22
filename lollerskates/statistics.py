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
from math import exp, pi, sqrt

# All of the erf() implementations come from CPython.

def erf_series(x):
    """
    Power-series-driven approximation of erf(x).

    Converges quickly for small x.
    """

    terms = 25
    x2 = x ** 2
    a = 0
    fk = terms + 0.5

    for i in range(terms):
        a = 2 + x2 * a / fk
        fk -= 1

    result = a * x * exp(-x2) / sqrt(pi)
    return result


def erfc_continued(x):
    """
    Continued fraction expansion of erfc(x).

    Converges decently for abs(x) >= 2.0.
    """

    # Above this point, erfc(x) is too close to 1 to be representable with any
    # kind of accuracy.
    if x >= 30:
        return 0

    x2 = x ** 2
    a = 0
    da = 0.5
    p = 1
    p_last = 0
    q = da + x2
    q_last = 0

    for i in range(50):
        a += da
        da += 2
        b = da + x2
        p, p_last = b * p - a * p_last, p
        q, q_last = b * q - a * q_last, q

    result = p / q * x * exp(-x2) / sqrt(pi)
    return result


def erf(x):
    """
    erf(x).
    """

    if -1.5 < x < 1.5:
        return erf_series(x)
    else:
        erfc = erfc_continued(abs(x))
        return 1 - erfc if x > 0 else erfc - 1


def cdf(x):
    """
    Cumulative standard normal distribution function.
    """

    return .5 * (1 + erf(x / sqrt(2)))
