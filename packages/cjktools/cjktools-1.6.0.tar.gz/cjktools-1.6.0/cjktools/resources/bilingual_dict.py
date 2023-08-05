# -*- coding: utf-8 -*-
#
#  bilingual_dict.py
#  cjktools
#

"""
A generic bilingual dictionary class.
"""

from cjktools.enum import Enum
from cjktools.errors import NotYetImplementedError

ClashPolicy = Enum('Overwrite', 'Merge')


class BilingualDictionary(dict):
    """
    An abstract bilingual dictionary, containing headwords in one
    language and translated senses in another language. Homographs are
    stored as senses of the same lexeme, rather than being separate.
    """

    def __init__(self, format):
        """
        @param format: The format object for this dictionary.
        @type format: DictionaryFormat
        """
        self.format = format

    def update(self, rhs_dictionary, clash_policy=ClashPolicy.Overwrite):
        "Merges another dictionary into this one, in-place."
        if clash_policy == ClashPolicy.Merge:
            raise NotYetImplementedError

        return dict.update(self, rhs_dictionary)


class DictionaryEntry(object):
    """
    A single entry in a dictionary, representing a word, it's reading,
    and its translation into senses.
    """
    __slots__ = ('word', 'readings', 'senses')

    def __init__(self, word, readings, senses):
        "There should be either one reading, or one per sense."
        assert len(readings) == 1 or len(readings) == len(senses)
        self.word = word
        self.readings = readings
        self.senses = senses

    def update(self, rhs_entry):
        """
        Update this entry with readings and senses from another homograph.
        The additional readings and senses are added to this entry.

        @param rhs_entry: Another entry to update details from.
        @type rhs_entry: DictionaryEntry
        """
        if not self.word == rhs_entry.word:
            raise Exception("Can only merge homographs")

        #print 'Merging entries for %s' % self.word
        # If we have only one reading, pad to the number of senses so that
        # we have one sense per reading.
        if len(self.readings) == 1:
            self.readings = len(self.senses)*self.readings

        # Do the same for the rhs_entry.
        if len(rhs_entry.readings) == 1:
            rhs_entry.readings = len(rhs_entry.senses)*rhs_entry.readings

        # Add the readings and senses from the other entry.
        self.readings += rhs_entry.readings
        self.senses += rhs_entry.senses

    def senses_by_reading(self):
        "Returns a dictionary mapping reading to senses."
        result = {}
        if len(self.readings) > 1:
            assert len(self.senses) == len(self.readings)
            for reading, sense in zip(self.readings, self.senses):
                sense_list = result.setdefault(reading, [])
                sense_list.append(sense)
        else:
            unique_reading, = self.readings
            result[unique_reading] = self.senses[:]

        return result

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return u'<DictionaryEntry: %s (%s readings, %s senses)>' % (
            self.word,
            len(set(self.readings)),
            len(self.senses),
        )

    def __hash__(self):
        return hash(self.name, tuple(self.readings), tuple(self.senses))
