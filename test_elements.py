from unittest import TestCase

from elements import match_word

class TestMatchWord(TestCase):

    def test_no_matches(self):
        self.assertEqual([], match_word("jazz"))

    def test_single_match(self):
        self.assertEqual([["i", "v", "y"]], match_word("ivy"))

    def test_multiple_matches(self):
        self.assertEqual([['no', 'se'], ['n', 'o', 'se']], match_word("nose"))
