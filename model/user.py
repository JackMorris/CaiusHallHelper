from service import booking_service


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

    def create_bookings(self, date):
        """ Make bookings for this user, based on their booking_preferences.
        :param date: datetime.date indicating the day the bookings should be
            made for
        :return: list of Booking instances that were made
        :raises BookingServiceError if the booking could not be made
        """
        day_index = int(date.strftime('%w'))
        events_to_book = self._booking_preferences[day_index]
        bookings = []
        for event in events_to_book:
            booking = booking_service.create_booking(event, self, date)
            bookings.append(booking)
        return bookings

    def __str__(self):
        """
        :return: String representation of this user, in the format '<crsid>'
        """
        return self._crsid