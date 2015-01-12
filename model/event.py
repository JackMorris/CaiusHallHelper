class Event:
    """ An Event represents a (possibly bookable) event that exists within the
    booking system.
    """

    def __init__(self, code, name):
        """ Construct a new Event instance.
        :param code: event code, used to identify this event within the
            booking system
        :param name: human-readable name for this event
        """
        self._code = code
        self._name = name

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    def url_for_date(self, date, booking_service_url):
        """ Return the URL for this event on `date`.
        :param date: datetime.date instance for the date to use for this URL
        :param booking_service_url: base URL for the booking service
        :return: full URL for this event, taking place on `date`
        """
        code_string = 'event=%d' % self.code
        date_string = 'date=%s' % date.strftime('%Y-%m-%d')
        return booking_service_url + '?' + code_string + '&' + date_string

    def __str__(self):
        """
        :return: String representation of this event, in the format
            '<name> [<code>]'
        """
        return '%s [%d]' % (self.name, self.code)


class Booking:
    """ A Booking represents a booking for an event that has been made. """

    def __init__(self, event, user, date):
        """ Construct a new booking.
        :param event: Event instance for the event that's booked in to
        :param user: User instance for the user that's booked in
        :param date: datetime.date instance for the day of the booking
        """
        self._event = event
        self._user = user
        self._date = date

    @property
    def event(self):
        return self._event

    @property
    def user(self):
        return self._user

    @property
    def date(self):
        return self._date

    def __str__(self):
        """
        :return: String representation of this booking, in the format
            '<user> - <date> - <event>'
        """
        return '%s - %s - %s' % (self._user, self._date, self._event)