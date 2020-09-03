""" wpsite """

# pylint: disable=invalid-name

import logging

LOG = logging.getLogger(__name__)

class WpSite:
    """ WpSite class """
    _siteHost = None
    _siteUrl = None
    _sitePath = None
    _dbName = None
    _dbHost = None
    _dbPort = 3306
    _dbUser = None
    _dbPassword = None

    ###########################################################################
    def __init__(self, siteHost, siteUrl, sitePath, dbName, dbHost, dbPort, dbUser, dbPassword): # pylint: disable=line-too-long
        self.SiteHost = siteHost
        self.SiteUrl = siteUrl
        self.SitePath = sitePath
        self.DatabaseName = dbName
        self.DatabaseHost = dbHost
        self.DatabasePort = dbPort
        self.DatabaseUser = dbUser
        self.DatabasePassword = dbPassword

        LOG.debug("SiteHost='%s', SiteUrl='%s', SitePath='%s', DatabaseName='%s', Database Host='%s', Database  Port='%s', Datebase User='%s', Database Password='%s'", # pylint: disable=line-too-long
                  self.SiteHost,
                  self.SiteUrl,
                  self.SitePath,
                  self.DatabaseName,
                  self.DatabaseHost,
                  self.DatabasePort,
                  self.DatabaseUser,
                  self.DatabasePassword
                  )

    ###########################################################################
    @property
    def SiteHost(self):
        """ Access Site Host """
        return self._siteHost

    ###########################################################################
    @SiteHost.setter
    def SiteHost(self, value):
        """ Set Site Host """
        self._siteHost = value

    ###########################################################################
    @property
    def SiteUrl(self):
        """ Access Site Url """
        return self._siteUrl

    ###########################################################################
    @SiteUrl.setter
    def SiteUrl(self, value):
        """ Set Site Url """
        self._siteHost = value

    ###########################################################################
    @property
    def SitePath(self):
        """ Access Site Path """
        return self._sitePath

    ###########################################################################
    @SitePath.setter
    def SitePath(self, value):
        """ Set Site Path """
        self._sitePath = value

    ###########################################################################
    @property
    def DatabaseName(self):
        """ Access Database Name """
        return self._dbName

    ###########################################################################
    @DatabaseName.setter
    def DatabaseName(self, value):
        """ Set Database Name """
        self._dbName = value

    ###########################################################################
    @property
    def DatabaseHost(self):
        """ Access Database Host """
        return self._dbHost

    ###########################################################################
    @DatabaseHost.setter
    def DatabaseHost(self, value):
        """ Set Database Host """
        self._dbHost = value

    ###########################################################################
    @property
    def DatabasePort(self):
        """ Access Database Port """
        return self._dbPort

    ###########################################################################
    @DatabasePort.setter
    def DatabasePort(self, value):
        """ Set Database Port """
        self._dbPort = value

    ###########################################################################
    @property
    def DatabaseUser(self):
        """ Access Database User """
        return self._dbUser

    ###########################################################################
    @DatabaseUser.setter
    def DatabaseUser(self, value):
        """ Set Database User """
        self._dbUser = value

    ###########################################################################
    @property
    def DatabasePassword(self):
        """ Access Database Password """
        return self._dbPassword

    ###########################################################################
    @DatabasePassword.setter
    def DatabasePassword(self, value):
        """ Set Database Password """
        self._dbPassword = value
