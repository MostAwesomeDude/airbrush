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
from unittest import TestCase

from lollerskates.formatting import canonical_champ


class TestCanonicalChamp(TestCase):

    cs = [
        "Cassiopeia",
        "Katarina",
        "Malphite",
        "Malzahar",
        "Sejuani",
    ]

    def test_exact(self):
        i = "Katarina"
        o = "Katarina"
        self.assertEqual(canonical_champ(self.cs, i), o)

    def test_lowercase(self):
        i = "katarina"
        o = "Katarina"
        self.assertEqual(canonical_champ(self.cs, i), o)

    def test_short(self):
        i = "Kat"
        o = "Katarina"
        self.assertEqual(canonical_champ(self.cs, i), o)

    def test_short_overlapping(self):
        i = "Mal"
        o = None
        self.assertEqual(canonical_champ(self.cs, i), o)

    def test_short_lowercase(self):
        i = "kat"
        o = "Katarina"
        self.assertEqual(canonical_champ(self.cs, i), o)

    def test_nickname(self):
        i = "pig"
        o = "Sejuani"
        self.assertEqual(canonical_champ(self.cs, i), o)

    def test_nickname_overlapping(self):
        i = "cassie"
        o = "Cassiopeia"
        self.assertEqual(canonical_champ(self.cs, i), o)
