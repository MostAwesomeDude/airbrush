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
