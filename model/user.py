from service import booking_service, email_service


class User:
    """ Represents a single user of the system, with a Raven login, booking
    preferences and friends.
    """

    def __init__(self, crsid, password, friends, booking_preferences):
        """ Construct a new User with the given members.
        :param crsid: crsid for this user, to be used for booking tasks
        :param password: password for this user, to be used for booking tasks
        :param friends: list of strings for the names of people who's
            attendance you wish to be notified of
        :param booking_preferences: list, indexed by day index (0 for Sunday,
            1 for Monday, ...) where the elements are lists of Event instances
            that the user wishes to book in to on that day
        :return:
        """
        self._crsid = crsid
        self._password = password
        self._friends = friends
        self._booking_preferences = booking_preferences

    @property
    def crsid(self):
        return self._crsid

    @property
    def password(self):
        return self._password

    @property
    def friends(self):
        return self._friends

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
        :param date: datetime.date instance for the report to reflect
        """
        email_html = ''
        bookings = self.get_all_bookings(date)
        if len(bookings) > 0:
            for booking in bookings:
                menu_text = booking_service.get_menu_text(booking.event, date)
                email_html += booking.html_report(menu_text)
        else:
            email_html += r'No bookings<br /><br />'
        email_html += self._friend_attendance_report(date)
        email_service.send_email(self, email_html)

    def _friend_attendance_report(self, date):
        """ Generate a HTML report containing the event attendance for this
        user's friends.
        :param date: datetime.date instance for date to check
        :return: String containing HTML report, describing which events each
            of this user's friends are attending on `date`
        """
        report_html = ''
        for event in booking_service.get_available_events():
            if not booking_service.is_event_occurring(event, date):
                continue
            attendees = booking_service.get_attendee_names(event, date)

            def predicate(name):
                name = name.lower()
                for friend in self.friends:
                    if friend.lower() in name:
                        return True
                return False
            friends_attending = filter(predicate, attendees)
            if len(friends_attending) > 0:
                report_html += r'Friends attending %s:<br>' % event.name
                report_html += r'<br />'.join(friends_attending)
                report_html += r'<br /><br />'
        if len(report_html) == 0:
            report_html += r'No friends in any hall'
        return report_html

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