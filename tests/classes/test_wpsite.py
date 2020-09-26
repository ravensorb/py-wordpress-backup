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
                          db_host='127.0.0.1:3306',
                          db_name='wp_default',
                          credentials=WpCredentials.from_username_and_password('username', 'password')) # pylint: disable=line-too-long

        self.assertIsInstance(instance, WpSite)
        self.assertEqual(instance.site_home, 'https://wordpress.local')
        self.assertEqual(instance.site_url, 'https://wordpress.local')
        self.assertEqual(instance.site_path, '/var/www/html')
        self.assertEqual(instance.db_host, '127.0.0.1')
        self.assertEqual(instance.db_port, '3306')
        self.assertEqual(instance.db_name, 'wp_default')
        self.assertIsInstance(instance.credentials, WpCredentials)
        self.assertEqual(instance.credentials.username, 'username')
        self.assertEqual(instance.credentials.password, 'password')

    def test_wpsite_from_wp_config_file_name(self):
        """ Test WpSite constructor """
        instance = WpSite.from_wp_config_file_name('tests/data/wp-config.php')

        self.assertTrue(isinstance(instance, WpSite))
        self.assertEqual(instance.db_name, 'wordpress')

    def test_wpsite_from_wp_config(self):
        """ Test  WpSite Constructor """

    def test_wpsite_properties_db_host_none(self):
        """ Test WpSite properties """

        instance = WpSite(site_home='https://wordpress.local',
                          site_url='https://wordpress.local',
                          site_path='/var/www/html',
                          db_host=None,
                          db_name='wp_default',
                          credentials=WpCredentials.from_username_and_password('username', 'password')) # pylint: disable=line-too-long

        self.assertIsInstance(instance, WpSite)
        self.assertEqual(instance.site_home, 'https://wordpress.local')
        self.assertEqual(instance.site_url, 'https://wordpress.local')
        self.assertEqual(instance.site_path, '/var/www/html')
        self.assertIsNone(instance.db_host)
        self.assertEqual(instance.db_name, 'wp_default')
        self.assertEqual(instance.credentials.username, 'username')
        self.assertEqual(instance.credentials.password, 'password')

    def test_wpsite_properties_db_name_none(self):
        """ Test WpSite properties """

        instance = WpSite(site_home='https://wordpress.local',
                          site_url='https://wordpress.local',
                          site_path='/var/www/html',
                          db_host='127.0.0.1',
                          db_name=None,
                          credentials=WpCredentials.from_username_and_password('username', 'password')) # pylint: disable=line-too-long

        self.assertIsInstance(instance, WpSite)
        self.assertEqual(instance.site_home, 'https://wordpress.local')
        self.assertEqual(instance.site_url, 'https://wordpress.local')
        self.assertEqual(instance.site_path, '/var/www/html')
        self.assertEqual(instance.db_host, '127.0.0.1')
        self.assertIsNone(instance.db_name)
        self.assertEqual(instance.credentials.username, 'username')
        self.assertEqual(instance.credentials.password, 'password')

    def test_wpsite_properties_credentials_username_none(self):
        """ Test WpSite properties """

        instance = WpSite(site_home='https://wordpress.local',
                          site_url='https://wordpress.local',
                          site_path='/var/www/html',
                          db_host='127.0.0.1',
                          db_name='wp_default',
                          credentials=WpCredentials.from_username_and_password(None, 'password')) # pylint: disable=line-too-long

        self.assertIsInstance(instance, WpSite)
        self.assertEqual(instance.site_home, 'https://wordpress.local')
        self.assertEqual(instance.site_url, 'https://wordpress.local')
        self.assertEqual(instance.site_path, '/var/www/html')
        self.assertEqual(instance.db_host, '127.0.0.1')
        self.assertEqual(instance.db_name, 'wp_default')
        self.assertIsNone(instance.credentials)
        
    def test_wpsite_properties_credentials_password_none(self):
        """ Test WpSite properties """

        instance = WpSite(site_home='https://wordpress.local',
                          site_url='https://wordpress.local',
                          site_path='/var/www/html',
                          db_host='127.0.0.1',
                          db_name='wp_default',
                          credentials=WpCredentials.from_username_and_password('username', None)) # pylint: disable=line-too-long

        self.assertIsInstance(instance, WpSite)
        self.assertEqual(instance.site_home, 'https://wordpress.local')
        self.assertEqual(instance.site_url, 'https://wordpress.local')
        self.assertEqual(instance.site_path, '/var/www/html')
        self.assertEqual(instance.db_host, '127.0.0.1')
        self.assertEqual(instance.db_name, 'wp_default')
        self.assertIsNone(instance.credentials)


if __name__ == '__main__':
    unittest.main()
