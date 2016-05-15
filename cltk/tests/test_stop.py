"""Test cltk.stop."""

__author__ = 'Kyle P. Johnson <kyle@kyle-p-johnson.com>'
__license__ = 'MIT License. See LICENSE.'

from cltk.corpus.utils.importer import CorpusImporter
from cltk.stop.greek.stops import STOPS_LIST as GREEK_STOPS
from cltk.stop.latin.stops import STOPS_LIST as LATIN_STOPS
from cltk.utils.file_operations import make_cltk_path
from nltk.tokenize.punkt import PunktLanguageVars
import os
import unittest


class TestSequenceFunctions(unittest.TestCase):
    """Class for unittest"""

    def setUp(self):
        """Clone Greek models in order to test pull function and other model
        tests later.
        """
        corpus_importer = CorpusImporter('greek')
        corpus_importer.import_corpus('greek_models_cltk')
        _file = make_cltk_path('greek', 'model', 'greek_models_cltk', 'README.md')
        file_exists = os.path.isfile(_file)
        self.assertTrue(file_exists)

        corpus_importer = CorpusImporter('latin')
        corpus_importer.import_corpus('latin_models_cltk')
        _file = make_cltk_path('latin', 'model', 'latin_models_cltk', 'README.md')
        file_exists = os.path.isfile(_file)
        self.assertTrue(file_exists)

    def test_greek_stopwords(self):
        """Test filtering Greek stopwords."""
        sentence = 'Ἅρπαγος δὲ καταστρεψάμενος Ἰωνίην ἐποιέετο στρατηίην \
        ἐπὶ Κᾶρας καὶ Καυνίους καὶ Λυκίους, ἅμα ἀγόμενος καὶ Ἴωνας καὶ \
        Αἰολέας.'
        lowered = sentence.lower()
        punkt = PunktLanguageVars()
        tokens = punkt.word_tokenize(lowered)
        no_stops = [w for w in tokens if w not in GREEK_STOPS]
        target_list = ['ἅρπαγος', 'καταστρεψάμενος', 'ἰωνίην', 'ἐποιέετο',
                       'στρατηίην', 'κᾶρας', 'καυνίους', 'λυκίους', ',',
                       'ἅμα', 'ἀγόμενος', 'ἴωνας', 'αἰολέας.']
        self.assertEqual(no_stops, target_list)

    def test_latin_stopwords(self):
        """Test filtering Latin stopwords."""
        sentence = 'Quo usque tandem abutere, Catilina, patientia nostra?'
        lowered = sentence.lower()
        punkt = PunktLanguageVars()
        tokens = punkt.word_tokenize(lowered)
        no_stops = [w for w in tokens if w not in LATIN_STOPS]
        target_list = ['usque', 'tandem', 'abutere', ',', 'catilina', ',',
                       'patientia', 'nostra', '?']
        self.assertEqual(no_stops, target_list)

if __name__ == '__main__':
    unittest.main()
