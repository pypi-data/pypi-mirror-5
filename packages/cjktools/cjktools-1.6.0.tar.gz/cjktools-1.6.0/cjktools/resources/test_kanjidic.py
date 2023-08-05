# -*- coding: utf-8 -*-
#
#  test_kanjidic.py
#

import unittest
from kanjidic import Kanjidic


def suite():
    test_suite = unittest.TestSuite((
        unittest.makeSuite(KanjidicTestCase)
    ))
    return test_suite


class KanjidicTestCase(unittest.TestCase):
    def setUp(self):
        self.kd = Kanjidic()

    def test_lookup(self):
        "Tests lookup of some kanji using kanjidic."
        key = u'冊'
        result = self.kd[key]
        self.assertEqual(result.stroke_count, 5)
        self.assertEqual(result.skip_code, (4, 5, 1))

        key = u'悪'
        result = self.kd[key]
        self.assertEqual(result.frequency, 530)

    def test_error_case(self):
        key = u'粉'
        assert u'こ'in self.kd[key].all_readings


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())
