from error import BookingServiceError
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

    def create_booking(self, date):
        """ Make booking for this user, based on their booking_preferences.
        :param date: datetime.date indicating the day the bookings should be
            made for
        :return: Booking instance that was made, or None if no booking was made
        """
        day_index = int(date.strftime('%w'))
        for event in self._booking_preferences[day_index]:
            try:
                return booking_service.create_booking(event, self, date)
            except BookingServiceError:
                # Try the next event
                continue
        return None

    def email_report(self, date):
        """ Email this user their report for `date`.
        :param date: datetime.date instance for the report to reflect
        """
        date_string = date.strftime('Report for %A, %B %d')
        email_html = '<h3><i>%s</i></h3>' % date_string
        email_html += self._bookings_report(date)
        email_html += self._friend_attendance_report(date)
        email_html = r'<center>' + email_html + r'</center>'
        email_service.send_email(self, email_html)

    def _bookings_report(self, date):
        """ Generate a HTML report containing booking information for `date`.
        :param date: datetime.date instance for date to check
        :return: String containing HTML report, describing which events this
            user's booked in to on `date` (along with menus if they exist)
        """
        report_html = ''
        bookings = self.get_all_bookings(date)
        if len(bookings) > 0:
            for booking in bookings:
                menu_text = booking_service.get_menu_text(booking.event, date)
                report_html += booking.html_report(menu_text)
        else:
            report_html += r'<i>No bookings</i><br /><br />'
        return '<h2>~ Bookings ~</h2>' + report_html

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
                report_html += r'<u><b>%s:</u></b><br /><br />' % event.name
                report_html += r'<br />'.join(friends_attending)
                report_html += r'<br /><br />'
        if len(report_html) == 0:
            report_html += r'<i>No friends in any hall</i>'
        return '<h2>~ Friends ~</h2>' + report_html

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