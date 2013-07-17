from unittest import TestCase

from lollerskates.statistics import cdf

class TestCDF(TestCase):

    def test_center(self):
        self.assertAlmostEqual(cdf(0), 0.5)
