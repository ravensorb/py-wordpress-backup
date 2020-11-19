""" Tests for the WpBackup class. """

import unittest
import shutil
#from pathlib import Path
import json
import os
import logging
import tempfile

from wpbackup2 import WpSite
from wpbackup2 import WpBackup

LOG = logging.getLogger(__name__)

class WpBackupTestCase(unittest.TestCase):
    """ Tests for the WpSite class. """
    _wp_site = None
    _temp_dir = tempfile.TemporaryDirectory(prefix='test_wpbackup_')
    _what_if = True

    #########################################################################
    def __del__(self):
        self._temp_dir = None

    #########################################################################
    def _load_settings(self):
        cwd = os.getcwd()
        settings_file_path = os.path.join(cwd, "tests", "test_settings.json")

        if not os.path.exists(settings_file_path):
            return None

        with open(settings_file_path) as file:
            db_settings = json.load(file)

            return db_settings

    #########################################################################
    def _setup_test_data(self):
        LOG.debug('Setting up test data in %s', self._temp_dir.name)

        cfg_path = os.path.join(os.getcwd(), 'tests/data/wp-config.php')
        os.makedirs(self._temp_dir.name, exist_ok=True)
        shutil.copy2(cfg_path, self._temp_dir.name + '/wp-config.php')

        self._wp_site = WpSite.from_wp_path(self._temp_dir.name)

    #########################################################################
    def _cleanup_test_data(self):
        LOG.debug('Cleaning  up test data')
        #shutil.rmtree(self._wp_site.site_path)

    #########################################################################
    def test_wpbackup_backup(self):
        """ Test WpBackup backup  """
        self._setup_test_data()

        instance = WpBackup(self._what_if)
        instance.backup(self._wp_site, "somerandomname.tar.gz")

        self._cleanup_test_data()

    #########################################################################
    def test_wpbackup_restore(self):
        """ Test WpBackup restore  """

        self._setup_test_data()

        instance = WpBackup(self._what_if)
        instance.restore(self._wp_site, "somerandomname.tar.gz")

        self._cleanup_test_data()

if __name__ == '__main__':
    unittest.main()
