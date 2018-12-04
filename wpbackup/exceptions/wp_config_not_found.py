""" Raised when "wp-config.php" cannot be found. """


class WpConfigNotFoundError(Exception):
    """
    Raised when "wp-config.php" cannot be found.

    Args:
        wp_directory (str): Directory where "wp-config.php" was expected.
    """

    def __init__(self, wp_directory):
        tmp = ('This version of wordpressbackup expects "wp-config.php" to '
               'exist in the root of the WordPress directory ("{}").')
        msg = tmp.format(wp_directory)
        super().__init__(msg)
