"""Import CLTK corpora.
TODO: Fix so ``import_corpora()`` can take relative path.
TODO: Add https://github.com/cltk/pos_latin
"""

from cltk.corpus.chinese.corpora import CHINESE_CORPORA
from cltk.corpus.coptic.corpora import COPTIC_CORPORA
from cltk.corpus.greek.corpora import GREEK_CORPORA
from cltk.corpus.latin.corpora import LATIN_CORPORA
from cltk.corpus.sanskrit.corpora import SANSKRIT_CORPORA
from cltk.corpus.multilingual.corpora import MULTILINGUAL_CORPORA
from cltk.corpus.pali.corpora import PALI_CORPORA
from cltk.corpus.tibetan.corpora import TIBETAN_CORPORA
from cltk.utils.cltk_logger import logger
from cltk.utils.file_operations import make_cltk_path

import errno
from git import RemoteProgress
from git import Repo
import os
import sys
import shutil
from urllib.parse import urljoin


__author__ = ['Kyle P. Johnson <kyle@kyle-p-johnson.com>',
              'Stephen Margheim <stephen.margheim@gmail.com>']
__license__ = 'MIT License. See LICENSE.'


AVAILABLE_LANGUAGES = ['chinese', 'coptic', 'greek', 'latin', 'multilingual', 'pali', 'tibetan', 'sanskrit']
LANGUAGE_CORPORA = {'chinese': CHINESE_CORPORA,
                    'coptic': COPTIC_CORPORA,
                    'greek': GREEK_CORPORA,
                    'latin': LATIN_CORPORA,
                    'multilingual': MULTILINGUAL_CORPORA,
                    'pali': PALI_CORPORA,
                    'tibetan': TIBETAN_CORPORA,
                    'sanskrit': SANSKRIT_CORPORA,}


class CorpusImportError(Exception):
    """CLTK exception to use when something goes wrong importing corpora"""
    pass


class ProgressPrinter(RemoteProgress):
    """Class that implements progress reporting."""
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            percentage = '%.0f' % (100*cur_count / (max_count or 100.0))
            sys.stdout.write('Downloaded %s%% %s \r' % (percentage, message))


class CorpusImporter():
    """Import CLTK corpora."""

    def __init__(self, language):
        self.language = language.lower()
        self._setup_language_variables()

    def __repr__(self):
        """Representation string for ipython
        :rtype : str
        """
        return 'CorpusImporter for: {}'.format(self.language)

    def _setup_language_variables(self):
        """Check for availability of corpora for a language.
        TODO: Make the selection of available languages dynamic from dirs
        within ``corpora`` which contain a ``corpora.py`` file.
        """
        if self.language not in AVAILABLE_LANGUAGES:
            msg = 'Corpora not available for the "{}" language.'.format(self.language)
            raise CorpusImportError(msg)

    @property
    def list_corpora(self):
        """Show corpora available for the CLTK to download."""
        try:
            corpora = LANGUAGE_CORPORA[self.language]
            corpus_names = [corpus['name'] for corpus in corpora]
            return corpus_names
        except (NameError, KeyError) as error:
            msg = 'Corpus not available for language "{}": {}'.format(self.language, error)
            logger.error(msg)
            raise CorpusImportError(msg)

    @staticmethod
    def _copy_dir_recursive(src, dst):
        """Copy contents of one directory to another. `dst` dir cannot
        exist. Source: http://stackoverflow.com/a/1994840
        TODO: Move this to file_operations.py module.
        :type src: str
        :param src: Directory to be copied.
        :type dst: str
        :param dst: Directory to be created with contents of ``src``.
        """
        try:
            shutil.copytree(src, dst)
            logger.info('Files copied from %s to %s', src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
                logger.info('Files copied from %s to %s', src, dst)
            else:
                raise

    def _get_corpus_properties(self, corpus_name):
        """Check whether a corpus is available for import.
        :type corpus_name: str
        :param corpus_name: Name of available corpus.
        :rtype : str
        """
        try:
            corpora = LANGUAGE_CORPORA[self.language]
        except NameError as name_error:
            msg = 'Corpus not available for language ' \
                  '"%s": %s' % (self.language, name_error)
            logger.error(msg)
            raise CorpusImportError(msg)
        for corpus_properties in corpora:
            if corpus_properties['name'] == corpus_name:
                return corpus_properties
        msg = 'Corpus "%s" not available for the ' \
              '"%s" language.' % (corpus_name, self.language)
        logger.error(msg)
        raise CorpusImportError(msg)

    def import_corpus(self, corpus_name, local_path=None):  # pylint: disable=R0912
        """Download a remote or load local corpus into dir ``~/cltk_data``.
        TODO: maybe add ``from git import RemoteProgress``
        TODO: refactor this, it's getting kinda long
        :type corpus_name: str
        :param corpus_name: The name of an available corpus.
        :param local_path: str
        :param local_path: A filepath, required when importing local corpora.
        """
        corpus_properties = self._get_corpus_properties(corpus_name)
        location = corpus_properties['location']
        corpus_type = corpus_properties['type']
        if location == 'remote':
            git_uri = urljoin('https://github.com/cltk/', corpus_name + '.git')
            # self._download_corpus(corpus_type, corpus_name, path)
            type_dir = make_cltk_path(self.language, corpus_type)
            target_dir = os.path.join(type_dir, corpus_name)
            target_file = os.path.join(type_dir, corpus_name, 'README.md')
            # check if corpus already present
            # if not, clone
            if not os.path.isfile(target_file):
                if not os.path.isdir(type_dir):
                    os.makedirs(type_dir)
                try:
                    msg = "Cloning '{}' from '{}'".format(corpus_name, git_uri)
                    logger.info(msg)
                    Repo.clone_from(git_uri, target_dir, depth=1,
                                    progress=ProgressPrinter())
                except CorpusImportError as corpus_imp_err:
                    msg = "Git clone of '{}' failed: '{}'".format(git_uri, corpus_imp_err)
                    logger.error(msg)
            # if corpus is present, pull latest
            else:
                try:
                    repo = Repo(target_dir)
                    assert not repo.bare  # or: assert repo.exists()
                    git_origin = repo.remotes.origin
                    msg = "Pulling latest '{}' from '{}'.".format(corpus_name, git_uri)
                    logger.info(msg)
                    git_origin.pull()
                except CorpusImportError as corpus_imp_err:
                    msg = "Git pull of '{}' failed: '{}'".format(git_uri, corpus_imp_err)
                    logger.error(msg)
        elif location == 'local':
            msg = "Importing from local path: '{}'".format(local_path)
            logger.info(msg)
            if corpus_name in ('phi5', 'phi7', 'tlg'):
                # normalize local_path for checking dir
                local_path = local_path.rstrip(os.pathsep)
                if corpus_name == 'phi5':
                    # check for right corpus dir
                    if os.path.split(local_path)[1] != 'PHI5':
                        logger.info("Directory must be named 'PHI5'.")
                if corpus_name == 'phi7':
                    # check for right corpus dir
                    if os.path.split(local_path)[1] != 'PHI7':
                        logger.info("Directory must be named 'PHI7'.")
                if corpus_name == 'tlg':
                    # check for right corpus dir
                    if os.path.split(local_path)[1] != 'TLG_E':
                        logger.info("Directory must be named 'TLG_E'.")
                # move the dir-checking commands into a function
                originals_dir = make_cltk_path('originals')
                # check for `originals` dir; if not present mkdir
                if not os.path.isdir(originals_dir):
                    os.makedirs(originals_dir)
                    msg = "Wrote directory at '{}'.".format(originals_dir)
                    logger.info(msg)
                tlg_originals_dir = make_cltk_path('originals', corpus_name)
                # check for `originals/<corpus_name>`; if pres, delete
                if os.path.isdir(tlg_originals_dir):
                    shutil.rmtree(tlg_originals_dir)
                    msg = "Removed directory at '{}'.".format(tlg_originals_dir)
                    logger.info(msg)
                # copy_dir requires that target
                if not os.path.isdir(tlg_originals_dir):
                    self._copy_dir_recursive(local_path, tlg_originals_dir)
