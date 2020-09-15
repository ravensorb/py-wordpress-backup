""" Tests for the WpBackup class. """

import unittest
import shutil
#from pathlib import Path
import json
import os
import logging
import tempfile

from wpconfigr import WpConfigFile
from wpdatabase2.classes import WpCredentials
from wpbackup2 import WpSite
from wpbackup2 import WpBackup

LOG = logging.getLogger(__name__)

class WpBackupTestCase(unittest.TestCase):
    """ Tests for the WpSite class. """
    _wp_site = None
    _temp_dir = tempfile.TemporaryDirectory(prefix='test_wpbackup_')

    def __del__(self):
        self._temp_dir = None

    def _load_settings(self):
        cwd = os.getcwd()
        settings_file_path = os.path.join(cwd, "tests", "test_settings.json")

        if not os.path.exists(settings_file_path):
            return None

        with open(settings_file_path) as f:
            db_settings = json.load(f)

            return db_settings

    def _setup_test_data(self):
        LOG.debug('Setting up test data in %s', self._temp_dir.name)

        cfg_path = os.path.join(os.getcwd(), 'tests/data/wp-config.php')
        os.makedirs(self._temp_dir.name, exist_ok=True)
        shutil.copy2(cfg_path, self._temp_dir.name + '/wp-config.php')

        self._wp_site = WpSite.from_wp_config_file_name(self._temp_dir.name)

    def _cleanup_test_data(self):
        LOG.debug('Cleaning  up test data')
        #shutil.rmtree(self._wp_site.site_path)

    def test_update_wpconfig(self):
        """ Test update wp-config file """

        self._setup_test_data()

        instance = WpBackup()

        wp_config_orig = WpConfigFile(self._wp_site.wp_config_filename)
        db_name_orig = wp_config_orig.get('DB_NAME')

        self.assertEqual(db_name_orig, self._wp_site.db_name)

        self._wp_site.db_name = "testdb"

        instance._update_config(wp_site=self._wp_site, # pylint: disable=protected-access
                                wp_config_filename=self._wp_site.wp_config_filename) # pylint: disable=line-too-long

        wp_config_new = WpConfigFile(self._wp_site.wp_config_filename)
        db_name_new = wp_config_new.get('DB_NAME')

        self._cleanup_test_data()

        self.assertEqual(db_name_new, self._wp_site.db_name)

    def test_wpbackup_backup(self):
        """ Test WpBackup backup  """
        self._setup_test_data()

        instance = WpBackup()

        #instance.backup(self._wp_site, '/tmp/wp-backup-test.tar.gz')

        #instance.backup(site, "test_backup.tar.gz")
        self._cleanup_test_data()


    def test_wpbackup_restore(self):
        """ Test WpBackup restore  """

        self._setup_test_data()

        #instance = WpBackup()

        #instance.restore(site, "test_backup.tar.gz")

        self._cleanup_test_data()

if __name__ == '__main__':
    unittest.main()
