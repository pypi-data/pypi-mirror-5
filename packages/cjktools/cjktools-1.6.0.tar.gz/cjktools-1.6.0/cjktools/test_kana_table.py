# -*- coding: utf-8 -*-
#
#  test_kana_table.py
#  cjktools
#

import unittest
import kana_table


def suite():
    test_suite = unittest.TestSuite((
        unittest.makeSuite(KanaTableTestCase),
    ))
    return test_suite


class KanaTableTestCase(unittest.TestCase):
    def setUp(self):
        self.table = kana_table.KanaTable.get_cached()
        self.test_script = u'AＡあア亜'

    def test_vowel_line(self):
        """
        Tests correct vowel line detection.
        """
        self.assertEqual(self.table.to_vowel_line(u'ご'), u'お')
        self.assertEqual(self.table.to_vowel_line(u'も'), u'お')
        self.assertEqual(self.table.to_vowel_line(u'さ'), u'あ')
        self.assertEqual(self.table.to_vowel_line(u'あ'), u'あ')
        self.assertEqual(self.table.to_vowel_line(u'ぎ'), u'い')

        self.assertEqual(self.table.to_vowel_line(u'わ'), u'あ')

    def test_consonant_line(self):
        self.assertEqual(self.table.to_consonant_line(u'わ'), None)

    def test_from_coords(self):
        """Rendering kana from (consonant, vowel) coordinates."""

        self.assertEqual(self.table.from_coords(u'か', u'お'), u'こ')
        self.assertEqual(self.table.from_coords(u'ぱ', u'え'), u'ぺ')

    def test_is_voiced(self):
        assert self.table.is_voiced(u'ば')
        assert self.table.is_voiced(u'ぱ')
        assert not self.table.is_voiced(u'は')
        assert self.table.is_voiced(u'だ')
        assert self.table.is_voiced(u'ざ')


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())
