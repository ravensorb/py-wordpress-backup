""" Tests for the WpInternalBackup class. """

# pylint: disable=line-too-long

import unittest
import shutil
import json
import os
import logging
import tempfile

from wpconfigr import WpConfigFile

from wpbackup2 import WpSite
from wpbackup2.classes.wp_internal_restore import WpInternalRestore
#from wpbackup2.classes.wp_internal_restore import WpRestoreMode

LOG = logging.getLogger(__name__)

class WpInternalBackupTestCase(unittest.TestCase):
    """ Tests for the WpSite class. """
    _wp_site = None
    _temp_dir = tempfile.TemporaryDirectory(prefix='test_wpbackup_')
    _what_if = False

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
    #########################################################################
    def test_update_wpconfig(self):
        """ Test update wp-config file """

        self._setup_test_data()

        wp_config_orig = WpConfigFile(self._wp_site.wp_config_filename)
        db_name_orig = wp_config_orig.get('DB_NAME')

        self.assertEqual(db_name_orig, self._wp_site.db_name)

        self._wp_site.db_name = "testdb"

        instance = WpInternalRestore(self._wp_site, self._temp_dir.name, self._what_if)
        instance.__update_config()

        wp_config_new = WpConfigFile(self._wp_site.wp_config_filename)
        db_name_new = wp_config_new.get('DB_NAME')

        self._cleanup_test_data()

        self.assertEqual(db_name_new, self._wp_site.db_name)

    #########################################################################
    def test_wpbackup_restore(self):
        """ Test WpBackup restore  """

        self._setup_test_data()

        #instance = WpInternalRestore()

        #instance.restore(site, "test_backup.tar.gz")

        self._cleanup_test_data()

if __name__ == '__main__':
    unittest.main()
