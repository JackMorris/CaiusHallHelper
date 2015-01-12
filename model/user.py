class User:
    """ Represents a single user of the system, with a Raven login, booking
    preferences and friends.
    """

    def __init__(self, crsid, password, booking_preferences):
        """ Construct a new User with the given members.
        :param crsid: crsid for this user, to be used for booking tasks
        :param password: password for this user, to be used for booking tasks
        :param booking_preferences: list, indexed by day index (0 for Sunday,
            1 for Monday, ...) where the elements are lists of Event instances
            that the user wishes to book in to on that day
        :return:
        """
        self._crsid = crsid
        self._password = password
        self._booking_preferences = booking_preferences

    @property
    def crsid(self):
        return self._crsid

    @property
    def password(self):
        return self._password

    def booking_preferences_for_date(self, date):
        """ Find the events this user wishes to book in to on `date`.
        :param date: datetime.date instance to retrieve events for
        :return: list of Event instances that this user wishes to book in to
        """
        day_index = int(date.strftime('%w'))
        return self._booking_preferences[day_index]

    def __str__(self):
        """
        :return: String representation of this user, in the format '<crsid>'
        """
        return self._crsid