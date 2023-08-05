# -*- coding: utf-8 -*-
#
#  test_alternations.py
#  cjktools
#

import unittest
import doctest
import alternations

from simplestats.comb import combinations


def suite():
    test_suite = unittest.TestSuite((
        unittest.makeSuite(AlternationsTestCase),
        doctest.DocTestSuite(alternations),
    ))
    return test_suite


class AlternationsTestCase(unittest.TestCase):
    def test_canonical_forms(self):
        base = (u'ゆっ', u'ぐり')
        seg1Cases = [u'ゆ' + c for c in u'いちりきつくっ']
        seg2Cases = [u'くり', u'ぐり']
        expected = set(combinations(seg1Cases, seg2Cases))

        self.assertEqual(set(alternations.canonical_forms(base)), expected)

    def test_canonical_segment_forms(self):
        voiced = u'ばり'
        expected = set([u'ばり', u'はり'])
        result = set(alternations.canonical_segment_forms(voiced, True, False))
        self.assertEqual(result, expected)

        self.assertEqual(alternations.canonical_segment_forms(u'わ'),
                         set([u'わ']))


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())
