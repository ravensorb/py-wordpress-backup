""" Tests for the WpSite class. """

import unittest

from wpdatabase2.classes import WpCredentials
from wpbackup2 import WpSite

class WpSiteTestCase(unittest.TestCase):
    """ Tests for the WpSite class. """
    def test_wpsite_properties(self):
        """ Test WpSite properties """

        instance = WpSite(site_home='https://wordpress.local',
                          site_url='https://wordpress.local',
                          site_path='/var/www/html',
                          db_host='127.0.0.1',
                          db_name='wp_default',
                          credentials=WpCredentials.from_username_and_password('root', 'password')) # pylint: disable=line-too-long

        self.assertTrue(isinstance(instance, WpSite))
        self.assertEqual(instance.site_home, 'https://wordpress.local')
        self.assertEqual(instance.site_url, 'https://wordpress.local')
        self.assertEqual(instance.site_path, '/var/www/html')
        self.assertEqual(instance.db_host, '127.0.0.1')
        self.assertTrue(isinstance(instance.credentials, WpCredentials))
        self.assertEqual(instance.credentials.username, 'root')
        self.assertEqual(instance.credentials.password, 'password')

    def test_wpsite_from_wp_config_file_name(self):
        """ Test WpSite constructor """
        instance = WpSite.from_wp_config_file_name('tests/data/wp-config.php')

        self.assertTrue(isinstance(instance, WpSite))
        self.assertEqual(instance.db_name, 'wordpress')

    def test_wpsite_from_wp_config(self):
        """ Test  WpSite Constructor """

if __name__ == '__main__':
    unittest.main()
