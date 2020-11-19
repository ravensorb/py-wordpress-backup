""" wpsite """

# pylint: disable=line-too-long

import os
import logging
from pathlib import Path
from wpconfigr import WpConfigFile

from wpdatabase2.classes import WpCredentials
from wpdatabase2.classes import WpConnection
from wpdatabase2.exceptions import InvalidArgumentsError

class WpSite(WpConnection):
    """ WpSite class """

    ###########################################################################
    def __init__(self, site_home, site_url, site_path, db_host, db_name, credentials, admin_credentials = None):
        """
        Constructor

        Args:
            site_home (str):                the wordpress site home
            site_url (str):                 the wordpress site url
            site_path (str):                the path to the wordpress site
            db_host (str):                  the database host name
            db_name (str):                  the database name
            credentials (WpCredentails):    the database credentials
        """
        super().__init__(db_host, db_name, credentials)

        self.log = logging.getLogger(__name__)

        self.site_home = site_home
        self.site_url = site_url

        if admin_credentials is not None and not isinstance(admin_credentials, WpCredentials):
            raise TypeError("admin_crednetials must be an instance of WpCredentials")

        self.admin_credentials = admin_credentials if admin_credentials is not None else credentials

        if "wp-config.php" in site_path:
            site_path = Path(site_path).parent

        self.site_path = site_path

        try:
            self.log.debug("SiteHome='%s', SiteUrl='%s', SitePath='%s', DatabaseName='%s', Database Host='%s', Database  Port='%s'",
                           self.site_home,
                           self.site_url,
                           self.site_path,
                           self.db_name,
                           self.db_host,
                           self.db_port
                           )
        except Exception: # pylint: disable=broad-except
            pass

    ###########################################################################
    @classmethod
    def from_wp_path(cls, wp_path):
        """ Creates an instance of WpSite from the wp-config.php file """

        wp_config_file_name = wp_path

        if "wp-config.php" not in wp_config_file_name:
            wp_config_file_name = os.path.join(wp_config_file_name,
                                               'wp-config.php')

        wp_config = WpConfigFile(wp_config_file_name)

        return cls.from_wp_config(wp_config, wp_path)

    ###########################################################################
    @classmethod
    def from_wp_config(cls, wp_config, site_path):
        """ Create an instance of WpSite from WpConfigFile """
        if not isinstance(wp_config, WpConfigFile):
            raise InvalidArgumentsError('wp_config must be an instance of WpConfigFile')

        return cls(site_home=wp_config.get('WP_HOME'),
                   site_url=wp_config.get('WP_SITEURL'),
                   site_path=site_path,
                   db_host=wp_config.get('DB_HOST'),
                   db_name=wp_config.get('DB_NAME'),
                   credentials=WpCredentials.from_username_and_password(username=wp_config.get('DB_USER'),
                                                                        password=wp_config.get('DB_PASSWORD')))

    ###########################################################################
    @property
    def site_host(self):
        """ Access Site Home """
        return self._site_host

    ###########################################################################
    @site_host.setter
    def site_host(self, value):
        """ Set Site Home """
        self._site_host = value

    ###########################################################################
    @property
    def site_url(self):
        """ Access Site Url """
        return self._site_url

    ###########################################################################
    @site_url.setter
    def site_url(self, value):
        """ Set Site Url """
        self._site_url = value

    ###########################################################################
    @property
    def site_path(self):
        """ Access Site Path """
        return self._site_path

    ###########################################################################
    @site_path.setter
    def site_path(self, value):
        """ Set Site Path """
        self._site_path = value

    ###########################################################################
    @property
    def admin_credentials(self):
        """ Access Admin Credentials """
        return self._admin_credentials

    ###########################################################################
    @admin_credentials.setter
    def admin_credentials(self, value):
        """ Set Admin Credentials """
        self._admin_credentials = value

    ###########################################################################
    @property
    def wp_config_filename(self):
        """ Access Wordpress Config file name """
        return os.path.join(self.site_path, 'wp-config.php')
