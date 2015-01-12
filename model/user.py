class User:
    """ Represents a single user of the system, with a Raven login, booking
    preferences and friends.
    """

    def __init__(self, crsid, password):
        """ Construct a new User with the given credentials. """
        self._crsid = crsid
        self._password = password

    @property
    def crsid(self):
        return self._crsid

    @property
    def password(self):
        return self._password

    def __str__(self):
        """
        :return: String representation of this user, in the format '<crsid>'
        """
        return self._crsid