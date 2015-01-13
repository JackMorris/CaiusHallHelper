from service import booking_service, email_service
import re


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

    def email_report(self, date):
        """ Email this user their report for `date`.
        :param date: datetime.date instance for the report to reflect.
        """
        email_html = ''
        for booking in self.get_all_bookings(date):
            email_html += r"You're booked into <b>%s</b>." % booking.event.name
            menu_text = booking_service.get_menu_text(booking.event, date)
            if menu_text is None:
                email_html += r" (no menu found)"
            else:
                menu_text = re.sub(r'\n', r'<br />', menu_text)
                email_html += r" The menu:<br />" + menu_text
            email_html += r"<br /><br />"
        email_service.send_email(self, email_html)

    def get_all_bookings(self, date):
        """ Find all bookings for this user on `date`.
        :param date: datetime.date instance for date to check
        :return: list of Booking instances for all bookings on `date`
        """
        all_events = booking_service.get_available_events()
        bookings = []
        for event in all_events:
            if booking_service.is_event_occurring(event, date):
                booking = booking_service.get_booking(event, self, date)
                if booking is not None:
                    bookings.append(booking)
        return bookings

    def __str__(self):
        """
        :return: String representation of this user, in the format '<crsid>'
        """
        return self._crsid